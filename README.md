# VocabAudio 2.0 Beta · 词汇发音工坊

把你的词汇表变成可用于跟读、听写的 MP3。简洁的办公风格桌面 UI，支持**浅色/深色主题切换**。

> **发行状态**：此仓库提供可直接使用的 Python 测试版以及 Windows EXE 自动构建工程。**源码 ZIP 不是免 Python 的 EXE**；GitHub Actions 成功执行后才能获得经 Windows 自检的免 Python ZIP。

## 功能

- 导入 PDF（含文字层）、Word/WPS 保存的 DOCX、TXT 和 CSV；旧 `.wps` 和扫描 PDF 暂不能直接解析。
- 自动提取词汇表中的英文词条，保留顺序，并支持编辑、去重、删除。
- 选择美式／英式发音、语速、词间停顿、单词重复 1–5 次。
- 联网获取发音并拼成 MP3，自动输出失败词报告，不会把漏词当成成功。
- 原生 Tkinter 办公风格 UI、可随时切换的浅色／深色主题、自动记住设置。
- **安全卸载脚本**：仅清理列入白名单的程序文件及 `%LOCALAPPDATA%\VocabAudio` 私有设置目录，不删除用户 PDF、DOCX、MP3 及其自行安装的 Python。

## Windows 用户：两种使用方式

### 方式 A：免 Python EXE（推荐正式发布）

1. 仓库维护者在 GitHub 的 Actions 页面运行 **Build VocabAudio Windows Beta**。
2. 工作流自动测试、打包 `VocabAudio.exe`、运行 `--self-test` 并上传 `VocabAudio-Windows-Beta`。
3. 下载构建产物 `VocabAudio_Windows_Beta.zip`，完整解压后双击 `VocabAudio.exe`。
4. 结束使用时，关闭程序并双击 `Uninstall_VocabAudio.bat`；输入 `UNINSTALL` 再确认清理。

> 注意：当前交付环境不能直接构建 Windows EXE，须在 Windows GitHub Actions 中验证。EXE 未数字签名，Windows 可能提示未知发布者。

### 方式 B：运行源码测试版（你现有的 Python 3.13 电脑）

1. 解压测试版到独立文件夹。
2. 双击 `INSTALL_DEPENDENCIES.bat`（之前安装过 V1.1 的用户通常可跳过）。
3. 双击 `START_APP.bat`；设置主题并导入词汇表。
4. 需要移除时，退出软件，运行 `Uninstall_VocabAudio.bat`。

也可用命令行：

```powershell
python -m pip install -r requirements.txt
python app.py
```

## 词典音源及隐私

- 当前版本使用第三方**非官方**有道发音接口。项目与有道／网易无关联，网络服务可能变化或限制访问，部分单词可能没有有效音频。
- 该服务返回的音频不保证均由真人录制。音源及音频版权不受本仓库 MIT 源码许可证覆盖，请遵循其适用许可与服务条款，勿大规模抓取或重新分发录音。
- 原文档在本机读取，不会上传整个文件。用于生成语音的英文词条会发送到第三方服务。
- 目前的音标预览列显示 `—`，并不自动生成或猜测 IPA；需要查标准发音请参考可靠词典。
- 生成的 MP3 存在你选择的位置。卸载不会删除它们。

## 开发与测试

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python app.py --self-test
```

- `app.py`：界面与用户操作
- `vocab_core.py`：词语识别与音频处理
- `settings_store.py`：设置存储和安全路径限制
- `tests/`：不联网的自动化测试
- `.github/workflows/build-windows.yml`：Windows PyInstaller 免安装构建
- `scripts/uninstall.ps1`：白名单式安全卸载

## 已知限制

- 扫描版 PDF 需要先在 WPS 或其他软件做 OCR。
- 不支持原生旧版 `.wps` 二进制文件直接读取；应另存为 DOCX。
- 不支持任意 PDF 排版的百分百自动识别；生成前请检查词表。
- 词典服务是否可用尚未在当前容器做真实联网端到端验证。
- Windows EXE 和卸载脚本需要在真实 Windows 机器上进行完整安装／卸载测试。

MIT License 仅覆盖本项目代码。详见 `LICENSE`。
