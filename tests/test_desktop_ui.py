import time
import threading

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtGui import QImage
from desktop_ui import App, ReviewDialog
from image_ocr import Recognition, smoke_image


@pytest.fixture
def window(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    app = QApplication.instance() or QApplication([])
    app.setStyle('Fusion')
    widget = App()
    widget.show()
    app.processEvents()
    yield widget
    assert not widget.busy
    widget.timer.stop()
    widget.close()
    app.processEvents()


def wait_for_task(window):
    deadline = time.monotonic() + 10
    while window.busy and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(.01)
    assert not window.busy


def test_ocr_import_reviews_before_updating_words(window, monkeypatch):
    window.words = ['existing']
    window.refresh_table()
    def accept_review(dialog):
        assert window.words == ['existing']
        assert 'apple' in dialog.editor.toPlainText()
        dialog.editor.setPlainText('apple\nlook up')
        dialog.accept_words(True)
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(ReviewDialog, 'exec', accept_review)
    window.start_ocr(smoke_image(), 'vocabulary.png')
    assert not window.image_btn.isEnabled()
    wait_for_task(window)
    assert window.words == ['existing', 'apple', 'look up']
    assert window.image_btn.isEnabled()
    assert window.table.rowCount() == 3
    window.search.setText('LOOK')
    assert window.table.isRowHidden(0)
    assert not window.table.isRowHidden(2)


def test_cancel_discards_completed_ocr_result(window):
    window.words = ['existing']
    window.refresh_table()
    gate = threading.Event()
    window.run_task('ocr', lambda: (gate.wait(3), None, 'test.png'))
    window.cancel_work()
    gate.set()
    wait_for_task(window)
    assert window.words == ['existing']
    assert window.image_btn.isEnabled()


def test_empty_and_invalid_images_keep_existing_list(window, monkeypatch, tmp_path):
    warnings = []
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: warnings.append(args[-1]))
    window.words = ['existing']
    window.start_ocr(tmp_path / 'missing.png', 'missing.png')
    wait_for_task(window)
    assert warnings and window.words == ['existing']
    def cancel_review(dialog):
        assert not dialog.editor.toPlainText()
        return QDialog.DialogCode.Rejected
    monkeypatch.setattr(ReviewDialog, 'exec', cancel_review)
    from PIL import Image
    window.start_ocr(Image.new('RGB', (300, 200), 'white'), 'blank.png')
    wait_for_task(window)
    assert window.words == ['existing']


def test_clipboard_image_and_theme_switch(window, monkeypatch):
    image = QImage(100, 100, QImage.Format.Format_RGB32)
    image.fill(0xFFFFFF)
    QApplication.clipboard().setImage(image)
    captured = []
    monkeypatch.setattr(window, 'start_ocr', lambda image, name: captured.append((image.size, name)))
    window.paste_image()
    assert captured == [((100, 100), '剪贴板图片')]
    theme = window.theme
    window.theme_btn.click()
    assert window.theme != theme
    assert window.gen_btn.isVisible()
    assert window.minimumWidth() <= 1080
