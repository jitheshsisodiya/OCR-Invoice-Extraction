import React, { useRef, useState, useCallback, useEffect } from "react";
import { Button, Text, Spinner } from "@fluentui/react-components";
import { useAppStore } from "../store/appStore";
import { useClip } from "../hooks/useClip";
import { normalizeBbox } from "../utils/bboxUtils";
import { getThumbnailUrl, createTextClip, createTableClip, extractPage, extractDocument } from "../api/client";
import { getActiveCellAddress, getSelectionAddress, writeCellValue, writeTableValues, writeFormula, applyValidationStyle } from "../hooks/useExcel";

export function DocumentViewer() {
  const { document, sessionId, currentPage, setCurrentPage, activeClipType, addClip } = useAppStore();
  const [imgSize, setImgSize] = useState({ w: 1, h: 1 });
  const [isExtracting, setIsExtracting] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { isDrawing, currentBbox, confirmedBbox, onMouseDown, onMouseMove, onMouseUp, reset } = useClip();

  if (!document) return null;

  const thumbnailUrl = getThumbnailUrl(document.id, currentPage);

  const onImgLoad = () => {
    if (imgRef.current) {
      setImgSize({ w: imgRef.current.clientWidth, h: imgRef.current.clientHeight });
    }
  };

  const getRelativePos = (e: React.MouseEvent) => {
    const rect = containerRef.current!.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!["text", "table"].includes(activeClipType)) return;
    const pos = getRelativePos(e);
    onMouseDown(pos.x, pos.y);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const pos = getRelativePos(e);
    onMouseMove(pos.x, pos.y);
  };

  const handleMouseUp = async (e: React.MouseEvent) => {
    const pos = getRelativePos(e);
    onMouseUp(pos.x, pos.y);

    const bbox = confirmedBbox || currentBbox;
    if (!bbox || !sessionId || !document) return;

    const normBbox = normalizeBbox(bbox, imgSize.w, imgSize.h);

    try {
      setIsExtracting(true);
      if (activeClipType === "text") {
        const cellAddr = await getActiveCellAddress();
        const res = await createTextClip({
          session_id: sessionId,
          document_id: document.id,
          file_path: (document as any).file_path || "",
          page_number: currentPage,
          bbox: normBbox,
          excel_cell: cellAddr,
        });
        const clip = res.data;
        const value = JSON.parse(clip.extracted_value || '""');
        await writeCellValue(cellAddr, String(value));
        await applyValidationStyle(cellAddr, "pending");
        addClip({ id: clip.id, clip_type: "text", page_number: currentPage, extracted_value: String(value), excel_cell: cellAddr, confidence: clip.confidence, validation_status: "pending" });
        reset();
      } else if (activeClipType === "table") {
        const selAddr = await getSelectionAddress();
        const res = await createTableClip({
          session_id: sessionId,
          document_id: document.id,
          file_path: (document as any).file_path || "",
          page_number: currentPage,
          bbox: normBbox,
          excel_range: selAddr,
        });
        const clip = res.data;
        const tableData = JSON.parse(clip.extracted_value || "[]");
        if (Array.isArray(tableData) && tableData.length) {
          const startCell = selAddr.split("!")[1]?.split(":")[0] || selAddr;
          await writeTableValues(startCell, tableData);
        }
        addClip({ id: clip.id, clip_type: "table", page_number: currentPage, extracted_value: JSON.stringify(tableData), excel_range: selAddr, confidence: clip.confidence, validation_status: "pending" });
        reset();
      }
    } catch (err) {
      console.error("Clip failed:", err);
    } finally {
      setIsExtracting(false);
    }
  };

  const handlePageExtract = async () => {
    if (!sessionId || !document) return;
    setIsExtracting(true);
    try {
      await extractPage(sessionId, (document as any).file_path || "", currentPage);
      alert("Page extracted. Assign clips to cells in the Data Grid below.");
    } finally {
      setIsExtracting(false);
    }
  };

  const handleDocExtract = async () => {
    if (!sessionId || !document) return;
    setIsExtracting(true);
    try {
      await extractDocument(sessionId, (document as any).file_path || "", [1, Math.min(document.page_count, 5)]);
      alert("Document extracted.");
    } finally {
      setIsExtracting(false);
    }
  };

  useEffect(() => {
    if (activeClipType === "page") handlePageExtract();
    if (activeClipType === "document") handleDocExtract();
  }, [activeClipType]);

  return (
    <div style={{ padding: "0 12px 12px" }}>
      {/* Page navigation */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <Button size="small" disabled={currentPage <= 1} onClick={() => setCurrentPage(currentPage - 1)}>‹</Button>
        <Text size={200}>Page {currentPage} / {document.page_count}</Text>
        <Button size="small" disabled={currentPage >= document.page_count} onClick={() => setCurrentPage(currentPage + 1)}>›</Button>
        {isExtracting && <Spinner size="tiny" />}
      </div>

      {/* Document preview with drawing canvas overlay */}
      <div
        ref={containerRef}
        style={{ position: "relative", cursor: ["text", "table"].includes(activeClipType) ? "crosshair" : "default", userSelect: "none" }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <img
          ref={imgRef}
          src={thumbnailUrl}
          alt={`Page ${currentPage}`}
          onLoad={onImgLoad}
          style={{ width: "100%", display: "block", border: "1px solid #ddd" }}
        />
        {/* Selection rectangle overlay */}
        {currentBbox && (
          <div
            style={{
              position: "absolute",
              left: currentBbox.x1,
              top: currentBbox.y1,
              width: currentBbox.x2 - currentBbox.x1,
              height: currentBbox.y2 - currentBbox.y1,
              border: "2px solid #0078D4",
              backgroundColor: "rgba(0,120,212,0.15)",
              pointerEvents: "none",
            }}
          />
        )}
      </div>
    </div>
  );
}
