# Cello Practice AI

Cello Practice AI is a planned score-aware performance analysis application for
solo cello students. A student uploads a MusicXML score, records a performance
directly through the device microphone, saves and replays the recording, and—in
later versions—receives feedback tied to the notes and measures in the score.

The project is currently in the documentation phase. No application code or
validated analysis results exist yet.

## Product direction

The application is designed to:

- accept MusicXML and present basic score information;
- record through the device microphone without requiring manual WAV upload;
- save and replay recorded performances;
- compare performed audio with the uploaded score;
- analyze pitch, intonation, rhythm, and dynamic contour in later versions;
- identify repeated mistakes across performances; and
- recommend specific measures for the student to isolate in practice.

Analysis must never be fabricated. If audio quality, score alignment, or an
analysis stage is insufficient, the application must show an unavailable,
uncertain, or failed state rather than inventing feedback.

## First successful milestone

A cellist records a simple passage and the application correctly identifies
notes that are consistently sharp or flat.

## Preferred technology direction

- React with Next.js for the frontend
- Python with FastAPI for the backend
- Separate UI, audio-processing, and music-analysis/scoring layers

These choices are the preferred starting architecture and should be confirmed
through implementation discovery.

## Roadmap summary

- **Version 0.1:** MusicXML upload, basic score information, microphone
  recording, saving, and replay.
- **Version 0.2:** Pitch and intonation analysis, including sustained notes and
  vibrato-center estimation.
- **Version 0.3:** Score alignment, incorrect-note and intonation detection,
  measure highlighting, and basic scoring.
- **Version 0.4:** Rhythm and timing analysis with allowance for expressive
  timing.
- **Version 0.5:** Dynamic contour and phrase-shape observations.

## Documentation

- [Product requirements](docs/ProductRequirements.md)
- [Architecture](docs/Architecture.md)
- [Version roadmap](docs/VersionRoadmap.md)

## Local development

The repository contains separate frontend and backend applications. The current
foundation implements a local health check, in-memory MusicXML upload, basic
metadata parsing, browser rendering with OpenSheetMusicDisplay, and temporary
in-browser microphone recording and replay. Pieces and MusicXML files persist
locally through SQLite and configurable backend filesystem storage. It does not
implement manual audio upload, recording persistence, cloud storage,
highlighting, analysis, scoring, authentication, or cloud deployment.

MusicXML upload accepts plain `.musicxml` and `.xml` files plus compressed `.mxl`
containers. MXL container metadata selects the root score document before the
existing parser validates and reads it.

The frontend is organized around a persistent local Piece library:

- `/` lists saved pieces in My Music.
- `/pieces/new` creates a persistent Piece from MusicXML.
- `/pieces/[id]` shows its metadata, score, and future-feature tabs.

Piece metadata and MusicXML survive restarts. Practice recordings remain
temporary while a workspace is open; their object URL
and audio data are released when replaced, discarded, or the app unmounts.

### Prerequisites

- Node.js 20.9 or later and pnpm
- Python 3.11 or later

### Start the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

By default, SQLite and MusicXML files are created under `backend/data/`. Override
them with `CELLO_DATABASE_URL` and `CELLO_MUSICXML_STORAGE_DIR`.

The API runs at `http://localhost:8000`. Its health endpoint is available at
`http://localhost:8000/health`.

### Start the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
pnpm install
pnpm dev
```

Open `http://localhost:3000`. The page checks the backend health endpoint and
reports whether it can connect. To use a different backend URL, copy
`frontend/.env.local.example` to `frontend/.env.local` and edit the value.

For a manual upload test, use
`sample-data/musicxml/twinkle-twinkle-little-star.musicxml`.

### Run checks

```powershell
cd backend
python -m pytest
```

```powershell
cd frontend
pnpm lint
pnpm build
```

## Status

The local frontend/backend foundation is implemented. Product capabilities in
the roadmap remain planned and are not represented as complete or validated.
