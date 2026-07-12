"use client";

import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

import type { Piece } from "../models/piece";

type PieceContextValue = {
  activePiece: Piece | null;
  setActivePiece: (piece: Piece) => void;
};

const PieceContext = createContext<PieceContextValue | null>(null);

export function PieceProvider({ children }: { children: ReactNode }) {
  const [activePiece, setActivePiece] = useState<Piece | null>(null);

  const replaceActivePiece = useCallback((piece: Piece) => {
    setActivePiece(piece);
  }, []);

  const value = useMemo(() => ({ activePiece, setActivePiece: replaceActivePiece }),
    [activePiece, replaceActivePiece]);
  return <PieceContext.Provider value={value}>{children}</PieceContext.Provider>;
}

export function usePieceWorkspace() {
  const context = useContext(PieceContext);
  if (!context) throw new Error("usePieceWorkspace must be used inside PieceProvider");
  return context;
}
