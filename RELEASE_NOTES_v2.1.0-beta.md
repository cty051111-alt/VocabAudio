## VocabAudio 2.1 Beta · 升级版 / Upgrade

把词汇表或图片转换为可校对的英文词表，再生成跟读、听写用 MP3。
Turn vocabulary documents or images into editable English word lists and MP3s for pronunciation and dictation practice.

### 更新内容 / What’s new
- 全面优化 UI：更新圆角卡片、按钮、输入框、下拉框和滑块，保留浅色与深色主题。
  Improved UI with refreshed cards, buttons, inputs, menus and sliders, while keeping light and dark themes.
- 新增本机离线图片识别，支持 PNG、JPG、WebP、BMP、TIFF、截图粘贴和文件拖入。
  Added local offline OCR for PNG, JPG, WebP, BMP and TIFF, with screenshot paste and file drag and drop.
- 对照原图校对文字，复制或导出 TXT，再替换或追加英文词表。
  Review and edit recognized text beside the image, copy or export TXT, then replace or append vocabulary.
- 增加词表搜索，保留文档提取、美式／英式发音、语速、停顿、重复与 MP3 导出。
  Added vocabulary search and retained document import, US/UK pronunciation, speed, pauses, repetitions and MP3 export.

### 下载与使用 / Download and use
下载 **VocabAudio_2.1_Beta_Windows.zip**，完整解压后运行 **VocabAudio.exe**，无需安装 Python。
Download **VocabAudio_2.1_Beta_Windows.zip**, extract the entire archive and run **VocabAudio.exe**. Python is not required.

源码包：**VocabAudio_2.1_Beta_Source.zip**。原 2.0 Beta 和旧下载包继续保留。
Source package: **VocabAudio_2.1_Beta_Source.zip**. The previous 2.0 Beta and its download remain available.

### 验证与说明 / Validation and notes
Windows 自动测试及构建已通过；独立 EXE 已通过离线 OCR、双主题界面和 FFmpeg 自检。另已完成 apple、banana 的在线发音与合成检查。
Windows automated tests and builds passed. The standalone EXE passed offline OCR, both UI themes and FFmpeg checks. Live pronunciation downloads and audio composition were also checked with apple and banana.

图片在本机识别，不上传原图，也不需要 API 密钥。生成音频时，英文词条会发送到第三方发音服务。
Images are recognized locally without uploads or API keys. Audio generation sends English entries to a third-party pronunciation service.

OCR 适合清晰的印刷中英文，请人工校对。扫描 PDF 请先导出图片；手写、模糊照片和复杂多栏可能误识别。中文文字可保存为 TXT，音频流程只提取英文词条。
OCR targets clear printed Chinese and English; review the results. Export scanned PDFs to images first. Handwriting, blurry photos and complex columns may be inaccurate. Chinese text can be saved as TXT; the audio workflow extracts English vocabulary.

完整应用源码和第三方许可随包提供。
Complete application source and third-party notices are included.
