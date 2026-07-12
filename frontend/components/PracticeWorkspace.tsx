"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { getPiece } from "../lib/pieces";
import {
  completePracticeSession,
  elapsedSessionSeconds,
  formatDuration,
  getPracticeSession,
  listPracticeRecordings,
  practiceRecordingAudioUrl,
  removePracticeRecording,
} from "../lib/practice";
import type { Piece } from "../models/piece";
import type { PracticeRecording, PracticeSession } from "../models/practice";
import { PracticeRecorder } from "./PracticeRecorder";

export function PracticeWorkspace() {
  const params = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<PracticeSession | null>(null);
  const [piece, setPiece] = useState<Piece | null>(null);
  const [recordings, setRecordings] = useState<PracticeRecording[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const [recorderBusy, setRecorderBusy] = useState(false);
  const [state, setState] = useState<"loading" | "ready" | "ending" | "error">("loading");
  const [message, setMessage] = useState<string | null>(null);

  const loadRecordings = useCallback(async () => {
    const items = await listPracticeRecordings(params.sessionId);
    setRecordings(items);
  }, [params.sessionId]);

  useEffect(() => {
    let current = true;
    void getPracticeSession(params.sessionId).then(async (loadedSession) => {
      const [loadedPiece, loadedRecordings] = await Promise.all([
        getPiece(loadedSession.pieceId), listPracticeRecordings(loadedSession.id),
      ]);
      if (!current) return;
      setSession(loadedSession); setPiece(loadedPiece); setRecordings(loadedRecordings);
      setElapsed(elapsedSessionSeconds(loadedSession, Date.now())); setState("ready");
    }).catch((error) => {
      if (!current) return;
      setState("error"); setMessage(error instanceof Error ? error.message : "Practice could not be loaded.");
    });
    return () => { current = false; };
  }, [params.sessionId]);

  useEffect(() => {
    if (!session || session.status !== "active") return;
    const timer = setInterval(() => setElapsed(elapsedSessionSeconds(session, Date.now())), 1000);
    return () => clearInterval(timer);
  }, [session]);

  async function endPractice() {
    if (!session || state === "ending") return;
    setState("ending"); setMessage(null);
    try {
      const completed = await completePracticeSession(session.id);
      setSession(completed); setElapsed(completed.elapsedSeconds); setState("ready");
    } catch (error) {
      setState("ready"); setMessage(error instanceof Error ? error.message : "Practice could not be ended.");
    }
  }

  async function removeRecording(recording: PracticeRecording) {
    if (!window.confirm(`Remove ${recording.label}?`)) return;
    try { await removePracticeRecording(recording.id); await loadRecordings(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "The recording could not be removed."); }
  }

  if (state === "loading") return <main className="workspace-main"><section className="workspace practice-shell"><p>Loading practice sessionâ€¦</p></section></main>;
  if (state === "error" || !session || !piece) return <main><section className="hero"><h1>Practice unavailable</h1>
    <p className="error-message" role="alert">{message ?? "This practice session could not be loaded."}</p>
    <Link href="/">Return to My Music</Link></section></main>;

  const active = session.status === "active";
  return <main className="workspace-main"><section className="workspace practice-shell">
    <header className="practice-header"><div><p className="eyebrow">{active ? "Practice session" : "Practice complete"}</p>
      <h1>{piece.title ?? "Untitled piece"}</h1><p className="summary">{piece.composer ?? "Composer not present"}</p></div>
      <div className="session-time" aria-live="off"><span>Session time</span><strong>{formatDuration(elapsed)}</strong></div></header>
    <section className="practice-context"><div><span className="status-label">Current passage</span>
      <strong>{session.currentSegment?.passageId ?? "Entire piece"}</strong></div>
      <div><span className="status-label">Focus</span><strong>{session.currentSegment?.focusCodes.join(", ") || "Open practice"}</strong></div></section>
    {message && <p className="error-message" role="alert">{message}</p>}
    {active && session.currentSegment ? <PracticeRecorder sessionId={session.id} segmentId={session.currentSegment.id}
      onBusyChange={setRecorderBusy}
      onSaved={(saved) => setRecordings((items) => [...items, saved].sort((a, b) => a.recordingNumber - b.recordingNumber))} /> :
      <section className="placeholder"><h2>Session ended</h2><p>Your saved recordings remain available below.</p></section>}
    <section className="recording-list" aria-labelledby="recordings-title"><div className="section-heading"><div>
      <p className="eyebrow">This session</p><h2 id="recordings-title">Saved recordings</h2></div>
      <span>{recordings.length} {recordings.length === 1 ? "recording" : "recordings"}</span></div>
      {!recordings.length ? <p className="empty-state">Your recordings will appear here.</p> : recordings.map((recording) =>
        <article className="recording-card" key={recording.id}><div><strong>{recording.label}</strong>
          <p>{recording.durationMs === null ? "Duration unavailable" : formatDuration(recording.durationMs / 1000)}</p></div>
          <audio controls preload="metadata" src={practiceRecordingAudioUrl(recording.id)}>Your browser does not support audio playback.</audio>
          {active && <button type="button" className="secondary-button remove-recording"
            onClick={() => void removeRecording(recording)}>Remove recording</button>}</article>)}</section>
    <footer className="practice-footer">{active ? <button type="button" className="end-practice-button"
      disabled={state === "ending" || recorderBusy} onClick={() => void endPractice()}>
        {state === "ending" ? "Ending practiceâ€¦" : recorderBusy ? "Finish recording first" : "End Practice"}</button> :
      <Link className="primary-link" href={`/pieces/${piece.id}`}>Return to piece</Link>}</footer>
  </section></main>;
}
