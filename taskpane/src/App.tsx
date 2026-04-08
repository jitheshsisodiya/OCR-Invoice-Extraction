import React from "react";
import { Text, Divider, Badge } from "@fluentui/react-components";
import { useAppStore } from "./store/appStore";
import { UploadPanel } from "./components/UploadPanel";
import { ClipToolbar } from "./components/ClipToolbar";
import { DocumentViewer } from "./components/DocumentViewer";
import { DataGrid } from "./components/DataGrid";
import { ValidationPanel } from "./components/ValidationPanel";
import { FormExtractionPanel } from "./components/FormExtraction";
import { SummarizePanel } from "./components/SummarizePanel";
import { ExportPanel } from "./components/ExportPanel";

export default function App() {
  const { document } = useAppStore();

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", maxHeight: "100vh", overflowY: "auto" }}>
      {/* Header */}
      <div style={{ background: "#0078D4", color: "#fff", padding: "10px 12px", display: "flex", alignItems: "center", gap: 8 }}>
        <Text weight="bold" size={400} style={{ color: "#fff" }}>OCR Invoice Extraction</Text>
        {document && (
          <Badge appearance="filled" color="informative" size="small">
            {document.doc_type}
          </Badge>
        )}
      </div>

      {/* Upload (always visible) */}
      <UploadPanel />

      {document && (
        <>
          <Divider />
          {/* Clip type toolbar */}
          <ClipToolbar />

          {/* Document viewer + clip drawing */}
          <DocumentViewer />

          {/* Validation buttons */}
          <ValidationPanel />

          {/* Extracted data table */}
          <DataGrid />

          {/* Form field extraction */}
          <FormExtractionPanel />

          {/* Document summarization */}
          <SummarizePanel />

          {/* Export */}
          <ExportPanel />
        </>
      )}

      {!document && (
        <div style={{ padding: "24px 12px", textAlign: "center", color: "#999" }}>
          <Text size={300}>Upload a document to get started.</Text>
        </div>
      )}
    </div>
  );
}
