"use client";

import { useCallback, useEffect, useState } from "react";

type ConnectionState = "checking" | "connected" | "unavailable";
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getBackendState(): Promise<ConnectionState> {
  try {
    const response = await fetch(`${apiUrl}/health`, { cache: "no-store" });
    if (!response.ok) return "unavailable";
    const body: unknown = await response.json();
    return typeof body === "object" && body !== null && "status" in body && body.status === "ok"
      ? "connected"
      : "unavailable";
  } catch {
    return "unavailable";
  }
}

export function BackendStatus() {
  const [state, setState] = useState<ConnectionState>("checking");
  const check = useCallback(async () => {
    setState("checking");
    setState(await getBackendState());
  }, []);

  useEffect(() => {
    let current = true;
    void getBackendState().then((result) => current && setState(result));
    return () => { current = false; };
  }, []);

  return (
    <div className="status-card" aria-live="polite">
      <div><p className="status-label">Backend connection</p>
        <p className={`status status-${state}`}>
          {state === "checking" ? "Checking…" : state === "connected" ? "Connected" : "Unavailable"}
        </p></div>
      <button type="button" onClick={() => void check()}>Check again</button>
    </div>
  );
}
