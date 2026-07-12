"use client";

import { useEffect, useRef, useState } from "react";

import {
  createPracticeRecording,
  removePracticeRecording,
  uploadPracticeRecording,
} from "../lib/practice";
import type { PracticeRecording } from "../models/practice";

type RecorderState =
  | "idle" | "requesting" | "recording" | "stopping" | "saving"
  | "upload_failed" | "denied" | "unavailable" | "error";

const MIME_CANDIDATES = [
  "audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus", "audio/ogg",
];

export function selectSupportedMimeType(isSupported: (type: string) => boolean): string | undefined {
  return MIME_CANDIDATES.find(isSupported);
}

type PendingCapture = {
  blob: Blob;
  durationMs: number;
  endedAt: string;
  objectUrl: string;
  recordingId?: string;
};

type PracticeRecorderProps = {
  sessionId: string;
  segmentId: string;
  disabled?: boolean;
  onSaved: (recording: PracticeRecording) => void;
  onBusyChange?: (busy: boolean) => void;
};

export function PracticeRecorder({
  sessionId, segmentId, disabled = false, onSaved, onBusyChange,
}: PracticeRecorderProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startedAtRef = useRef(0);
  const startedAtIsoRef = useRef("");
  const pendingUrlRef = useRef<string | null>(null);
  const mountedRef = useRef(true);
  const [state, setState] = useState<RecorderState>("idle");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [pending, setPending] = useState<PendingCapture | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  function clearTimer() {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
  }

  function releaseStream() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  function clearPending() {
    if (pendingUrlRef.current) URL.revokeObjectURL(pendingUrlRef.current);
    pendingUrlRef.current = null; setPending(null);
  }

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false; clearTimer();
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") { try { recorder.stop(); } catch {} }
      recorderRef.current = null; releaseStream();
      if (pendingUrlRef.current) URL.revokeObjectURL(pendingUrlRef.current);
    };
  }, []);

  useEffect(() => {
    const busy = ["requesting", "recording", "stopping", "saving", "upload_failed"].includes(state);
    onBusyChange?.(busy);
    return () => onBusyChange?.(false);
  }, [onBusyChange, state]);

  async function persistCapture(capture: PendingCapture) {
    setState("saving"); setMessage(null);
    let current = capture;
    try {
      if (!current.recordingId) {
        const created = await createPracticeRecording(sessionId, segmentId, startedAtIsoRef.current);
        current = { ...current, recordingId: created.id };
        if (mountedRef.current) setPending(current);
      }
      const recordingId = current.recordingId;
      if (!recordingId) throw new Error("The recording could not be created.");
      const saved = await uploadPracticeRecording(recordingId, current.blob, current.endedAt, current.durationMs);
      if (!mountedRef.current) return;
      clearPending(); setElapsedMs(0); setState("idle"); onSaved(saved);
    } catch (error) {
      if (!mountedRef.current) return;
      setPending(current); setState("upload_failed");
      setMessage(error instanceof Error ? error.message : "The recording could not be saved.");
    }
  }

  async function startRecording() {
    if (disabled || ["requesting", "recording", "stopping", "saving", "upload_failed"].includes(state)) return;
    setMessage(null);
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setState("unavailable"); setMessage("This browser does not support direct microphone recording."); return;
    }
    setState("requesting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: { ideal: 1 } } });
      if (!mountedRef.current) { stream.getTracks().forEach((track) => track.stop()); return; }
      streamRef.current = stream;
      const mimeType = selectSupportedMimeType((type) => MediaRecorder.isTypeSupported(type));
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      const chunks: BlobPart[] = [];
      recorderRef.current = recorder;
      recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
      recorder.addEventListener("error", () => {
        clearTimer(); releaseStream();
        if (mountedRef.current) { setState("error"); setMessage("Recording failed. Please try again."); }
      });
      recorder.addEventListener("stop", () => {
        clearTimer(); releaseStream(); recorderRef.current = null;
        if (!mountedRef.current) return;
        const durationMs = Date.now() - startedAtRef.current;
        const blob = new Blob(chunks, { type: recorder.mimeType || mimeType || "audio/webm" });
        if (!blob.size) { setState("error"); setMessage("No audio was captured. Please try again."); return; }
        const objectUrl = URL.createObjectURL(blob);
        pendingUrlRef.current = objectUrl;
        const capture = { blob, durationMs, endedAt: new Date().toISOString(), objectUrl };
        setPending(capture); void persistCapture(capture);
      });
      startedAtRef.current = Date.now(); startedAtIsoRef.current = new Date().toISOString();
      recorder.start(250); setState("recording");
      timerRef.current = setInterval(() => setElapsedMs(Date.now() - startedAtRef.current), 250);
    } catch (error) {
      clearTimer(); releaseStream(); recorderRef.current = null;
      if (!mountedRef.current) return;
      if (error instanceof DOMException && error.name === "NotAllowedError") {
        setState("denied"); setMessage("Microphone permission was denied. Allow access in browser settings and try again.");
      } else if (error instanceof DOMException && error.name === "NotFoundError") {
        setState("unavailable"); setMessage("No microphone is available on this device.");
      } else { setState("error"); setMessage("The microphone could not start. Please try again."); }
    }
  }

  function stopRecording() {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state !== "recording") return;
    setState("stopping");
    try { recorder.stop(); } catch {
      clearTimer(); releaseStream(); recorderRef.current = null;
      setState("error"); setMessage("The recording could not be stopped cleanly. Please try again.");
    }
  }

  async function discardPending() {
    if (pending?.recordingId) {
      try { await removePracticeRecording(pending.recordingId); } catch {
        setMessage("The unsaved recording could not be discarded. Try again."); return;
      }
    }
    clearPending(); setState("idle"); setMessage(null); setElapsedMs(0);
  }

  const seconds = Math.floor(elapsedMs / 1000);
  return <section className="practice-recorder" aria-labelledby="recording-title">
    <h2 id="recording-title">Recording</h2>
    <p className="field-help">Microphone access is requested only when you press Record. Saved audio remains private.</p>
    <p className="recorder-status" aria-live="polite">
      {state === "idle" && "Ready for your next attempt."}
      {state === "requesting" && "Requesting microphone permission…"}
      {state === "recording" && `Recording ${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`}
      {state === "stopping" && "Finishing recording…"}
      {state === "saving" && "Saving recording…"}
      {state === "upload_failed" && "Recording captured, but not yet saved."}
      {message}
    </p>
    <div className="recording-actions">
      {(state === "idle" || state === "denied" || state === "unavailable" || state === "error") &&
        <button type="button" className="record-button" disabled={disabled} onClick={() => void startRecording()}>Record</button>}
      {state === "recording" && <button type="button" className="stop-button" onClick={stopRecording}>Stop</button>}
      {state === "upload_failed" && pending && <>
        <button type="button" onClick={() => void persistCapture(pending)}>Retry save</button>
        <button type="button" className="secondary-button" onClick={() => void discardPending()}>Discard local recording</button>
      </>}
    </div>
    {state === "upload_failed" && pending && <audio controls src={pending.objectUrl}>Your browser does not support audio playback.</audio>}
  </section>;
}
