"""Tesseract OCR engine wrapper."""
from __future__ import annotations
import pytesseract
from PIL import Image
from .base import OCREngine
from .result import BoundingBox, OCRResult, OCRWord
from loguru import logger


class TesseractOCREngine(OCREngine):
    """Wraps pytesseract, returns normalized OCRResult."""

    def __init__(self, cmd_path: str | None = None):
        if cmd_path:
            pytesseract.pytesseract.tesseract_cmd = cmd_path

    @property
    def name(self) -> str:
        return "tesseract"

    def extract(self, image: Image.Image, lang: str = "eng") -> OCRResult:
        try:
            data = pytesseract.image_to_data(
                image, lang=lang, output_type=pytesseract.Output.DICT
            )
        except Exception as exc:
            logger.error(f"Tesseract extraction failed: {exc}")
            return OCRResult.empty(self.name)

        words: list[OCRWord] = []
        img_w, img_h = image.size

        for i, text in enumerate(data["text"]):
            text = text.strip()
            if not text:
                continue
            conf_raw = data["conf"][i]
            if conf_raw < 0:
                continue
            conf = float(conf_raw) / 100.0
            bbox = BoundingBox.from_pixels(
                x=data["left"][i],
                y=data["top"][i],
                w=data["width"][i],
                h=data["height"][i],
                img_w=img_w,
                img_h=img_h,
            )
            words.append(OCRWord(text=text, bbox=bbox, confidence=conf))

        full_text = pytesseract.image_to_string(image, lang=lang).strip()
        mean_conf = sum(w.confidence for w in words) / len(words) if words else 0.0

        return OCRResult(
            full_text=full_text,
            words=words,
            confidence=mean_conf,
            engine=self.name,
        )

    def extract_region(self, image: Image.Image, bbox_norm: dict, lang: str = "eng") -> OCRResult:
        img_w, img_h = image.size
        x1 = int(bbox_norm["x1"] * img_w)
        y1 = int(bbox_norm["y1"] * img_h)
        x2 = int(bbox_norm["x2"] * img_w)
        y2 = int(bbox_norm["y2"] * img_h)
        cropped = image.crop((x1, y1, x2, y2))
        return self.extract(cropped, lang=lang)
