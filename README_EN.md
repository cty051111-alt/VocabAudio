# VocabAudio 2.1 Beta

[下载 2.1 Beta 升级版 / Download 2.1](https://github.com/cty051111-alt/VocabAudio/releases/tag/v2.1.0-beta) · [保留的 2.0 Beta / Previous 2.0](https://github.com/cty051111-alt/VocabAudio/releases/tag/v2.0.0-beta)

将词汇表或图片转换为可校对的英文词表，再生成跟读、听写用 MP3。  
Turn vocabulary documents and images into editable English word lists and pronunciation MP3s. [中文说明](README.md)

## Windows

Extract the entire `VocabAudio_2.1_Beta_Windows.zip` and launch `VocabAudio.exe`. Python is not required. The previous 2.0 release does not contain OCR.

1. Import a PDF/DOCX/TXT/CSV document or a PNG/JPEG/BMP/WebP/TIFF image. Single-file drag and drop is supported.
2. Paste a copied screenshot with **Ctrl+Shift+V**.
3. Review the image beside its recognized text. Edit, copy, or save the text as TXT.
4. Replace or append to the English vocabulary list, then adjust pronunciation settings and generate MP3.

The desktop UI has been improved with updated cards, buttons, inputs, menus and sliders. Both light and dark themes remain available. Vocabulary extraction and audio composition use the existing core.

## Privacy and limits

OCR models are included and run locally without an API key or image uploads. Only audio generation sends English entries to an unofficial third-party Youdao pronunciation endpoint; availability is not guaranteed.

OCR targets clear printed Chinese and English. Handwriting, blurry photos, IPA and complex column layouts may be inaccurate. Review before generating audio. Images are limited to 25 MB / 24 million pixels and resized to a maximum dimension of 2400; crop long pages for better results. Only the first frame of multi-frame images is read. Scanned PDFs must be exported to images first. Chinese text can be copied or exported; the audio workflow extracts English vocabulary only. Failed pronunciation entries are omitted and reported.

## Source and build

Windows x64 and Python 3.13 are recommended. Use a virtual environment, install `requirements-lock.txt`, then run `python app.py`. Run `python -m pytest -q`, `python app.py --self-test`, and `python scripts/build_windows.py` to test and build. Runtime model downloads are disabled: missing models produce an error. The self-test performs real OCR while blocking socket connections and checks both UI themes and FFmpeg. See `VALIDATION.md` for the actual verification scope.

The portable package includes `SOURCE.zip`, corresponding application source and build instructions, and dependency notices. You may modify the application or replace its Qt dependencies and rebuild it. Original application files are MIT licensed; distribution with AGPL PyMuPDF/MuPDF also requires compliance with AGPL v3. See `THIRD_PARTY_NOTICES.md` and `licenses/`.

To remove the app, close it and run `Uninstall_VocabAudio.bat`, review its scope and type `UNINSTALL`. Keep personal files outside app-owned scripts/tests/docs folders. System Python is not removed.
