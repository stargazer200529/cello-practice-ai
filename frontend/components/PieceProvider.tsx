"use client";

import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import type { Piece, PracticeRecording } from "../models/piece";

type PieceContextValue = {
  activePiece: Piece | null;
  setActivePiece: (piece: Piece) => void;
  setPracticeRecording: (recording: PracticeRecording | null) => void;
};

const PieceContext = createContext<PieceContextValue | null>(null);

export function PieceProvider({ children }: { children: ReactNode }) {
  const [activePiece, setActivePiece] = useState<Piece | null>(null);
  const pieceRef = useRef<Piece | null>(null);

  const replaceActivePiece = useCallback((piece: Piece) => {
    const oldUrl = pieceRef.current?.practiceRecording?.objectUrl;
    if (oldUrl && oldUrl !== piece.practiceRecording?.objectUrl) URL.revokeObjectURL(oldUrl);
    pieceRef.current = piece;
    setActivePiece(piece);
  }, []);

  const setPracticeRecording = useCallback((recording: PracticeRecording | null) => {
    setActivePiece((piece) => {
      if (!piece) return piece;
      const oldUrl = piece.practiceRecording?.objectUrl;
      if (oldUrl && oldUrl !== recording?.objectUrl) URL.revokeObjectURL(oldUrl);
      const updated = { ...piece, practiceRecording: recording };
      pieceRef.current = updated;
      return updated;
    });
  }, []);

  useEffect(() => () => {
    const url = pieceRef.current?.practiceRecording?.objectUrl;
    if (url) URL.revokeObjectURL(url);
  }, []);

  const value = useMemo(() => ({ activePiece, setActivePiece: replaceActivePiece, setPracticeRecording }),
    [activePiece, replaceActivePiece, setPracticeRecording]);
  return <PieceContext.Provider value={value}>{children}</PieceContext.Provider>;
}

export function usePieceWorkspace() {
  const context = useContext(PieceContext);
  if (!context) throw new Error("usePieceWorkspace must be used inside PieceProvider");
  return context;
}
