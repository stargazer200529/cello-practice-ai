// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PracticeRecorder } from "../components/PracticeRecorder";
import { PracticeWorkspace } from "../components/PracticeWorkspace";
import { StartPracticeButton } from "../components/StartPracticeButton";

const mocks = vi.hoisted(() => ({
  push: vi.fn(), createPracticeSession: vi.fn(), getPracticeSession: vi.fn(),
  completePracticeSession: vi.fn(), listPracticeRecordings: vi.fn(), createPracticeRecording: vi.fn(),
  uploadPracticeRecording: vi.fn(), removePracticeRecording: vi.fn(), getPiece: vi.fn(),
}));
const { push, createPracticeSession, getPracticeSession, completePracticeSession, listPracticeRecordings,
  createPracticeRecording, uploadPracticeRecording, getPiece } = mocks;

vi.mock("next/navigation", () => ({
  useParams: () => ({ sessionId: "session-1" }),
  useRouter: () => ({ push: mocks.push }),
}));

vi.mock("../lib/pieces", () => ({ getPiece: mocks.getPiece }));
vi.mock("../lib/practice", () => ({
  createPracticeSession: mocks.createPracticeSession,
  getPracticeSession: mocks.getPracticeSession,
  completePracticeSession: mocks.completePracticeSession,
  listPracticeRecordings: mocks.listPracticeRecordings,
  createPracticeRecording: mocks.createPracticeRecording,
  uploadPracticeRecording: mocks.uploadPracticeRecording,
  removePracticeRecording: mocks.removePracticeRecording,
  practiceRecordingAudioUrl: (id: string) => `http://api.test/api/v1/recordings/${id}/audio`,
  formatDuration: (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`,
  elapsedSessionSeconds: (session: typeof activeSession) => session.status === "active" ? 10 : session.elapsedSeconds,
}));

const segment = {
  id: "segment-1", passageId: null, focusCodes: [], sequenceNumber: 0,
  startedAt: "2026-07-12T12:00:00Z", endedAt: null, targetTempoBpm: null, notes: null,
};
const activeSession = {
  id: "session-1", pieceId: "piece-1", status: "active" as const, practiceSource: "musician_choice" as const,
  startedAt: "2026-07-12T12:00:00Z", endedAt: null, elapsedSeconds: 0,
  currentSegment: segment, segments: [segment],
};
const completedSession = {
  ...activeSession, status: "completed" as const, endedAt: "2026-07-12T12:05:00Z",
  elapsedSeconds: 300, currentSegment: null,
};
const savedRecording = {
  id: "recording-1", practiceSessionId: "session-1", practiceSegmentId: "segment-1",
  passageId: null, recordingNumber: 1, label: "Recording 1", status: "saved" as const,
  startedAt: "2026-07-12T12:01:00Z", endedAt: "2026-07-12T12:01:03Z", durationMs: 3000,
  originalMimeType: "audio/webm", microphoneLabel: null,
};
const piece = {
  id: "piece-1", title: "Cello Study", composer: "Ada Example", partNames: ["Cello"], measureCount: 8,
  timeSignatures: ["4/4"], keySignatures: ["C major"], originalFilename: "study.musicxml",
  createdAt: "2026-07-12T11:00:00Z", updatedAt: "2026-07-12T11:00:00Z",
};

class FakeMediaRecorder {
  static isTypeSupported = () => true;
  state: RecordingState = "inactive";
  mimeType = "audio/webm";
  private listeners = new Map<string, Array<(event: { data: Blob }) => void>>();
  constructor() {}
  addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
    const callback = listener as unknown as (event: { data: Blob }) => void;
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), callback]);
  }
  start() { this.state = "recording"; }
  stop() {
    this.state = "inactive";
    this.listeners.get("dataavailable")?.forEach((listener) => listener({ data: new Blob(["audio"], { type: this.mimeType }) }));
    this.listeners.get("stop")?.forEach((listener) => listener({ data: new Blob() }));
  }
}

function installMicrophone(getUserMedia: ReturnType<typeof vi.fn> = vi.fn().mockResolvedValue({
  getTracks: () => [{ stop: vi.fn() }],
})) {
  Object.defineProperty(navigator, "mediaDevices", { configurable: true, value: { getUserMedia } });
  vi.stubGlobal("MediaRecorder", FakeMediaRecorder);
  Object.defineProperty(URL, "createObjectURL", { configurable: true, value: vi.fn(() => "blob:local") });
  Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });
}

beforeEach(() => {
  vi.clearAllMocks();
  createPracticeSession.mockResolvedValue(activeSession);
  getPracticeSession.mockResolvedValue(activeSession);
  completePracticeSession.mockResolvedValue(completedSession);
  listPracticeRecordings.mockResolvedValue([savedRecording]);
  getPiece.mockResolvedValue(piece);
  createPracticeRecording.mockResolvedValue({ ...savedRecording, status: "capturing" });
  uploadPracticeRecording.mockResolvedValue(savedRecording);
  installMicrophone();
});

afterEach(() => {
  cleanup(); vi.unstubAllGlobals();
});

describe("persistent Practice Workspace UI", () => {
  it("starts a session and navigates to its practice route", async () => {
    render(<StartPracticeButton pieceId="piece-1" />);
    fireEvent.click(screen.getByRole("button", { name: "Start Practice" }));
    await waitFor(() => expect(createPracticeSession).toHaveBeenCalledWith("piece-1"));
    expect(push).toHaveBeenCalledWith("/practice/session-1");
  });

  it("loads an existing session and its recordings", async () => {
    render(<PracticeWorkspace />);
    expect(await screen.findByRole("heading", { name: "Cello Study" })).toBeTruthy();
    expect(screen.getByText("Recording 1")).toBeTruthy();
    expect(getPracticeSession).toHaveBeenCalledWith("session-1");
    expect(listPracticeRecordings).toHaveBeenCalledWith("session-1");
  });

  it("shows a visible microphone permission denial", async () => {
    installMicrophone(vi.fn().mockRejectedValue(new DOMException("Denied", "NotAllowedError")));
    render(<PracticeRecorder sessionId="session-1" segmentId="segment-1" onSaved={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Record" }));
    expect(await screen.findByText(/Microphone permission was denied/)).toBeTruthy();
  });

  it("retains failed audio, retries the existing row, and keeps End Practice disabled while busy", async () => {
    listPracticeRecordings.mockResolvedValueOnce([]);
    let rejectUpload: (reason?: unknown) => void = () => {};
    uploadPracticeRecording.mockImplementationOnce(() => new Promise((_resolve, reject) => { rejectUpload = reject; }));
    render(<PracticeWorkspace />);
    await screen.findByRole("heading", { name: "Cello Study" });
    const endPractice = screen.getByRole("button", { name: "End Practice" });
    fireEvent.click(screen.getByRole("button", { name: "Record" }));
    await waitFor(() => expect((endPractice as HTMLButtonElement).disabled).toBe(true));
    fireEvent.click(screen.getByRole("button", { name: "Stop" }));
    await waitFor(() => expect(uploadPracticeRecording).toHaveBeenCalledTimes(1));
    expect((endPractice as HTMLButtonElement).disabled).toBe(true);
    rejectUpload(new Error("Upload failed"));
    expect(await screen.findByRole("button", { name: "Retry save" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Discard local recording" })).toBeTruthy();
    expect((endPractice as HTMLButtonElement).disabled).toBe(true);

    uploadPracticeRecording.mockResolvedValueOnce(savedRecording);
    fireEvent.click(screen.getByRole("button", { name: "Retry save" }));
    await waitFor(() => expect(uploadPracticeRecording).toHaveBeenCalledTimes(2));
    expect(createPracticeRecording).toHaveBeenCalledTimes(1);
    expect(uploadPracticeRecording.mock.calls[1][0]).toBe("recording-1");
    await waitFor(() => expect((endPractice as HTMLButtonElement).disabled).toBe(false));
  });

  it("completes the session and renders completed state", async () => {
    render(<PracticeWorkspace />);
    await screen.findByRole("heading", { name: "Cello Study" });
    fireEvent.click(screen.getByRole("button", { name: "End Practice" }));
    await waitFor(() => expect(completePracticeSession).toHaveBeenCalledWith("session-1"));
    expect(await screen.findByText("Practice complete")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Session ended" })).toBeTruthy();
  });
});
