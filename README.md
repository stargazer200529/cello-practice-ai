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

## Status

Documentation and design only. Planned features are not represented as complete
or validated.
