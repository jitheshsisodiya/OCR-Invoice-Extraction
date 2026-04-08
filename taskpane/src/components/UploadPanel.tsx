import React, { useRef, useCallback } from "react";
import { Button, Text, Spinner } from "@fluentui/react-components";
import { uploadDocument, uploadClipboard, createSession } from "../api/client";
import { useAppStore } from "../store/appStore";
import { getActiveSheetName } from "../hooks/useExcel";

export function UploadPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setDocument, setSessionId, setIsLoading, isLoading } = useAppStore();

  const handleFileUpload = useCallback(async (file: File) => {
    setIsLoading(true);
    try {
      const uploadRes = await uploadDocument(file);
      const doc = uploadRes.data;
      setDocument({ ...doc, file_path: doc.file_path });

      const sheetName = await getActiveSheetName().catch(() => "Sheet1");
      const sessionRes = await createSession(`Session - ${file.name}`, doc.id, sheetName);
      setSessionId(sessionRes.data.id);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed. Make sure the OCR server is running.");
    } finally {
      setIsLoading(false);
    }
  }, [setDocument, setSessionId, setIsLoading]);

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
  }, [handleFileUpload]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileUpload(file);
  }, [handleFileUpload]);

  const onPaste = useCallback(async (e: React.ClipboardEvent) => {
    for (const item of Array.from(e.clipboardData.items)) {
      if (item.type.startsWith("image/")) {
        const blob = item.getAsFile();
        if (!blob) continue;
        const reader = new FileReader();
        reader.onload = async () => {
          const dataUrl = reader.result as string;
          const b64 = dataUrl.split(",")[1];
          setIsLoading(true);
          try {
            const res = await uploadClipboard(b64, ".png");
            const doc = res.data;
            setDocument({ ...doc });
            const sheetName = await getActiveSheetName().catch(() => "Sheet1");
            const sessionRes = await createSession("Clipboard Session", doc.id, sheetName);
            setSessionId(sessionRes.data.id);
          } finally {
            setIsLoading(false);
          }
        };
        reader.readAsDataURL(blob);
        break;
      }
    }
  }, [setDocument, setSessionId, setIsLoading]);

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
      onPaste={onPaste}
      style={{ padding: 12 }}
    >
      <Text weight="semibold" size={400} block>Upload Document</Text>
      <Text size={200} block style={{ color: "#666", marginBottom: 8 }}>
        PDF, PNG, JPG, TIFF — or paste a screenshot
      </Text>

      <Button
        appearance="primary"
        onClick={() => fileInputRef.current?.click()}
        disabled={isLoading}
        style={{ marginBottom: 8 }}
      >
        {isLoading ? <Spinner size="tiny" /> : "Choose File"}
      </Button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
        style={{ display: "none" }}
        onChange={onFileChange}
      />

      <div
        style={{
          border: "2px dashed #ccc",
          borderRadius: 4,
          padding: "16px 8px",
          textAlign: "center",
          color: "#999",
          marginTop: 8,
        }}
      >
        <Text size={200}>Drop file here or paste screenshot (Ctrl+V)</Text>
      </div>
    </div>
  );
}
