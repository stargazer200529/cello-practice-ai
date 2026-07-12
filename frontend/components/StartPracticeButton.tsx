"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createPracticeSession } from "../lib/practice";

export function StartPracticeButton({ pieceId }: { pieceId: string }) {
  const router = useRouter();
  const [state, setState] = useState<"idle" | "starting" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  async function startPractice() {
    if (state === "starting") return;
    setState("starting"); setMessage(null);
    try {
      const session = await createPracticeSession(pieceId);
      router.push(`/practice/${session.id}`);
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : "Practice could not be started.");
    }
  }

  return <div className="start-practice">
    <button type="button" className="practice-primary-button" disabled={state === "starting"}
      onClick={() => void startPractice()}>{state === "starting" ? "Starting practice…" : "Start Practice"}</button>
    {message && <p className="error-message" role="alert">{message}</p>}
  </div>;
}
