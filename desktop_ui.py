"""VocabAudio's modern desktop workspace; processing stays in the existing core."""
from __future__ import annotations

import io
import os
import queue
import threading
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import (QAction, QDesktopServices, QFont, QIcon, QImage,
                           QKeySequence, QPixmap, QShortcut)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSlider, QComboBox, QCheckBox, QProgressBar, QFileDialog,
    QMessageBox, QDialog, QScrollArea, QButtonGroup, QSplitter,
)

from image_ocr import (IMAGE_EXTENSIONS, load_image, recognize_image,
                       words_from_ocr_text)
from settings_store import data_dir, load_settings, save_settings
from vocab_core import read_file, deduplicate, render_audio

VERSION = '2.1 Beta'
ROOT = Path(__file__).resolve().parent
DOCUMENT_EXTENSIONS = ('.pdf', '.docx', '.txt', '.csv', '.wps', '.doc')
FILE_FILTER = '词汇表与图片 (*.pdf *.docx *.txt *.csv *.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;所有文件 (*)'
COLORS = {
    'light': dict(bg='#F5F7FA', panel='#FFFFFF', soft='#F7F9FC', text='#202A37',
                  muted='#697586', line='#E1E6ED', accent='#2374E8', hover='#EDF3FD',
                  selected='#EAF2FF', ok='#29815C'),
    'dark': dict(bg='#131A23', panel='#1B2532', soft='#222E3D', text='#EAF0F8',
                 muted='#A3B0C1', line='#354256', accent='#579BFF', hover='#283B55',
                 selected='#263D5B', ok='#74CCA7'),
}


def layout(widget, margins=0, spacing=12, horizontal=False):
    result = QHBoxLayout(widget) if horizontal else QVBoxLayout(widget)
    result.setContentsMargins(*([margins] * 4))
    result.setSpacing(spacing)
    return result


def label(text, role='', wrap=False):
    item = QLabel(text)
    item.setProperty('role', role)
    item.setWordWrap(wrap)
    return item


def button(text, callback=None, role='secondary'):
    item = QPushButton(text)
    item.setProperty('role', role)
    item.setCursor(Qt.CursorShape.PointingHandCursor)
    item.setMinimumHeight(38)
    if callback:
        item.clicked.connect(callback)
    return item


def image_pixmap(image):
    data = image.convert('RGB').tobytes()
    return QPixmap.fromImage(QImage(data, image.width, image.height,
                                   image.width * 3, QImage.Format.Format_RGB888).copy())


def stylesheet(theme):
    p = COLORS[theme]
    return f'''
    QWidget {{ color: {p['text']}; font-family: "Microsoft YaHei UI", "Segoe UI"; font-size: 13px; }}
    QMainWindow, QDialog, QWidget#workspace {{ background: {p['bg']}; }}
    QFrame#sidebar, QFrame[role="card"] {{ background: {p['panel']}; }}
    QFrame#sidebar {{ border-right: 1px solid {p['line']}; }}
    QFrame[role="card"] {{ border: 1px solid {p['line']}; border-radius: 10px; }}
    QFrame#dropzone {{ background: {p['soft']}; border: 1px dashed {p['line']}; border-radius: 8px; }}
    QLabel {{ background: transparent; border: none; }}
    QLabel[role="title"] {{ font-size: 25px; font-weight: 700; }}
    QLabel[role="heading"] {{ font-size: 16px; font-weight: 600; }}
    QLabel[role="brand"] {{ font-size: 19px; font-weight: 700; }}
    QLabel[role="muted"] {{ color: {p['muted']}; font-size: 12px; }}
    QLabel[role="step"] {{ color: {p['accent']}; font-size: 12px; font-weight: 600; }}
    QLabel[role="badge"] {{ background: {p['selected']}; color: {p['accent']}; border-radius: 5px; padding: 4px 8px; font-size: 11px; }}
    QLabel#brandmark {{ background: {p['accent']}; color: white; border-radius: 10px; font-size: 18px; font-weight: 700; }}
    QPushButton {{ background: {p['panel']}; border: 1px solid {p['line']}; border-radius: 6px; padding: 7px 14px; font-weight: 500; }}
    QPushButton:hover {{ background: {p['hover']}; border-color: {p['accent']}; }}
    QPushButton:pressed {{ background: {p['selected']}; }}
    QPushButton:focus {{ border: 2px solid {p['accent']}; padding: 6px 13px; }}
    QPushButton:disabled {{ color: {p['muted']}; background: {p['soft']}; border-color: {p['line']}; }}
    QPushButton[role="primary"] {{ background: {p['accent']}; border-color: {p['accent']}; color: {'#111B29' if theme == 'dark' else 'white'}; font-weight: 600; }}
    QPushButton[role="primary"]:hover {{ background: {'#78AFFF' if theme == 'dark' else '#155FC5'}; }}
    QPushButton[role="primary"]:disabled {{ background: {p['soft']}; border-color: {p['line']}; color: {p['muted']}; }}
    QPushButton[role="nav"] {{ background: transparent; border: 1px solid transparent; text-align: left; padding: 11px 16px; color: {p['muted']}; border-radius: 7px; }}
    QPushButton[role="nav"]:hover, QPushButton[role="nav"]:checked {{ background: {p['selected']}; color: {p['accent']}; }}
    QPushButton[role="segment"]:checked {{ background: {p['selected']}; border-color: {p['accent']}; color: {p['accent']}; }}
    QLineEdit, QPlainTextEdit, QComboBox {{ background: {p['panel']}; border: 1px solid {p['line']}; border-radius: 6px; padding: 8px 10px; selection-background-color: {p['selected']}; selection-color: {p['text']}; }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{ border-color: {p['accent']}; }}
    QLineEdit:disabled {{ background: {p['soft']}; color: {p['muted']}; }}
    QComboBox {{ min-height: 20px; padding-right: 25px; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox::down-arrow {{ image: url(assets/chevron.svg); width: 12px; height: 12px; }}
    QComboBox QAbstractItemView {{ background: {p['panel']}; border: 1px solid {p['line']}; selection-background-color: {p['selected']}; padding: 5px; }}
    QCheckBox {{ spacing: 9px; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid {p['muted']}; background: {p['panel']}; }}
    QCheckBox::indicator:checked {{ background: {p['accent']}; border: 4px solid {p['accent']}; image: url(assets/check.svg); }}
    QSlider::groove:horizontal {{ height: 5px; background: {p['line']}; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {p['accent']}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 14px; margin: -5px 0; border-radius: 7px; background: {p['panel']}; border: 2px solid {p['accent']}; }}
    QSlider:focus {{ border: 1px solid {p['accent']}; border-radius: 5px; }}
    QTableWidget {{ background: {p['panel']}; alternate-background-color: {p['soft']}; border: none; gridline-color: {p['line']}; selection-background-color: {p['selected']}; selection-color: {p['text']}; outline: 0; }}
    QTableWidget::item {{ padding: 0 10px; border-bottom: 1px solid {p['line']}; }}
    QHeaderView::section {{ background: {p['soft']}; color: {p['muted']}; padding: 11px 10px; border: none; border-bottom: 1px solid {p['line']}; font-size: 12px; font-weight: 500; }}
    QTableCornerButton::section {{ background: {p['soft']}; border: none; }}
    QProgressBar {{ height: 5px; max-height: 5px; background: {p['line']}; border: none; border-radius: 2px; }}
    QProgressBar::chunk {{ background: {p['accent']}; border-radius: 2px; }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ width: 8px; background: transparent; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {p['line']}; border-radius: 4px; min-height: 30px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    QToolTip {{ background: {p['panel']}; color: {p['text']}; border: 1px solid {p['line']}; padding: 5px; }}
    '''.replace('url(assets/check.svg)', f'url({(ROOT / "assets" / "check.svg").as_posix()})').replace('url(assets/chevron.svg)', f'url({(ROOT / "assets" / "chevron.svg").as_posix()})')


class ReviewDialog(QDialog):
    def __init__(self, parent, image, recognition):
        super().__init__(parent)
        self.setWindowTitle('图片文字识别 · 校对结果')
        self.resize(980, 660)
        self.setMinimumSize(760, 500)
        self.words = None
        self.append = False
        outer = layout(self, 24, 16)
        outer.addWidget(label('检查图片里的文字', 'title'))
        outer.addWidget(label('图片在本机识别。请先校对，再提取英文词汇；中文文字可复制或保存。', 'muted', True))
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QFrame()
        left.setProperty('role', 'card')
        ll = layout(left, 14)
        ll.addWidget(label('原图', 'heading'))
        picture = QLabel()
        picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        picture.setPixmap(image_pixmap(image).scaled(QSize(390, 410), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        scroll = QScrollArea()
        scroll.setWidget(picture)
        scroll.setWidgetResizable(True)
        ll.addWidget(scroll, 1)
        right = QWidget()
        rl = layout(right, 4)
        rl.addWidget(label('识别文字 · 可直接修改', 'heading'))
        self.editor = QPlainTextEdit(recognition.text)
        self.editor.setPlaceholderText('未识别到文字。可以手动输入，或关闭后换一张更清晰的图片。')
        rl.addWidget(self.editor, 1)
        note = f'检测到 {recognition.low_confidence} 处低置信度文字，请特别核对。' if recognition.low_confidence else '请核对相似字符，例如 l / I / 1、o / 0。'
        rl.addWidget(label(note, 'muted', True))
        self.summary = label('', 'step')
        rl.addWidget(self.summary)
        self.editor.textChanged.connect(self.update_count)
        self.update_count()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([420, 480])
        outer.addWidget(splitter, 1)
        actions = QHBoxLayout()
        actions.addWidget(button('复制文字', self.copy_text))
        actions.addWidget(button('保存 TXT', self.save_text))
        actions.addStretch()
        actions.addWidget(button('取消', self.reject))
        actions.addWidget(button('追加到词表', lambda: self.accept_words(True)))
        actions.addWidget(button('提取并替换词表', lambda: self.accept_words(False), 'primary'))
        outer.addLayout(actions)

    def update_count(self):
        words = words_from_ocr_text(self.editor.toPlainText())
        self.summary.setText(f'可提取 {len(words)} 个英文单词 / 词组')

    def copy_text(self):
        QApplication.clipboard().setText(self.editor.toPlainText())
        self.summary.setText('文字已复制')

    def save_text(self):
        path, _ = QFileDialog.getSaveFileName(self, '保存识别文字', '识别文字.txt', '文本 (*.txt)')
        if path:
            try:
                Path(path).write_text(self.editor.toPlainText(), encoding='utf-8-sig')
                self.summary.setText('文字已保存')
            except OSError as exc:
                QMessageBox.warning(self, '保存失败', str(exc))

    def accept_words(self, append):
        words = words_from_ocr_text(self.editor.toPlainText())
        if not words:
            QMessageBox.information(self, '没有英文词汇', '可以复制或保存识别文字。若要生成词汇音频，请先在右侧校对英文词条。')
            return
        if not append and self.parent().words:
            if QMessageBox.question(self, '替换词表', '将替换当前词表，是否继续？') != QMessageBox.StandardButton.Yes:
                return
        self.words, self.append = words, append
        self.accept()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.theme = self.settings['theme']
        self.words = []
        self.source_name = ''
        self.output_dir = self.settings['last_output_dir'] or str(Path.home() / 'Downloads')
        self.busy = False
        self.cancel_event = threading.Event()
        self.q = queue.Queue()
        self.close_requested = False
        self.setWindowTitle(f'VocabAudio · 词汇发音工坊 {VERSION}')
        self.setWindowIcon(QIcon(str(ROOT / 'assets' / 'VocabAudio.ico')))
        self.resize(1260, 850)
        self.setMinimumSize(1080, 760)
        self.setAcceptDrops(True)
        self.make_layout()
        self.apply_theme()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(80)
        QShortcut(QKeySequence('Ctrl+O'), self, activated=self.choose)
        QShortcut(QKeySequence('Ctrl+Shift+V'), self, activated=self.paste_image)
        QShortcut(QKeySequence('Delete'), self.table, activated=self.remove_selected)

    def card(self):
        item = QFrame()
        item.setProperty('role', 'card')
        return item

    def make_layout(self):
        workspace = QWidget()
        workspace.setObjectName('workspace')
        self.setCentralWidget(workspace)
        shell = layout(workspace, 0, 0, True)
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(202)
        side = layout(sidebar, 18, 8)
        brand = QHBoxLayout()
        mark = label('Va')
        mark.setObjectName('brandmark')
        mark.setFixedSize(38, 38)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.addWidget(mark)
        brand.addWidget(label('VocabAudio', 'brand'))
        side.addSpacing(14)
        side.addLayout(brand)
        side.addWidget(label('词汇发音工坊', 'muted'))
        side.addSpacing(27)
        self.nav = []
        for text, callback in [('工作台', lambda: self.search.setFocus()), ('词汇管理', self.edit_words),
                               ('朗读设置', lambda: self.name_entry.setFocus()), ('使用帮助', self.help_dialog)]:
            b = button(text, callback, 'nav')
            b.setCheckable(not self.nav)
            side.addWidget(b)
            self.nav.append(b)
        self.nav[0].setChecked(True)
        side.addStretch()
        side.addWidget(label('本地图片识别', 'step'))
        side.addWidget(label('无需密钥 · 图片不上传', 'muted'))
        side.addSpacing(14)
        self.theme_btn = button('切换深色主题', self.toggle_theme)
        side.addWidget(self.theme_btn)
        side.addWidget(button('软件与隐私', self.about_dialog, 'nav'))
        side.addWidget(label(f'{VERSION}  /  WINDOWS', 'muted'))
        shell.addWidget(sidebar)
        content = QWidget()
        body = layout(content, 28, 20)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(5)
        titles.addWidget(label('把生词，变成随身听。', 'title'))
        titles.addWidget(label('导入词汇表或图片，校对后生成你的跟读音频。', 'muted'))
        header.addLayout(titles)
        header.addStretch()
        badge = label('图片识别  NEW', 'badge')
        header.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        body.addLayout(header)
        columns = QHBoxLayout()
        columns.setSpacing(18)
        main = QVBoxLayout()
        main.setSpacing(16)
        imports = self.card()
        il = layout(imports, 20, 10)
        il.addWidget(label('01  导入内容', 'heading'))
        il.addWidget(label('文档、截图、拍照的词汇表，都可以从这里开始。', 'muted'))
        drop = QFrame()
        drop.setObjectName('dropzone')
        dl = layout(drop, 16, 10)
        dl.addWidget(label('将文件拖到窗口，或选择导入方式', 'heading'), 0, Qt.AlignmentFlag.AlignCenter)
        dl.addWidget(label('PDF / DOCX / TXT / CSV   ·   PNG / JPG / WebP / BMP / TIFF', 'muted'), 0, Qt.AlignmentFlag.AlignCenter)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch()
        self.choose_btn = button('选择文档', self.choose)
        self.image_btn = button('导入图片', self.choose_image, 'primary')
        self.paste_btn = button('粘贴图片', self.paste_image)
        self.paste_btn.setToolTip('复制截图后按 Ctrl+Shift+V')
        for b in (self.choose_btn, self.image_btn, self.paste_btn):
            actions.addWidget(b)
        actions.addStretch()
        dl.addLayout(actions)
        il.addWidget(drop)
        self.file_hint = label('尚未导入文件', 'muted')
        il.addWidget(self.file_hint)
        main.addWidget(imports)
        preview = self.card()
        pl = layout(preview, 18, 12)
        row = QHBoxLayout()
        row.addWidget(label('02  校对词汇', 'heading'))
        row.addStretch()
        self.count = label('0 个词条', 'badge')
        row.addWidget(self.count)
        pl.addLayout(row)
        self.search = QLineEdit()
        self.search.setPlaceholderText('搜索当前词表…')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filter_words)
        pl.addWidget(self.search)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['序号', '英文单词 / 词组', '状态'])
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setColumnWidth(0, 58)
        self.table.setColumnWidth(2, 95)
        self.table.cellDoubleClicked.connect(lambda *_: self.edit_words())
        pl.addWidget(self.table, 1)
        self.empty = label('词表还是空的\n\n导入一份文件，或点击「编辑词表」手动粘贴。', 'muted', True)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setMinimumHeight(100)
        pl.addWidget(self.empty, 1)
        tools = QHBoxLayout()
        self.edit_btn = button('编辑词表', self.edit_words)
        self.remove_btn = button('删除选中', self.remove_selected)
        tools.addWidget(self.edit_btn)
        tools.addWidget(self.remove_btn)
        tools.addStretch()
        tools.addWidget(label('双击词条可编辑', 'muted'))
        pl.addLayout(tools)
        main.addWidget(preview, 1)
        footer = QHBoxLayout()
        status_box = QVBoxLayout()
        self.status = label('就绪，等待导入内容。', 'muted', True)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        status_box.addWidget(self.status)
        status_box.addWidget(self.progress)
        footer.addLayout(status_box, 1)
        self.cancel_btn = button('取消', self.cancel_work)
        self.cancel_btn.hide()
        footer.addWidget(self.cancel_btn)
        main.addLayout(footer)
        columns.addLayout(main, 1)
        settings = self.card()
        settings.setFixedWidth(286)
        sl = layout(settings, 20, 16)
        sl.addWidget(label('03  朗读与导出', 'heading'))
        sl.addWidget(label('按自己的节奏，反复听与练。', 'muted'))
        sl.addSpacing(2)
        sl.addWidget(label('发音口音'))
        accents = QHBoxLayout()
        accents.setSpacing(8)
        self.accent_group = QButtonGroup(self)
        for n, (text, value) in enumerate([('美式英语', 'us'), ('英式英语', 'uk')]):
            b = button(text, role='segment')
            b.setCheckable(True)
            b.setChecked(self.settings['accent'] == value)
            self.accent_group.addButton(b, n)
            accents.addWidget(b)
        self.accent_group.buttonClicked.connect(self.persist)
        sl.addLayout(accents)
        self.speed, self.speed_value = self.slider(sl, '语速', 7, 13, round(self.settings['speed'] * 10), lambda v: f'{v/10:.1f}×')
        self.gap, self.gap_value = self.slider(sl, '词间停顿', 2, 30, round(self.settings['gap'] * 10), lambda v: f'{v/10:.1f} 秒')
        sl.addWidget(label('重复次数'))
        self.repeat = QComboBox()
        self.repeat.addItems([f'{n} 次' for n in range(1, 6)])
        self.repeat.setCurrentIndex(max(0, min(4, self.settings['repeat'] - 1)))
        self.repeat.currentIndexChanged.connect(self.persist)
        sl.addWidget(self.repeat)
        sl.addWidget(label('输出文件名'))
        self.name_entry = QLineEdit('vocabulary_audio')
        self.name_entry.setPlaceholderText('vocabulary_audio')
        self.name_entry.setToolTip('自动添加 .mp3 扩展名')
        sl.addWidget(self.name_entry)
        self.folder_btn = button('选择保存文件夹', self.choose_dir)
        sl.addWidget(self.folder_btn)
        self.folder_hint = label(self.output_dir, 'muted', True)
        self.folder_hint.setMaximumHeight(42)
        self.folder_hint.setToolTip(self.output_dir)
        sl.addWidget(self.folder_hint)
        self.open_folder = QCheckBox('生成后打开文件夹')
        self.open_folder.setChecked(self.settings['open_folder'])
        self.open_folder.toggled.connect(self.persist)
        sl.addWidget(self.open_folder)
        sl.addStretch()
        self.gen_btn = button('生成 MP3 音频  →', self.start_audio, 'primary')
        self.gen_btn.setMinimumHeight(46)
        sl.addWidget(self.gen_btn)
        sl.addWidget(label('仅生成音频时需要联网', 'muted'), 0, Qt.AlignmentFlag.AlignCenter)
        columns.addWidget(settings)
        body.addLayout(columns, 1)
        shell.addWidget(content, 1)
        self.refresh_table()

    def slider(self, target, title, low, high, value, formatter):
        row = QHBoxLayout()
        row.addWidget(label(title))
        row.addStretch()
        value_label = label(formatter(value), 'step')
        row.addWidget(value_label)
        target.addLayout(row)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(low, high)
        slider.setValue(value)
        slider.setMinimumHeight(20)
        slider.setAccessibleName(title)
        slider.valueChanged.connect(lambda v: value_label.setText(formatter(v)))
        slider.valueChanged.connect(self.persist)
        target.addWidget(slider)
        return slider, value_label

    def apply_theme(self):
        self.setStyleSheet(stylesheet(self.theme))
        self.theme_btn.setText('切换浅色主题' if self.theme == 'dark' else '切换深色主题')

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.apply_theme()
        self.persist()

    def persist(self, *_):
        if not hasattr(self, 'open_folder'):
            return
        try:
            save_settings({'theme': self.theme, 'accent': 'us' if self.accent_group.checkedId() == 0 else 'uk',
                           'speed': self.speed.value() / 10, 'gap': self.gap.value() / 10,
                           'repeat': self.repeat.currentIndex() + 1, 'open_folder': self.open_folder.isChecked(),
                           'last_output_dir': self.output_dir})
        except OSError:
            pass

    def choose(self):
        if self.busy:
            return
        path, _ = QFileDialog.getOpenFileName(self, '选择词汇表', '', FILE_FILTER)
        if path:
            self.import_path(path)

    def choose_image(self):
        if self.busy:
            return
        path, _ = QFileDialog.getOpenFileName(self, '导入图片', '', '图片 (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)')
        if path:
            self.import_path(path)

    def paste_image(self):
        if self.busy:
            return
        clipboard = QApplication.clipboard()
        image = clipboard.image()
        if image.isNull():
            urls = clipboard.mimeData().urls()
            if urls and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).suffix.lower() in IMAGE_EXTENSIONS:
                self.import_path(urls[0].toLocalFile())
                return
            QMessageBox.information(self, '剪贴板没有图片', '请先复制图片或截图，再点击「粘贴图片」。快捷键：Ctrl+Shift+V。')
            return
        from PySide6.QtCore import QBuffer, QIODevice
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, 'PNG')
        raw = bytes(buffer.data())
        self.start_ocr(Image.open(io.BytesIO(raw)), '剪贴板图片')

    def import_path(self, path):
        if self.busy:
            return
        if Path(path).suffix.lower() in IMAGE_EXTENSIONS:
            self.start_ocr(path, Path(path).name)
        else:
            self.run_task('document', lambda: (*read_file(path), str(path)))

    def start_ocr(self, source, name):
        def task():
            image = load_image(source)
            if self.cancel_event.is_set():
                raise InterruptedError('已取消识别')
            recognition = recognize_image(image)
            return image, recognition, name
        self.run_task('ocr', task)

    def run_task(self, kind, function):
        if self.busy:
            return
        self.busy = True
        self.task_kind = kind
        self.cancel_event.clear()
        self.set_busy(True)
        self.progress.setRange(0, 0)
        self.status.setText({'ocr': '正在本机识别图片，首次加载模型可能需要几秒…',
                             'document': '正在读取文档…', 'audio': '正在下载并生成音频…'}[kind])
        def worker():
            try:
                self.q.put(('done', kind, function()))
            except Exception as exc:
                self.q.put(('error', kind, str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def set_busy(self, busy):
        for item in (self.choose_btn, self.image_btn, self.paste_btn, self.edit_btn,
                     self.remove_btn, self.folder_btn, self.gen_btn, self.name_entry):
            item.setEnabled(not busy)
        self.cancel_btn.setVisible(busy)
        self.cancel_btn.setEnabled(busy)
        for b in self.nav[1:3]:
            b.setEnabled(not busy)

    def cancel_work(self):
        self.cancel_event.set()
        self.cancel_btn.setEnabled(False)
        self.status.setText('正在取消，当前处理结束后返回；识别结果不会写入词表。')

    def poll(self):
        while True:
            try:
                item = self.q.get_nowait()
            except queue.Empty:
                return
            if item[0] == 'progress':
                if not self.cancel_event.is_set():
                    _, i, n, word, state = item
                    self.progress.setRange(0, n)
                    self.progress.setValue(i)
                    self.status.setText(f'{i}/{n} · {word} · {state}')
                continue
            self.busy = False
            self.set_busy(False)
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            if self.close_requested:
                self.close()
                return
            if self.cancel_event.is_set():
                # Audio may finish its atomic export just before cancellation.
                self.status.setText('任务已停止。词表保持原样。' + ('请检查输出文件夹是否已有完成的音频。' if item[1] == 'audio' else ''))
                continue
            if item[0] == 'error':
                self.status.setText('处理失败，可以重试。')
                QMessageBox.warning(self, '处理失败', item[2])
            elif item[1] == 'ocr':
                image, recognition, name = item[2]
                self.status.setText('识别完成，请校对文字。')
                dialog = ReviewDialog(self, image, recognition)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.words = deduplicate(self.words + dialog.words) if dialog.append else dialog.words
                    self.source_name = name
                    self.file_hint.setText('图片：' + name)
                    self.name_entry.setText(Path(name).stem + '_audio')
                    self.refresh_table()
                    self.status.setText(f'已提取词汇，共 {len(self.words)} 个。生成前仍可编辑。')
                else:
                    self.status.setText('已关闭识别结果，当前词表保持原样。')
            elif item[1] == 'document':
                words, method, path = item[2]
                if not words:
                    QMessageBox.information(self, '没有找到单词', '文档没有可提取的英文词汇。扫描 PDF 请先导出为图片，再使用「导入图片」。')
                    self.status.setText('未找到单词，当前词表保持原样。')
                else:
                    self.words = words
                    self.source_name = Path(path).name
                    self.file_hint.setText('文档：' + self.source_name)
                    self.name_entry.setText(Path(path).stem + '_audio')
                    self.refresh_table()
                    self.status.setText(f'已读取 {len(words)} 个词条（{method}）。')
            elif item[1] == 'audio':
                target, good, failed = item[2]
                self.progress.setValue(100)
                self.status.setText(f'已导出 {len(good)} 个词条的音频。')
                if failed:
                    report = Path(target).with_suffix('.失败词表.txt')
                    try:
                        report.write_text('\n'.join(f'{w}: {e}' for w, e in failed), encoding='utf-8-sig')
                        detail = f'失败词未包含在音频中。失败清单：\n{report}'
                    except OSError as exc:
                        detail = '失败清单保存失败：' + str(exc)
                    QMessageBox.warning(self, '部分完成', f'成功 {len(good)} 个，失败 {len(failed)} 个。\n{detail}')
                else:
                    QMessageBox.information(self, '音频生成完成', str(target))
                if self.open_folder.isChecked():
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(target).parent)))

    def refresh_table(self):
        self.table.setRowCount(len(self.words))
        for row, word in enumerate(self.words):
            for col, value in enumerate((str(row + 1).zfill(2), word, '待生成')):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.count.setText(f'{len(self.words)} 个词条')
        self.empty.setVisible(not self.words)
        self.table.setVisible(bool(self.words))
        self.filter_words()

    def filter_words(self, *_):
        text = self.search.text().strip().casefold()
        for row, word in enumerate(self.words):
            self.table.setRowHidden(row, text not in word.casefold())

    def remove_selected(self):
        if self.busy:
            return
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            if not self.table.isRowHidden(row):
                del self.words[row]
        self.refresh_table()

    def edit_words(self):
        if self.busy:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle('编辑词汇列表')
        dialog.resize(560, 590)
        box = layout(dialog, 24, 16)
        box.addWidget(label('校对你的词汇', 'title'))
        box.addWidget(label('每行一个英文单词或词组，保存时自动去重并保留顺序。', 'muted', True))
        editor = QPlainTextEdit('\n'.join(self.words))
        editor.setPlaceholderText('apple\nlook up\nbanana')
        box.addWidget(editor, 1)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(button('取消', dialog.reject))
        actions.addWidget(button('保存词表', dialog.accept, 'primary'))
        box.addLayout(actions)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.words = deduplicate(editor.toPlainText().splitlines())
            self.refresh_table()
            self.status.setText(f'已更新，共 {len(self.words)} 个词条。')

    def choose_dir(self):
        folder = QFileDialog.getExistingDirectory(self, '选择音频保存文件夹', self.output_dir)
        if folder:
            self.output_dir = folder
            self.folder_hint.setText(folder)
            self.folder_hint.setToolTip(folder)
            self.persist()

    def start_audio(self):
        if self.busy:
            return
        words = deduplicate(self.words)
        if not words:
            QMessageBox.information(self, '词表为空', '请先导入文件或图片，或点击「编辑词表」粘贴词汇。')
            return
        base = self.name_entry.text().strip()
        reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{p}{n}' for p in ('COM', 'LPT') for n in range(1, 10)}
        if not base or any(c in base for c in '\\/:*?"<>|') or base.endswith(('.', ' ')) or base.split('.')[0].upper() in reserved:
            QMessageBox.warning(self, '文件名无效', '请输入合法的 Windows 文件名，不含特殊符号或系统保留名称。')
            return
        target = Path(self.output_dir) / (base + '.mp3')
        if target.exists() and QMessageBox.question(self, '覆盖音频', '同名音频已存在，是否覆盖？') != QMessageBox.StandardButton.Yes:
            return
        accent = 'us' if self.accent_group.checkedId() == 0 else 'uk'
        gap, speed, repeat = self.gap.value() * 100, self.speed.value() / 10, self.repeat.currentIndex() + 1
        self.persist()
        def task():
            good, failed = render_audio(words, str(target), accent=accent, gap_ms=gap,
                                        pace=speed, repeat=repeat,
                                        progress=lambda i, n, w, s: self.q.put(('progress', i, n, w, s)),
                                        is_cancelled=self.cancel_event.is_set)
            return target, good, failed
        self.run_task('audio', task)

    def help_dialog(self):
        QMessageBox.information(self, '使用帮助',
            '1. 导入文档、图片，或复制截图后按 Ctrl+Shift+V。\n'
            '2. 图片识别后先校对文字，再提取并替换 / 追加词表。\n'
            '3. 双击词表或点击「编辑词表」修改词汇。\n'
            '4. 设置美式 / 英式、语速、停顿及重复次数，生成 MP3。\n\n'
            '图片支持印刷中英文；模糊、手写、复杂多栏可能误识别。\n'
            '扫描 PDF 请先导出图片；原生 WPS / DOC 请另存为 DOCX。\n'
            '识别文字可复制或保存 TXT，音频流程只提取英文词条。')

    def about_dialog(self):
        QMessageBox.information(self, '软件与隐私',
            f'VocabAudio {VERSION}\n\n'
            '图片识别与文档解析均在本机完成，不上传原文件。\n'
            '生成音频时，英文词条会发送到第三方有道发音接口。\n'
            '本软件不保证第三方服务可用，也不保证音频为真人录音。\n\n'
            f'设置目录：{data_dir()}\n\n'
            '卸载：关闭软件后运行同目录的 Uninstall_VocabAudio.bat。\n'
            '开源许可与依赖声明见 LICENSE 和 THIRD_PARTY_NOTICES.md。')

    def dragEnterEvent(self, event):
        if not self.busy and event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile() and Path(urls[0].toLocalFile()).suffix.lower() in IMAGE_EXTENSIONS + DOCUMENT_EXTENSIONS:
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not self.busy and len(urls) == 1 and urls[0].isLocalFile():
            self.import_path(urls[0].toLocalFile())
            event.acceptProposedAction()

    def closeEvent(self, event):
        if self.busy:
            if QMessageBox.question(self, '结束当前任务', '是否取消当前任务并退出？当前处理结束后会自动关闭。') == QMessageBox.StandardButton.Yes:
                self.close_requested = True
                self.cancel_work()
            event.ignore()
            return
        self.persist()
        event.accept()


def run():
    application = QApplication.instance() or QApplication([])
    application.setStyle('Fusion')
    application.setApplicationName('VocabAudio')
    window = App()
    window.show()
    return application.exec()
