"""Write CalcClip SUM formulas to Excel cells."""
from openpyxl.worksheet.worksheet import Worksheet


def write_calc_clip(ws: Worksheet, excel_cell: str, formula: str) -> None:
    """Write a SUM formula to a cell. formula is e.g. '=SUM(B2,B3,B4)'."""
    cell_ref = excel_cell.split("!")[-1] if "!" in excel_cell else excel_cell
    ws[cell_ref] = formula
