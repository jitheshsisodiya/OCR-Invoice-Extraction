/** Strip sheet prefix from cell address. e.g. "Sheet1!B5" → "B5" */
export function stripSheetPrefix(address: string): string {
  return address.includes("!") ? address.split("!")[1] : address;
}

/** Parse column letter + row number from cell address. */
export function parseCellAddress(address: string): { col: string; row: number } {
  const clean = stripSheetPrefix(address).toUpperCase();
  const match = clean.match(/^([A-Z]+)(\d+)$/);
  if (!match) return { col: "A", row: 1 };
  return { col: match[1], row: parseInt(match[2], 10) };
}
