"""Offline tests: do not contact a pronunciation provider."""
import pytest
from docx import Document
import vocab_core as core


def test_deduplication_retains_order_and_normalizes():
    words = ["  Acquire ", "acquire", "adopt", "apply", "adopt", "优先"]
    assert core.deduplicate(words) == ["Acquire", "adopt", "apply"]


def test_youdao_us_and_uk_url_encoding():
    assert "audio=look+up" in core.youdao_url("look up", "us")
    assert "type=2" in core.youdao_url("look up", "us")
    assert "type=1" in core.youdao_url("look up", "uk")


def test_word_column_preferred_over_ipa_and_expansion(tmp_path):
    path = tmp_path / "vocabulary.docx"
    doc = Document()
    table = doc.add_table(rows=1, cols=7)
    headers = ["序号", "英文单词", "音标", "词性", "中文释义", "词形拓展／搭配", "默写区"]
    for cell, h in zip(table.rows[0].cells, headers):
        cell.text = h
    for n, word, extra in [(1, "acquire", "acquisition n."), (2, "deterioration", "deteriorate v."), (3, "combination", "combine v.")]:
        row = table.add_row().cells
        for cell, value in zip(row, [str(n), word, "/əˈkwaɪə/", "n.", "中文释义", extra, "________"]):
            cell.text = value
    doc.save(path)
    words, method = core.read_file(path)
    assert words == ["acquire", "deterioration", "combination"]
    assert method == "Word 表格"


def test_simple_txt(tmp_path):
    path = tmp_path / "vocab.txt"
    path.write_text("1. acquire\n2. adopt\n3. acquire\n", encoding="utf-8")
    words, _ = core.read_file(path)
    assert words == ["acquire", "adopt"]


def test_pdf_text_layer(tmp_path):
    import pymupdf
    path = tmp_path / "vocab.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 60), "acquire", fontsize=12)
    page.insert_text((50, 80), "adopt", fontsize=12)
    doc.save(path)
    words, method = core.read_file(path)
    assert words == ["acquire", "adopt"]
    assert method.startswith("PDF")


def test_legacy_file_rejected(tmp_path):
    path = tmp_path / "old.wps"
    path.write_bytes(b"fake")
    with pytest.raises(ValueError, match="docx"):
        core.read_file(path)
