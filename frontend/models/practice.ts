export type PracticeSegment = {
  id: string;
  passageId: string | null;
  focusCodes: string[];
  sequenceNumber: number;
  startedAt: string;
  endedAt: string | null;
  targetTempoBpm: number | null;
  notes: string | null;
};

export type PracticeSession = {
  id: string;
  pieceId: string;
  status: "active" | "completed" | "abandoned" | "interrupted";
  practiceSource: "musician_choice" | "teacher_assignment" | "application_recommendation";
  startedAt: string;
  endedAt: string | null;
  elapsedSeconds: number;
  currentSegment: PracticeSegment | null;
  segments: PracticeSegment[];
};

export type PracticeRecording = {
  id: string;
  practiceSessionId: string;
  practiceSegmentId: string;
  passageId: string | null;
  recordingNumber: number;
  label: string;
  status: "capturing" | "saved" | "processing" | "ready" | "invalid" | "removed" | "failed";
  startedAt: string;
  endedAt: string | null;
  durationMs: number | null;
  originalMimeType: string | null;
  microphoneLabel: string | null;
};

export type PracticeSegmentResponse = {
  id: string; passage_id: string | null; focus_codes: string[]; sequence_number: number;
  started_at: string; ended_at: string | null; target_tempo_bpm: number | null; notes: string | null;
};

export type PracticeSessionResponse = {
  id: string; piece_id: string; status: PracticeSession["status"];
  practice_source: PracticeSession["practiceSource"]; started_at: string; ended_at: string | null;
  elapsed_seconds: number; current_segment: PracticeSegmentResponse | null; segments: PracticeSegmentResponse[];
};

export type PracticeRecordingResponse = {
  id: string; practice_session_id: string; practice_segment_id: string; passage_id: string | null;
  recording_number: number; label: string; status: PracticeRecording["status"]; started_at: string;
  ended_at: string | null; duration_ms: number | null; original_mime_type: string | null;
  microphone_label: string | null;
};

export function segmentFromResponse(value: PracticeSegmentResponse): PracticeSegment {
  return { id: value.id, passageId: value.passage_id, focusCodes: value.focus_codes,
    sequenceNumber: value.sequence_number, startedAt: value.started_at, endedAt: value.ended_at,
    targetTempoBpm: value.target_tempo_bpm, notes: value.notes };
}

export function sessionFromResponse(value: PracticeSessionResponse): PracticeSession {
  return { id: value.id, pieceId: value.piece_id, status: value.status, practiceSource: value.practice_source,
    startedAt: value.started_at, endedAt: value.ended_at, elapsedSeconds: value.elapsed_seconds,
    currentSegment: value.current_segment ? segmentFromResponse(value.current_segment) : null,
    segments: value.segments.map(segmentFromResponse) };
}

export function recordingFromResponse(value: PracticeRecordingResponse): PracticeRecording {
  return { id: value.id, practiceSessionId: value.practice_session_id,
    practiceSegmentId: value.practice_segment_id, passageId: value.passage_id,
    recordingNumber: value.recording_number, label: value.label, status: value.status,
    startedAt: value.started_at, endedAt: value.ended_at, durationMs: value.duration_ms,
    originalMimeType: value.original_mime_type, microphoneLabel: value.microphone_label };
}
