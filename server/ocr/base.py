"""Abstract base class for OCR engines."""
from abc import ABC, abstractmethod
from PIL import Image
from .result import OCRResult


class OCREngine(ABC):
    """All OCR engines must implement this interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique engine identifier e.g. 'tesseract', 'easyocr'."""

    @abstractmethod
    def extract(self, image: Image.Image, lang: str = "eng") -> OCRResult:
        """
        Run OCR on the given PIL image.

        Args:
            image: PIL Image (RGB or grayscale).
            lang:  Language code (e.g. 'eng', 'fra').

        Returns:
            OCRResult with full_text, word list, and confidence.
        """

    @abstractmethod
    def extract_region(self, image: Image.Image, bbox_norm: dict, lang: str = "eng") -> OCRResult:
        """
        Run OCR on a sub-region of the image.

        Args:
            image:     Full page PIL Image.
            bbox_norm: Normalized bbox dict {x1,y1,x2,y2} in 0–1 range.
            lang:      Language code.
        """
