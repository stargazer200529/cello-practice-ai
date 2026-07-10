# Architecture

## 1. Status and goals

This is the preferred architecture for a score-aware cello performance analysis
application. It is a design proposal; no application components or analysis
results are implemented yet.

The architecture should:

- support MusicXML upload and score-aware data structures;
- record directly through a device microphone, then save and replay audio;
- keep the user interface separate from audio processing and musical scoring;
- support asynchronous, versioned analysis without fabricated fallback results;
- preserve traceability from observations to score notes and measures; and
- allow pitch, alignment, rhythm, and dynamics capabilities to evolve
  independently.

## 2. Preferred technology stack

- **Frontend:** React with Next.js and browser media APIs.
- **Backend:** Python with FastAPI.
- **Storage:** a relational database for metadata plus private object storage for
  MusicXML and recordings.
- **Background work:** a job queue and Python analysis workers when analysis is
  introduced.

Specific libraries, infrastructure providers, and deployment targets remain
implementation decisions.

## 3. Layered design

### 3.1 UI layer

The React/Next.js frontend is responsible for:

- MusicXML selection and upload status;
- basic score information and later score-linked highlights;
- microphone permission and recording controls;
- local recording-state feedback;
- saved recording playback;
- analysis progress, limitations, results, and measure recommendations; and
- accessible interaction and error recovery.

It must not invent analysis values when the backend returns pending, uncertain,
unsupported, or failed states.

### 3.2 Application/API layer

The FastAPI backend is responsible for:

- authentication and resource authorization;
- score and recording lifecycle APIs;
- MusicXML validation and orchestration;
- issuing narrowly scoped upload and playback access;
- persisting recording-to-score relationships;
- creating analysis jobs and exposing state transitions; and
- coordinating export, retention, and deletion.

This layer should not contain UI presentation logic or tightly couple API routes
to a particular signal-processing implementation.

### 3.3 Audio-processing layer

The audio-processing layer is responsible for:

- decoding the browser-recorded supported audio format;
- validating duration, sample properties, clipping, and signal quality;
- channel handling, resampling, and normalization where appropriate;
- deriving time-based audio representations;
- pitch tracking and note-event segmentation; and
- later timing and loudness-envelope feature extraction.

Processing must retain enough metadata to reproduce a result and must report
unsupported or low-quality input rather than manufacturing measurements.

### 3.4 Music-analysis and scoring layer

The music-analysis/scoring layer is responsible for:

- representing MusicXML notes, rests, measures, tempo, meter, and dynamics;
- converting pitch tracks into note and cents observations;
- handling sustained notes and estimating vibrato center;
- aligning performed events with notated events;
- classifying supported note, intonation, rhythm, and contour deviations;
- aggregating observations by measure and across comparable recordings;
- identifying repeated mistakes and recommending measures to isolate; and
- generating explainable basic scoring only when evidence is sufficient.

Musical rules and thresholds belong here rather than in UI components or API
controllers.

## 4. Supporting components

- **MusicXML parser:** validates and converts supported notation into an
  internal score representation.
- **Relational database:** stores users, score metadata, recordings, analysis
  jobs, results, and method versions.
- **Private object storage:** stores original MusicXML and recorded media.
- **Job queue:** decouples API requests from longer analysis work.
- **Analysis workers:** execute versioned pipelines outside request/response
  processing.
- **Operational telemetry:** reports service health while excluding raw audio
  and complete score content from routine logs.

A modular monolith for the Next.js and FastAPI product surfaces plus a separate
Python worker is an appropriate initial deployment shape. Logical layers should
remain separate even if they share a repository or deployment unit initially.

## 5. Conceptual data model

- **User:** identity and privacy preferences.
- **Score:** ownership, original MusicXML reference, parsed version, and status.
- **ScorePart:** instrument/part metadata and selection state.
- **Measure:** stable number or identifier, meter, key, tempo context, and
  location.
- **NotatedEvent:** pitch, onset, duration, voice, ties, and notation metadata.
- **Recording:** owner, score, passage, media reference, format, duration, and
  capture metadata.
- **AnalysisJob:** pipeline type, state, input versions, timestamps, and error
  category.
- **PerformedEvent:** estimated onset, duration, pitch, and quality fields.
- **Alignment:** relationship between performed and notated events with
  confidence.
- **Observation:** typed deviation with units, evidence, score location, and
  method version.
- **MeasureRecommendation:** measure, supporting observations, recurrence data,
  and explanation.

## 6. Primary data flows

### 6.1 Upload MusicXML

1. The UI sends the selected MusicXML file to the FastAPI backend.
2. The backend validates size and type, stores the original privately, and
   invokes the supported parser.
3. Parsed score entities are stored with parser-version metadata.
4. The API returns basic score information or an explicit unsupported/failed
   state.

### 6.2 Record, save, and replay

1. The student initiates recording and grants microphone permission.
2. The browser records in a supported format; no manual WAV upload is required.
3. The UI uploads the captured media with score and passage identifiers.
4. The backend validates and privately stores the recording.
5. The UI receives a confirmed saved state and authorized playback access.
6. The student replays or deletes the recording.

The application must not report “saved” before persistence is confirmed.

### 6.3 Analyze against the score

1. The backend creates a versioned analysis job for a recording and parsed
   score.
2. The audio-processing layer validates and extracts supported features.
3. The music-analysis layer creates performed events and aligns them to score
   events.
4. Supported observations are stored with quality and confidence information.
5. The API exposes completed, partial/uncertain, unsupported, or failed output.
6. The UI links observations to notes and measures without filling missing data.

### 6.4 Detect repeated mistakes

1. Eligible observations are grouped across recordings of the same score
   passage and compatible analysis version.
2. A documented recurrence rule identifies consistent patterns.
3. Measures are ranked using evidence quality and recurrence, not a fabricated
   value.
4. Recommendations retain links to the supporting recordings and observations.

## 7. Analysis pipeline evolution

- **Version 0.1:** no performance analysis; score, recording, save, and replay
  foundations only.
- **Version 0.2:** pitch tracking, note conversion, cents, sustained-note logic,
  and vibrato-center estimation.
- **Version 0.3:** score alignment, note/intonation observations, measure
  highlighting, and basic scoring.
- **Version 0.4:** rhythm and timing features with expressive-timing tolerance.
- **Version 0.5:** loudness contour, dynamics, and phrase-shape observations.

Each pipeline result should include input identifiers, score parser version,
analysis version, reference tuning, units, quality indicators, and timestamps.

## 8. Security and privacy

- Enforce ownership checks for every score, recording, and result.
- Keep stored media and MusicXML private; use short-lived access for transfer and
  playback.
- Protect data in transit and at rest using platform-appropriate controls.
- Exclude raw audio, full score content, tokens, and result payloads from routine
  logs.
- Validate file type and size and isolate media parsing from public request
  handling.
- Document retention, export, deletion, and backup expiration before release.
- Do not train models on user data without separate informed consent.

## 9. Quality and validation

- Unit tests for score parsing, conversions, musical rules, and state machines.
- Integration tests for upload, authorization, storage, playback, and deletion.
- Contract tests between UI, FastAPI, audio processing, and scoring layers.
- End-to-end tests for MusicXML upload and record/save/replay.
- Curated evaluation passages and ground truth for each analysis stage.
- Device and microphone coverage for supported recording environments.
- Explicit false-positive, false-negative, and insufficient-signal behavior.

The first analysis milestone must be validated before it is claimed: a cellist
records a simple passage and the application correctly identifies notes that are
consistently sharp or flat.

## 10. Decisions still required

- Supported MusicXML versions and notation subset.
- Browser-recorded media format and transcoding policy.
- Score rendering and passage-selection approach.
- Pitch-detection and alignment algorithms.
- Reference tuning and temperament defaults.
- Recurrence thresholds for repeated mistakes.
- Storage retention and regional hosting requirements.
- Evaluation datasets and acceptance thresholds for each version.
