/**
 * Hook to manage clip selection state (drawing bounding boxes on document).
 */
import { useState, useCallback } from "react";

export interface Bbox {
  x1: number; y1: number; x2: number; y2: number;
}

export function useClip() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const [currentBbox, setCurrentBbox] = useState<Bbox | null>(null);
  const [confirmedBbox, setConfirmedBbox] = useState<Bbox | null>(null);

  const onMouseDown = useCallback((x: number, y: number) => {
    setIsDrawing(true);
    setStartPoint({ x, y });
    setCurrentBbox(null);
  }, []);

  const onMouseMove = useCallback((x: number, y: number) => {
    if (!isDrawing || !startPoint) return;
    setCurrentBbox({
      x1: Math.min(startPoint.x, x),
      y1: Math.min(startPoint.y, y),
      x2: Math.max(startPoint.x, x),
      y2: Math.max(startPoint.y, y),
    });
  }, [isDrawing, startPoint]);

  const onMouseUp = useCallback((x: number, y: number) => {
    if (!isDrawing || !startPoint) return;
    setIsDrawing(false);
    const bbox: Bbox = {
      x1: Math.min(startPoint.x, x),
      y1: Math.min(startPoint.y, y),
      x2: Math.max(startPoint.x, x),
      y2: Math.max(startPoint.y, y),
    };
    setCurrentBbox(bbox);
    setConfirmedBbox(bbox);
    setStartPoint(null);
  }, [isDrawing, startPoint]);

  const reset = useCallback(() => {
    setIsDrawing(false);
    setStartPoint(null);
    setCurrentBbox(null);
    setConfirmedBbox(null);
  }, []);

  return { isDrawing, currentBbox, confirmedBbox, onMouseDown, onMouseMove, onMouseUp, reset };
}
