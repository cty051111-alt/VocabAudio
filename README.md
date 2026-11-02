# VocabAudio 2.1 Beta �� �ʻ㷢������

���ʻ����ͼƬת��Ϊ��У�Ե�Ӣ�Ĵʱ��������ɸ�������д�� MP3��

[English guide](README_EN.md) �� [��Ŀ�ֿ�](https://github.com/cty051111-alt/VocabAudio)

## Windows ʹ��

���ر����ṩ�� `VocabAudio_2.1_Beta_Windows.zip`��������ѹ��˫�� `VocabAudio.exe`�����谲װ Python����ʷ 2.0 Release ������ͼƬʶ���ܡ����α��ع����Ͳ��Է�Χ�� [VALIDATION.md](VALIDATION.md)��

1. ѡ���ĵ�������������ͼƬ����Ҳ�ɽ������ļ��ϵ����ڡ�
2. ��ͼ������ճ��ͼƬ������ **Ctrl+Shift+V**��
3. ʶ������ԭͼ�޸����֣��ɸ������ֻ򱣴� TXT��
4. �������ȡ���滻�ʱ�����׷�ӵ��ʱ�������У��Ӣ�Ĵ�����
5. ������ʽ / Ӣʽ�����١�ͣ�ٺ��ظ�������ѡ���ļ��в����� MP3��

## ��������

- ���ŷ�ѧ��������ϰ����ķ������ʵ������ UI��Բ�ǿ�Ƭ��ϸ�߿򡢱�ƽ��ť��ͳһ�ؼ�������ǳɫ / ��ɫ��
- ֧�� PNG��JPG��BMP��WebP��TIFF ͼƬ�ͼ������ͼ���ڱ���ʶ��ӡˢ��Ӣ�ġ�
- ����ʶ������У�ԡ����ơ�TXT �����ʹʱ�������
- ���� PDF��DOCX��TXT��CSV �ʻ���ȡ���Լ�ԭ����Ƶ�ϳɡ��ظ���ʧ�ܱ��档
- ģ���Ѱ����� Windows ���У�����Ҫ OCR API ��Կ���״����� EXE ���ѹ����������������

## ��˽������

ͼƬ���ĵ��ڱ���������ʶ��ʱ���ϴ���ֻ��������Ƶʱ��Ӣ�Ĵ����ᷢ�͵��������е������ӿڡ��ýӿ�δ���ٷ�����֧�֣������������仯��ʧЧ����Ŀ���е��޹�����

OCR �ʺ�������ӡˢ��Ӣ�ģ�����֤��д��ģ����Ƭ�����Ӷ����������ʶ�����������У�ԡ���ͼ��ȱ�����С����� 2400 ���أ������Ȳü����ʻ����򡣵�ͼ���� 25 MB / 2400 �����ء�TIFF �ȶ�֡ͼƬֻ��ȡ��һ֡��

ɨ�� PDF Ŀǰ�����ȵ���ΪͼƬ���ɰ� WPS / DOC ������Ϊ DOCX���ɸ��ƻ򱣴��������֣���ԭ�з�������ֻ��ȡӢ�Ĵʻ㣬���ṩ�����ʶ�������δ���سɹ�ʱ�����������Ƶ�У���鿴ʧ�ܱ��档

## Դ�����С������빹��

���� Windows 64 λ��Python 3.13�������汾���ռ� `build-environment.txt`��

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
.venv/Scripts/python.exe app.py
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe app.py --self-test
.venv/Scripts/python.exe scripts/build_windows.py
```

Ҳ��ʹ�� `requirements-dev.txt` ��װ���ݷ�Χ�������������� PyInstaller���������й����ű���Windows ���ڵ� `SOURCE.zip` ����������Ӧ��Դ�롣�����޸�Ӧ�ü����������¹�����

## ж��������

�ر����������� `Uninstall_VocabAudio.bat`���˶Է�Χ������ `UNINSTALL`������ڶ����ļ����У��������ϲ�Ҫ�������� scripts/tests/docs ��Ŀ¼��ԭ�ļ��͵����� MP3 ����ɾ�������У�ϵͳ Python ���ᱻж�ء�

��Ŀ��������Ϊ [MIT](LICENSE)��������ģ�ͱ����������ɡ��ַ����� PyMuPDF/MuPDF ����������ʱ�������� AGPL v3������Դ������ṩ����� [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) �� `licenses/`��
