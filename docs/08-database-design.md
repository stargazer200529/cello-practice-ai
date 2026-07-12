# Database Design

## Purpose

This document translates the **Practice with Purpose** domain model into a relational database design.

It defines:

- tables
- primary and foreign keys
- constraints
- indexes
- lifecycle and retention rules
- migration strategy
- boundaries between database storage and file storage

This document is implementation-oriented, but it does not define API endpoints or analysis algorithms.

The initial application uses **SQLite** with SQLAlchemy. The design should remain compatible with a future migration to **PostgreSQL** without requiring a fundamental redesign.

---

# Design Goals

The database should:

1. Preserve the musician's practice history.
2. Support fast access to pieces, sessions, recordings, and current recommendations.
3. Keep analysis results versioned and reproducible.
4. Avoid storing large audio or score files directly in relational tables.
5. Enforce privacy and ownership boundaries.
6. Support SQLite during early development.
7. Support PostgreSQL for future multi-user deployment.
8. Allow analysis and recommendation models to evolve without rewriting historical data.
9. Keep user-facing concepts separate from internal measurements.
10. Avoid premature complexity that does not support the first working milestone.

---

# Technology Direction

## Initial Development

- Database: SQLite
- ORM: SQLAlchemy
- Migrations: Alembic
- Backend: FastAPI
- File storage: Local filesystem

## Future Production Direction

- Database: PostgreSQL
- File storage: Object storage such as Amazon S3, Cloudflare R2, or equivalent
- Background jobs: Queue-based analysis workers
- Authentication: External identity provider or application-managed accounts

The schema should use portable SQLAlchemy types and avoid SQLite-specific behavior wherever practical.

---

# Database Conventions

## Table Names

Use lowercase plural snake case.

Examples:

```text
users
pieces
practice_sessions
recordings
analysis_runs
measure_observations
```

## Primary Keys

Use UUID-compatible string identifiers.

Recommended SQLAlchemy representation:

```python
String(36)
```

Store canonical UUID text:

```text
123e4567-e89b-12d3-a456-426614174000
```

Reasons:

- identifiers can be created before database insertion
- safer future synchronization between devices
- easier migration from SQLite to PostgreSQL
- avoids exposing sequential record counts

PostgreSQL may later use its native UUID type without changing domain semantics.

## Timestamps

Store timestamps in UTC.

Each mutable table should normally include:

```text
created_at
updated_at
```

Use timezone-aware datetime values in application code.

User-facing local times should be derived using the user's configured time zone.

## Enumerations

During early SQLite development, store enum values as constrained strings rather than database-specific enum types.

Example:

```text
status = "active"
```

Use application enums and database check constraints where practical.

## Soft Deletion

Use soft deletion only where history, privacy, or audit requirements justify it.

Recommended fields:

```text
deleted_at
archived_at
```

Do not add soft-delete fields to every table by default.

---

# Storage Boundaries

## Relational Database

Store:

- users and ownership
- piece metadata
- score metadata
- practice sessions
- passage definitions
- goals and notes
- recording metadata
- analysis metadata and results
- observations
- practice-map states
- recommendations
- summaries
- teacher relationships and assignments

## File Storage

Store outside the relational database:

- MusicXML files
- MXL files
- audio recordings
- generated waveform files
- future PDF scores
- future analysis artifacts too large for normal relational storage

The database stores:

- storage key or relative path
- file size
- MIME type
- checksum
- creation date
- status

## JSON Storage

JSON may be used for:

- flexible analysis configuration
- engine metadata
- raw diagnostic summaries
- non-critical display metadata

JSON should not replace structured columns needed for filtering, joins, constraints, or reporting.

---

# Core Schema

## users

Represents a musician account.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| email | String(320) | Yes | Unique when present |
| display_name | String(120) | Yes | User-facing name |
| timezone | String(64) | No | Default `UTC` |
| account_status | String(32) | No | `active`, `disabled`, `pending_deletion` |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |
| deleted_at | DateTime | Yes | Account deletion workflow |

### Constraints

- `email` must be unique when not null.
- `account_status` must contain a supported value.

### Initial Version Note

Version 0.x may use one local default user while preserving the `user_id` relationship in all owned records.

---

## user_settings

Stores one settings record per user.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | Foreign key to `users.id` |
| theme | String(32) | No | Default `system` |
| pitch_reference_hz | Numeric(6,2) | No | Default `440.00` |
| default_practice_minutes | Integer | Yes | Optional |
| accessibility_settings_json | JSON/Text | Yes | Flexible settings |
| recording_settings_json | JSON/Text | Yes | Flexible settings |
| notification_settings_json | JSON/Text | Yes | Flexible settings |
| privacy_settings_json | JSON/Text | Yes | Flexible settings |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Constraints

- Unique `user_id`.
- `pitch_reference_hz` should remain within a reasonable configured range.
- `default_practice_minutes` must be positive when present.

---

## instrument_profiles

Stores an instrument and tuning context.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | Foreign key |
| instrument_type | String(64) | No | Initial value `cello` |
| display_name | String(120) | No | Example: `My Cello` |
| tuning_json | JSON/Text | Yes | Example: C2, G2, D3, A3 |
| transposition_semitones | Integer | No | Default `0` |
| pitch_reference_hz | Numeric(6,2) | No | Default from settings |
| is_default | Boolean | No | Default false |
| is_active | Boolean | No | Default true |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Constraints

- At most one default active instrument profile per user.
- Version 1.0 should create a default cello profile.

---

## pieces

Represents one musical work in the user's library.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | Owner |
| instrument_profile_id | String(36) | Yes | Foreign key |
| title | String(255) | No | Required |
| composer | String(255) | Yes | |
| arranger | String(255) | Yes | |
| collection_name | String(255) | Yes | |
| difficulty_label | String(64) | Yes | Descriptive only |
| is_favorite | Boolean | No | Default false |
| archived_at | DateTime | Yes | Removes from active library |
| last_practiced_at | DateTime | Yes | Cached convenience value |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Constraints

- `title` must not be blank.
- Ownership is defined by `user_id`.
- Archiving a piece must not delete practice history.

### Indexes

- `(user_id, archived_at)`
- `(user_id, last_practiced_at)`
- `(user_id, title)`

---

## movements

Represents a major division within a piece.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| piece_id | String(36) | No | Foreign key |
| title | String(255) | Yes | |
| sequence_number | Integer | No | Display order |
| displayed_start_measure | Integer | Yes | |
| displayed_end_measure | Integer | Yes | |
| measure_count | Integer | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Constraints

- Unique `(piece_id, sequence_number)`.
- `sequence_number` must be non-negative.
- A single-movement work should receive one default movement.

---

## score_sources

Stores metadata for uploaded score files.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| piece_id | String(36) | No | Foreign key |
| uploaded_by_user_id | String(36) | No | Foreign key |
| original_filename | String(512) | No | |
| storage_key | String(1024) | No | File path or object key |
| file_type | String(32) | No | `musicxml`, `mxl`, future `pdf` |
| mime_type | String(255) | Yes | |
| size_bytes | BigInteger | Yes | |
| sha256_checksum | String(64) | No | Integrity and duplicate detection |
| parsing_status | String(32) | No | |
| parse_version | String(64) | Yes | |
| parse_error | Text | Yes | Safe diagnostic text |
| copyright_confirmed_at | DateTime | No | Required |
| copyright_confirmation_version | String(32) | No | Terms version |
| is_active | Boolean | No | One active source per piece |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Parsing Status Values

```text
uploaded
queued
parsing
ready
failed
superseded
```

### Constraints

- `copyright_confirmed_at` is required.
- `storage_key` must be unique.
- `sha256_checksum` must contain a valid SHA-256 value.
- At most one active score source per piece.

### Indexes

- `(piece_id, is_active)`
- `sha256_checksum`
- `parsing_status`

---

## score_measures

Stores stable measure-level structure parsed from a score source.

The initial database does not need to store every notation object as a normalized row. Measure-level structure is sufficient for early practice selection and feedback.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| score_source_id | String(36) | No | Foreign key |
| movement_id | String(36) | No | Foreign key |
| internal_sequence | Integer | No | Stable order within source |
| displayed_measure_number | String(32) | Yes | May include values such as `12a` |
| start_division | Integer | Yes | Parsed score position |
| duration_divisions | Integer | Yes | |
| metadata_json | JSON/Text | Yes | Time/key/clef summary |
| created_at | DateTime | No | UTC |

### Constraints

- Unique `(score_source_id, internal_sequence)`.
- Do not assume displayed measure numbers are unique.
- Internal sequence is the authoritative order.

### Indexes

- `(movement_id, internal_sequence)`
- `(score_source_id, displayed_measure_number)`

---

## score_notes

Stores parsed note events needed for future score-to-performance comparison.

This table may be deferred until Version 0.3, but the design reserves it now.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| score_measure_id | String(36) | No | Foreign key |
| event_sequence | Integer | No | Order within measure |
| voice_number | Integer | Yes | |
| staff_number | Integer | Yes | |
| onset_divisions | Integer | No | |
| duration_divisions | Integer | No | |
| midi_pitch | Integer | Yes | Null for rest |
| written_pitch | String(16) | Yes | Example `F#3` |
| is_rest | Boolean | No | |
| tie_type | String(16) | Yes | |
| metadata_json | JSON/Text | Yes | Articulation and notation metadata |
| created_at | DateTime | No | UTC |

### Constraints

- Unique `(score_measure_id, event_sequence)`.
- `midi_pitch` is null for rests.
- Durations must be non-negative.

### Indexes

- `(score_measure_id, event_sequence)`

---

# Practice Session Schema

## practice_sessions

Represents one independent period of practice.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | Owner |
| piece_id | String(36) | No | Practiced piece |
| instrument_profile_id | String(36) | Yes | Instrument context |
| status | String(32) | No | |
| practice_source | String(32) | No | |
| started_at | DateTime | No | UTC |
| ended_at | DateTime | Yes | |
| elapsed_seconds | Integer | No | Default `0` |
| active_practice_seconds | Integer | Yes | Future refinement |
| target_duration_seconds | Integer | Yes | Optional |
| session_notes | Text | Yes | User-authored |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Status Values

```text
active
completed
abandoned
interrupted
```

### Practice Source Values

```text
musician_choice
teacher_assignment
application_recommendation
```

### Constraints

- `ended_at` is required when status is `completed`, `abandoned`, or `interrupted`.
- Durations must be non-negative.
- Completed sessions are never reactivated.
- The piece must belong to the same user.

### Indexes

- `(user_id, started_at)`
- `(piece_id, started_at)`
- `(user_id, status)`

---

## passage_definitions

Stores reusable or session-specific passage scope.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| piece_id | String(36) | No | Foreign key |
| movement_id | String(36) | Yes | Optional |
| passage_type | String(32) | No | |
| display_label | String(255) | No | |
| created_by_user_id | String(36) | Yes | Null for system-generated |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Passage Type Values

```text
entire_piece
entire_movement
measure_range
non_contiguous_ranges
score_selection
custom
unspecified
```

---

## passage_ranges

Stores one or more ordered ranges belonging to a passage definition.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| passage_definition_id | String(36) | No | Foreign key |
| sequence_number | Integer | No | Order within passage |
| movement_id | String(36) | Yes | |
| start_score_measure_id | String(36) | Yes | Foreign key |
| end_score_measure_id | String(36) | Yes | Foreign key |
| displayed_start_measure | String(32) | Yes | Historical fallback |
| displayed_end_measure | String(32) | Yes | Historical fallback |
| created_at | DateTime | No | UTC |

### Constraints

- Unique `(passage_definition_id, sequence_number)`.
- Start and end must belong to the same piece.
- Displayed measure values are preserved so history remains understandable if score references change.

---

## practice_segments

Tracks changes in passage and focus during a session.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| practice_session_id | String(36) | No | Foreign key |
| passage_definition_id | String(36) | Yes | Foreign key |
| sequence_number | Integer | No | |
| started_at | DateTime | No | |
| ended_at | DateTime | Yes | |
| target_tempo_bpm | Numeric(6,2) | Yes | |
| notes | Text | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Constraints

- Unique `(practice_session_id, sequence_number)`.
- Segments may not overlap within one session.
- One segment may remain open only while the session is active.

### Indexes

- `(practice_session_id, sequence_number)`

---

## practice_focuses

Reference table for supported focus categories.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| code | String(64) | No | Unique stable code |
| display_name | String(120) | No | |
| is_active | Boolean | No | |
| sort_order | Integer | No | |

### Initial Codes

```text
intonation
rhythm
timing
dynamics
technique
musical_expression
performance_preparation
warm_up
learn_new_material
custom
```

---

## practice_segment_focuses

Many-to-many relationship between segments and focus categories.

| Column | Type | Null | Notes |
|---|---|---:|---|
| practice_segment_id | String(36) | No | Composite primary key |
| practice_focus_id | String(36) | No | Composite primary key |
| priority_order | Integer | Yes | Optional emphasis order |

---

## practice_goals

Stores optional goals.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| practice_session_id | String(36) | No | Foreign key |
| practice_segment_id | String(36) | Yes | Optional narrower scope |
| goal_type | String(32) | No | |
| description | String(512) | No | |
| target_value | Numeric(12,3) | Yes | |
| target_unit | String(32) | Yes | |
| current_value | Numeric(12,3) | Yes | |
| completion_method | String(32) | No | |
| status | String(32) | No | |
| completed_at | DateTime | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Goal Types

```text
duration
repetitions
successful_repetitions
target_tempo
passage_completion
teacher_assignment
custom
```

### Completion Methods

```text
user_confirmed
system_detected
hybrid
```

### Status Values

```text
active
completed
abandoned
```

---

## practice_notes

Stores musician, teacher, or application notes.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | Student owner |
| author_type | String(32) | No | |
| author_user_id | String(36) | Yes | Future teacher/user account |
| piece_id | String(36) | No | Foreign key |
| practice_session_id | String(36) | Yes | |
| passage_definition_id | String(36) | Yes | |
| assignment_id | String(36) | Yes | Future foreign key |
| note_text | Text | No | |
| is_active | Boolean | No | |
| archived_at | DateTime | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Author Types

```text
musician
teacher
application
```

### Constraints

- `note_text` must not be blank.
- Application-generated observations should normally be stored in analysis tables rather than as permanent practice notes.
- An application note should only be created when intentionally promoted into the practice workflow.

---

# Recording Schema

## recordings

Stores metadata for one audio recording.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| practice_session_id | String(36) | No | Foreign key |
| practice_segment_id | String(36) | No | Foreign key |
| passage_definition_id | String(36) | Yes | Snapshot of intended scope |
| recording_number | Integer | No | Neutral label within session |
| status | String(32) | No | |
| started_at | DateTime | No | |
| ended_at | DateTime | Yes | |
| duration_ms | Integer | Yes | |
| storage_key | String(1024) | Yes | Required after save |
| original_mime_type | String(255) | Yes | |
| normalized_audio_format | String(32) | Yes | |
| size_bytes | BigInteger | Yes | |
| sha256_checksum | String(64) | Yes | |
| sample_rate_hz | Integer | Yes | |
| channel_count | Integer | Yes | |
| microphone_label | String(255) | Yes | |
| removal_reason | String(64) | Yes | |
| removed_at | DateTime | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Status Values

```text
capturing
saved
processing
ready
invalid
removed
failed
```

### Constraints

- Unique `(practice_session_id, recording_number)`.
- `duration_ms` must be non-negative.
- Removed recordings require `removed_at`.
- `storage_key` must be unique when present.
- The segment and session must match.
- Recording numbers should never be reused within a session.

### Indexes

- `(practice_session_id, recording_number)`
- `(practice_session_id, status)`
- `sha256_checksum`
- `status`

---

# Analysis Schema

## analysis_runs

Stores one versioned execution of the analysis engine.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| recording_id | String(36) | No | Foreign key |
| score_source_id | String(36) | Yes | Score version used |
| engine_version | String(64) | No | |
| configuration_version | String(64) | No | |
| status | String(32) | No | |
| started_at | DateTime | Yes | |
| completed_at | DateTime | Yes | |
| overall_confidence | Numeric(5,4) | Yes | Internal only |
| failure_code | String(64) | Yes | |
| failure_message | Text | Yes | Sanitized |
| configuration_json | JSON/Text | Yes | Reproducibility |
| diagnostics_json | JSON/Text | Yes | Development diagnostics |
| is_preferred | Boolean | No | Current selected run |
| superseded_at | DateTime | Yes | |
| created_at | DateTime | No | UTC |

### Status Values

```text
queued
processing
completed
partially_completed
failed
superseded
```

### Constraints

- Completed results are immutable.
- At most one preferred analysis run per recording.
- `overall_confidence`, when present, must be between 0 and 1.
- Failed runs should include a failure code or message.
- A new engine execution always creates a new row.

### Indexes

- `(recording_id, created_at)`
- `(recording_id, is_preferred)`
- `status`
- `(engine_version, configuration_version)`

---

## alignment_events

Maps performed events to expected score events.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| analysis_run_id | String(36) | No | Foreign key |
| score_note_id | String(36) | Yes | Expected note |
| sequence_number | Integer | No | Per run |
| match_type | String(32) | No | |
| performed_start_ms | Integer | Yes | |
| performed_end_ms | Integer | Yes | |
| detected_midi_pitch | Numeric(8,3) | Yes | Supports fractional pitch |
| onset_deviation_ms | Integer | Yes | |
| duration_deviation_ms | Integer | Yes | |
| confidence | Numeric(5,4) | No | |
| metadata_json | JSON/Text | Yes | |
| created_at | DateTime | No | UTC |

### Match Types

```text
matched
missing
extra
ambiguous
unalignable
```

### Indexes

- `(analysis_run_id, sequence_number)`
- `score_note_id`

---

## pitch_observations

Stores pitch results for aligned notes or sustained regions.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| analysis_run_id | String(36) | No | Foreign key |
| alignment_event_id | String(36) | Yes | Foreign key |
| score_measure_id | String(36) | Yes | |
| expected_midi_pitch | Numeric(8,3) | Yes | |
| detected_pitch_center_midi | Numeric(8,3) | Yes | |
| average_cents_deviation | Numeric(8,3) | Yes | |
| pitch_stability_cents | Numeric(8,3) | Yes | |
| vibrato_width_cents | Numeric(8,3) | Yes | |
| vibrato_rate_hz | Numeric(8,3) | Yes | |
| start_ms | Integer | No | |
| end_ms | Integer | No | |
| confidence | Numeric(5,4) | No | |
| created_at | DateTime | No | UTC |

### Constraints

- `end_ms >= start_ms`.
- Confidence must be between 0 and 1.
- Values are internal measurements and are not automatically user-facing.

### Indexes

- `(analysis_run_id, score_measure_id)`
- `alignment_event_id`

---

## rhythm_observations

Stores onset and duration comparisons.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| analysis_run_id | String(36) | No | Foreign key |
| alignment_event_id | String(36) | Yes | |
| score_measure_id | String(36) | Yes | |
| expected_onset_ms | Integer | Yes | |
| performed_onset_ms | Integer | Yes | |
| onset_deviation_ms | Integer | Yes | |
| expected_duration_ms | Integer | Yes | |
| performed_duration_ms | Integer | Yes | |
| duration_deviation_ms | Integer | Yes | |
| local_tempo_bpm | Numeric(7,3) | Yes | |
| confidence | Numeric(5,4) | No | |
| created_at | DateTime | No | UTC |

### Indexes

- `(analysis_run_id, score_measure_id)`
- `alignment_event_id`

---

## dynamic_observations

Stores intensity and contour results.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| analysis_run_id | String(36) | No | Foreign key |
| score_measure_id | String(36) | Yes | |
| start_ms | Integer | No | |
| end_ms | Integer | No | |
| mean_rms | Numeric(12,6) | Yes | |
| peak_rms | Numeric(12,6) | Yes | |
| contour_type | String(32) | Yes | |
| contour_slope | Numeric(12,6) | Yes | |
| confidence | Numeric(5,4) | No | |
| created_at | DateTime | No | UTC |

---

## measure_observations

Stores interpreted, location-specific analysis findings.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| analysis_run_id | String(36) | No | Foreign key |
| piece_id | String(36) | No | Denormalized for queries |
| movement_id | String(36) | Yes | |
| score_measure_id | String(36) | Yes | |
| displayed_measure_number | String(32) | Yes | Historical fallback |
| category | String(32) | No | |
| observation_code | String(64) | No | Stable machine code |
| severity | Numeric(5,4) | Yes | Internal only |
| confidence | Numeric(5,4) | No | |
| evidence_count | Integer | No | Default `1` |
| user_message | Text | No | Evidence-based wording |
| evidence_json | JSON/Text | Yes | Supporting references |
| created_at | DateTime | No | UTC |

### Categories

```text
intonation
rhythm
timing
dynamics
tempo
technical_pattern
insufficient_data
```

### Constraints

- Confidence and severity must be between 0 and 1 when present.
- `evidence_count >= 1`.
- `user_message` must not claim certainty beyond the evidence.
- The piece must match the recording's piece.

### Indexes

- `(piece_id, score_measure_id, category)`
- `(analysis_run_id, category)`
- `(piece_id, created_at)`

---

## technical_patterns

Stores repeated tendencies across recordings or sessions.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | |
| piece_id | String(36) | Yes | Null for cross-piece pattern |
| instrument_profile_id | String(36) | Yes | |
| pattern_code | String(64) | No | |
| category | String(32) | No | |
| display_message | Text | No | |
| confidence | Numeric(5,4) | No | |
| evidence_count | Integer | No | |
| first_observed_at | DateTime | No | |
| last_observed_at | DateTime | No | |
| status | String(32) | No | |
| evidence_json | JSON/Text | Yes | |
| created_at | DateTime | No | UTC |
| updated_at | DateTime | No | UTC |

### Status Values

```text
active
improving
resolved
insufficient_evidence
superseded
```

### Constraints

- A long-term pattern requires more than one supporting observation unless an explicit future rule permits otherwise.
- Confidence must be between 0 and 1.

---

# Practice Map and Recommendation Schema

## practice_map_states

Stores the current derived priority for one location and category.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| piece_id | String(36) | No | |
| movement_id | String(36) | Yes | |
| score_measure_id | String(36) | Yes | |
| displayed_measure_number | String(32) | Yes | |
| category | String(32) | No | |
| priority_label | String(32) | No | |
| confidence | Numeric(5,4) | Yes | Internal |
| evidence_count | Integer | No | |
| explanation | Text | Yes | |
| evidence_window_start | DateTime | Yes | |
| evidence_window_end | DateTime | Yes | |
| last_analysis_run_id | String(36) | Yes | |
| updated_at | DateTime | No | UTC |

### Priority Labels

```text
comfortable
needs_reinforcement
recommended_focus
insufficient_data
```

### Constraints

- Unique `(piece_id, score_measure_id, category)`.
- Priority labels are descriptive practice states, not grades.
- `evidence_count` must be non-negative.
- Map state should not update while an associated recording is actively capturing.

### Indexes

- `(piece_id, category)`
- `(piece_id, priority_label)`
- `(piece_id, updated_at)`

---

## practice_map_snapshots

Stores a historical map version.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| piece_id | String(36) | No | |
| triggering_session_id | String(36) | Yes | |
| map_version | Integer | No | |
| created_at | DateTime | No | UTC |

### Constraints

- Unique `(piece_id, map_version)`.

---

## practice_map_snapshot_items

Copies map-state values into a snapshot.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| snapshot_id | String(36) | No | |
| score_measure_id | String(36) | Yes | |
| displayed_measure_number | String(32) | Yes | |
| category | String(32) | No | |
| priority_label | String(32) | No | |
| confidence | Numeric(5,4) | Yes | |
| explanation | Text | Yes | |

### Indexes

- `(snapshot_id, category)`
- `(snapshot_id, score_measure_id)`

---

## recommendations

Stores actionable suggestions.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| user_id | String(36) | No | |
| piece_id | String(36) | No | |
| passage_definition_id | String(36) | Yes | |
| source_type | String(32) | No | |
| recommendation_type | String(64) | No | |
| focus_category | String(32) | Yes | |
| title | String(255) | No | |
| reason | Text | No | |
| suggested_method | Text | Yes | |
| estimated_minutes | Integer | Yes | |
| internal_priority | Numeric(8,4) | Yes | Not user-facing |
| status | String(32) | No | |
| created_at | DateTime | No | UTC |
| expires_at | DateTime | Yes | |
| resolved_at | DateTime | Yes | |
| superseded_by_id | String(36) | Yes | Self-reference |
| evidence_json | JSON/Text | Yes | |
| updated_at | DateTime | No | UTC |

### Source Types

```text
analysis
teacher_assignment
user_goal
combined
```

### Status Values

```text
active
accepted
deferred
completed
dismissed
expired
superseded
```

### Constraints

- Recommendations must include a reason.
- `estimated_minutes` must be positive when present.
- User choice is never blocked by recommendation status.
- `internal_priority` must not be presented as a mastery score.

### Indexes

- `(user_id, status, created_at)`
- `(piece_id, status)`
- `(piece_id, focus_category)`

---

## recommendation_evidence

Links recommendations to supporting records.

| Column | Type | Null | Notes |
|---|---|---:|---|
| recommendation_id | String(36) | No | Composite primary key |
| evidence_type | String(32) | No | Composite primary key |
| evidence_id | String(36) | No | Composite primary key |
| created_at | DateTime | No | UTC |

### Evidence Types

```text
measure_observation
technical_pattern
practice_map_state
assignment
practice_goal
```

This polymorphic reference is acceptable for traceability, but application code must validate referenced records.

---

# Session Summary Schema

## session_summaries

Stores one generated summary per session version.

Because analysis may finish after the musician ends practice, summaries should be versioned.

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| practice_session_id | String(36) | No | |
| summary_version | Integer | No | |
| generation_status | String(32) | No | |
| practice_duration_seconds | Integer | No | |
| recording_count | Integer | No | |
| improvements_text | Text | Yes | |
| attention_text | Text | Yes | |
| looking_ahead_text | Text | Yes | |
| teacher_reminder_text | Text | Yes | |
| generated_from_analysis_at | DateTime | Yes | |
| is_current | Boolean | No | |
| created_at | DateTime | No | UTC |

### Constraints

- Unique `(practice_session_id, summary_version)`.
- At most one current summary per session.
- Previous summary versions remain immutable.
- Summary text must not fabricate analysis.
- Recording count and duration must be non-negative.

---

# Teacher Schema

Teacher functionality is future-facing. These tables may be deferred, but their relationships should remain reserved.

## teachers

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| linked_user_id | String(36) | Yes | Future teacher account |
| display_name | String(120) | No | |
| email | String(320) | Yes | |
| created_at | DateTime | No | |
| updated_at | DateTime | No | |

---

## teacher_relationships

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| student_user_id | String(36) | No | |
| teacher_id | String(36) | No | |
| status | String(32) | No | |
| permissions_json | JSON/Text | Yes | |
| sharing_preferences_json | JSON/Text | Yes | |
| started_at | DateTime | Yes | |
| ended_at | DateTime | Yes | |
| created_at | DateTime | No | |
| updated_at | DateTime | No | |

### Status Values

```text
invited
active
paused
ended
```

### Constraints

- Unique active relationship between one student and teacher.
- Ended relationships must not retain future access.

---

## assignments

| Column | Type | Null | Notes |
|---|---|---:|---|
| id | String(36) | No | Primary key |
| teacher_relationship_id | String(36) | No | |
| piece_id | String(36) | No | |
| passage_definition_id | String(36) | Yes | |
| title | String(255) | No | |
| instructions | Text | Yes | |
| due_at | DateTime | Yes | |
| status | String(32) | No | |
| created_at | DateTime | No | |
| completed_at | DateTime | Yes | |
| updated_at | DateTime | No | |

### Status Values

```text
active
completed
deferred
archived
```

---

## assignment_focuses

| Column | Type | Null | Notes |
|---|---|---:|---|
| assignment_id | String(36) | No | Composite primary key |
| practice_focus_id | String(36) | No | Composite primary key |

---

# Foreign-Key Deletion Rules

Use explicit deletion behavior.

## User Deletion

Account deletion should trigger an application-managed privacy workflow rather than immediate uncontrolled cascade deletion.

Expected sequence:

1. Mark user as pending deletion.
2. Revoke access.
3. Delete or anonymize uploaded score and audio files.
4. Delete dependent database records according to policy.
5. Preserve only legally required minimal records.
6. Mark deletion complete.

## Piece Deletion

Default user action should be **Archive Piece**.

Permanent deletion should remove:

- score files
- recordings
- analysis results
- practice sessions
- recommendations
- practice-map history

The application should require explicit confirmation.

## Recording Removal

Normal removal should:

- mark the recording as removed
- record a removal reason
- remove or queue deletion of audio storage
- prevent future analysis
- retain minimal metadata if needed for session consistency and audit

## Analysis Deletion

Analysis normally follows the recording lifecycle.

Old runs may be marked superseded and later purged according to retention policy.

---

# Required Index Strategy

The following user paths must remain efficient:

## Home

Queries:

- recent pieces
- active recommendations
- active teacher assignments
- latest completed sessions

Indexes:

```text
pieces(user_id, last_practiced_at)
recommendations(user_id, status, created_at)
practice_sessions(user_id, started_at)
assignments(teacher_relationship_id, status, due_at)
```

## Piece Home

Queries:

- recent sessions for one piece
- current practice-map states
- active recommendations
- active assignment

Indexes:

```text
practice_sessions(piece_id, started_at)
practice_map_states(piece_id, category)
recommendations(piece_id, status)
```

## Practice Workspace

Queries:

- current session and segment
- recordings ordered by number
- active notes
- current passage and goals

Indexes:

```text
practice_segments(practice_session_id, sequence_number)
recordings(practice_session_id, recording_number)
practice_notes(piece_id, is_active)
practice_goals(practice_session_id, status)
```

## Analysis Review

Queries:

- preferred run for recording
- observations by measure and category
- repeated patterns

Indexes:

```text
analysis_runs(recording_id, is_preferred)
measure_observations(piece_id, score_measure_id, category)
technical_patterns(user_id, piece_id, status)
```

---

# Transaction Boundaries

## Score Upload

One transaction should create:

- Piece when needed
- Score Source metadata
- copyright confirmation record

File persistence and score parsing may occur outside the transaction.

If file storage fails, the database record should be marked failed or rolled back.

## Start Session

One transaction should create:

- Practice Session
- default Passage Definition if required
- initial Practice Segment
- optional goals

## Stop Recording

The sequence should be:

1. finalize browser recording
2. persist audio file
3. update Recording metadata and status
4. commit
5. enqueue analysis

Analysis must never begin against an uncommitted or incomplete recording.

## Complete Analysis

One transaction should store:

- analysis run status
- alignment results
- pitch/rhythm/dynamic observations
- measure observations

Practice-map and recommendation updates may occur in a second transaction so an aggregation failure does not invalidate the underlying analysis.

## End Session

One transaction should:

- close active segment
- mark session completed
- store final duration

Summary generation may occur asynchronously afterward.

---

# Concurrency and Idempotency

Although the initial app is local, operations should be designed for future asynchronous processing.

## Recording Upload

Use a client-generated recording ID or idempotency key so retries do not create duplicate recordings.

## Analysis Run

An analysis job should be idempotent for:

```text
recording_id
engine_version
configuration_version
score_source_id
```

A retry may resume or replace a failed job, but it must not create duplicate completed results without intent.

## Practice Map Update

Use a transaction when replacing current map states.

A map update should be traceable to the analysis runs used as evidence.

## Preferred Analysis Run

Changing the preferred run should atomically:

- set the selected run to preferred
- clear the prior preferred run
- mark supersession where applicable

---

# Migration Strategy

Use Alembic from the beginning.

## Rules

1. Never modify a production database schema manually.
2. Every schema change receives an Alembic revision.
3. Migration files are committed with the related code.
4. Migrations must support existing user data.
5. Destructive migrations require an explicit backup and migration plan.
6. SQLite limitations must be tested, especially table alteration and constraints.
7. Seed reference data through migrations or controlled startup logic.

## Recommended Initial Revisions

```text
001_create_users_and_settings
002_create_instrument_profiles
003_create_pieces_movements_and_score_sources
004_create_score_measures_and_notes
005_create_practice_sessions_segments_and_goals
006_create_recordings
007_create_analysis_runs_and_observations
008_create_practice_map_and_recommendations
009_create_session_summaries
010_create_teacher_tables
```

These may be combined during early development, but migration history should remain understandable.

---

# Data Retention

Retention rules must eventually align with the Privacy Policy and Terms of Service.

## Suggested Initial Policy

### Active Account

Retain:

- score files
- recordings
- practice history
- current and historical analysis
- recommendations
- summaries

until the user deletes them or closes the account.

### Removed Recording

- Immediately hide from normal UI.
- Queue audio deletion.
- Retain minimal metadata only as needed for integrity and diagnostics.
- Do not use removed recordings in future analysis or recommendations.

### Superseded Analysis Runs

- Retain during development for reproducibility.
- Future production may purge older runs after a defined period while preserving current user-facing observations.

### Account Deletion

- Delete uploaded scores and recordings.
- Delete or anonymize associated practice data.
- Complete deletion within the period stated in the Privacy Policy.
- Preserve only records required for legal, billing, fraud, or security purposes.

---

# Privacy and Copyright Requirements

## Ownership Isolation

Every user-owned query must be scoped by `user_id`.

Do not rely only on knowing a Piece or Recording identifier.

Authorization should verify the ownership chain:

```text
User
→ Piece
→ Practice Session
→ Recording
→ Analysis Run
```

## Uploaded Music

The database must record:

- who uploaded the score
- when copyright confirmation occurred
- which policy version was accepted
- whether the score is private
- which file is active

Uploaded scores must not appear in a public or shared catalog.

## Teacher Access

Future teacher access must be permission-based.

A teacher should receive access only to the student data explicitly allowed by the active Teacher Relationship.

## Sensitive Audio

Practice recordings are personal user content.

Storage paths must not expose predictable public URLs.

---

# Initial Implementation Scope

The first database implementation should not create every future table at once.

## Already Needed or Near-Term

Implement first:

```text
users
user_settings
instrument_profiles
pieces
movements
score_sources
score_measures
practice_sessions
passage_definitions
passage_ranges
practice_segments
practice_segment_focuses
practice_goals
practice_notes
recordings
analysis_runs
pitch_observations
measure_observations
practice_map_states
recommendations
session_summaries
```

## Defer Until Required

```text
score_notes
alignment_events
rhythm_observations
dynamic_observations
technical_patterns
practice_map_snapshots
teachers
teacher_relationships
assignments
assignment_focuses
```

Deferring implementation does not remove them from the design.

---

# Recommended Version 0.2 Minimum Schema

For the first successful intonation milestone, the minimum new schema is:

```text
pieces
score_sources
score_measures
practice_sessions
practice_segments
recordings
analysis_runs
pitch_observations
measure_observations
```

This supports:

1. selecting a piece
2. recording a passage
3. analyzing pitch over time
4. linking results to a measure or passage
5. reporting average cents sharp or flat
6. retaining results across attempts

The milestone should be able to support feedback such as:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

That statement requires:

- stable score location
- recording history
- versioned analysis
- pitch observations
- aggregation across recordings

---

# Example Query Flows

## My Music

```sql
SELECT *
FROM pieces
WHERE user_id = :user_id
  AND archived_at IS NULL
ORDER BY last_practiced_at DESC NULLS LAST, title;
```

SQLite does not support identical `NULLS LAST` behavior in every version, so SQLAlchemy ordering may need a portable expression.

## Recent Sessions for a Piece

```sql
SELECT *
FROM practice_sessions
WHERE user_id = :user_id
  AND piece_id = :piece_id
  AND status = 'completed'
ORDER BY started_at DESC
LIMIT 10;
```

## Current Practice Map

```sql
SELECT *
FROM practice_map_states
WHERE piece_id = :piece_id
ORDER BY score_measure_id, category;
```

## Preferred Analysis Run

```sql
SELECT *
FROM analysis_runs
WHERE recording_id = :recording_id
  AND is_preferred = true
LIMIT 1;
```

## Repeated Intonation Tendency

Conceptual query:

```sql
SELECT
    score_measure_id,
    AVG(average_cents_deviation) AS average_deviation,
    COUNT(*) AS observation_count
FROM pitch_observations
WHERE analysis_run_id IN (:preferred_analysis_runs)
GROUP BY score_measure_id
HAVING COUNT(*) >= 3;
```

The production implementation should also filter by confidence, expected note, passage context, and analysis version.

---

# Validation Rules

Validation should occur at both application and database levels.

## Application-Level Validation

Use application logic for:

- ownership checks
- score and movement consistency
- active session rules
- preferred analysis selection
- one active score source per piece
- one default instrument profile per user
- complex passage range validation
- recommendation evidence validation
- copyright acknowledgment workflow

## Database-Level Validation

Use constraints for:

- required fields
- unique identifiers
- foreign keys
- non-negative durations
- valid confidence range
- unique recording number per session
- unique segment sequence per session
- unique current practice-map state per location/category

SQLite foreign-key enforcement must be explicitly enabled for every connection.

---

# Backup and Recovery

## Local Development

Back up:

- SQLite database file
- `storage/` score directory
- `storage/` recording directory

A database backup without matching files is incomplete.

## Production

Use:

- automated database backups
- versioned object storage where appropriate
- encrypted storage
- documented restoration tests
- file checksum validation

Database and file-storage backups should share a recoverable point-in-time strategy.

---

# Database Non-Goals

The relational database should not:

- store raw audio as binary blobs by default
- act as a public sheet-music library
- calculate analysis results through database triggers
- store a single global mastery score
- overwrite completed analysis results
- treat recommendations as mandatory tasks
- infer teacher permissions implicitly
- use color names as the only meaning of practice-map states

Store semantic labels such as:

```text
recommended_focus
```

The interface may render that state as red, patterned, labeled, or otherwise accessible.

---

# Open Database Decisions

The following decisions should be resolved before their related features are implemented:

1. Whether UUID values should use strings initially or SQLAlchemy's portable UUID type.
2. How parsed score-note data should be versioned when a score source is replaced.
3. Whether passage definitions should be reusable or always session-specific.
4. How much diagnostic analysis data should remain in JSON versus normalized tables.
5. How long superseded analysis runs should be retained.
6. Whether practice-map snapshots should be full copies or event-based deltas.
7. Whether summary versions need a separate child table for structured observations.
8. How account deletion should handle teacher-authored notes and assignments.
9. Which fields should be encrypted at the application level.
10. When the application should migrate from SQLite to PostgreSQL.

---

# Recommended Next Step

After this database design is approved:

1. Compare the existing SQLAlchemy models with this schema.
2. Identify the smallest migration needed for Version 0.2.
3. Create an Alembic migration plan.
4. Draft the analysis-engine specification.
5. Implement only the tables required for the next working milestone.

The database should grow with working features rather than attempting to implement the entire future model immediately.

---

# Summary

The primary persistent relationship is:

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
Observations
  ↓
Practice Map and Recommendations
```

The design intentionally separates:

- relational metadata
- large uploaded files
- immutable analysis history
- current derived guidance
- user-authored practice information

This separation allows the application to improve its analysis algorithms without losing the musician's practice history or rewriting past evidence.
