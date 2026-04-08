/** Normalize pixel bbox to 0-1 relative coordinates. */
export function normalizeBbox(px: { x1: number; y1: number; x2: number; y2: number }, imgW: number, imgH: number) {
  return {
    x1: px.x1 / imgW,
    y1: px.y1 / imgH,
    x2: px.x2 / imgW,
    y2: px.y2 / imgH,
  };
}

/** Convert normalized bbox back to pixel coordinates. */
export function denormalizeBbox(norm: { x1: number; y1: number; x2: number; y2: number }, imgW: number, imgH: number) {
  return {
    x1: norm.x1 * imgW,
    y1: norm.y1 * imgH,
    x2: norm.x2 * imgW,
    y2: norm.y2 * imgH,
  };
}
