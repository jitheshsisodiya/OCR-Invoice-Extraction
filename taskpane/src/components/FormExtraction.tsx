import React, { useCallback } from "react";
import { Button, Text, Spinner, Divider } from "@fluentui/react-components";
import { useAppStore } from "../store/appStore";
import { extractFormFields } from "../api/client";

export function FormExtractionPanel() {
  const { document, formFields, setFormFields, isLoading, setIsLoading } = useAppStore();

  const handleExtract = useCallback(async () => {
    if (!document) return;
    setIsLoading(true);
    try {
      const res = await extractFormFields(document.id);
      setFormFields(res.data.fields || {});
    } catch (err) {
      console.error("Form extraction failed:", err);
    } finally {
      setIsLoading(false);
    }
  }, [document, setFormFields, setIsLoading]);

  if (!document) return null;

  const hasFields = Object.keys(formFields).length > 0;

  return (
    <div style={{ padding: "8px 12px" }}>
      <Divider style={{ marginBottom: 8 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <Text weight="semibold" size={300}>Form Fields</Text>
        <Button size="small" onClick={handleExtract} disabled={isLoading}>
          {isLoading ? <Spinner size="tiny" /> : "Extract"}
        </Button>
      </div>
      {hasFields && (
        <table style={{ width: "100%", fontSize: 11, borderCollapse: "collapse" }}>
          <tbody>
            {Object.entries(formFields).map(([key, value]) => (
              <tr key={key} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "2px 4px", fontWeight: 600, color: "#555", width: "40%" }}>
                  {key.replace(/_/g, " ")}
                </td>
                <td style={{ padding: "2px 4px" }}>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {!hasFields && !isLoading && (
        <Text size={200} style={{ color: "#999" }}>Click Extract to identify invoice fields.</Text>
      )}
    </div>
  );
}
