import { apiUrl, checked } from "./api";
import {
  PracticeRecording,
  PracticeRecordingResponse,
  PracticeSession,
  PracticeSessionResponse,
  recordingFromResponse,
  sessionFromResponse,
} from "../models/practice";

export async function createPracticeSession(pieceId: string): Promise<PracticeSession> {
  const response = await checked(await fetch(`${apiUrl}/api/v1/practice-sessions`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ piece_id: pieceId }),
  }));
  return sessionFromResponse((await response.json()) as PracticeSessionResponse);
}

export async function getPracticeSession(sessionId: string): Promise<PracticeSession> {
  const response = await checked(await fetch(`${apiUrl}/api/v1/practice-sessions/${sessionId}`, { cache: "no-store" }));
  return sessionFromResponse((await response.json()) as PracticeSessionResponse);
}

export async function completePracticeSession(sessionId: string): Promise<PracticeSession> {
  const response = await checked(await fetch(`${apiUrl}/api/v1/practice-sessions/${sessionId}/complete`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: "{}",
  }));
  return sessionFromResponse((await response.json()) as PracticeSessionResponse);
}

export async function createPracticeRecording(
  sessionId: string, segmentId: string, startedAt: string,
): Promise<PracticeRecording> {
  const response = await checked(await fetch(`${apiUrl}/api/v1/practice-sessions/${sessionId}/recordings`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ practice_segment_id: segmentId, started_at: startedAt }),
  }));
  return recordingFromResponse((await response.json()) as PracticeRecordingResponse);
}

export async function uploadPracticeRecording(
  recordingId: string, blob: Blob, endedAt: string, durationMs: number,
): Promise<PracticeRecording> {
  const data = new FormData();
  data.append("file", blob, `capture.${blob.type.includes("mp4") ? "m4a" : blob.type.includes("ogg") ? "ogg" : "webm"}`);
  data.append("ended_at", endedAt); data.append("duration_ms", String(durationMs));
  if (blob.type) data.append("original_mime_type", blob.type);
  const response = await checked(await fetch(`${apiUrl}/api/v1/recordings/${recordingId}/audio`, { method: "POST", body: data }));
  return recordingFromResponse((await response.json()) as PracticeRecordingResponse);
}

export async function listPracticeRecordings(sessionId: string): Promise<PracticeRecording[]> {
  const response = await checked(await fetch(`${apiUrl}/api/v1/practice-sessions/${sessionId}/recordings`, { cache: "no-store" }));
  return ((await response.json()) as PracticeRecordingResponse[]).map(recordingFromResponse);
}

export async function removePracticeRecording(recordingId: string): Promise<void> {
  await checked(await fetch(`${apiUrl}/api/v1/recordings/${recordingId}/remove`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason: "user_requested_removal" }),
  }));
}

export function practiceRecordingAudioUrl(recordingId: string): string {
  return `${apiUrl}/api/v1/recordings/${recordingId}/audio`;
}

export function formatDuration(totalSeconds: number): string {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

export function elapsedSessionSeconds(session: PracticeSession, now: number): number {
  if (session.status !== "active") return session.elapsedSeconds;
  return Math.max(0, Math.floor((now - Date.parse(session.startedAt)) / 1000));
}
