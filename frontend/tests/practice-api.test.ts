import { afterEach, describe, expect, it, vi } from "vitest";

import {
  createPracticeRecording,
  createPracticeSession,
  listPracticeRecordings,
  uploadPracticeRecording,
} from "../lib/practice";

const segment = {
  id: "segment-1", passage_id: null, focus_codes: [], sequence_number: 0,
  started_at: "2026-07-12T12:00:00Z", ended_at: null, target_tempo_bpm: null, notes: null,
};
const session = {
  id: "session-1", piece_id: "piece-1", status: "active" as const, practice_source: "musician_choice" as const,
  started_at: "2026-07-12T12:00:00Z", ended_at: null, elapsed_seconds: 0,
  current_segment: segment, segments: [segment],
};
const recording = {
  id: "recording-1", practice_session_id: "session-1", practice_segment_id: "segment-1",
  passage_id: null, recording_number: 1, label: "Recording 1", status: "saved" as const,
  started_at: "2026-07-12T12:01:00Z", ended_at: "2026-07-12T12:01:03Z", duration_ms: 3000,
  original_mime_type: "audio/webm", microphone_label: null,
};

afterEach(() => vi.unstubAllGlobals());

describe("practice API integration", () => {
  it("creates a session for the selected piece", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(session), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    const created = await createPracticeSession("piece-1");
    expect(created.currentSegment?.id).toBe("segment-1");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ piece_id: "piece-1" });
  });

  it("creates metadata before uploading captured audio", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...recording, status: "capturing", ended_at: null, duration_ms: null }), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(recording), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const created = await createPracticeRecording("session-1", "segment-1", recording.started_at);
    const saved = await uploadPracticeRecording(created.id, new Blob(["audio"], { type: "audio/webm" }), recording.ended_at, 3000);
    expect(created.recordingNumber).toBe(1);
    expect(saved.status).toBe("saved");
    expect(fetchMock.mock.calls[1][1].body).toBeInstanceOf(FormData);
  });

  it("maps the persisted recording list in backend order", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify([recording]), { status: 200 })));
    await expect(listPracticeRecordings("session-1")).resolves.toMatchObject([{ label: "Recording 1", durationMs: 3000 }]);
  });
});
