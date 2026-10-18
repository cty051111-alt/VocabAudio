# VocabAudio 2.0 Beta

An office-style desktop utility that turns your own PDF/DOCX/TXT/CSV vocabulary lists into a listening-practice MP3.

Features include a persistent light/dark theme, editable headword list, US/UK pronunciation, speed, word gaps, and repetitions. Failed downloads are reported explicitly.

**Source beta:** Install Python 3.10+ and dependencies via `INSTALL_DEPENDENCIES.bat` and launch `START_APP.bat`.

**Portable Windows beta:** Run the GitHub Actions workflow `Build VocabAudio Windows Beta`; download its artifact. The artifact contains a standalone `VocabAudio.exe` and a safe uninstaller. No Python is required by end users. This ZIP contains build instructions and source files, **not a prebuilt Windows EXE**.

**Uninstallation:** `Uninstall_VocabAudio.bat` only removes allow-listed program files and the application's own local settings/cache. It does not delete imported documents, exported MP3s, or system Python.

**Caveats:** Uses an unofficial third-party pronunciation endpoint which may become unavailable or be subject to licensing restrictions. No provider audio is redistributed. Image-only PDFs require OCR. Native WPS files should be exported to DOCX. The program does not generate IPA; the preview shows a dash where no transcription is available.

See [README.md](README.md) for full instructions. MIT license covers code, not third-party voices.
