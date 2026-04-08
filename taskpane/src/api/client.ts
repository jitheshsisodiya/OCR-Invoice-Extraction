import axios from "axios";

const BASE_URL = "http://127.0.0.1:7432/api/v1";

const api = axios.create({ baseURL: BASE_URL, timeout: 60000 });

export default api;

// Documents
export const uploadDocument = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form);
};

export const uploadClipboard = (dataB64: string, suffix = ".png") =>
  api.post("/documents/from-clipboard", { data_b64: dataB64, suffix });

export const uploadEmail = (dataB64: string, filename: string) =>
  api.post("/documents/from-email", { data_b64: dataB64, filename });

export const getDocument = (id: string) => api.get(`/documents/${id}`);
export const getPage = (docId: string, pageNum: number) =>
  api.get(`/documents/${docId}/pages/${pageNum}`);
export const getThumbnailUrl = (docId: string, pageNum: number) =>
  `${BASE_URL}/documents/${docId}/pages/${pageNum}/thumbnail`;

// Sessions
export const createSession = (name: string, documentId: string, excelSheet = "Sheet1") =>
  api.post("/sessions", { name, document_id: documentId, excel_sheet: excelSheet });

// Clips
export const createTextClip = (payload: {
  session_id: string; document_id: string; file_path: string;
  page_number: number; bbox: Record<string, number>; excel_cell: string;
}) => api.post("/clips/text", payload);

export const createTableClip = (payload: {
  session_id: string; document_id: string; file_path: string;
  page_number: number; bbox: Record<string, number>; excel_range: string;
}) => api.post("/clips/table", payload);

export const createCalcClip = (payload: {
  session_id: string; clip_ids: string[]; excel_cell: string;
}) => api.post("/clips/calc", payload);

// Extractions
export const extractPage = (sessionId: string, filePath: string, pageNumber: number) =>
  api.post("/extractions/page", { session_id: sessionId, file_path: filePath, page_number: pageNumber });

export const extractDocument = (sessionId: string, filePath: string, pageRange: [number, number]) =>
  api.post("/extractions/document", { session_id: sessionId, file_path: filePath, page_range: pageRange });

// Validations
export const createValidation = (clipMappingId: string, status: string, note?: string) =>
  api.post("/validations", { clip_mapping_id: clipMappingId, status, note });

export const updateValidation = (validationId: string, status: string, note?: string) =>
  api.patch(`/validations/${validationId}`, { status, note });

// Form extraction + summarize
export const extractFormFields = (documentId: string, pageNumber?: number) =>
  api.post("/form-extraction", { document_id: documentId, page_number: pageNumber });

export const summarizeDocument = (documentId: string) =>
  api.post("/summarize", { document_id: documentId });

// Export
export const exportExcel = (sessionId: string) =>
  api.post("/export/excel", { session_id: sessionId }, { responseType: "blob" });
