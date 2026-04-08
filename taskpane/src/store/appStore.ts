import { create } from "zustand";

export type ClipType = "text" | "table" | "calc" | "page" | "document";
export type ValidationStatus = "pending" | "validated" | "exception";

export interface DocumentInfo {
  id: string;
  filename: string;
  doc_type: string;
  page_count: number;
  file_path?: string;
}

export interface ClipRecord {
  id: string;
  clip_type: string;
  page_number: number;
  extracted_value: string;
  excel_cell?: string;
  excel_range?: string;
  confidence: number;
  validation_status: ValidationStatus;
  validation_id?: string;
  needs_review?: boolean;
}

interface FormFields {
  [key: string]: string;
}

interface AppState {
  // Document
  document: DocumentInfo | null;
  setDocument: (doc: DocumentInfo | null) => void;

  // Session
  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  // Page navigation
  currentPage: number;
  setCurrentPage: (n: number) => void;

  // Active clip tool
  activeClipType: ClipType;
  setActiveClipType: (t: ClipType) => void;

  // Clips
  clips: ClipRecord[];
  addClip: (clip: ClipRecord) => void;
  updateClipValidation: (clipId: string, status: ValidationStatus) => void;

  // Form fields
  formFields: FormFields;
  setFormFields: (fields: FormFields) => void;

  // Summary
  summary: string;
  setSummary: (s: string) => void;

  // Loading state
  isLoading: boolean;
  setIsLoading: (b: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  document: null,
  setDocument: (doc) => set({ document: doc }),

  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),

  currentPage: 1,
  setCurrentPage: (n) => set({ currentPage: n }),

  activeClipType: "text",
  setActiveClipType: (t) => set({ activeClipType: t }),

  clips: [],
  addClip: (clip) => set((s) => ({ clips: [...s.clips, clip] })),
  updateClipValidation: (clipId, status) =>
    set((s) => ({
      clips: s.clips.map((c) =>
        c.id === clipId ? { ...c, validation_status: status } : c
      ),
    })),

  formFields: {},
  setFormFields: (fields) => set({ formFields: fields }),

  summary: "",
  setSummary: (s) => set({ summary: s }),

  isLoading: false,
  setIsLoading: (b) => set({ isLoading: b }),
}));
