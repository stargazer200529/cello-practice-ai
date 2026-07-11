"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { ScoreViewer } from "../components/ScoreViewer";

type ConnectionState = "checking" | "connected" | "unavailable";
type UploadState = "idle" | "uploading" | "success" | "error";

type ScoreMetadata = {
  title: string | null;
  composer: string | null;
  part_names: string[];
  measure_count: number;
  time_signatures: string[];
  key_signatures: string[];
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getBackendState(): Promise<ConnectionState> {
  try {
    const response = await fetch(`${apiUrl}/health`, { cache: "no-store" });
    if (!response.ok) return "unavailable";
    const body: unknown = await response.json();
    return typeof body === "object" &&
      body !== null &&
      "status" in body &&
      body.status === "ok"
      ? "connected"
      : "unavailable";
  } catch {
    return "unavailable";
  }
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
    ) {
      return body.detail;
    }
  } catch {
    // Use the stable fallback below when an error response is not JSON.
  }
  return "The score could not be processed. Please try again.";
}

function MetadataList({ values }: { values: string[] }) {
  return values.length ? <span>{values.join(", ")}</span> : <span>Not present</span>;
}

export default function Home() {
  const [connectionState, setConnectionState] = useState<ConnectionState>("checking");
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [metadata, setMetadata] = useState<ScoreMetadata | null>(null);
  const [scoreXML, setScoreXML] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const checkBackend = useCallback(async () => {
    setConnectionState("checking");
    setConnectionState(await getBackendState());
  }, []);

  useEffect(() => {
    let isCurrent = true;
    void getBackendState().then((state) => {
      if (isCurrent) setConnectionState(state);
    });
    return () => {
      isCurrent = false;
    };
  }, []);

  async function uploadScore(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setUploadState("error");
      setUploadError("Choose a MusicXML file before uploading.");
      return;
    }

    setUploadState("uploading");
    setUploadError(null);
    setMetadata(null);
    setScoreXML(null);
    const data = new FormData();
    data.append("file", file);

    try {
      const response = await fetch(`${apiUrl}/scores/metadata`, {
        method: "POST",
        body: data,
      });
      if (!response.ok) throw new Error(await errorMessage(response));
      setMetadata((await response.json()) as ScoreMetadata);
      setScoreXML(await file.text());
      setUploadState("success");
    } catch (error) {
      setUploadState("error");
      setUploadError(
        error instanceof Error
          ? error.message
          : "The score could not be processed. Please try again.",
      );
    }
  }

  return (
    <main>
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Version 0.1 foundation</p>
        <h1 id="page-title">Cello Practice AI</h1>
        <p className="summary">
          Upload a MusicXML score to inspect its basic metadata. Files are
          processed for this request and are not permanently stored.
        </p>

        <div className="status-card" aria-live="polite">
          <div>
            <p className="status-label">Backend connection</p>
            <p className={`status status-${connectionState}`}>
              {connectionState === "checking" && "Checking…"}
              {connectionState === "connected" && "Connected"}
              {connectionState === "unavailable" && "Unavailable"}
            </p>
          </div>
          <button type="button" onClick={() => void checkBackend()}>
            Check again
          </button>
        </div>

        <form className="upload-card" onSubmit={(event) => void uploadScore(event)}>
          <div>
            <label htmlFor="score-file">MusicXML score</label>
            <p className="field-help">Choose a .musicxml or .xml file, up to 5 MB.</p>
          </div>
          <input
            id="score-file"
            type="file"
            accept=".musicxml,.xml,application/vnd.recordare.musicxml+xml,application/xml,text/xml"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setUploadState("idle");
              setUploadError(null);
              setMetadata(null);
              setScoreXML(null);
            }}
          />
          <button type="submit" disabled={uploadState === "uploading"}>
            {uploadState === "uploading" ? "Processing…" : "Upload score"}
          </button>
        </form>

        <div aria-live="polite">
          {uploadError && <p className="error-message" role="alert">{uploadError}</p>}
          {metadata && (
            <section className="metadata-card" aria-labelledby="metadata-title">
              <h2 id="metadata-title">Score metadata</h2>
              <dl>
                <div><dt>Title</dt><dd>{metadata.title ?? "Not present"}</dd></div>
                <div><dt>Composer</dt><dd>{metadata.composer ?? "Not present"}</dd></div>
                <div><dt>Parts</dt><dd><MetadataList values={metadata.part_names} /></dd></div>
                <div><dt>Measures</dt><dd>{metadata.measure_count}</dd></div>
                <div><dt>Time signatures</dt><dd><MetadataList values={metadata.time_signatures} /></dd></div>
                <div><dt>Key signatures</dt><dd><MetadataList values={metadata.key_signatures} /></dd></div>
              </dl>
            </section>
          )}
          {scoreXML && <ScoreViewer musicXML={scoreXML} />}
        </div>
      </section>
    </main>
  );
}
