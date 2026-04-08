import React, { useCallback } from "react";
import { Button, Text, Spinner, Divider } from "@fluentui/react-components";
import { useAppStore } from "../store/appStore";
import { exportExcel } from "../api/client";

export function ExportPanel() {
  const { sessionId, document, isLoading, setIsLoading } = useAppStore();

  const handleExport = useCallback(async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const res = await exportExcel(sessionId);
      // Create download link
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = window.document.createElement("a");
      a.href = url;
      a.download = `OCR_Export_${Date.now()}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
      alert("Export failed.");
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, setIsLoading]);

  if (!document) return null;

  return (
    <div style={{ padding: "8px 12px 16px" }}>
      <Divider style={{ marginBottom: 8 }} />
      <Text weight="semibold" size={300} block style={{ marginBottom: 6 }}>Export</Text>
      <Text size={200} block style={{ color: "#666", marginBottom: 8 }}>
        Downloads .xlsx with all clips + Source Map traceability sheet.
      </Text>
      <Button
        appearance="primary"
        onClick={handleExport}
        disabled={isLoading || !sessionId}
      >
        {isLoading ? <Spinner size="tiny" /> : "Download Excel (.xlsx)"}
      </Button>
    </div>
  );
}
