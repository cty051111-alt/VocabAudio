"""Local image OCR. No image URLs, uploads, or runtime model downloads."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
import re
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from vocab_core import from_lines

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tif', '.tiff')
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_PIXELS = 24_000_000


def load_image(source):
    """Read only local images, flatten transparency and apply phone orientation."""
    try:
        if isinstance(source, Image.Image):
            image = source
            owned = False
        else:
            path = Path(source)
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                raise ValueError('请选择 PNG、JPG、BMP、WebP 或 TIFF 图片。')
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError('图片超过 25 MB，请先压缩或裁剪。')
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                image = Image.open(path)
            owned = True
        opened = image
        try:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError('图片超过 2400 万像素，请先缩小或裁剪。')
            if min(image.size) < 16:
                raise ValueError('图片尺寸太小，请使用清晰的原图。')
            image = ImageOps.exif_transpose(image)
            rgba = image.convert('RGBA')
            background = Image.new('RGBA', rgba.size, 'white')
            background.alpha_composite(rgba)
            result = background.convert('RGB')
            result.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
            return result
        finally:
            if owned:
                opened.close()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError('无法读取图片，请确认文件完整，或转换为 PNG / JPG 后重试。') from exc


def blocks_to_text(boxes, texts):
    """Group horizontal blocks into rows; preserve wide column gaps as tabs."""
    blocks = []
    for box, text in zip(boxes, texts):
        text = str(text).strip()
        if not text:
            continue
        xs = [float(point[0]) for point in box]
        ys = [float(point[1]) for point in box]
        blocks.append((min(xs), min(ys), max(xs), max(ys), text))
    rows = []
    for block in sorted(blocks, key=lambda b: ((b[1] + b[3]) / 2, b[0])):
        middle = (block[1] + block[3]) / 2
        height = max(1, block[3] - block[1])
        row = next((r for r in reversed(rows)
                    if abs(r[0] - middle) <= .45 * min(r[1], height)), None)
        if row is None:
            rows.append([middle, height, [block]])
        else:
            row[2].append(block)
    lines = []
    for _, _, row in rows:
        row.sort(key=lambda b: b[0])
        line = row[0][4]
        for previous, block in zip(row, row[1:]):
            gap = block[0] - previous[2]
            separator = '\t' if gap > 1.5 * max(1, block[3] - block[1]) else ' '
            line += separator + block[4]
        lines.append(line)
    return '\n'.join(lines)


def words_from_ocr_text(text):
    """Use the existing vocabulary parser, including attached Chinese meanings."""
    lines = []
    for line in text.splitlines():
        # OCR often removes the separator between an English word and its meaning.
        line = re.split(r'[\u3400-\u9fff]', line, maxsplit=1)[0].rstrip()
        lines.append(line)
    return from_lines(lines)


@lru_cache(maxsize=1)
def get_engine():
    import rapidocr
    from rapidocr import RapidOCR
    models = Path(rapidocr.__file__).parent / 'models'
    files = {'Det': 'PP-OCRv6_det_small.onnx',
             'Cls': 'ch_ppocr_mobile_v2.0_cls_mobile.onnx',
             'Rec': 'PP-OCRv6_rec_small.onnx'}
    params = {'Global.log_level': 'error',
              'EngineConfig.onnxruntime.intra_op_num_threads': 2,
              'EngineConfig.onnxruntime.inter_op_num_threads': 1}
    for task, filename in files.items():
        path = models / filename
        if not path.is_file():
            raise RuntimeError('本地 OCR 模型缺失，请重新安装完整软件包。不会自动联网下载。')
        params[f'{task}.model_path'] = str(path)
    return RapidOCR(params=params)


@dataclass
class Recognition:
    text: str
    low_confidence: int


def recognize_image(image):
    import numpy as np
    result = get_engine()(np.asarray(image))
    if result.txts is None or result.boxes is None:
        return Recognition('', 0)
    scores = result.scores if result.scores is not None else []
    return Recognition(blocks_to_text(result.boxes, result.txts),
                       sum(float(score) < .8 for score in scores))


def smoke_image():
    """Portable generated fixture used for real offline EXE OCR verification."""
    from PIL import ImageDraw, ImageFont
    image = Image.new('RGB', (700, 200), 'white')
    # Pillow's bundled font needs no system font or network access.
    font = ImageFont.load_default(size=40)
    draw = ImageDraw.Draw(image)
    draw.text((35, 30), 'apple', font=font, fill='black')
    draw.text((35, 110), 'banana', font=font, fill='black')
    return image
