"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { ScoreViewer } from "./ScoreViewer";
import { PracticeRecorder } from "./PracticeRecorder";
import { usePieceWorkspace } from "./PieceProvider";

const TABS = ["Practice", "Score", "Recordings", "Analysis", "Progress"] as const;
type Tab = (typeof TABS)[number];

function Values({ values }: { values: string[] }) {
  return values.length ? values.join(", ") : "Not present";
}

export function PieceWorkspace() {
  const params = useParams<{ id: string }>();
  const { activePiece, setPracticeRecording } = usePieceWorkspace();
  const [tab, setTab] = useState<Tab>("Score");
  const piece = activePiece?.id === params.id ? activePiece : null;

  if (!piece) return (
    <main><section className="hero"><p className="eyebrow">Temporary workspace</p>
      <h1>Piece unavailable</h1>
      <p className="summary">This temporary piece is no longer available. Refreshing or restarting clears it because persistence is not implemented yet.</p>
      <Link className="primary-link" href="/pieces/new">Upload a MusicXML score</Link>
    </section></main>
  );

  return (
    <main className="workspace-main"><section className="workspace">
      <header className="workspace-header"><div><p className="eyebrow">Piece workspace</p>
        <h1>{piece.title ?? "Untitled piece"}</h1><p className="summary">{piece.composer ?? "Composer not present"}</p></div>
        <Link href="/pieces/new">Create another temporary piece</Link></header>
      <nav className="workspace-tabs" aria-label="Piece workspace">
        {TABS.map((item) => <button key={item} type="button" aria-current={tab === item ? "page" : undefined}
          className={tab === item ? "tab-active" : "tab"} onClick={() => setTab(item)}>{item}</button>)}
      </nav>
      {tab === "Practice" ? <PracticeRecorder pieceId={piece.id} recording={piece.practiceRecording}
        onRecordingChange={setPracticeRecording} />
      : tab === "Score" ? <div><section className="metadata-card" aria-labelledby="metadata-title">
        <h2 id="metadata-title">Score metadata</h2><dl>
          <div><dt>Original file</dt><dd>{piece.originalFilename}</dd></div>
          <div><dt>Parts</dt><dd><Values values={piece.partNames} /></dd></div>
          <div><dt>Measures</dt><dd>{piece.measureCount}</dd></div>
          <div><dt>Time signatures</dt><dd><Values values={piece.timeSignatures} /></dd></div>
          <div><dt>Key signatures</dt><dd><Values values={piece.keySignatures} /></dd></div>
        </dl></section><ScoreViewer musicXML={piece.musicXML} /></div>
      : <section className="placeholder" aria-live="polite"><h2>{tab}</h2><p>Not implemented yet.</p></section>}
    </section></main>
  );
}
