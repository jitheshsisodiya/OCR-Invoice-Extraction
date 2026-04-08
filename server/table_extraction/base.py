"""Abstract base class for table extractors."""
from abc import ABC, abstractmethod
from pathlib import Path


class TableExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str | Path, page_number: int) -> list[list[list[str]]]:
        """
        Extract tables from a document page.

        Returns:
            List of tables. Each table is a 2D list: table[row][col] = str.
        """
