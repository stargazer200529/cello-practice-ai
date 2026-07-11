"use client";

import { useCallback, useEffect, useState } from "react";

type ConnectionState = "checking" | "connected" | "unavailable";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getBackendState(): Promise<ConnectionState> {
  try {
    const response = await fetch(`${apiUrl}/health`, { cache: "no-store" });

    if (!response.ok) {
      return "unavailable";
    }

    const body: unknown = await response.json();
    const isHealthy =
      typeof body === "object" &&
      body !== null &&
      "status" in body &&
      body.status === "ok";

    return isHealthy ? "connected" : "unavailable";
  } catch {
    return "unavailable";
  }
}

export default function Home() {
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("checking");

  const checkBackend = useCallback(async () => {
    setConnectionState("checking");
    setConnectionState(await getBackendState());
  }, []);

  useEffect(() => {
    let isCurrent = true;

    void getBackendState().then((state) => {
      if (isCurrent) {
        setConnectionState(state);
      }
    });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main>
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Version 0.1 foundation</p>
        <h1 id="page-title">Cello Practice AI</h1>
        <p className="summary">
          The local application foundation is ready. Score and recording
          features will be implemented in later issues.
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
      </section>
    </main>
  );
}
