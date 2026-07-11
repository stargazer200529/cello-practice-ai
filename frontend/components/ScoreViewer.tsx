"use client";

import { useEffect, useRef, useState } from "react";

const ZOOM_LEVELS = [0.75, 1, 1.25, 1.5] as const;

export function ScoreViewer({ musicXML }: { musicXML: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const osmdRef = useRef<import("opensheetmusicdisplay").OpenSheetMusicDisplay | null>(null);
  const [zoom, setZoom] = useState(1);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(true);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let isCurrent = true;
    let resizeTimer: ReturnType<typeof setTimeout> | undefined;
    let observer: ResizeObserver | undefined;

    async function renderScore() {
      setIsRendering(true);
      setRenderError(null);
      try {
        const { OpenSheetMusicDisplay } = await import("opensheetmusicdisplay");
        if (!isCurrent || !containerRef.current) return;
        const osmd = new OpenSheetMusicDisplay(containerRef.current, {
          autoResize: false,
          backend: "svg",
          drawTitle: true,
        });
        osmdRef.current = osmd;
        await osmd.load(musicXML);
        if (!isCurrent) return;
        osmd.Zoom = 1;
        osmd.render();
        observer = new ResizeObserver(() => {
          clearTimeout(resizeTimer);
          resizeTimer = setTimeout(() => {
            if (isCurrent && osmdRef.current) osmdRef.current.render();
          }, 150);
        });
        observer.observe(containerRef.current);
      } catch {
        if (isCurrent) {
          osmdRef.current = null;
          containerRef.current?.replaceChildren();
          setRenderError("The score could not be rendered. Try another MusicXML file.");
        }
      } finally {
        if (isCurrent) setIsRendering(false);
      }
    }
    void renderScore();
    return () => {
      isCurrent = false;
      observer?.disconnect();
      clearTimeout(resizeTimer);
      osmdRef.current = null;
      container.replaceChildren();
    };
  }, [musicXML]);

  useEffect(() => {
    if (!osmdRef.current) return;
    osmdRef.current.Zoom = zoom;
    osmdRef.current.render();
  }, [zoom]);

  return (
    <section className="score-viewer" aria-labelledby="score-viewer-title">
      <div className="score-viewer-header">
        <h2 id="score-viewer-title">Rendered score</h2>
        <fieldset className="zoom-controls">
          <legend>Zoom</legend>
          {ZOOM_LEVELS.map((level) => (
            <button key={level} type="button"
              className={zoom === level ? "zoom-active" : "zoom-button"}
              aria-pressed={zoom === level} onClick={() => setZoom(level)}>
              {Math.round(level * 100)}%
            </button>
          ))}
        </fieldset>
      </div>
      <div aria-live="polite">
        {isRendering && <p className="render-message">Rendering score…</p>}
        {renderError && <p className="error-message" role="alert">{renderError}</p>}
      </div>
      <div ref={containerRef} className="score-canvas" aria-label="Music notation" />
    </section>
  );
}
