"""Deduplicate and merge tables from multiple extractors."""
from __future__ import annotations


def reconcile_tables(
    tables_primary: list[list[list[str]]],
    tables_fallback: list[list[list[str]]],
) -> list[list[list[str]]]:
    """
    Return primary tables if non-empty, else fallback.
    Simple strategy: primary (camelot) wins; fallback (opencv/tabula) used only when primary yields nothing.
    """
    if tables_primary:
        return tables_primary
    return tables_fallback


def normalize_table(table: list[list[str]]) -> list[list[str]]:
    """Strip whitespace from all cells and ensure uniform row width."""
    if not table:
        return table
    max_cols = max(len(row) for row in table)
    normalized = []
    for row in table:
        stripped = [cell.strip() for cell in row]
        # Pad short rows
        padded = stripped + [""] * (max_cols - len(stripped))
        normalized.append(padded)
    return normalized
