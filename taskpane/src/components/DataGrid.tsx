import React from "react";
import { Text, Badge } from "@fluentui/react-components";
import { useAppStore } from "../store/appStore";

const CONFIDENCE_COLOR = (c: number) => c >= 0.8 ? "success" : c >= 0.5 ? "warning" : "danger";

export function DataGrid() {
  const { clips } = useAppStore();

  if (!clips.length) {
    return (
      <div style={{ padding: "8px 12px", color: "#999" }}>
        <Text size={200}>No clips yet. Draw a selection on the document to extract data.</Text>
      </div>
    );
  }

  return (
    <div style={{ padding: "0 12px", overflowX: "auto" }}>
      <Text weight="semibold" size={300} block style={{ marginBottom: 6 }}>Extracted Data</Text>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
        <thead>
          <tr style={{ background: "#f3f3f3" }}>
            <th style={th}>Type</th>
            <th style={th}>Value</th>
            <th style={th}>Cell</th>
            <th style={th}>Conf.</th>
            <th style={th}>Status</th>
          </tr>
        </thead>
        <tbody>
          {clips.map((clip) => {
            let displayValue = clip.extracted_value;
            try {
              const parsed = JSON.parse(clip.extracted_value);
              if (Array.isArray(parsed)) displayValue = `[Table ${parsed.length}×${parsed[0]?.length ?? 0}]`;
              else displayValue = String(parsed);
            } catch {}

            return (
              <tr key={clip.id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={td}>{clip.clip_type}</td>
                <td style={{ ...td, maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{displayValue}</td>
                <td style={td}>{clip.excel_cell || clip.excel_range || "—"}</td>
                <td style={td}>
                  <Badge color={CONFIDENCE_COLOR(clip.confidence)} size="small">
                    {Math.round(clip.confidence * 100)}%
                  </Badge>
                </td>
                <td style={td}>
                  <StatusBadge status={clip.validation_status} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const th: React.CSSProperties = { textAlign: "left", padding: "4px 6px", fontWeight: 600, fontSize: 11 };
const td: React.CSSProperties = { padding: "3px 6px", fontSize: 11 };

function StatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, "success" | "danger" | "warning"> = {
    validated: "success",
    exception: "danger",
    pending: "warning",
  };
  return <Badge color={colorMap[status] ?? "warning"} size="small">{status}</Badge>;
}
