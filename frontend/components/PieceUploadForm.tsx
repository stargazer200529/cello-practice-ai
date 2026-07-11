"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createPiece } from "../lib/pieces";
import { usePieceWorkspace } from "./PieceProvider";

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
    try {
      const piece = await createPiece(file);
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
        <p className="field-help">Choose a .musicxml or .xml file, up to 5 MB.</p></div>
      <input id="score-file" type="file"
        accept=".musicxml,.xml,application/vnd.recordare.musicxml+xml,application/xml,text/xml"
        onChange={(event) => { setFile(event.target.files?.[0] ?? null); setState("idle"); setError(null); }} />
      <button type="submit" disabled={state === "uploading"}>
        {state === "uploading" ? "Creating piece…" : "Create piece workspace"}
      </button>
      {error && <p className="error-message" role="alert">{error}</p>}
    </form>
  );
}
