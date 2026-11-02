import os
import socket

import pytest
from PIL import Image
from image_ocr import (blocks_to_text, load_image, words_from_ocr_text,
                       recognize_image, smoke_image)


def box(x, y, width=80, height=24):
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


def test_table_rows_keep_columns_and_reading_order():
    text = blocks_to_text([box(160, 50), box(20, 10), box(20, 50), box(160, 10)],
                          ['香蕉', 'apple', 'banana', '苹果'])
    assert text == 'apple\t苹果\nbanana\t香蕉'
    assert words_from_ocr_text(text) == ['apple', 'banana']


def test_phrase_blocks_are_joined_and_text_is_editable():
    assert blocks_to_text([box(20, 10, 50), box(78, 10, 30)], ['look', 'up']) == 'look up'
    assert words_from_ocr_text('单词\n1. apple苹果\n2. look up 查找\napple\n3. banana') == ['apple', 'look up', 'banana']


def test_transparency_is_white_and_original_is_preserved():
    source = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
    image = load_image(source)
    assert image.mode == 'RGB' and image.getpixel((0, 0)) == (255, 255, 255)
    assert source.mode == 'RGBA'


def test_orientation_is_corrected(tmp_path):
    image = Image.new('RGB', (80, 40), 'white')
    exif = image.getexif()
    exif[274] = 6
    path = tmp_path / 'phone.jpg'
    image.save(path, exif=exif)
    assert load_image(path).size == (40, 80)


def test_unreadable_unsupported_and_oversize_images(tmp_path, monkeypatch):
    path = tmp_path / 'bad.png'
    path.write_bytes(b'not an image')
    with pytest.raises(ValueError, match='无法读取'):
        load_image(path)
    with pytest.raises(ValueError, match='请选择'):
        load_image(tmp_path / 'file.svg')
    monkeypatch.setattr('image_ocr.MAX_FILE_BYTES', 1)
    with pytest.raises(ValueError, match='25 MB'):
        load_image(path)
    monkeypatch.setattr('image_ocr.MAX_PIXELS', 100)
    with pytest.raises(ValueError, match='万像素'):
        load_image(Image.new('RGB', (30, 30)))


def test_real_ocr_runs_without_network(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('OCR must not access the network')
    monkeypatch.setattr(socket.socket, 'connect', no_network)
    result = recognize_image(smoke_image())
    assert words_from_ocr_text(result.text) == ['apple', 'banana']
    assert recognize_image(Image.new('RGB', (400, 300), 'white')).text == ''
