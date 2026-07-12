"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getPiece, getPieceMusicXML } from "../lib/pieces";
import { ScoreViewer } from "./ScoreViewer";
import { StartPracticeButton } from "./StartPracticeButton";
import { usePieceWorkspace } from "./PieceProvider";

const TABS = ["Practice", "Score", "Recordings", "Analysis", "Progress"] as const;
type Tab = (typeof TABS)[number];
function Values({ values }: { values: string[] }) { return values.length ? values.join(", ") : "Not present"; }

export function PieceWorkspace() {
  const params = useParams<{ id: string }>();
  const { activePiece, setActivePiece } = usePieceWorkspace();
  const [piece, setPiece] = useState(activePiece?.id === params.id ? activePiece : null);
  const [xml, setXml] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Score");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let current = true;
    void Promise.all([getPiece(params.id), getPieceMusicXML(params.id)]).then(([loaded, content]) => {
      if (!current) return;
      setActivePiece(loaded); setPiece(loaded); setXml(content);
    }).catch(() => current && setError("This Piece could not be loaded."));
    return () => { current = false; };
  }, [params.id, setActivePiece]);

  const displayed = activePiece?.id === params.id ? activePiece : piece;
  if (error) return <main><section className="hero"><h1>Piece unavailable</h1><p className="error-message">{error}</p><Link href="/">Return to My Music</Link></section></main>;
  if (!displayed || !xml) return <main><section className="hero"><p>Loading Piece…</p></section></main>;

  return <main className="workspace-main"><section className="workspace"><header className="workspace-header"><div>
    <p className="eyebrow">Piece workspace</p><h1>{displayed.title ?? "Untitled piece"}</h1><p className="summary">{displayed.composer ?? "Composer not present"}</p></div>
    <div className="workspace-actions"><StartPracticeButton pieceId={displayed.id} /><Link href="/">My Music</Link></div></header>
    <nav className="workspace-tabs" aria-label="Piece workspace">{TABS.map((item) => <button key={item} type="button" aria-current={tab === item ? "page" : undefined} className={tab === item ? "tab-active" : "tab"} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {tab === "Practice" ? <section className="practice-recorder"><h2>Practice this piece</h2>
      <p className="field-help">Use Start Practice above to begin a persistent session and record multiple attempts.</p></section>
    : tab === "Score" ? <div><section className="metadata-card"><h2>Score metadata</h2><dl>
      <div><dt>Original file</dt><dd>{displayed.originalFilename}</dd></div><div><dt>Parts</dt><dd><Values values={displayed.partNames} /></dd></div>
      <div><dt>Measures</dt><dd>{displayed.measureCount}</dd></div><div><dt>Time signatures</dt><dd><Values values={displayed.timeSignatures} /></dd></div>
      <div><dt>Key signatures</dt><dd><Values values={displayed.keySignatures} /></dd></div></dl></section><ScoreViewer musicXML={xml} /></div>
    : <section className="placeholder"><h2>{tab}</h2><p>Not implemented yet.</p></section>}
  </section></main>;
}
