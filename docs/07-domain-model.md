# Domain Model

## Purpose

This document defines the core product concepts used by **Practice with Purpose** and the relationships between them.

It describes the application domain independently of:

- database tables
- API endpoints
- frontend components
- storage technology
- analysis libraries

The domain model establishes a shared vocabulary for product design, software development, and future analysis work.

The model should remain stable even as the technical implementation changes.

---

# Domain Principles

The domain model follows these rules:

1. The musician remains the owner of the practice process.
2. A piece is the primary organizational object for repertoire.
3. A practice session represents one independent period of practice.
4. Recordings belong to practice sessions.
5. Analysis results are versioned and may be regenerated.
6. Recommendations are derived guidance, not commands.
7. Practice-map states represent practice priority, not musical ability.
8. Teacher assignments may guide practice but never restrict independent practice.
9. Uploaded scores remain private by default.
10. The model must support solo cello first without preventing future instrument expansion.

---

# High-Level Model

```text
User
│
├── Instrument Profiles
│
├── Pieces
│   ├── Movements
│   ├── Score Sources
│   ├── Practice Notes
│   ├── Practice Sessions
│   │   ├── Practice Segments
│   │   ├── Practice Goals
│   │   ├── Recordings
│   │   │   └── Analysis Runs
│   │   │       └── Measure Observations
│   │   └── Session Summary
│   │
│   ├── Practice Map States
│   └── Recommendations
│
├── Teacher Relationships
│   └── Assignments
│
└── User Settings
```

---

# Core Entities

## User

A **User** represents a musician using the application.

### Responsibilities

The User owns:

- uploaded music
- practice sessions
- recordings
- notes
- recommendations
- settings
- teacher relationships

### Key Attributes

- User identifier
- Display name
- Account status
- Preferred time zone
- Created date
- Last active date

### Relationships

```text
User
├── has many Instrument Profiles
├── has many Pieces
├── has many Practice Sessions
├── has many Teacher Relationships
└── has one User Settings record
```

### Rules

- A user may use the application without a teacher relationship.
- A user may have more than one instrument profile in the future.
- Version 1.0 may create one default cello profile.

---

## Instrument Profile

An **Instrument Profile** describes the instrument context used for practice and analysis.

### Examples

- Cello
- Violin
- Viola
- Voice
- Piano

### Key Attributes

- Instrument type
- Display name
- Tuning
- Transposition
- Clef preferences
- Pitch reference
- Active status

### Cello-Specific Examples

- Standard tuning: C2, G2, D3, A3
- Pitch reference: A4 = 440 Hz
- Primary clefs: bass, tenor, treble

### Relationships

```text
User
└── Instrument Profiles
    └── referenced by Pieces and Practice Sessions
```

### Rules

- Version 1.0 is optimized for solo cello.
- Instrument assumptions should not be embedded directly into unrelated entities.
- Analysis behavior may depend on the selected instrument profile.

---

## Piece

A **Piece** represents one musical work in the user's library.

Examples:

- Bach Cello Suite No. 1
- Popper Etude No. 6
- C Major Scale
- Teacher-created exercise

### Key Attributes

- Title
- Composer
- Arranger
- Instrument
- Difficulty
- Collection
- Favorite status
- Archived status
- Created date
- Last practiced date

### Relationships

```text
Piece
├── has many Movements
├── has many Score Sources
├── has many Practice Sessions
├── has many Practice Notes
├── has many Practice Map States
├── has many Recommendations
└── may be referenced by Assignments
```

### Rules

- A Piece is the primary container for all long-term practice information.
- A Piece may exist before a score file is uploaded.
- A Piece may contain one or more movements.
- A Piece may use multiple score sources over time.
- A Piece is private to the user unless explicitly shared through a future feature.

---

## Movement

A **Movement** represents a major structural division within a Piece.

Examples:

- Prelude
- Allemande
- Movement I
- Scale Exercise 1

### Key Attributes

- Title
- Sequence number
- Measure count
- Starting measure number
- Ending measure number

### Relationships

```text
Piece
└── Movements
    ├── referenced by Practice Segments
    ├── referenced by Assignments
    └── referenced by Measure Observations
```

### Rules

- A single-movement piece may still have one default Movement.
- Measure numbering may restart between movements.
- Movement identity should not rely only on displayed measure numbers.

---

## Score Source

A **Score Source** represents an uploaded or linked source of musical notation.

### Supported Types

- MusicXML
- Compressed MusicXML (`.mxl`)
- PDF in a future version
- Scanned score in a future version

### Key Attributes

- Original filename
- File type
- Storage location
- File checksum
- Upload date
- Parsing status
- Parse version
- Copyright acknowledgment status
- Active source status

### Relationships

```text
Piece
└── Score Sources
    └── parsed into musical structure used by analysis
```

### Rules

- Uploaded scores are private by default.
- A user must confirm that they own the score or have permission to upload and use it.
- Copyright remains with the original rights holder.
- A Piece may have multiple score sources, but one should be designated as active.
- Replacing a score source must not silently invalidate historical practice data.
- Parsed score content should retain stable identifiers where practical.

---

## Score Element

A **Score Element** represents a parsed musical object from the active score source.

This may include:

- measure
- note
- rest
- chord
- dynamic marking
- tempo marking
- articulation
- phrase marking

### Key Attributes

- Stable score element identifier
- Movement identifier
- Measure identifier
- Voice
- Staff
- Beat position
- Duration
- Pitch
- Notation metadata

### Rules

- Score Elements are reference objects used by alignment and analysis.
- They are not necessarily exposed directly to the user.
- Stable identifiers are important so analysis remains linked to the correct musical location.

---

## Practice Session

A **Practice Session** represents one independent period of practice.

A session begins when the musician enters the Practice Workspace and ends when they choose **End Practice** or the application safely closes the session.

### Key Attributes

- Start time
- End time
- Duration
- Instrument profile
- Session status
- Selected focus areas
- Target duration
- User-entered notes

### Session Status

- Active
- Completed
- Abandoned
- Interrupted

### Relationships

```text
Practice Session
├── belongs to one User
├── belongs to one Piece
├── may reference one Movement
├── has many Practice Segments
├── has many Practice Goals
├── has many Recordings
└── has one Session Summary
```

### Rules

- Every session is independent.
- A new day does not continue the prior session.
- Previous sessions may inform defaults and recommendations.
- Focus, passage, and goals may change without restarting the session.
- A session may include more than one passage.
- A session may contain no recordings.
- Session duration should distinguish active practice time from elapsed wall-clock time when possible.

---

## Practice Segment

A **Practice Segment** represents a portion of a Practice Session during which the musician works on a defined scope and focus.

It records how practice changed within one session.

### Examples

- Measures 23–25, intonation focus
- Measures 40–42, rhythm focus
- Entire movement, performance run-through
- Open practice without a defined passage

### Key Attributes

- Start time
- End time
- Passage definition
- Focus areas
- Sequence order
- Optional target tempo
- Optional notes

### Relationships

```text
Practice Session
└── Practice Segments
    ├── referenced by Recordings
    ├── referenced by Practice Goals
    └── referenced by Session Summary
```

### Rules

- Changing passage or focus creates or updates the current Practice Segment.
- Segment changes do not end the Practice Session.
- A Practice Session must have at least one segment, even if the segment covers the entire piece.
- A segment may define contiguous or non-contiguous passages.

---

## Passage Definition

A **Passage Definition** identifies the musical scope being practiced.

### Supported Forms

- Entire piece
- Entire movement
- Contiguous measure range
- Non-contiguous measure ranges
- Direct score selection
- Custom user label
- Unspecified passage

### Examples

```text
Measures 23–25
Measures 23–25 and 40–42
Movement II
Entire Piece
Opening Shift Exercise
```

### Key Attributes

- Passage type
- Movement references
- Measure ranges
- Score element references
- Display label

### Rules

- Passage definitions should remain understandable even if the score is later replaced.
- Measure references should use stable internal identifiers where available.
- User-facing labels should use musical notation familiar to the musician.

---

## Practice Focus

A **Practice Focus** identifies what the musician wants additional attention on during practice.

### Initial Focus Types

- Intonation
- Rhythm
- Timing
- Dynamics
- Technique
- Musical expression
- Performance preparation
- Warm-up
- Learn new material
- Custom

### Rules

- A session or segment may have multiple focus areas.
- Focus affects emphasis, tools, and recommendations.
- Focus does not prevent the application from analyzing other measurable areas.
- Focus may be changed at any time.
- Practice Focus is not the same as Practice Source.

---

## Practice Source

A **Practice Source** identifies what prompted the practice activity.

### Values

- Musician choice
- Teacher assignment
- Application recommendation

### Rules

- Practice Source provides context only.
- It must not restrict what the musician can practice.
- A user may begin from one source and change direction during the session.
- The musician remains the final decision-maker.

---

## Practice Goal

A **Practice Goal** represents an optional intention for the session or segment.

### Examples

- Practice for 20 minutes
- Complete three successful repetitions
- Reach 72 BPM
- Work through Measures 23–25
- Follow teacher assignment
- Custom goal

### Key Attributes

- Goal type
- Target value
- Current progress
- Completion status
- Created time
- Completed time

### Goal Status

- Active
- Completed
- Abandoned

### Rules

- Goals are optional.
- Goals never prevent continued practice.
- Multiple goals may exist at the same time.
- Goal completion may be user-confirmed, system-detected, or both.
- “Successful repetition” must eventually have a configurable or explainable definition.

---

## Practice Note

A **Practice Note** records a musician or teacher observation associated with a Piece, Passage, Session, or Assignment.

### Examples

- Relax left thumb
- Keep bow parallel to the bridge
- Shift from first position earlier
- Use less bow in Measure 18

### Key Attributes

- Note text
- Author type
- Created date
- Updated date
- Scope
- Active status

### Author Types

- Musician
- Teacher
- Application

### Rules

- User and teacher notes should be distinguishable.
- Application observations should not be represented as teacher notes.
- Notes may remain active across multiple sessions.
- Notes may be archived without deleting historical context.

---

## Recording

A **Recording** represents one captured audio attempt within a Practice Session.

### Key Attributes

- Recording number within session
- Start time
- End time
- Duration
- Audio format
- Storage location
- File checksum
- Recording status
- Microphone metadata
- Associated passage
- Associated practice segment

### Recording Status

- Capturing
- Saved
- Processing
- Ready
- Invalid
- Removed

### Relationships

```text
Recording
├── belongs to one Practice Session
├── belongs to one Practice Segment
├── may reference one Passage Definition
└── has many Analysis Runs
```

### Rules

- Recordings are labeled neutrally: Recording 1, Recording 2, and so on.
- Recordings document the learning process, not only polished performances.
- Removal is a secondary action for accidental or invalid recordings.
- Removing a recording should preserve minimal audit metadata when legally and technically appropriate.
- Audio format conversion may occur internally without changing the identity of the Recording.
- A recording may exist even if analysis fails.

---

## Recording Removal Reason

A **Recording Removal Reason** explains why a recording was removed.

### Initial Values

- Accidental recording
- Wrong piece or passage
- No usable audio
- User requested removal
- Other

### Rules

- The reason is optional unless required for diagnostics.
- Removal should not be presented as a normal step in repeated practice.
- Deleted audio should follow the application's data-retention and privacy policy.

---

## Analysis Run

An **Analysis Run** represents one execution of the analysis engine against a Recording.

A Recording may have multiple Analysis Runs because algorithms, score versions, or configuration may change.

### Key Attributes

- Analysis run identifier
- Analysis engine version
- Configuration version
- Score source version
- Start time
- Completion time
- Status
- Confidence
- Failure reason

### Analysis Status

- Queued
- Processing
- Completed
- Partially completed
- Failed
- Superseded

### Relationships

```text
Recording
└── Analysis Runs
    ├── Pitch Analysis
    ├── Rhythm Analysis
    ├── Timing Analysis
    ├── Dynamic Analysis
    ├── Alignment Result
    └── Measure Observations
```

### Rules

- Analysis results are immutable after completion.
- A new algorithm or configuration creates a new Analysis Run.
- One Analysis Run may be designated as the current preferred result.
- Partial results may be preserved when one analysis component fails.
- User-facing feedback must identify insufficient confidence rather than pretending certainty.
- Analysis must not produce a single global performance grade.

---

## Alignment Result

An **Alignment Result** maps performed audio events to written score events.

### Key Attributes

- Score element reference
- Detected performance event
- Alignment confidence
- Start-time difference
- Duration difference
- Match type

### Match Types

- Matched
- Missing
- Extra
- Ambiguous
- Unalignable

### Rules

- Alignment is foundational to score comparison.
- Low-confidence alignment should limit downstream conclusions.
- The system should distinguish “wrong note” from “uncertain alignment.”
- Expressive timing should not automatically be classified as error.

---

## Pitch Observation

A **Pitch Observation** represents a measured pitch result for a performed note or sustained region.

### Key Attributes

- Expected pitch
- Detected pitch center
- Average cents deviation
- Pitch stability
- Vibrato width
- Vibrato rate
- Confidence
- Observation time range

### Rules

- Pitch center should be used rather than instantaneous pitch where vibrato is present.
- Normal cello vibrato should not be penalized.
- Low-confidence pitch results must be identified.
- The model should preserve both raw measurements and interpreted observations.

---

## Rhythm Observation

A **Rhythm Observation** describes timing behavior relative to the score.

### Key Attributes

- Expected onset
- Performed onset
- Onset deviation
- Expected duration
- Performed duration
- Duration deviation
- Local tempo
- Confidence

### Rules

- Rhythm analysis should account for tempo context.
- Expressive timing should not be treated as incorrect solely because it is non-mechanical.
- Repeated patterns are more significant than isolated deviations.

---

## Dynamic Observation

A **Dynamic Observation** describes measured intensity and contour.

### Key Attributes

- Relative intensity
- Dynamic contour
- Crescendo or diminuendo execution
- Phrase-shape measurements
- Confidence

### Rules

- Dynamic analysis describes measurable sound intensity.
- It should not claim that artistic interpretation is objectively wrong.
- Comparisons against written dynamics should allow reasonable expressive variation.

---

## Measure Observation

A **Measure Observation** summarizes analysis evidence for a specific musical location.

### Examples

- Measure 18: F-sharp averaged 17 cents flat.
- Measure 24: Shift entrance was late in three recordings.
- Measures 30–32: Crescendo contour was limited.

### Key Attributes

- Movement
- Measure
- Score element references
- Observation category
- Severity
- Frequency
- Confidence
- Evidence count
- User-facing explanation

### Categories

- Intonation
- Rhythm
- Timing
- Dynamics
- Tempo
- Technique pattern
- Insufficient data

### Rules

- Observations should explain what happened and where.
- Observations should distinguish isolated events from repeated patterns.
- Severity and confidence are internal measurements and need not be shown as numbers.
- A Measure Observation belongs to an Analysis Run.
- Similar observations may later be aggregated across sessions.

---

## Technical Pattern

A **Technical Pattern** represents a repeated tendency across notes, passages, or sessions.

### Examples

- Fourth-finger notes trend flat.
- Shifts into higher positions begin late.
- Dotted rhythms become compressed at faster tempos.
- Dynamic contrast decreases during long phrases.

### Key Attributes

- Pattern type
- Instrument context
- Evidence count
- First observed date
- Most recent date
- Confidence
- Active status

### Relationships

```text
User or Piece
└── Technical Patterns
    ├── supported by Measure Observations
    └── may produce Recommendations
```

### Rules

- Patterns require repeated evidence.
- One recording should rarely create a long-term technical pattern.
- Patterns must remain explainable through supporting observations.
- Technical patterns should not claim a physical cause unless directly supported.

---

## Practice Map State

A **Practice Map State** represents practice priority for a musical location and analysis category.

### Priority Labels

- Comfortable
- Needs reinforcement
- Recommended focus
- Insufficient data

### Key Attributes

- Piece
- Movement
- Passage or measure
- Analysis category
- Priority label
- Confidence
- Evidence window
- Last updated date
- Explanation

### Relationships

```text
Piece
└── Practice Map States
    └── derived from observations across Practice Sessions
```

### Rules

- Practice Map State is derived, not manually authored analysis.
- It represents practice priority, not ability or mastery.
- A musical location may have different states by category.

Example:

```text
Measure 24
├── Intonation: Recommended focus
├── Rhythm: Comfortable
└── Dynamics: Insufficient data
```

- The current Practice Map may change as new evidence is added.
- Historical snapshots may be retained for progress review.
- Practice-map colors should not update while the musician is actively playing.

---

## Practice Map Snapshot

A **Practice Map Snapshot** preserves the state of a Piece's Practice Map at a point in time.

### Key Attributes

- Piece
- Snapshot date
- Triggering session
- Map version
- Included Practice Map States

### Rules

- Snapshots support long-term progress review.
- The current map should not be overwritten without preserving meaningful history.
- Snapshot retention may be optimized later.

---

## Recommendation

A **Recommendation** is an actionable suggestion generated from analysis, practice history, teacher assignments, or user goals.

### Example

> Practice Measures 24–27 at a slower tempo. Remove vibrato and isolate the shift into Measure 26. The same flat tendency appeared in three recordings.

### Key Attributes

- Recommendation type
- Piece
- Passage
- Focus category
- Reason
- Evidence
- Suggested method
- Estimated focus time
- Priority
- Created date
- Expiration date
- Status

### Recommendation Status

- Active
- Accepted
- Deferred
- Completed
- Dismissed
- Expired
- Superseded

### Rules

- Recommendations are optional.
- The musician may accept, ignore, defer, or modify them.
- Recommendations must explain why they were made.
- Recommendations should rely on repeated or significant evidence.
- Recommendations should avoid repeating indefinitely without new value.
- Teacher assignments may influence priority but do not automatically override musician choice.
- Recommendations should not use unexplained scores.

---

## Session Summary

A **Session Summary** provides closure and reflection after a Practice Session.

### Key Attributes

- Total practice duration
- Recording count
- Passages practiced
- Improvements observed
- Areas needing attention
- Repeated patterns
- Suggested starting point for next session
- Teacher reminders
- Generated date
- User-edited notes

### Relationships

```text
Practice Session
└── one Session Summary
```

### Rules

- A summary is not a report card.
- It should include:
  - what improved
  - what still needs attention
  - where to begin next time
- Statements should be evidence-based.
- The summary should avoid fake praise.
- The summary should remain understandable without exposing internal scoring formulas.
- A summary may be regenerated when new analysis becomes available, but historical versions should not be silently rewritten.

---

## Teacher

A **Teacher** represents an instructor connected to one or more users.

### Key Attributes

- Display name
- Contact information
- Account status
- Teaching relationship status

### Rules

- Teacher support is optional.
- The application must remain fully usable without a teacher.
- Teacher identity and permissions require explicit user consent.

---

## Teacher Relationship

A **Teacher Relationship** connects a musician and teacher.

### Status

- Invited
- Active
- Paused
- Ended

### Key Attributes

- Student
- Teacher
- Start date
- End date
- Permissions
- Sharing preferences

### Rules

- Users control what information is shared.
- Ending a relationship must revoke future access.
- Historical assignments may remain in the student's account.
- Teacher access should follow least-privilege principles.

---

## Assignment

An **Assignment** represents teacher-provided practice guidance.

### Key Attributes

- Teacher
- Student
- Piece
- Passage
- Instructions
- Focus areas
- Due date
- Created date
- Completion status

### Assignment Status

- Active
- Completed
- Deferred
- Archived

### Rules

- Assignments may reference one or more passages.
- Assignments may include notes and goals.
- Assignments should appear naturally in Home, Piece Home, and Practice Workspace.
- Assignments never prevent independent practice.
- Completion may be student-confirmed, teacher-confirmed, or supported by practice evidence.

---

## User Settings

**User Settings** control how the application behaves for one user.

### Categories

- General
- Recording
- Tuner
- Metronome
- Theme
- Accessibility
- Notifications
- Teacher connection
- Privacy
- Data retention

### Rules

- Settings belong to the User.
- Defaults should allow immediate practice.
- Required setup should be minimized.
- Accessibility preferences should apply consistently across the application.

---

# Derived Concepts

The following concepts are derived from other entities rather than treated as primary records.

## Recent Piece

Derived from the user's Piece activity and last practiced date.

## Resume Your Progress

A Home-screen presentation derived from:

- the most relevant recent Piece
- active Recommendations
- recent Practice Map States
- active Assignments

It starts a new Practice Session. It does not reopen the previous session.

## Practice Trend

Derived from observations across multiple sessions.

Examples:

- Intonation becoming more consistent
- Rhythm remaining stable
- Passage requiring less practice time
- Repeated fourth-finger flat tendency

## Current Preferred Analysis

The most appropriate completed Analysis Run for a Recording based on:

- engine version
- score version
- completion status
- confidence
- supersession rules

---

# Entity Ownership

| Entity | Primary Owner |
|---|---|
| User | Account |
| Instrument Profile | User |
| Piece | User |
| Movement | Piece |
| Score Source | Piece |
| Practice Session | User and Piece |
| Practice Segment | Practice Session |
| Practice Goal | Practice Session or Practice Segment |
| Practice Note | User, Teacher, Piece, or Session |
| Recording | Practice Session |
| Analysis Run | Recording |
| Measure Observation | Analysis Run |
| Technical Pattern | User or Piece |
| Practice Map State | Piece |
| Practice Map Snapshot | Piece |
| Recommendation | Piece |
| Session Summary | Practice Session |
| Teacher Relationship | User and Teacher |
| Assignment | Teacher Relationship |
| User Settings | User |

---

# Core Relationships

```text
User 1 ─── * Instrument Profile

User 1 ─── * Piece

Piece 1 ─── * Movement

Piece 1 ─── * Score Source

Piece 1 ─── * Practice Session

Practice Session 1 ─── * Practice Segment

Practice Session 1 ─── * Practice Goal

Practice Session 1 ─── * Recording

Recording 1 ─── * Analysis Run

Analysis Run 1 ─── * Measure Observation

Piece 1 ─── * Practice Map State

Piece 1 ─── * Practice Map Snapshot

Piece 1 ─── * Recommendation

Practice Session 1 ─── 0..1 Session Summary

User 1 ─── * Teacher Relationship

Teacher Relationship 1 ─── * Assignment
```

---

# Lifecycle Examples

## Uploading a Piece

```text
User selects score file
        ↓
Copyright confirmation recorded
        ↓
Piece created
        ↓
Score Source stored
        ↓
Score parsed
        ↓
Movements and Score Elements created
        ↓
Piece becomes available in My Music
```

---

## Starting Practice

```text
User selects Start Practice
        ↓
New Practice Session created
        ↓
Default Practice Segment created
        ↓
Passage, focus, and goals remain editable
        ↓
Practice timer begins
```

---

## Recording and Analysis

```text
User starts recording
        ↓
Recording created with Capturing status
        ↓
User stops recording
        ↓
Audio saved
        ↓
Recording marked Saved
        ↓
Analysis Run queued
        ↓
Analysis components execute
        ↓
Measure Observations created
        ↓
Practice Map and Recommendations may update
```

Analysis should not block the musician from starting another recording.

---

## Ending Practice

```text
User selects End Practice
        ↓
Practice Session marked Completed
        ↓
Available analysis is aggregated
        ↓
Session Summary generated
        ↓
Practice Map snapshot may be created
        ↓
Next-session recommendation may be created
```

---

# Domain Invariants

The following rules must always remain true:

1. A Recording belongs to exactly one Practice Session.
2. An Analysis Run belongs to exactly one Recording.
3. Completed Analysis Runs are immutable.
4. A new analysis version creates a new Analysis Run.
5. A Practice Session is never resumed after completion.
6. A new session may use information from prior sessions.
7. Recommendations never prevent musician-selected practice.
8. Teacher assignments never prevent independent practice.
9. Practice Map labels represent priority, not grades.
10. A numerical mastery score is not presented to the user.
11. Uploaded scores are private by default.
12. Copyright acknowledgment is required before score import.
13. The application must not fabricate analysis when confidence is insufficient.
14. The score is optional during active practice.
15. Passage, focus, and goals may change without restarting the session.

---

# Version 1.0 Scope

The initial domain implementation should prioritize:

- one user
- one default cello instrument profile
- MusicXML and MXL score sources
- pieces and movements
- independent practice sessions
- editable passages and focus areas
- audio recordings
- versioned analysis runs
- pitch and intonation observations
- measure-level feedback
- practice-map states
- session summaries
- recommendations

Teacher entities, assignments, rhythm analysis, dynamic analysis, and multi-instrument support may be implemented later, but the model should reserve a clear place for them.

---

# Out of Scope for the Initial Domain

The following are not required for the first working milestone:

- public score sharing
- community music libraries
- social feeds
- leaderboards
- competitions
- global performance grades
- public recording sharing
- ensemble synchronization
- accompaniment analysis
- automatic artistic judgment
- replacement of printed music
- full score annotation comparable to dedicated score-reader applications

---

# Open Decisions

The following questions require later product or technical decisions:

1. How should successful repetitions be defined?
2. How long should raw recordings and old analysis runs be retained?
3. When should Practice Map snapshots be created?
4. How should score replacement preserve historical measure references?
5. How should the system distinguish expressive timing from rhythm error?
6. What confidence threshold is required before generating a user-facing observation?
7. How should multiple recommendations be prioritized?
8. Which teacher permissions should be available in the first teacher-enabled version?
9. Should users be allowed to manually override Practice Map states?
10. How should non-contiguous passages be represented in the user interface?

These questions should be resolved in later specifications rather than embedded prematurely in the database design.

---

# Summary

The core domain flow is:

```text
User
  ↓
Piece
  ↓
Practice Session
  ↓
Practice Segment
  ↓
Recording
  ↓
Analysis Run
  ↓
Measure Observation
  ↓
Practice Map and Recommendation
  ↓
Session Summary
```

This model separates:

- what the musician chooses
- what the application records
- what the analysis engine measures
- what the recommendation engine suggests

That separation is essential to keeping the application accurate, explainable, and respectful of musical judgment.
