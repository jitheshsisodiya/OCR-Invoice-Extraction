/**
 * Office.js function commands invoked directly by ribbon buttons.
 * These run in the hidden commands.html iframe — NO task pane is opened.
 */

const VALIDATED_COLOR = "#C6EFCE";
const EXCEPTION_COLOR = "#FFC7CE";
const PENDING_COLOR   = "";          // clear fill

Office.onReady(() => {
  // Register functions on the global Office object so Excel can invoke them.
  (globalThis as any).validateCell  = validateCell;
  (globalThis as any).markException = markException;
});

/** Mark the active cell as Validated (green fill). */
function validateCell(event: Office.AddinCommands.Event) {
  Excel.run(async (ctx) => {
    const cell = ctx.workbook.getActiveCell();
    cell.format.fill.color = VALIDATED_COLOR;
    cell.format.font.color  = "#276221";
    await ctx.sync();
    event.completed();
  }).catch((err) => {
    console.error("validateCell error:", err);
    event.completed();
  });
}

/** Mark the active cell as an Exception (red fill). */
function markException(event: Office.AddinCommands.Event) {
  Excel.run(async (ctx) => {
    const cell = ctx.workbook.getActiveCell();
    cell.format.fill.color = EXCEPTION_COLOR;
    cell.format.font.color  = "#9C0006";
    await ctx.sync();
    event.completed();
  }).catch((err) => {
    console.error("markException error:", err);
    event.completed();
  });
}

/** Clear any validation styling from the active cell. */
function clearValidation(event: Office.AddinCommands.Event) {
  Excel.run(async (ctx) => {
    const cell = ctx.workbook.getActiveCell();
    cell.format.fill.color = PENDING_COLOR;
    cell.format.font.color  = "";
    await ctx.sync();
    event.completed();
  }).catch((err) => {
    console.error("clearValidation error:", err);
    event.completed();
  });
}

(globalThis as any).clearValidation = clearValidation;
