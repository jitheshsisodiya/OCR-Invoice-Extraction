/**
 * Office.js Excel API wrappers.
 * All functions return Promises.
 */

/** Get the address of the currently selected cell (e.g. "Sheet1!B5"). */
export async function getActiveCellAddress(): Promise<string> {
  return Excel.run(async (ctx) => {
    const cell = ctx.workbook.getActiveCell();
    cell.load("address");
    await ctx.sync();
    return cell.address;
  });
}

/** Get the address range of the current selection (e.g. "Sheet1!B5:D8"). */
export async function getSelectionAddress(): Promise<string> {
  return Excel.run(async (ctx) => {
    const range = ctx.workbook.getSelectedRange();
    range.load("address");
    await ctx.sync();
    return range.address;
  });
}

/** Write a single text value to a cell. */
export async function writeCellValue(cellAddress: string, value: string): Promise<void> {
  return Excel.run(async (ctx) => {
    const ref = cellAddress.includes("!") ? cellAddress.split("!")[1] : cellAddress;
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    const cell = sheet.getRange(ref);
    cell.values = [[value]];
    await ctx.sync();
  });
}

/** Write a 2D array to a range starting at the given cell. */
export async function writeTableValues(startCell: string, data: string[][]): Promise<void> {
  if (!data.length) return;
  return Excel.run(async (ctx) => {
    const ref = startCell.includes("!") ? startCell.split("!")[1] : startCell;
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange(ref).getResizedRange(data.length - 1, data[0].length - 1);
    range.values = data;
    await ctx.sync();
  });
}

/** Write a formula to a cell. */
export async function writeFormula(cellAddress: string, formula: string): Promise<void> {
  return Excel.run(async (ctx) => {
    const ref = cellAddress.includes("!") ? cellAddress.split("!")[1] : cellAddress;
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    const cell = sheet.getRange(ref);
    cell.formulas = [[formula]];
    await ctx.sync();
  });
}

/** Apply a fill color to a cell. */
export async function setCellFill(cellAddress: string, hexColor: string): Promise<void> {
  return Excel.run(async (ctx) => {
    const ref = cellAddress.includes("!") ? cellAddress.split("!")[1] : cellAddress;
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    const cell = sheet.getRange(ref);
    cell.format.fill.color = hexColor;
    await ctx.sync();
  });
}

/** Mark a cell as validated (green) or exception (red). */
export async function applyValidationStyle(cellAddress: string, status: "validated" | "exception" | "pending"): Promise<void> {
  const colorMap: Record<string, string> = {
    validated: "#C6EFCE",
    exception: "#FFC7CE",
    pending: "#FFEB9C",
  };
  return setCellFill(cellAddress, colorMap[status] ?? "#FFFFFF");
}

/** Get the active sheet name. */
export async function getActiveSheetName(): Promise<string> {
  return Excel.run(async (ctx) => {
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    sheet.load("name");
    await ctx.sync();
    return sheet.name;
  });
}
