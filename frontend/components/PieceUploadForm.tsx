"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createTemporaryPiece, ScoreMetadataResponse } from "../models/piece";
import { usePieceWorkspace } from "./PieceProvider";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function errorMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string") {
      return body.detail;
    }
  } catch {}
  return "The score could not be processed. Please try again.";
}

export function PieceUploadForm() {
  const router = useRouter();
  const { setActivePiece } = usePieceWorkspace();
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<"idle" | "uploading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setState("error"); setError("Choose a MusicXML file before uploading."); return;
    }
    setState("uploading"); setError(null);
    const data = new FormData(); data.append("file", file);
    try {
      const response = await fetch(`${apiUrl}/scores/metadata`, { method: "POST", body: data });
      if (!response.ok) throw new Error(await errorMessage(response));
      const metadata = (await response.json()) as ScoreMetadataResponse;
      const piece = createTemporaryPiece(metadata, file.name, metadata.musicxml);
      setActivePiece(piece);
      router.push(`/pieces/${piece.id}`);
    } catch (uploadError) {
      setState("error");
      setError(uploadError instanceof Error ? uploadError.message : "The score could not be processed. Please try again.");
    }
  }

  return (
    <form className="upload-card" onSubmit={(event) => void submit(event)}>
      <div><label htmlFor="score-file">MusicXML score</label>
        <p className="field-help">Choose a .musicxml, .xml, or compressed .mxl file, up to 5 MB.</p></div>
      <input id="score-file" type="file"
        accept=".musicxml,.xml,.mxl,application/vnd.recordare.musicxml+xml,application/vnd.recordare.musicxml,application/xml,text/xml"
        onChange={(event) => { setFile(event.target.files?.[0] ?? null); setState("idle"); setError(null); }} />
      <button type="submit" disabled={state === "uploading"}>
        {state === "uploading" ? "Creating piece…" : "Create piece workspace"}
      </button>
      {error && <p className="error-message" role="alert">{error}</p>}
    </form>
  );
}
