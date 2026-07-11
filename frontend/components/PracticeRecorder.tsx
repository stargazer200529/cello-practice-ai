"use client";

import { useEffect, useRef, useState } from "react";

import type { PracticeRecording } from "../models/piece";

type RecorderState = "idle" | "requesting" | "ready" | "recording" | "complete" | "denied" | "unavailable" | "error";

const MIME_CANDIDATES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
  "audio/ogg",
];

function formatDuration(milliseconds: number) {
  const seconds = Math.floor(milliseconds / 1000);
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

function supportedMimeType() {
  return MIME_CANDIDATES.find((type) => MediaRecorder.isTypeSupported(type));
}

type PracticeRecorderProps = {
  pieceId: string;
  recording: PracticeRecording | null;
  onRecordingChange: (recording: PracticeRecording | null) => void;
};

export function PracticeRecorder({ pieceId, recording, onRecordingChange }: PracticeRecorderProps) {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startedAtRef = useRef(0);
  const mountedRef = useRef(true);
  const [state, setState] = useState<RecorderState>(recording ? "complete" : "idle");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [message, setMessage] = useState<string | null>(null);

  function clearTimer() {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
  }

  function releaseStream() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearTimer();
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        try { recorder.stop(); } catch {}
      }
      recorderRef.current = null;
      releaseStream();
    };
  }, []);

  async function startRecording() {
    if (state === "requesting" || state === "recording") return;
    setMessage(null);
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setState("unavailable");
      setMessage("This browser does not support direct microphone recording.");
      return;
    }

    onRecordingChange(null);
    setElapsedMs(0);
    setState("requesting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: { ideal: 1 } } });
      if (!mountedRef.current) { stream.getTracks().forEach((track) => track.stop()); return; }
      streamRef.current = stream;
      setState("ready");
      const mimeType = supportedMimeType();
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
        const blob = new Blob(chunks, { type: recorder.mimeType || mimeType || "" });
        if (!blob.size) { setState("error"); setMessage("No audio was captured. Please try again."); return; }
        const completed: PracticeRecording = {
          id: crypto.randomUUID(), pieceId, createdAt: new Date().toISOString(), durationMs,
          mimeType: blob.type, blob, objectUrl: URL.createObjectURL(blob),
        };
        onRecordingChange(completed); setElapsedMs(durationMs); setState("complete");
      });
      startedAtRef.current = Date.now();
      recorder.start(250);
      setState("recording");
      timerRef.current = setInterval(() => setElapsedMs(Date.now() - startedAtRef.current), 250);
    } catch (error) {
      clearTimer(); releaseStream(); recorderRef.current = null;
      if (!mountedRef.current) return;
      if (error instanceof DOMException && error.name === "NotAllowedError") {
        setState("denied"); setMessage("Microphone permission was denied. Allow access in your browser settings to record.");
      } else if (error instanceof DOMException && error.name === "NotFoundError") {
        setState("unavailable"); setMessage("No microphone is available on this device.");
      } else {
        setState("error"); setMessage("The microphone could not start. Please try again.");
      }
    }
  }

  function stopRecording() {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state !== "recording") return;
    try { recorder.stop(); } catch {
      clearTimer(); releaseStream(); recorderRef.current = null;
      setState("error"); setMessage("The recording could not be stopped cleanly. Please try again.");
    }
  }

  function discard() {
    onRecordingChange(null); setElapsedMs(0); setMessage(null); setState("idle");
  }

  const currentRecording = recording && recording.pieceId === pieceId ? recording : null;
  return (
    <section className="practice-recorder" aria-labelledby="practice-title">
      <h2 id="practice-title">Practice recording</h2>
      <p className="field-help">Record directly from this device. Audio remains only in this temporary Piece workspace.</p>
      <div className="recorder-status" aria-live="polite">
        {state === "requesting" && "Requesting microphone permission…"}
        {state === "ready" && "Microphone ready."}
        {state === "recording" && `Recording ${formatDuration(elapsedMs)}`}
        {state === "complete" && "Recording complete."}
        {state === "idle" && "Microphone not yet requested."}
        {message}
      </div>
      <div className="recording-actions">
        {(state === "idle" || state === "denied" || state === "unavailable" || state === "error") &&
          <button type="button" onClick={() => void startRecording()}>Record</button>}
        {state === "recording" && <button type="button" className="stop-button" onClick={stopRecording}>Stop</button>}
      </div>
      {currentRecording && state === "complete" && <div className="recording-complete">
        <p><strong>Duration:</strong> {formatDuration(currentRecording.durationMs)}</p>
        <audio controls src={currentRecording.objectUrl}>Your browser does not support audio playback.</audio>
        <div className="recording-actions">
          <button type="button" onClick={() => void startRecording()}>Record another attempt</button>
          <button type="button" className="secondary-button" onClick={discard}>Discard recording</button>
        </div>
      </div>}
      <p className="temporary-note">Permanent recording storage is not implemented. Refreshing or restarting clears this audio.</p>
    </section>
  );
}
