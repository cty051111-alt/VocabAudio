# VocabAudio 2.0 Beta · 词汇发音工坊

## 中文说明

把 PDF、DOCX、TXT、CSV 词汇表转换成用于跟读和听写的 MP3。

### 本版功能
- 保留 V1.1 的词汇提取与音频生成功能。
- 浅色／深色办公风格界面，自动保存偏好设置。
- 词表预览、编辑、添加、删除、调序与去重。
- 美式／英式发音，可调语速、词间停顿及 1–5 次重复。
- 生成失败词报告；失败词不计入输出音频。

### 下载与使用
在下方 **Assets** 下载 **VocabAudio_Windows_Beta.zip**，完整解压后双击 **VocabAudio.exe**，无需安装 Python。GitHub 的 Source code 为源码包。

### 验证与限制
Windows Python 3.10、3.13 的 11 项离线测试均通过；独立 EXE 构建和离线自检通过；发布的 ZIP 已下载并通过完整性检查。在线发音、Windows 界面交互和卸载仍需人工实测。EXE 未数字签名。

扫描 PDF 需要 OCR；原生旧版 WPS／DOC 应转换为 DOCX；当前不自动提供 IPA。文档在本地解析，发音词条会发送到第三方非官方有道接口。项目 MIT 许可不覆盖第三方音频。

卸载前查看脚本显示的清理范围。请在独立文件夹使用，勿将个人文件保存在程序的 scripts、tests、docs 等子目录，脚本会递归清理这些子目录。

---

## English

Convert PDF, DOCX, TXT and CSV vocabulary lists into MP3 audio for listening and dictation practice.

### Features
- Preserves vocabulary extraction and audio generation from v1.1.
- Light/dark office-style UI with persistent preferences.
- Preview, edit, add, remove, reorder and deduplicate vocabulary.
- US/UK pronunciation, adjustable speed and gaps, 1–5 repetitions.
- Explicit failure reports; failed words are omitted from the audio.

### Download and use
Download **VocabAudio_Windows_Beta.zip** under **Assets**, extract it fully and run **VocabAudio.exe**. No Python installation is needed. GitHub's Source code archives contain source files.

### Validation and limitations
All 11 offline tests passed on Windows with Python 3.10 and 3.13. The standalone EXE build and offline self-test passed, and the published ZIP was downloaded and checked for integrity. Live pronunciation, interactive Windows UI behavior and uninstallation still require manual testing. The executable is unsigned.

Scanned PDFs require OCR; legacy native WPS/DOC files require conversion to DOCX. Automatic IPA is not implemented. Documents are parsed locally; pronunciation entries are sent to an unofficial third-party Youdao endpoint. The project's MIT license does not cover third-party audio.

Review the uninstaller's deletion scope before confirming. Use a separate app folder and keep personal files out of scripts, tests, docs and other program subdirectories, which the script removes recursively.
