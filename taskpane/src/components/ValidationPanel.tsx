import React, { useCallback } from "react";
import { Button, Text, Divider } from "@fluentui/react-components";
import { useAppStore, ValidationStatus } from "../store/appStore";
import { createValidation } from "../api/client";
import { getActiveCellAddress, applyValidationStyle } from "../hooks/useExcel";

export function ValidationPanel() {
  const { clips, updateClipValidation, document } = useAppStore();

  const setStatus = useCallback(async (status: ValidationStatus) => {
    try {
      const cellAddr = await getActiveCellAddress();
      // Find clip mapped to this cell
      const clip = clips.find(
        (c) => c.excel_cell === cellAddr || (c.excel_cell || "").includes(cellAddr)
      );
      if (clip) {
        await createValidation(clip.id, status);
        await applyValidationStyle(cellAddr, status);
        updateClipValidation(clip.id, status);
      } else {
        // Just apply color even if no clip mapped yet
        await applyValidationStyle(cellAddr, status);
      }
    } catch (err) {
      console.error("Validation failed:", err);
    }
  }, [clips, updateClipValidation]);

  if (!document) return null;

  return (
    <div style={{ padding: "8px 12px" }}>
      <Divider style={{ marginBottom: 8 }} />
      <Text weight="semibold" size={300} block style={{ marginBottom: 6 }}>
        Validate Active Cell
      </Text>
      <div style={{ display: "flex", gap: 6 }}>
        <Button
          size="small"
          appearance="primary"
          style={{ background: "#107C10" }}
          onClick={() => setStatus("validated")}
        >
          ✓ Validate
        </Button>
        <Button
          size="small"
          appearance="primary"
          style={{ background: "#D13438" }}
          onClick={() => setStatus("exception")}
        >
          ✗ Exception
        </Button>
        <Button size="small" appearance="outline" onClick={() => setStatus("pending")}>
          Reset
        </Button>
      </div>
    </div>
  );
}
