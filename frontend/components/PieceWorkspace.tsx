"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { getPiece, getPieceMusicXML } from "../lib/pieces";
import { ScoreViewer } from "./ScoreViewer";
import { PracticeRecorder } from "./PracticeRecorder";
import { usePieceWorkspace } from "./PieceProvider";

const TABS = ["Practice", "Score", "Recordings", "Analysis", "Progress"] as const;
type Tab = (typeof TABS)[number];
function Values({ values }: { values: string[] }) { return values.length ? values.join(", ") : "Not present"; }

export function PieceWorkspace() {
  const params = useParams<{ id: string }>();
  const { activePiece, setActivePiece, setPracticeRecording } = usePieceWorkspace();
  const [piece, setPiece] = useState(activePiece?.id === params.id ? activePiece : null);
  const [xml, setXml] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Score");
  const [error, setError] = useState<string | null>(null);
  const retainedRecording = useRef(activePiece?.id === params.id ? activePiece.practiceRecording : null);

  useEffect(() => {
    let current = true;
    void Promise.all([getPiece(params.id), getPieceMusicXML(params.id)]).then(([loaded, content]) => {
      if (!current) return;
      const hydrated = { ...loaded, practiceRecording: retainedRecording.current };
      setActivePiece(hydrated); setPiece(hydrated); setXml(content);
    }).catch(() => current && setError("This Piece could not be loaded."));
    return () => { current = false; };
  }, [params.id, setActivePiece]);

  const displayed = activePiece?.id === params.id ? activePiece : piece;
  if (error) return <main><section className="hero"><h1>Piece unavailable</h1><p className="error-message">{error}</p><Link href="/">Return to My Music</Link></section></main>;
  if (!displayed || !xml) return <main><section className="hero"><p>Loading Piece…</p></section></main>;

  return <main className="workspace-main"><section className="workspace"><header className="workspace-header"><div>
    <p className="eyebrow">Piece workspace</p><h1>{displayed.title ?? "Untitled piece"}</h1><p className="summary">{displayed.composer ?? "Composer not present"}</p></div><Link href="/">My Music</Link></header>
    <nav className="workspace-tabs" aria-label="Piece workspace">{TABS.map((item) => <button key={item} type="button" aria-current={tab === item ? "page" : undefined} className={tab === item ? "tab-active" : "tab"} onClick={() => setTab(item)}>{item}</button>)}</nav>
    {tab === "Practice" ? <PracticeRecorder pieceId={displayed.id} recording={displayed.practiceRecording} onRecordingChange={setPracticeRecording} />
    : tab === "Score" ? <div><section className="metadata-card"><h2>Score metadata</h2><dl>
      <div><dt>Original file</dt><dd>{displayed.originalFilename}</dd></div><div><dt>Parts</dt><dd><Values values={displayed.partNames} /></dd></div>
      <div><dt>Measures</dt><dd>{displayed.measureCount}</dd></div><div><dt>Time signatures</dt><dd><Values values={displayed.timeSignatures} /></dd></div>
      <div><dt>Key signatures</dt><dd><Values values={displayed.keySignatures} /></dd></div></dl></section><ScoreViewer musicXML={xml} /></div>
    : <section className="placeholder"><h2>{tab}</h2><p>Not implemented yet.</p></section>}
  </section></main>;
}
