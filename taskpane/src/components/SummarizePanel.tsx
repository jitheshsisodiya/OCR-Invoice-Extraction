import React, { useCallback } from "react";
import { Button, Text, Spinner, Divider } from "@fluentui/react-components";
import { useAppStore } from "../store/appStore";
import { summarizeDocument } from "../api/client";

export function SummarizePanel() {
  const { document, summary, setSummary, isLoading, setIsLoading } = useAppStore();

  const handleSummarize = useCallback(async () => {
    if (!document) return;
    setIsLoading(true);
    try {
      const res = await summarizeDocument(document.id);
      setSummary(res.data.summary || res.data.note || "No summary available.");
    } catch (err) {
      console.error("Summarize failed:", err);
    } finally {
      setIsLoading(false);
    }
  }, [document, setSummary, setIsLoading]);

  if (!document) return null;

  return (
    <div style={{ padding: "8px 12px" }}>
      <Divider style={{ marginBottom: 8 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <Text weight="semibold" size={300}>Summary</Text>
        <Button size="small" onClick={handleSummarize} disabled={isLoading}>
          {isLoading ? <Spinner size="tiny" /> : "Summarize"}
        </Button>
      </div>
      {summary && (
        <Text size={200} block style={{ whiteSpace: "pre-wrap", background: "#f9f9f9", padding: 6, borderRadius: 4 }}>
          {summary}
        </Text>
      )}
    </div>
  );
}
