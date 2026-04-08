"""OCR result data structures shared across all OCR engines."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BoundingBox:
    """Normalized bounding box (0–1 relative to page dimensions)."""
    x1: float
    y1: float
    x2: float
    y2: float

    @classmethod
    def from_pixels(cls, x: int, y: int, w: int, h: int, img_w: int, img_h: int) -> "BoundingBox":
        return cls(
            x1=x / img_w,
            y1=y / img_h,
            x2=(x + w) / img_w,
            y2=(y + h) / img_h,
        )

    def to_pixels(self, img_w: int, img_h: int) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) in pixel coordinates."""
        x = int(self.x1 * img_w)
        y = int(self.y1 * img_h)
        w = int((self.x2 - self.x1) * img_w)
        h = int((self.y2 - self.y1) * img_h)
        return x, y, w, h

    def to_dict(self) -> dict:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}

    @classmethod
    def from_dict(cls, d: dict) -> "BoundingBox":
        return cls(x1=d["x1"], y1=d["y1"], x2=d["x2"], y2=d["y2"])


@dataclass
class OCRWord:
    """A single recognized word with its position and confidence."""
    text: str
    bbox: BoundingBox
    confidence: float  # 0.0–1.0


@dataclass
class OCRResult:
    """Full OCR result for a page or region."""
    full_text: str
    words: list[OCRWord] = field(default_factory=list)
    confidence: float = 0.0  # mean confidence across all words
    engine: str = "unknown"

    @classmethod
    def empty(cls, engine: str = "unknown") -> "OCRResult":
        return cls(full_text="", words=[], confidence=0.0, engine=engine)
