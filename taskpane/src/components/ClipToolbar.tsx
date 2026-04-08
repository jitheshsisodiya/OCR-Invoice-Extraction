import React from "react";
import { Button, Tooltip, Divider, Text } from "@fluentui/react-components";
import { useAppStore, ClipType } from "../store/appStore";

const CLIP_BUTTONS: { type: ClipType; label: string; tooltip: string }[] = [
  { type: "text",     label: "Text",     tooltip: "Draw selection to extract text into active cell" },
  { type: "table",    label: "Table",    tooltip: "Draw selection to extract a table" },
  { type: "calc",     label: "Calc",     tooltip: "Sum selected text clips into a formula" },
  { type: "page",     label: "Page",     tooltip: "Extract entire current page" },
  { type: "document", label: "Document", tooltip: "Extract up to 5 pages from this document" },
];

export function ClipToolbar() {
  const { activeClipType, setActiveClipType, document } = useAppStore();

  if (!document) return null;

  return (
    <div style={{ padding: "8px 12px" }}>
      <Text weight="semibold" size={300} block style={{ marginBottom: 6 }}>
        Clip Type
      </Text>
      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
        {CLIP_BUTTONS.map(({ type, label, tooltip }) => (
          <Tooltip key={type} content={tooltip} relationship="label">
            <Button
              size="small"
              appearance={activeClipType === type ? "primary" : "outline"}
              onClick={() => setActiveClipType(type)}
            >
              {label}
            </Button>
          </Tooltip>
        ))}
      </div>
      <Divider style={{ marginTop: 8 }} />
    </div>
  );
}
