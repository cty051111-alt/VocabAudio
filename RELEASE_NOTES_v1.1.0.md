# VocabAudio v1.1.0 — First public source release

**词汇发音工坊 / Vocabulary Audio Studio**

Convert vocabulary lists from DOCX, selectable-text PDF and TXT/CSV into one pronunciation MP3.

### Features
- Automatically extract vocabulary headwords while preserving order.
- Review and edit the detected words before generating audio.
- US/UK pronunciation choices, adjustable gap and speed.
- Audio stitching into MP3 with failure reporting.
- Chinese-language Windows Tkinter UI.

### Installation
Requires **Python 3.10+**. Extract the release and run `INSTALL_DEPENDENCIES.bat`, then `START_APP.bat`. For non-default Python configurations use `python -m pip install -r requirements.txt` and `python app.py`.

### Known limits
- No standalone EXE in this release.
- Scanned PDFs require OCR; native `.wps` must be converted to DOCX.
- Online pronunciation source is an unofficial external service and may stop working or restrict access.
- Downloaded audio may not be real human narration; it is not bundled or licensed by the project's MIT license.
- Users should verify their rights to download/use external audio and should not redistribute it without permission.

### Validation
Core parsing and configuration unit tests run offline. The Windows launcher is based on V1.1 confirmed functional by its original user. Third-party online pronunciation access was not verified in the packaging environment.
