import { describe, expect, it } from "vitest";

import { selectSupportedMimeType } from "../components/PracticeRecorder";
import { elapsedSessionSeconds, formatDuration } from "../lib/practice";
import type { PracticeSession } from "../models/practice";

const session: PracticeSession = {
  id: "session-1", pieceId: "piece-1", status: "active", practiceSource: "musician_choice",
  startedAt: "2026-07-12T12:00:00.000Z", endedAt: null, elapsedSeconds: 0,
  currentSegment: null, segments: [],
};

describe("practice workspace utilities", () => {
  it("derives active elapsed time from the backend start time", () => {
    expect(elapsedSessionSeconds(session, Date.parse("2026-07-12T12:03:04.900Z"))).toBe(184);
    expect(formatDuration(184)).toBe("3:04");
  });

  it("uses the finalized backend duration for completed sessions", () => {
    expect(elapsedSessionSeconds({ ...session, status: "completed", elapsedSeconds: 75 }, Date.now())).toBe(75);
  });

  it("selects the first browser-supported recording MIME type", () => {
    expect(selectSupportedMimeType((type) => type === "audio/mp4")).toBe("audio/mp4");
    expect(selectSupportedMimeType(() => false)).toBeUndefined();
  });
});
