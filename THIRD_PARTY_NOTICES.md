# Third-party notices

VocabAudio's own code is MIT licensed. Dependencies and model weights keep their own licenses.

- **PySide6 Essentials / Shiboken6 / Qt**: LGPL v3 (or the alternative licenses offered by their authors). The Qt libraries are dynamically loaded, not statically linked. LGPL and GPL v3 texts are in `licenses/`. Source and build instructions for this application are provided in the source archive. You may modify the application or replace its Qt dependencies and rebuild the executable using `BUILD_EXE.bat`; reverse engineering for debugging such library modifications is not prohibited. Upstream sources: https://code.qt.io/cgit/pyside/pyside-setup.git/ and https://code.qt.io/cgit/qt/qtbase.git/ (select the release tag matching `build-environment.txt`).
- **RapidOCR 3.10.0**: Apache-2.0. Copyright (c) 2021 RapidOCR Authors. Bundled models: `PP-OCRv6_det_small.onnx`, `PP-OCRv6_rec_small.onnx` and `ch_ppocr_mobile_v2.0_cls_mobile.onnx`. These are converted PaddleOCR models, whose upstream project is Apache-2.0: https://github.com/PaddlePaddle/PaddleOCR . RapidOCR sources and model attribution: https://github.com/RapidAI/RapidOCR and https://rapidai.github.io/RapidOCRDocs/ . Model files are not modified.
- **ONNX Runtime**: MIT, Microsoft Corporation. https://github.com/microsoft/onnxruntime
- **Pillow**: MIT-CMU and notices for its bundled imaging libraries. https://github.com/python-pillow/Pillow
- **PyMuPDF / MuPDF**: AGPL v3 or commercial license. https://github.com/pymupdf/PyMuPDF and https://mupdf.com/ . Because this distribution includes the AGPL version, distribution of the combined application must also satisfy AGPL v3; the complete application source and build instructions accompany this beta distribution. VocabAudio's own MIT files remain MIT and are compatible with distribution under AGPL v3. See `licenses/AGPL-3.0.txt`.
- **python-docx**: MIT. https://github.com/python-openxml/python-docx
- **imageio-ffmpeg**: BSD-2-Clause wrapper; bundled FFmpeg has separate LGPL/GPL component notices and license terms. https://github.com/imageio/imageio-ffmpeg and https://ffmpeg.org/legal.html . Refer to the bundled FFmpeg version/configuration when rebuilding or redistributing.
- Other dependencies, including NumPy, OpenCV, Shapely, pyclipper, OmegaConf, Requests and their transitive dependencies, retain their respective notices. Copies of notices present in the installed distributions are collected under `licenses/` in the Windows package.

No third-party pronunciation recording is included in the download. The unofficial Youdao endpoint is contacted only when the user generates audio. Permission to use this application's code does not grant additional rights to third-party audio.
