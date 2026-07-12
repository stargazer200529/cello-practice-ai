# Frontend Architecture

## Purpose

This document defines the frontend architecture for **Practice with Purpose**.

The frontend must support a musician who wants to:

- open the application
- select a piece
- begin practicing within seconds
- record multiple attempts
- replay recordings
- review observations
- end with a useful next step

The frontend should remain calm, fast, and unobtrusive.

It is a companion beside the music stand, not a replacement for printed music.

---

# Architectural Goals

The frontend should be:

- mobile-friendly
- tablet-first for music-stand use
- usable on desktop
- fast to load
- easy to maintain
- accessible
- resilient to temporary API delays
- compatible with later offline support
- structured for incremental analysis features
- clear about the difference between user intent, recorded evidence, analysis, and recommendations

---

# Technology Stack

## Framework

Use:

```text
Next.js
React
TypeScript
```

The current application already uses Next.js.

## Styling

Use the existing styling approach if already established.

Do not introduce a second CSS framework unless necessary.

Preferred options:

- CSS Modules
- Tailwind CSS
- a small internal component library

The project should avoid adopting a large UI framework unless it materially reduces implementation effort.

## Score Rendering

Continue using:

```text
OpenSheetMusicDisplay
```

The rendered score is a reference and planning aid.

It should not dominate the Practice Workspace.

## Audio Recording

Use the browser:

```text
MediaRecorder API
```

The browser should:

- request microphone access
- record audio
- expose recording state
- provide a local preview
- upload the result to the backend
- preserve metadata needed by the recording API

---

# Frontend Responsibilities

The frontend is responsible for:

- navigation
- layout
- displaying user-owned content
- collecting practice intent
- microphone interaction
- local recording state
- upload progress
- API error presentation
- replay controls
- practice timer display
- responsive behavior
- accessible controls
- presentation of analysis and recommendations

The frontend is not responsible for:

- pitch detection
- score alignment
- analysis confidence calculations
- recommendation ranking
- authoritative ownership checks
- permanent recording numbering
- storage paths
- database persistence

---

# Application Routes

Recommended routes:

```text
/
├── /music
├── /music/new
├── /pieces/[pieceId]
├── /practice/[sessionId]
├── /sessions/[sessionId]
├── /progress
├── /teacher
└── /settings
```

## Route Meaning

### `/`

Home.

Practice-oriented starting point.

### `/music`

My Music library.

### `/music/new`

Add Piece.

### `/pieces/[pieceId]`

Piece Dashboard.

### `/practice/[sessionId]`

Active Practice Workspace.

### `/sessions/[sessionId]`

Completed Session Details.

### `/progress`

Progress and long-term insights.

### `/teacher`

Teacher assignments and relationships.

May be hidden until teacher features exist.

### `/settings`

User and practice settings.

---

# Route Ownership

Each route should load only the data it needs.

## Home

Loads:

- primary recommendation
- teacher assignment when present
- recent pieces
- recent session context

## My Music

Loads:

- piece list
- filters
- search state

## Piece Dashboard

Loads:

- piece metadata
- active score source
- recent sessions
- active recommendations
- Practice Map summary

## Practice Workspace

Loads:

- active practice session
- current segment
- current passage
- goals
- recording list

Analysis details should load separately and should not block the workspace.

---

# Folder Structure

Recommended frontend structure:

```text
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── music/
│   │   ├── page.tsx
│   │   └── new/
│   │       └── page.tsx
│   ├── pieces/
│   │   └── [pieceId]/
│   │       └── page.tsx
│   ├── practice/
│   │   └── [sessionId]/
│   │       └── page.tsx
│   ├── sessions/
│   │   └── [sessionId]/
│   │       └── page.tsx
│   ├── progress/
│   │   └── page.tsx
│   ├── teacher/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
├── components/
│   ├── app-shell/
│   ├── navigation/
│   ├── pieces/
│   ├── practice/
│   ├── recordings/
│   ├── score/
│   ├── recommendations/
│   ├── feedback/
│   └── ui/
├── features/
│   ├── pieces/
│   ├── practice-sessions/
│   ├── recordings/
│   ├── score-viewer/
│   ├── analysis/
│   └── recommendations/
├── lib/
│   ├── api/
│   ├── audio/
│   ├── formatting/
│   ├── validation/
│   └── storage/
├── hooks/
├── types/
└── tests/
```

---

# Folder Responsibilities

## `app/`

Route composition only.

Pages should avoid containing large amounts of business logic.

## `components/`

Reusable presentation components.

## `features/`

Feature-specific state, hooks, API functions, and feature composition.

## `lib/api/`

Shared API client and transport concerns.

## `lib/audio/`

MediaRecorder integration, MIME support, and recording helpers.

## `types/`

Shared frontend types when not generated from API contracts.

## `tests/`

Cross-feature tests and utilities.

---

# Component Hierarchy

## Application Shell

```text
AppShell
├── Header
├── PrimaryNavigation
├── MainContent
└── OptionalBottomNavigation
```

## Home

```text
HomePage
├── Greeting
├── PrimaryPracticeCard
├── TeacherAssignmentCard
├── RecentPieces
└── AddPieceAction
```

## My Music

```text
MusicLibraryPage
├── LibraryHeader
├── SearchAndFilters
├── PieceGrid
│   └── PieceCard
└── AddPieceButton
```

## Piece Dashboard

```text
PieceDashboard
├── PieceHeader
├── StartPracticeButton
├── PracticeMapSummary
├── PrimaryRecommendation
├── RecentSessions
└── ReferenceScore
```

## Practice Workspace

```text
PracticeWorkspace
├── PracticeHeader
│   ├── PieceTitle
│   ├── SessionTimer
│   └── EndPracticeButton
├── PracticeContext
│   ├── CurrentPassage
│   ├── FocusTags
│   └── Goals
├── RecordingPanel
│   ├── RecordButton
│   ├── StopButton
│   ├── UploadState
│   └── LatestObservation
├── RecordingList
│   └── RecordingCard
├── ContextualTool
└── CollapsibleReferenceScore
```

---

# Server and Client Component Strategy

Use Server Components for:

- route-level data loading
- static page shells
- non-interactive summaries
- initial piece and session reads

Use Client Components for:

- microphone access
- recording state
- timers
- playback
- editable focus tags
- editable goals
- local upload state
- dialogs
- score interaction
- live tuner later

Do not convert an entire route to a Client Component because one child needs browser APIs.

---

# API Client

Create a centralized API client.

Recommended location:

```text
frontend/lib/api/client.ts
```

Responsibilities:

- base URL configuration
- JSON headers
- multipart requests
- standardized error parsing
- request cancellation
- typed return values

Example API groups:

```text
frontend/lib/api/
├── client.ts
├── pieces.ts
├── practice-sessions.ts
├── recordings.ts
├── analysis.ts
└── recommendations.ts
```

Do not scatter raw `fetch()` calls across page components.

---

# API Base URL

Use an environment variable:

```text
NEXT_PUBLIC_API_BASE_URL
```

Development example:

```text
http://127.0.0.1:8000
```

The application should not hard-code local development URLs throughout the codebase.

---

# API Error Model

Normalize backend errors into one frontend shape:

```ts
type ApiError = {
  code?: string;
  message: string;
  status: number;
  details?: unknown;
};
```

The UI should distinguish:

- validation error
- unavailable backend
- permission denied
- missing resource
- conflict
- upload too large
- unsupported audio
- unexpected error

---

# Data Fetching

Use the simplest reliable strategy first.

Recommended:

- server-side fetch for initial route data
- client-side mutation for recording and editable state
- explicit refresh after successful mutations

Do not introduce a complex global data library unless repeated caching problems justify it.

A library such as TanStack Query may be added later when:

- analysis polling becomes common
- recommendation state changes frequently
- optimistic updates are needed
- multiple screens share live cached data

---

# State Management

Use local component state by default.

Use React Context only for true cross-cutting concerns.

Potential context:

- app shell state
- theme
- active microphone permission status
- active practice session controls

Avoid storing all application data in one global store.

## Practice Session State

The Practice Workspace may use a feature-level reducer.

Example state:

```ts
type PracticeWorkspaceState = {
  session;
  currentSegment;
  recordings;
  recordingState;
  uploadState;
  elapsedSeconds;
  microphonePermission;
  error;
};
```

---

# Recording State Machine

Recording behavior should follow explicit states.

```text
idle
→ requesting_permission
→ ready
→ recording
→ stopping
→ preview_ready
→ creating_record
→ uploading
→ saved
```

Error states:

```text
permission_denied
unsupported_browser
upload_failed
save_failed
```

Rules:

- only one recording may be active
- Stop must remain available while recording
- upload should not block starting another recording after the prior capture is finalized locally
- unsaved local audio must not be discarded without warning
- backend recording number is authoritative

---

# Recording Workflow

Recommended sequence:

```text
1. User presses Record
2. Frontend creates local MediaRecorder
3. Audio capture begins
4. User presses Stop
5. Local blob becomes available
6. Frontend creates backend recording record
7. Frontend uploads audio
8. Backend returns saved recording metadata
9. Recording list refreshes
```

The frontend may create the backend recording before capture in a later version.

For the current MVP, the sequence should prioritize reliability and avoid orphaned `capturing` rows.

---

# Audio MIME Handling

The browser should inspect supported types using:

```ts
MediaRecorder.isTypeSupported(...)
```

Preferred order:

```text
audio/webm;codecs=opus
audio/webm
audio/mp4
audio/ogg;codecs=opus
```

Fallback behavior must be explicit.

Do not assume every browser supports the same MIME type.

---

# Timer Architecture

The timer should derive from:

- backend session `started_at`
- current time
- session status

Do not persist a client-only timer value as the source of truth.

The displayed timer may update once per second.

When the session ends:

- stop the timer
- use backend `elapsed_seconds`
- display the finalized value

---

# Practice Context Editing

The musician may edit:

- passage
- focus tags
- goals
- target tempo
- notes

These changes should not restart the session.

The frontend should create a new practice segment when passage or focus changes once segment APIs exist.

Until then, editable controls may be limited to values currently supported by the backend.

Do not display controls that appear functional if persistence is not implemented.

---

# Piece Selection

Starting practice from a piece should require one primary action.

Recommended:

```text
Start Practice
```

The app should create a session immediately using sensible defaults.

Optional settings may be edited in the Practice Workspace after the session begins.

Do not use a blocking setup wizard.

---

# Score Display

The score should be:

- optional
- collapsible
- usable for selecting passages
- visible before or after playing
- non-dominant during active practice

The Practice Workspace should support:

```text
Show Score
Hide Score
```

On phone, the score should normally open in a separate full-width panel or sheet.

---

# Practice Map

Practice Map overlays should be visible:

- before practice
- after analysis
- during planning
- during review

They should be hidden during active recording by default.

States:

- Comfortable
- Needs reinforcement
- Recommended focus
- Insufficient data

The UI must not show numerical mastery percentages.

---

# Responsive Design

## Tablet

Primary target.

The interface should be readable from a music stand.

## Phone

Use a stacked layout.

Prioritize:

1. timer
2. Record/Stop
3. current passage
4. latest recording
5. recording list
6. optional score

## Desktop

Use additional width for:

- score reference
- recording history
- progress details

Desktop should support planning and review, not define the mobile layout.

---

# Touch Targets

Interactive controls should meet a minimum target size of approximately:

```text
44 × 44 CSS pixels
```

The primary Record and Stop controls should be substantially larger.

---

# Accessibility

The frontend must support:

- keyboard navigation
- screen-reader labels
- visible focus states
- color-independent status indicators
- high contrast
- reduced motion
- semantic headings
- accessible dialogs
- readable tuner output at a distance
- error messages associated with relevant controls

Color must never be the only indicator.

---

# Design System

Create a small internal design system.

## Core Components

```text
Button
IconButton
Card
Badge
StatusLabel
Dialog
Drawer
Tabs
TextField
Select
Checkbox
ProgressIndicator
EmptyState
ErrorState
Skeleton
```

## Practice-Specific Components

```text
RecordButton
StopButton
RecordingCard
SessionTimer
FocusTag
PracticeStatusLabel
PassageSelector
RecommendationCard
PracticeMapLegend
```

---

# Visual Language

The interface should feel:

- calm
- restrained
- clear
- quiet
- trustworthy
- practice-oriented

Avoid:

- excessive gradients
- celebratory confetti
- streak pressure
- XP systems
- leaderboard patterns
- report-card visuals
- aggressive red error states
- flashing live analysis during playing

---

# Loading States

Every route should have a defined loading state.

## Practice Workspace

Show the session shell immediately, then load recordings.

Do not show a blank page while waiting.

## Analysis

Use:

```text
Analyzing recording…
```

Analysis must not block another recording.

---

# Empty States

## No Pieces

```text
Add your first piece to begin practicing.
```

## No Recordings

```text
Your recordings will appear here.
```

## No Recommendation

```text
Practice this piece to begin building personalized guidance.
```

---

# Error States

Errors should tell the user:

- what happened
- whether their recording is safe
- what action to take

Example:

```text
Your recording was captured, but it could not be uploaded.
Retry upload or keep the local copy for now.
```

---

# Offline and Network Resilience

Full offline mode is not required initially.

The architecture should still prepare for:

- detecting offline state
- preserving a completed local recording blob temporarily
- retrying failed uploads
- avoiding silent data loss

A later offline queue may use IndexedDB.

Do not rely on `localStorage` for audio blobs.

---

# Security and Privacy

The frontend must:

- avoid exposing storage keys
- avoid logging raw recording data
- avoid putting private IDs into analytics unnecessarily
- revoke object URLs when no longer needed
- request microphone permission only when needed
- explain why microphone permission is required
- provide a clear response when permission is denied

---

# Microphone Permission Experience

Before the first recording attempt, the interface may show:

```text
Practice with Purpose needs microphone access to record your playing.
Audio is stored privately in your account.
```

The permission request should occur only after a user action.

Do not request microphone access automatically on page load.

---

# Testing Strategy

## Unit Tests

Test:

- formatters
- API error normalization
- recording reducer
- timer calculations
- MIME selection
- status mapping

## Component Tests

Test:

- Record button states
- Stop button availability
- recording upload state
- recording list ordering
- removed recording behavior
- empty and error states

## Integration Tests

Test:

```text
Start session
→ record
→ stop
→ upload
→ list recording
→ replay
→ end session
```

## Responsive Tests

Verify:

- phone portrait
- tablet portrait
- tablet landscape
- desktop

## Accessibility Tests

Verify:

- keyboard-only use
- screen-reader labels
- focus order
- contrast
- color-independent states

---

# Frontend Acceptance Criteria

The frontend MVP is successful when a musician can:

1. open the application
2. select a piece
3. start a practice session
4. see a session timer
5. record cello audio
6. stop recording
7. upload the recording
8. replay the saved recording
9. create another recording
10. end the session
11. reopen the application and still see the recordings

The workflow should not require a setup wizard.

---

# Initial Implementation Sequence

To reduce Codex usage, bundle related frontend work into a small number of vertical-slice issues.

## Issue A — Practice Workspace Integration

Implement:

- start session from Piece Dashboard
- route to active session
- timer
- microphone permission
- record
- stop
- upload
- saved recording list
- replay
- end session
- refresh persistence

This is one coherent vertical slice.

## Issue B — Home and My Music Refinement

Implement:

- Home screen
- recent pieces
- primary practice action
- My Music refinement
- responsive navigation

## Issue C — Piece Dashboard Refinement

Implement:

- primary Start Practice action
- practice history
- recommendation placeholder only where data is unavailable
- collapsible score reference

Do not split every component into a separate Codex issue.

---

# Immediate Next Issue

The next implementation issue should be:

```text
Integrate Persistent Practice Workspace
```

It should connect the existing frontend recorder to:

- practice-session creation
- recording creation
- audio upload
- persisted recording list
- playback
- session completion

No pitch analysis should be included.

---

# Open Decisions

1. Whether to create the backend recording row before or after local capture.
2. Whether to adopt TanStack Query before analysis polling.
3. Whether the active session route should recover abandoned local recording blobs.
4. Whether the score remains embedded or opens in a sheet on phone.
5. Whether one active session should be automatically resumed.
6. Whether users may have multiple active sessions across pieces.
7. How microphone device selection should work.
8. Whether recording upload retries should use IndexedDB in the MVP.
9. Whether Practice Workspace state should use a reducer or state machine library.
10. Whether responsive bottom navigation is needed immediately.

---

# Summary

The frontend architecture follows this separation:

```text
Route
  ↓
Feature Component
  ↓
API Client
  ↓
Backend Resource
```

For recording:

```text
Musician Action
  ↓
Browser MediaRecorder
  ↓
Local Blob
  ↓
Recording API
  ↓
Persistent Audio
  ↓
Replay and Future Analysis
```

The frontend should make the application feel immediate while preserving the backend as the source of truth.

The next milestone is concrete:

> A musician can select a piece, start practicing, record multiple attempts, replay them, and end the session without leaving the Practice Workspace.
