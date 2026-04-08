"""EasyOCR engine wrapper (used for cross-validation)."""
from __future__ import annotations
import numpy as np
from PIL import Image
from .base import OCREngine
from .result import BoundingBox, OCRResult, OCRWord
from loguru import logger


class EasyOCREngine(OCREngine):
    """Wraps EasyOCR reader; lazy-initializes to avoid slow startup."""

    def __init__(self, model_dir: str | None = None, gpu: bool = False):
        self._gpu = gpu
        self._model_dir = model_dir
        self._reader = None  # lazy init

    @property
    def name(self) -> str:
        return "easyocr"

    def _get_reader(self, lang: str):
        """Lazy-load EasyOCR reader (downloads models on first use)."""
        import easyocr
        if self._reader is None:
            logger.info("Initializing EasyOCR reader (first use may download models)...")
            kwargs = {"gpu": self._gpu}
            if self._model_dir:
                kwargs["model_storage_directory"] = self._model_dir
            self._reader = easyocr.Reader([lang], **kwargs)
        return self._reader

    def extract(self, image: Image.Image, lang: str = "eng") -> OCRResult:
        try:
            reader = self._get_reader(lang)
            img_array = np.array(image)
            results = reader.readtext(img_array, detail=1)
        except Exception as exc:
            logger.error(f"EasyOCR extraction failed: {exc}")
            return OCRResult.empty(self.name)

        img_w, img_h = image.size
        words: list[OCRWord] = []
        texts: list[str] = []

        for bbox_pts, text, conf in results:
            text = text.strip()
            if not text:
                continue
            # bbox_pts: [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
            xs = [p[0] for p in bbox_pts]
            ys = [p[1] for p in bbox_pts]
            bbox = BoundingBox(
                x1=min(xs) / img_w,
                y1=min(ys) / img_h,
                x2=max(xs) / img_w,
                y2=max(ys) / img_h,
            )
            words.append(OCRWord(text=text, bbox=bbox, confidence=float(conf)))
            texts.append(text)

        mean_conf = sum(w.confidence for w in words) / len(words) if words else 0.0
        return OCRResult(
            full_text=" ".join(texts),
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
