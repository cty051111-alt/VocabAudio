"""VocabAudio desktop entry point and offline runtime check."""
from pathlib import Path
import subprocess
import sys


def self_test():
    import socket
    from unittest.mock import patch
    from PySide6.QtWidgets import QApplication
    from desktop_ui import App
    from image_ocr import recognize_image, smoke_image, words_from_ocr_text
    from vocab_core import deduplicate, ffmpeg_executable, youdao_url
    import requests, docx, pymupdf

    def offline(*args, **kwargs):
        raise RuntimeError("Offline self-test attempted network access")

    with patch.object(socket.socket, "connect", offline):
        assert deduplicate(["apple", "banana", "apple"]) == ["apple", "banana"]
        assert "type=2" in youdao_url("apple", "us")
        result = recognize_image(smoke_image())
        assert words_from_ocr_text(result.text) == ["apple", "banana"], result.text
        application = QApplication.instance() or QApplication([])
        application.setStyle("Fusion")
        window = App()
        for theme in ("light", "dark"):
            window.theme = theme
            window.apply_theme()
            window.show()
            application.processEvents()
            assert window.image_btn.isVisible()
        window.hide()
        window.timer.stop()
        # No settings are changed by the offline check.
        window.deleteLater()
        application.processEvents()
    result = subprocess.run([ffmpeg_executable(), "-version"], capture_output=True,
                            timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert result.returncode == 0
    report = "VocabAudio 2.1 Beta self-test: PASS (offline OCR, UI, FFmpeg)"
    if sys.stdout is not None:
        print(report, flush=True)
    if "--self-test-report" in sys.argv:
        Path(sys.argv[sys.argv.index("--self-test-report") + 1]).write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        try:
            sys.exit(self_test())
        except Exception:
            import traceback
            detail = traceback.format_exc()
            if '--self-test-report' in sys.argv:
                Path(sys.argv[sys.argv.index('--self-test-report') + 1]).write_text(
                    'FAIL\n' + detail, encoding='utf-8')
            if sys.stderr is not None:
                print(detail, file=sys.stderr)
            sys.exit(1)
    from desktop_ui import run
    sys.exit(run())
