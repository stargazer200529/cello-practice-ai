"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { deletePiece, listPieces } from "../lib/pieces";
import type { Piece } from "../models/piece";

export function MusicLibrary() {
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => { void listPieces().then((items) => { setPieces(items); setState("ready"); }).catch(() => setState("error")); }, []);

  async function remove(piece: Piece) {
    if (!window.confirm(`Delete ${piece.title ?? piece.originalFilename}? This cannot be undone.`)) return;
    try { await deletePiece(piece.id); setPieces((items) => items.filter((item) => item.id !== piece.id)); }
    catch { setState("error"); }
  }

  if (state === "loading") return <p aria-live="polite">Loading My Music…</p>;
  if (state === "error") return <p className="error-message" role="alert">My Music could not be loaded. Check the backend and try again.</p>;
  if (!pieces.length) return <section className="placeholder"><h2>Your library is empty</h2><p>Add a MusicXML score to begin.</p><Link className="primary-link" href="/pieces/new">Add a piece</Link></section>;
  return <div className="library-grid">{pieces.map((piece) => <article className="library-card" key={piece.id}>
    <h2><Link href={`/pieces/${piece.id}`}>{piece.title ?? "Untitled piece"}</Link></h2>
    <p>{piece.composer ?? "Composer not present"}</p><p>{piece.originalFilename}</p><p>{piece.measureCount} measures</p>
    <div className="recording-actions"><Link className="primary-link" href={`/pieces/${piece.id}`}>Open workspace</Link>
      <button className="secondary-button" type="button" onClick={() => void remove(piece)}>Delete</button></div>
  </article>)}</div>;
}
