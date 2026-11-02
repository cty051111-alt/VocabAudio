"""Build and verify the portable Windows package from this source checkout."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'VocabAudio 2.1 Beta self-test: PASS (offline OCR, UI, FFmpeg)'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=ROOT, check=True)
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
               '--onefile', '--windowed', '--name', 'VocabAudio',
               '--icon', 'assets/VocabAudio.ico', '--add-data', 'assets;assets',
               '--collect-all', 'imageio_ffmpeg', '--collect-all', 'pymupdf',
               '--collect-all', 'rapidocr', '--collect-all', 'onnxruntime',
               '--collect-data', 'omegaconf', '--hidden-import', 'fitz',
               '--exclude-module', 'tkinter', '--exclude-module', 'pytest',
               '--exclude-module', 'rapidocr.inference_engine.pytorch',
               '--exclude-module', 'rapidocr.inference_engine.paddle',
               '--exclude-module', 'rapidocr.inference_engine.openvino',
               '--exclude-module', 'rapidocr.inference_engine.tensorrt',
               '--exclude-module', 'rapidocr.inference_engine.mnn', 'app.py']
    # Never resolve runtime DLLs from unrelated apps added to the host PATH.
    system = Path(os.environ.get('SystemRoot', 'C:/Windows'))
    environment = os.environ.copy()
    environment['PATH'] = os.pathsep.join([str(Path(sys.executable).parent),
                                          sys.base_prefix, str(system / 'System32'), str(system)])
    import PySide6
    qt_directory = Path(PySide6.__file__).parent
    for name in ('MSVCP140.dll', 'MSVCP140_1.dll', 'MSVCP140_2.dll',
                 'VCRUNTIME140.dll', 'VCRUNTIME140_1.dll'):
        path = qt_directory / name
        if path.exists():
            command[-1:-1] = ['--add-binary', f'{path};.']
    subprocess.run(command, cwd=ROOT, env=environment, check=True)
    source_archive = output / 'VocabAudio_2.1_Beta_Source.zip'
    with zipfile.ZipFile(source_archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        sources = [p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in ('.py', '.md', '.txt', '.bat')]
        sources += [ROOT / 'LICENSE', ROOT / '.gitignore']
        for directory in ('assets', 'scripts', 'tests', 'docs', 'licenses', '.github'):
            sources += [p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        for file in sources:
            bundle.write(file, Path('VocabAudio_2.1_Beta_Source') / file.relative_to(ROOT))
    with tempfile.TemporaryDirectory(prefix='vocabaudio_release_') as temporary:
        package = Path(temporary) / 'VocabAudio_2.1_Beta'
        package.mkdir()
        shutil.copy2(ROOT / 'dist/VocabAudio.exe', package)
        for filename in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'Uninstall_VocabAudio.bat'):
            shutil.copy2(ROOT / filename, package)
        shutil.copy2(source_archive, package / 'SOURCE.zip')
        shutil.copy2(ROOT / 'build-environment.txt', package)
        shutil.copytree(ROOT / 'licenses', package / 'licenses')
        (package / 'scripts').mkdir()
        shutil.copy2(ROOT / 'scripts/uninstall.ps1', package / 'scripts')
        shutil.copy2(ROOT / 'docs/QUICK_START_EXE.txt', package / 'START_HERE.txt')
        # Include notices supplied with every installed dependency, without secrets.
        for distribution in importlib.metadata.distributions():
            name = distribution.metadata.get('Name', 'unknown')
            for file in distribution.files or []:
                if any(token in str(file).lower() for token in ('license', 'copying', 'notice')):
                    path = Path(distribution.locate_file(file))
                    if path.is_file() and path.suffix.lower() in ('', '.txt', '.md', '.rst'):
                        destination = package / 'licenses' / name / Path(str(file))
                        # Wheel paths must not escape the dependency's notice folder.
                        if '..' in file.parts or file.is_absolute():
                            continue
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, destination)
        report = package / 'self-test.txt'
        process = subprocess.run([str(package / 'VocabAudio.exe'), '--self-test',
                                  '--self-test-report', str(report)], cwd=package,
                                 timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if process.returncode != 0 or not report.exists() or report.read_text(encoding='utf-8') != REPORT:
            raise RuntimeError(f'EXE runtime self-test failed ({process.returncode})')
        archive = output / 'VocabAudio_2.1_Beta_Windows.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            for file in package.rglob('*'):
                if file.is_file():
                    bundle.write(file, file.relative_to(package.parent))
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.testzip() is None
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (output / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n', encoding='ascii')
        print(f'Verified package: {archive}\nSHA256: {digest}', flush=True)


if __name__ == '__main__':
    main()
