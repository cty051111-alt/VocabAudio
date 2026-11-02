# VocabAudio 2.1 Beta · 词汇发音工坊

[下载 2.1 Beta 升级版 / Download 2.1](https://github.com/cty051111-alt/VocabAudio/releases/tag/v2.1.0-beta) · [保留的 2.0 Beta / Previous 2.0](https://github.com/cty051111-alt/VocabAudio/releases/tag/v2.0.0-beta)

将词汇表或图片转换为可校对的英文词表，再生成跟读、听写用 MP3。

[English guide](README_EN.md) · [项目仓库](https://github.com/cty051111-alt/VocabAudio)

## Windows 使用

下载本次提供的 `VocabAudio_2.1_Beta_Windows.zip`，完整解压后双击 `VocabAudio.exe`，无需安装 Python。历史 2.0 Release 不包含图片识别功能。本次本地构建和测试范围见 [VALIDATION.md](VALIDATION.md)。

1. 选择文档，或点击「导入图片」。也可将单个文件拖到窗口。
2. 截图后点击「粘贴图片」，或按 **Ctrl+Shift+V**。
3. 识别后对照原图修改文字；可复制文字或保存 TXT。
4. 点击「提取并替换词表」或「追加到词表」，再校对英文词条。
5. 设置美式 / 英式、语速、停顿和重复次数，选择文件夹并生成 MP3。

## 本次升级

- 按九分学长智能练习插件的风格重新实现桌面 UI：圆角卡片、细边框、扁平按钮和统一控件，保留浅色 / 深色。
- 支持 PNG、JPG、BMP、WebP、TIFF 图片和剪贴板截图，在本机识别印刷中英文。
- 增加识别文字校对、复制、TXT 导出和词表搜索。
- 沿用 PDF、DOCX、TXT、CSV 词汇提取，以及原有音频合成、重复和失败报告。
- 模型已包含在 Windows 包中，不需要 OCR API 密钥；首次启动 EXE 会解压依赖，可能稍慢。

## 隐私与限制

图片、文档在本机处理，识别时不上传；只有生成音频时，英文词条会发送到第三方有道发音接口。该接口未经官方公开支持，可能限流、变化或失效，项目与有道无关联。

OCR 适合清晰的印刷中英文，不保证手写、模糊照片、复杂多栏和音标的识别质量。务必校对。长图会等比例缩小到最长边 2400 像素，建议先裁剪到词汇区域。单图限制 25 MB / 2400 万像素。TIFF 等多帧图片只读取第一帧。

扫描 PDF 目前仍需先导出为图片；旧版 WPS / DOC 请另存为 DOCX。可复制或保存中文文字，但原有发音流程只提取英文词汇，不提供中文朗读。词条未下载成功时不会包含在音频中，请查看失败报告。

## 源码运行、测试与构建

建议 Windows 64 位、Python 3.13。依赖版本快照见 `build-environment.txt`。

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe app.py
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe app.py --self-test
.venv/Scripts/python.exe scripts/build_windows.py
```

也可使用 `requirements-dev.txt` 安装兼容范围依赖（构建另需 PyInstaller），再运行构建脚本。Windows 包内的 `SOURCE.zip` 含本次完整应用源码。可以修改应用及依赖后重新构建。

## 卸载与许可

关闭软件后运行 `Uninstall_VocabAudio.bat`，核对范围并输入 `UNINSTALL`。请放在独立文件夹中，个人资料不要存入程序的 scripts/tests/docs 子目录。原文件和导出的 MP3 不在删除名单中，系统 Python 不会被卸载。

项目自身代码为 [MIT](LICENSE)；依赖及模型保留各自许可。分发包含 PyMuPDF/MuPDF 的完整软件时还需满足 AGPL v3。完整源码随包提供，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 `licenses/`。
