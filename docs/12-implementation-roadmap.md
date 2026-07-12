# Implementation Roadmap

## Purpose

This document translates the product, domain, database, analysis, recommendation, and API specifications into an incremental delivery plan for **Practice with Purpose**.

The roadmap prioritizes:

- working prototypes
- real cello validation
- small implementation steps
- technical accuracy
- testable milestones
- minimal rework
- clear separation between user interface, audio processing, and music analysis

The roadmap does not attempt to build the full long-term product at once.

The first successful milestone remains:

> A cellist records a simple passage and the application correctly identifies notes that are consistently sharp or flat.

---

# Current State

The project already includes the following foundation:

## Frontend

- Next.js application
- piece upload workflow
- MusicXML and MXL support
- score rendering with OpenSheetMusicDisplay
- My Music library
- piece workspace
- browser microphone recording
- replay of the current recording

## Backend

- FastAPI application
- SQLite persistence
- SQLAlchemy models
- uploaded score storage
- parsed score metadata
- persistent piece library

## Product Documentation

- Product Vision
- Practice Workflow
- Design Principles
- UI Specification
- Information Architecture
- Experience Mockups
- Domain Model
- Database Design
- Analysis Engine
- Recommendation Engine
- API Specification

## Current Limitations

- recordings are not yet persisted across sessions
- practice sessions are not yet modeled in the product flow
- pitch analysis is not implemented
- analysis results are not stored
- score-to-performance alignment is not implemented
- recommendations are not implemented
- session summaries are not implemented
- authentication is not implemented
- legal documents are drafts or pending

---

# Delivery Strategy

Development should follow this sequence:

```text
Foundation
    ↓
Persist Practice Sessions and Recordings
    ↓
Detect Pitch Reliably
    ↓
Estimate Vibrato-Aware Pitch Center
    ↓
Store Versioned Analysis
    ↓
Compare Performance to Score
    ↓
Generate Measure-Level Observations
    ↓
Create Practice Recommendations
    ↓
Add Rhythm and Dynamic Analysis
    ↓
Prepare for Public Beta
```

Each phase must end with a working, demonstrable product increment.

---

# Roadmap Rules

## Build Only What the Next Milestone Needs

Do not implement all future database tables, APIs, or UI states at once.

## Validate With Real Cello Recordings

Synthetic tones are useful for unit tests, but real cello recordings determine whether the feature is useful.

## Preserve Versioning

Analysis results must record engine and configuration versions from the beginning.

## Avoid Fake Intelligence

Do not display placeholder analysis results as though they are real.

## Keep Feedback Explainable

Every user-facing observation must trace back to measurable evidence.

## Protect the Practice Flow

Analysis should not block the user from recording again.

## Keep the Musician in Control

Recommendations remain optional.

---

# Phase 0 — Documentation Reconciliation

## Goal

Ensure the active project documentation is internally consistent before new implementation work begins.

## Tasks

- standardize all documentation filenames with `.md`
- archive obsolete or conflicting documents
- confirm `03-design-principles.md` contains the music-stand principle
- confirm `04-ui-specification.md` removes numerical mastery
- replace `06-experience-mockups.md` with the revised version
- add legal-document placeholders
- confirm documents 07 through 11 are stored in `docs/`

## Deliverables

```text
docs/
├── 01-product-vision.md
├── 02-practice-workflow.md
├── 03-design-principles.md
├── 04-ui-specification.md
├── 05-information-architecture.md
├── 06-experience-mockups.md
├── 07-domain-model.md
├── 08-database-design.md
├── 09-analysis-engine.md
├── 10-recommendation-engine.md
└── 11-api-specification.md
```

Legal:

```text
docs/legal/
├── 01-terms-of-service.md
├── 02-privacy-policy.md
├── 03-copyright-policy.md
└── 04-dmca-policy.md
```

## Acceptance Criteria

- no contradictory active design documents remain
- every current document has a stable filename
- the repository reflects the current product direction

---

# Phase 1 — Practice Session and Recording Persistence

## Goal

Create the persistent practice-session foundation required for all future analysis.

## Product Outcome

A musician can:

- start a practice session
- record multiple attempts
- stop and replay each recording
- end the session
- reopen the application and still see the saved session and recordings

## Backend Tasks

### Database

Implement:

```text
practice_sessions
passage_definitions
passage_ranges
practice_segments
practice_focuses
practice_segment_focuses
practice_goals
practice_notes
recordings
```

### Storage

Create private recording storage.

Initial structure:

```text
storage/
├── scores/
└── recordings/
    └── {user_id}/
        └── {practice_session_id}/
            └── {recording_id}.{extension}
```

### API

Implement:

```text
POST /api/v1/practice-sessions
GET /api/v1/practice-sessions/{session_id}
POST /api/v1/practice-sessions/{session_id}/segments
POST /api/v1/practice-sessions/{session_id}/recordings
POST /api/v1/recordings/{recording_id}/audio
GET /api/v1/recordings/{recording_id}
GET /api/v1/recordings/{recording_id}/audio
GET /api/v1/practice-sessions/{session_id}/recordings
POST /api/v1/practice-sessions/{session_id}/complete
POST /api/v1/recordings/{recording_id}/remove
```

## Frontend Tasks

Implement the first real Practice Workspace:

- session timer
- current passage
- focus selection
- large Record and Stop controls
- neutral recording labels
- replay
- recording list
- End Practice
- quiet interface while recording

## Testing

- create session
- record three attempts
- replay all three
- refresh browser
- confirm recordings persist
- complete session
- confirm session cannot be resumed as active
- remove one accidental recording
- confirm numbering is not reused

## Acceptance Criteria

- recordings persist after browser refresh
- multiple recordings belong to one session
- each recording preserves passage and segment context
- completing the session closes it permanently
- no analysis is shown yet unless real analysis exists

---

# Phase 2 — Audio Normalization and Validation

## Goal

Create a reliable audio-ingestion pipeline before implementing pitch detection.

## Product Outcome

Every saved recording receives a clear status:

- ready for analysis
- invalid
- insufficient signal
- unsupported format

## Backend Tasks

Implement:

- audio decoding
- format inspection
- mono conversion
- sample-rate normalization
- duration extraction
- clipping detection
- silence detection
- checksum generation
- normalized WAV or PCM analysis copy
- temporary-file cleanup

## Recommended Library Evaluation

Evaluate:

- `soundfile`
- `librosa`
- `scipy`
- `ffmpeg`
- `pydub`

Use the smallest dependable stack.

## Data Model

Add:

```text
analysis_runs
audio validation metadata
recording status transitions
```

## API

Implement:

```text
POST /api/v1/recordings/{recording_id}/analysis-runs
GET /api/v1/analysis-runs/{analysis_run_id}
```

## Testing

Create test recordings for:

- valid cello tone
- silence
- severe clipping
- very low level
- short accidental tap
- unsupported file
- corrupted file

## Acceptance Criteria

- invalid audio does not enter pitch analysis
- validation failures produce clear messages
- one invalid category does not corrupt session data
- recording remains replayable when technically possible
- analysis metadata records engine and configuration versions

---

# Phase 3 — Basic Pitch Detection

## Goal

Detect pitch over time from a solo cello recording.

## Product Outcome

The application can display:

- detected frequency
- nearest note
- cents sharp or flat
- confidence
- pitch trace over time

## Technical Tasks

Evaluate pitch algorithms using real cello recordings.

Candidates may include:

- YIN
- probabilistic YIN
- CREPE
- TorchCrepe
- autocorrelation-based approaches
- instrument-specific hybrid methods

Selection should be evidence-based.

## Implementation Tasks

- frame-level pitch estimation
- voiced/unvoiced classification
- confidence output
- frequency-to-MIDI conversion
- MIDI-to-note naming
- cents calculation
- octave-error mitigation
- cello-range filtering
- pitch-trace diagnostics

## Database

Implement:

```text
pitch_observations
```

For early work, frame-level diagnostics may remain in files or JSON rather than fully normalized tables.

## Frontend

Create a developer-facing analysis panel showing:

- pitch trace
- detected note
- cents deviation
- confidence
- audio-quality warning

This may be hidden behind a development flag.

## Testing

Record:

- open C string
- open G string
- open D string
- open A string
- stopped notes
- deliberately sharp notes
- deliberately flat notes
- low and high cello register

## Acceptance Criteria

- all four open strings are identified reliably
- sharp and flat direction is correct
- octave-error rate is acceptably low
- low-confidence frames are suppressed
- results are stored as a versioned Analysis Run

---

# Phase 4 — Sustained Notes and Vibrato-Aware Pitch Center

## Goal

Estimate the center pitch of sustained cello notes without penalizing normal vibrato.

## Product Outcome

The application can report:

```text
Detected note: A3
Pitch center: 12 cents flat
Vibrato detected
Pitch stability: moderate
Confidence: sufficient
```

## Technical Tasks

Implement:

- note-region segmentation
- attack exclusion
- release exclusion
- stable-region detection
- robust pitch-center estimation
- vibrato-width estimation
- vibrato-rate estimation
- pitch-stability calculation
- outlier rejection
- confidence combination

## Experiment Sequence

### Experiment A

Sustained notes without vibrato.

### Experiment B

Sustained notes with narrow vibrato.

### Experiment C

Sustained notes with wide vibrato.

### Experiment D

Notes with expressive pitch drift.

### Experiment E

Portamento into sustained note.

## Testing

Compare results against:

- reference tuner
- manual pitch measurement
- annotated expected center

## Acceptance Criteria

- normal vibrato does not create repeated sharp/flat errors
- pitch center remains stable across repeated analysis
- attacks and releases do not dominate the result
- short or ambiguous notes return insufficient data
- the user sees pitch-center feedback, not raw oscillation penalties

---

# Phase 5 — Version 0.2 User Experience

## Goal

Integrate real pitch analysis into the Practice Workspace.

## Product Outcome

A musician can record a sustained note or simple passage and receive real intonation feedback.

## Frontend Tasks

Implement:

- analysis processing state
- non-blocking next recording
- latest pitch result
- confidence label
- live or post-recording tuner display
- pitch-center display
- recording-level result details
- clear insufficient-data state

## Backend Tasks

- automatically queue pitch analysis after recording save
- expose pitch observations
- select preferred analysis run
- support retry
- preserve failed runs
- return partial results safely

## API

Finalize:

```text
POST /recordings/{id}/analysis-runs
GET /analysis-runs/{id}
GET /analysis-runs/{id}/pitch-observations
POST /analysis-runs/{id}/retry
POST /analysis-runs/{id}/prefer
```

## Acceptance Criteria

- analysis does not block another recording
- results survive page refresh
- one recording may be reprocessed
- the UI clearly distinguishes:
  - processing
  - reliable result
  - uncertain result
  - failed analysis

## Milestone

This completes Version 0.2.

---

# Phase 6 — Score Note Extraction

## Goal

Create the normalized score representation required for comparison.

## Product Outcome

The backend can provide stable note events for a selected passage.

## Backend Tasks

Implement or refine:

```text
movements
score_measures
score_notes
```

Parse:

- note pitch
- rests
- onset
- duration
- ties
- voice
- staff
- measure order
- key signature
- time signature
- tempo context

## API

Implement:

```text
GET /api/v1/pieces/{piece_id}/score-outline
GET /api/v1/movements/{movement_id}/measures
```

Add internal score-note access for analysis.

## Testing

Use MusicXML files containing:

- tied notes
- rests
- pickup measures
- repeated measure numbers
- multiple voices
- tenor clef
- treble clef
- key changes
- tempo changes

## Acceptance Criteria

- every score note has a stable identifier
- displayed measure number is not treated as the primary key
- tied notes are represented consistently
- parsed note order matches rendered score order
- passage definitions resolve to valid score-note sequences

---

# Phase 7 — Note Segmentation and Score Alignment

## Goal

Match performed note events to written score notes.

## Product Outcome

The application can identify which played note corresponds to which score location.

## Technical Tasks

Implement:

- performed-note segmentation
- sequence representation
- intended-passage restriction
- tempo-scale estimation
- dynamic sequence alignment
- skipped-note handling
- extra-note handling
- ambiguous-alignment detection
- alignment confidence

## Database

Implement:

```text
alignment_events
```

## Testing

Use short passages with:

- correct performance
- one incorrect note
- one missing note
- one extra note
- repeated note
- tied note
- slow tempo
- uneven tempo
- starting one measure late

## Acceptance Criteria

- performed notes align to the correct measure
- incorrect notes are distinguishable from intonation deviations
- missing and extra notes are represented explicitly
- low-confidence alignment suppresses strong feedback
- user-selected passage materially improves alignment reliability

---

# Phase 8 — Measure-Level Intonation Feedback

## Goal

Produce specific intonation observations tied to score location.

## Product Outcome

The application can say:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

## Backend Tasks

Implement:

```text
measure_observations
technical_patterns
```

Add aggregation across:

- notes
- recordings
- session
- score location
- repeated attempts

## Rules

- require sufficient confidence
- separate wrong note from out-of-tune note
- group repeated evidence
- preserve direction and magnitude
- suppress trivial deviations
- avoid unsupported fingering claims

## Frontend Tasks

Implement:

- measure-linked observation display
- recording evidence count
- descriptive language
- expandable details
- Practice Map intonation layer

## Acceptance Criteria

- feedback identifies measure and expected note
- repeated attempts are aggregated
- insufficient evidence is reported honestly
- no global grade is displayed
- observations are traceable to recordings

## Milestone

This completes the core Version 0.3 intonation milestone.

---

# Phase 9 — Practice Map

## Goal

Convert repeated analysis evidence into a visual practice-priority map.

## Product Outcome

The piece view can show:

- Comfortable
- Needs reinforcement
- Recommended focus
- Insufficient data

by measure and category.

## Backend Tasks

Implement:

```text
practice_map_states
practice_map_snapshots
practice_map_snapshot_items
```

## Update Logic

Use:

- recency
- recurrence
- severity
- confidence
- improvement
- unresolved pattern
- selected focus
- teacher relevance later

## Frontend Tasks

- render accessible overlays
- support category filtering
- show text labels and icons in addition to color
- hide updates during active recording
- display map before and after practice

## Acceptance Criteria

- one measure may hold different category states
- one low-confidence event does not create a red state
- state explanation is available
- updates occur only after recording analysis completes
- map labels remain descriptive rather than evaluative

---

# Phase 10 — Recommendation Engine

## Goal

Generate one useful, explainable practice recommendation.

## Product Outcome

The application can recommend:

```text
Measures 24–25

Reason:
The F-sharp after the shift averaged 17 cents flat across three recordings.

Suggested practice:
Slow the passage.
Practice the shift separately without vibrato.
Record three repetitions.
```

## Backend Tasks

Implement:

```text
recommendations
recommendation_evidence
```

Start with transparent rules:

- repeated intonation deviation
- shift destination pattern
- insufficient-data rule
- improvement detected
- reconnect passage after isolated success

## Frontend Tasks

- primary recommendation on Piece Home
- quiet post-recording suggestion
- recommendation details
- accept
- defer
- complete
- dismiss
- start practice from recommendation

## Acceptance Criteria

- recommendation is evidence-based
- recommendation identifies a passage
- recommendation explains why
- recommendation suggests a concrete method
- low-confidence evidence does not create strong guidance
- user can ignore it
- no more than one immediate recommendation appears during practice

---

# Phase 11 — Session Summary

## Goal

End each practice session with clear reflection and a next step.

## Product Outcome

The musician sees:

- duration
- recording count
- passages practiced
- what improved
- what still needs attention
- where to begin next time
- one suggested practice method

## Backend Tasks

Implement:

```text
session_summaries
```

Support summary versioning.

## Frontend Tasks

Implement revised Practice Summary screen.

## Rules

- no fake praise
- no report-card tone
- compare only compatible attempts
- allow partial summary when some analyses are pending
- regenerate when late analysis completes
- preserve prior summary versions

## Acceptance Criteria

- summary is specific
- summary cites measurable improvement
- unresolved issue is explained
- next-session recommendation is actionable
- summary remains useful when analysis is incomplete

---

# Phase 12 — Rhythm and Timing Analysis

## Goal

Add score-relative rhythm feedback.

## Product Outcome

The application can report:

> Measure 12: The second eighth note entered early in three attempts.

## Backend Tasks

Implement:

```text
rhythm_observations
```

Add:

- onset comparison
- duration comparison
- local tempo
- beat-relative deviation
- tempo drift
- repeated rhythm pattern detection

## Frontend Tasks

- rhythm focus tool
- tempo display
- optional metronome
- rhythm observations
- Practice Map rhythm layer

## Acceptance Criteria

- timing is evaluated relative to tempo
- written tempo changes are respected
- expressive timing is not automatically penalized
- repeated rhythm errors are prioritized over isolated events

## Milestone

This completes Version 0.4.

---

# Phase 13 — Dynamic Contour

## Goal

Add relative dynamic-shape analysis.

## Product Outcome

The application can show a measured dynamic contour and describe broad execution.

## Backend Tasks

Implement:

```text
dynamic_observations
```

Add:

- RMS and peak intensity
- smoothed contour
- crescendo slope
- diminuendo slope
- gain-stability detection
- broad score comparison

## Frontend Tasks

- dynamic contour visualization
- written-versus-performed shape comparison
- confidence and device warning
- Practice Map dynamics layer

## Acceptance Criteria

- analysis is relative, not absolute
- automatic gain instability is detected
- the application does not judge artistic interpretation
- user-facing statements remain descriptive

## Milestone

This completes Version 0.5.

---

# Phase 14 — Progress and Long-Term Trends

## Goal

Transform practice history into narrative progress.

## Product Outcome

The application can state:

- rhythm became more consistent across five sessions
- a previously difficult passage now needs less practice
- a repeated intonation tendency remains active
- practice has been consistent for three weeks

## Backend Tasks

- compatible analysis-version comparison
- cross-session aggregation
- recency weighting
- technical-pattern lifecycle
- progress narratives
- retention evidence

## Frontend Tasks

Implement:

- musician progress
- piece progress
- narrative-first summaries
- optional supporting charts
- Practice Map history

## Acceptance Criteria

- no single daily score
- incompatible engine versions are not compared silently
- progress statements are evidence-based
- trend confidence is visible when needed

---

# Phase 15 — Teacher Features

## Goal

Add optional teacher-supported practice.

## Product Outcome

A teacher may assign passages and notes while the student remains free to practice independently.

## Backend Tasks

Implement:

```text
teachers
teacher_relationships
assignments
assignment_focuses
```

Add:

- permission model
- invitation flow
- sharing preferences
- assignment lifecycle
- teacher notes
- access revocation

## Frontend Tasks

- Teacher screen
- assignments on Home
- assignments on Piece Home
- start practice from assignment
- student-controlled sharing

## Acceptance Criteria

- app works fully without a teacher
- teacher access is explicit
- ended relationships revoke future access
- app recommendations do not rewrite teacher guidance
- assignments never block other practice

---

# Phase 16 — Authentication, Privacy, and Public Beta Readiness

## Goal

Prepare the product for real external users.

## Required Work

### Authentication

- account creation
- login
- password or identity-provider security
- session management
- account recovery

### Storage Security

- private score storage
- private audio storage
- protected download endpoints
- non-predictable storage keys
- encrypted production storage

### Privacy

- account deletion
- recording deletion
- score deletion
- data export
- retention rules
- consent tracking

### Copyright

- required upload acknowledgment
- private-by-default score storage
- Terms of Service
- Copyright Policy
- DMCA process
- takedown workflow

### Operations

- backups
- restoration testing
- monitoring
- structured logs
- error reporting
- rate limiting
- upload limits
- abuse prevention

## Acceptance Criteria

- no private file is publicly accessible
- user data is isolated by ownership
- users can delete account data
- legal pages are accessible
- copyright confirmation is recorded
- security review is completed
- attorney review is obtained before public release where practical

---

# Version Milestones

## Version 0.1 — Foundation

Status: substantially implemented.

Includes:

- interface foundation
- MusicXML upload
- MXL upload
- score metadata
- score rendering
- browser recording
- replay
- persistent piece library

Remaining before closing Version 0.1:

- persistent recording storage
- persistent practice session
- basic Practice Workspace refinement

---

## Version 0.2 — Pitch Analysis

Includes:

- recording persistence
- audio validation
- normalized audio
- pitch over time
- note detection
- cents sharp or flat
- sustained-note analysis
- vibrato-aware pitch center
- versioned analysis runs

Success statement:

> The application reliably identifies whether a sustained cello note centers sharp or flat without penalizing normal vibrato.

---

## Version 0.3 — Score Comparison and Intonation Guidance

Includes:

- parsed score notes
- performed-note segmentation
- score alignment
- incorrect-note detection
- measure-level intonation observations
- repeated evidence
- basic Practice Map
- one useful recommendation

Success statement:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

---

## Version 0.4 — Rhythm and Timing

Includes:

- onset comparison
- note-duration comparison
- tempo drift
- repeated rhythm patterns
- expressive-timing tolerance

---

## Version 0.5 — Dynamics

Includes:

- dynamic contour
- crescendo and diminuendo analysis
- dynamic contrast
- phrase-shape visualization
- gain-stability safeguards

---

# GitHub Issue Strategy

Each issue should represent a small, testable unit.

## Good Issue Size

A good issue should generally:

- affect one layer or one vertical slice
- have clear acceptance criteria
- be reviewable in one pull request
- avoid unrelated refactoring
- include tests

## Example Epic Structure

```text
Epic: Version 0.2 Pitch Analysis

├── Create practice session tables
├── Persist recordings
├── Add recording replay endpoint
├── Add audio validation service
├── Normalize audio to mono WAV
├── Add analysis_runs table
├── Evaluate pitch detection libraries
├── Implement frame-level pitch detection
├── Add cents conversion
├── Add sustained-note segmentation
├── Add vibrato-center estimation
├── Store pitch observations
├── Add analysis status UI
└── Display pitch-center result
```

---

# Recommended Immediate Issue Sequence

The next implementation work should be created in this order.

## Issue 1 — Persist Practice Sessions

### Scope

- add `practice_sessions`
- add `practice_segments`
- add initial passage context
- start and complete session APIs
- tests

## Issue 2 — Persist Recordings

### Scope

- add `recordings`
- save browser audio
- recording numbering
- replay endpoint
- persistence tests

## Issue 3 — Practice Workspace Session Integration

### Scope

- start session from Piece Home
- session timer
- recording list
- End Practice
- browser refresh recovery

## Issue 4 — Audio Validation Service

### Scope

- decode
- duration
- silence
- clipping
- format support
- failure statuses

## Issue 5 — Analysis Run Lifecycle

### Scope

- add `analysis_runs`
- queue/status model
- engine version
- configuration version
- failure handling

## Issue 6 — Pitch Detection Prototype

### Scope

- compare at least two candidate algorithms
- test four open cello strings
- record accuracy and octave errors
- select initial approach

## Issue 7 — Frame-Level Pitch Analysis

### Scope

- implement selected algorithm
- note conversion
- cents conversion
- confidence
- diagnostics

## Issue 8 — Vibrato-Aware Pitch Center

### Scope

- stable region
- pitch center
- vibrato detection
- pitch stability
- real cello tests

## Issue 9 — Pitch Observation API

### Scope

- store results
- expose result endpoint
- retry
- preferred run

## Issue 10 — Pitch Result UI

### Scope

- processing state
- note
- cents
- vibrato
- confidence
- insufficient-data state

This sequence reaches the Version 0.2 milestone without implementing future features prematurely.

---

# Pull Request Standards

Every pull request should include:

- concise purpose
- linked issue
- scope summary
- screenshots for UI changes
- database migration notes
- tests added or updated
- manual validation steps
- known limitations

## Database Pull Requests

Must include:

- Alembic migration
- rollback consideration
- existing-data handling
- SQLite test
- model tests

## Analysis Pull Requests

Must include:

- engine version change when behavior changes
- test recordings or reproducible fixtures
- accuracy notes
- failure cases
- confidence behavior

---

# Testing Layers

## Frontend

- component tests
- state tests
- recording-control tests
- responsive checks
- accessibility checks

## Backend

- API tests
- ownership tests
- validation tests
- migration tests
- file-storage tests

## Analysis

- unit tests
- synthetic-audio tests
- retained cello regression recordings
- confidence calibration
- version compatibility

## End-to-End

Critical flows:

```text
Upload piece
→ Start practice
→ Record
→ Save
→ Analyze
→ View result
→ End session
→ View summary
```

---

# Definition of Done

A feature is done when:

1. acceptance criteria pass
2. tests pass
3. errors are handled
4. user data persists correctly
5. ownership is enforced
6. accessibility is considered
7. documentation is updated
8. no fake analysis is shown
9. known limitations are recorded
10. the feature is validated manually with a real cello recording when applicable

---

# Performance Priorities

Optimize in this order:

1. correctness
2. reliability
3. explainability
4. practice-flow responsiveness
5. processing speed
6. visual polish

The application should never trade trustworthy feedback for faster but misleading output.

---

# Product Validation Checkpoints

## Checkpoint 1 — Recording Persistence

Ask:

- does the workflow feel natural?
- can a musician start within five seconds?
- are controls readable from a stand?
- does session history make sense?

## Checkpoint 2 — Pitch Feedback

Ask:

- is the note identified correctly?
- is sharp or flat direction correct?
- does vibrato produce false errors?
- is the feedback understandable?

## Checkpoint 3 — Score Comparison

Ask:

- did the app identify the correct measure?
- did it distinguish wrong note from intonation?
- are false positives acceptable?
- is the recommendation useful?

## Checkpoint 4 — Practice Guidance

Ask:

- would a teacher agree with the suggestion?
- is the passage small enough?
- does the reason build trust?
- does the musician know what to do next?

---

# Risks

## Pitch Detection Accuracy

Risk:

Cello overtones and vibrato may cause octave errors or unstable pitch tracking.

Mitigation:

- test multiple algorithms
- use cello-specific range constraints
- preserve confidence
- suppress uncertain output

## Score Alignment Reliability

Risk:

Skipped notes, repeats, and tempo variation may misalign the performance.

Mitigation:

- require selected passage
- use confidence thresholds
- start with short passages
- reject ambiguous results

## Overbuilding

Risk:

The schema and product scope may become too large before the first useful milestone.

Mitigation:

- implement only minimum tables
- use phased epics
- defer teacher, rhythm, and dynamic tables

## False Authority

Risk:

Users may trust inaccurate recommendations.

Mitigation:

- evidence links
- confidence labels
- no global score
- explainable rules
- teacher validation
- user feedback controls

## Copyright and Privacy

Risk:

Uploaded music and recordings are private copyrighted content.

Mitigation:

- private-by-default storage
- required copyright acknowledgment
- no community score library
- protected file endpoints
- deletion workflows
- legal review

---

# Decision Gates

Do not proceed automatically through every phase.

## Gate After Basic Pitch Detection

Proceed only if open strings and stopped notes are reliably detected.

## Gate After Vibrato Analysis

Proceed only if normal vibrato no longer produces misleading intonation feedback.

## Gate After Score Alignment

Proceed only if short passages align reliably enough to support measure-level claims.

## Gate Before Recommendations

Proceed only if observations are accurate and explainable.

## Gate Before Public Beta

Proceed only after privacy, storage security, deletion, and legal requirements are in place.

---

# Recommended Next Action

The next development epic should be:

```text
Version 0.2 — Persistent Practice Sessions and Pitch Analysis
```

Begin with:

```text
Issue 1 — Persist Practice Sessions
```

Do not begin rhythm, dynamics, teacher features, or advanced recommendation work until the pitch-analysis milestone works with real cello recordings.

---

# Summary

The implementation path is:

```text
Persist Practice
      ↓
Validate Audio
      ↓
Detect Pitch
      ↓
Handle Vibrato
      ↓
Store Analysis
      ↓
Align to Score
      ↓
Generate Observations
      ↓
Update Practice Map
      ↓
Recommend Next Action
```

The roadmap succeeds when each phase produces a real, usable improvement rather than a collection of disconnected technical components.

The immediate objective is precise:

> Record a cello note, identify its pitch center accurately, and tell the musician whether it is consistently sharp or flat.
