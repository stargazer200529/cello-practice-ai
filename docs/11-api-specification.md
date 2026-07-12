# API Specification

## Purpose

This document defines the application programming interface for **Practice with Purpose**.

The API connects:

- the frontend user interface
- the persistent database
- score storage and parsing
- audio recording storage
- analysis processing
- practice-map updates
- recommendation generation
- session summaries
- future teacher workflows

The initial backend uses **FastAPI**.

This specification is implementation-oriented, but it remains independent of any one frontend framework.

---

# API Principles

The API should be:

- predictable
- resource-oriented
- versioned
- explicit about ownership
- confidence-aware
- safe for asynchronous processing
- compatible with SQLite during development
- compatible with PostgreSQL and object storage later
- usable from desktop, tablet, and phone interfaces

The API must not expose internal scoring as a global performance grade.

---

# Base Path

All Version 1 endpoints use:

```text
/api/v1
```

Example:

```text
GET /api/v1/pieces
```

---

# Content Types

## JSON Requests and Responses

```text
Content-Type: application/json
```

## File Uploads

```text
Content-Type: multipart/form-data
```

## Audio Streaming or Download

The backend should return the appropriate MIME type.

Examples:

```text
audio/webm
audio/wav
audio/mpeg
```

---

# Authentication

## Initial Local Development

The first development version may operate with a single local default user.

The backend should still structure endpoints around authenticated ownership.

## Future Production

Production requests should use an authenticated user identity.

Possible mechanism:

```text
Authorization: Bearer <token>
```

The API must derive the current user from authentication context rather than accepting arbitrary `user_id` values from the client for normal operations.

---

# Authorization

Every user-owned resource must be checked through its ownership chain.

Example:

```text
Authenticated User
→ Piece
→ Practice Session
→ Recording
→ Analysis Run
```

A caller must not gain access merely by knowing a UUID.

The API should return `404 Not Found` rather than exposing the existence of another user's private resource.

---

# Response Conventions

## Successful Single Resource

```json
{
  "data": {
    "id": "uuid",
    "title": "Bach Suite No. 1"
  }
}
```

## Successful Collection

```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Bach Suite No. 1"
    }
  ],
  "meta": {
    "count": 1,
    "next_cursor": null
  }
}
```

## Successful Action

```json
{
  "data": {
    "status": "accepted"
  }
}
```

## Error Response

```json
{
  "error": {
    "code": "recording_not_ready",
    "message": "The recording has not finished saving.",
    "details": null,
    "request_id": "uuid"
  }
}
```

---

# HTTP Status Codes

Use standard status codes consistently.

| Code | Meaning |
|---:|---|
| 200 | Successful read or update |
| 201 | Resource created |
| 202 | Asynchronous work accepted |
| 204 | Successful action with no response body |
| 400 | Invalid request |
| 401 | Authentication required |
| 403 | Authenticated but not permitted |
| 404 | Resource not found |
| 409 | Resource state conflict |
| 413 | Uploaded file too large |
| 415 | Unsupported file type |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error |
| 503 | Analysis service unavailable |

---

# Error Codes

The API should return stable machine-readable codes.

Examples:

```text
validation_error
resource_not_found
piece_archived
unsupported_score_format
copyright_confirmation_required
score_parse_failed
session_already_completed
recording_not_ready
recording_invalid
analysis_already_running
analysis_failed
insufficient_signal
alignment_failed
recommendation_not_active
teacher_permission_denied
storage_failure
```

---

# Pagination

Collection endpoints should support cursor-based pagination where practical.

Example:

```text
GET /api/v1/practice-sessions?limit=20&cursor=<token>
```

Response:

```json
{
  "data": [],
  "meta": {
    "count": 20,
    "next_cursor": "opaque-token"
  }
}
```

Initial local versions may use limit/offset internally, but the public contract should avoid exposing database-specific pagination assumptions.

---

# Sorting and Filtering

Use explicit query parameters.

Examples:

```text
GET /api/v1/pieces?archived=false&favorite=true
GET /api/v1/practice-sessions?piece_id=<uuid>&status=completed
GET /api/v1/recommendations?piece_id=<uuid>&status=active
```

Reject unsupported sort fields rather than silently ignoring them.

---

# Idempotency

Create operations that may be retried should accept:

```text
Idempotency-Key: <client-generated-key>
```

Recommended for:

- recording creation
- recording finalization
- analysis submission
- score upload completion
- session completion

The server should return the original result for a repeated valid request with the same key.

---

# Resource Overview

```text
/api/v1
├── /health
├── /me
├── /settings
├── /instrument-profiles
├── /pieces
├── /score-sources
├── /practice-sessions
├── /practice-segments
├── /practice-goals
├── /practice-notes
├── /recordings
├── /analysis-runs
├── /practice-map
├── /recommendations
├── /session-summaries
└── /teacher
```

---

# Health Endpoints

## GET `/health`

Basic service health.

### Response

```json
{
  "status": "ok"
}
```

## GET `/health/ready`

Readiness check for:

- database
- storage
- analysis dependencies

### Response

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "storage": "ok",
    "analysis": "ok"
  }
}
```

---

# Current User

## GET `/me`

Returns the authenticated user's profile.

### Response

```json
{
  "data": {
    "id": "uuid",
    "display_name": "Kara",
    "email": "user@example.com",
    "timezone": "America/Denver",
    "account_status": "active"
  }
}
```

---

# Settings

## GET `/settings`

Returns user settings.

## PATCH `/settings`

Updates selected settings.

### Request

```json
{
  "theme": "system",
  "pitch_reference_hz": 440.0,
  "default_practice_minutes": 20
}
```

### Rules

- omitted fields remain unchanged
- invalid pitch references are rejected
- accessibility settings should be validated against supported keys

---

# Instrument Profiles

## GET `/instrument-profiles`

Returns active instrument profiles.

## POST `/instrument-profiles`

Creates a profile.

### Request

```json
{
  "instrument_type": "cello",
  "display_name": "My Cello",
  "pitch_reference_hz": 440.0,
  "is_default": true
}
```

## GET `/instrument-profiles/{instrument_profile_id}`

Returns one profile.

## PATCH `/instrument-profiles/{instrument_profile_id}`

Updates profile metadata.

## DELETE `/instrument-profiles/{instrument_profile_id}`

Deactivates or deletes an unused profile.

### Rules

- Version 1.0 should always preserve at least one active cello profile.
- Setting one profile as default should clear the prior default in the same transaction.

---

# Pieces

## GET `/pieces`

Returns the user's library.

### Query Parameters

```text
archived
favorite
search
limit
cursor
sort
```

### Example Response

```json
{
  "data": [
    {
      "id": "piece-uuid",
      "title": "Cello Suite No. 1",
      "composer": "J. S. Bach",
      "is_favorite": true,
      "last_practiced_at": "2026-07-10T18:22:00Z",
      "practice_status": "needs_reinforcement",
      "active_recommendation": {
        "title": "Reinforce the shift into Measure 24",
        "passage_label": "Measures 23–25"
      }
    }
  ],
  "meta": {
    "count": 1,
    "next_cursor": null
  }
}
```

### Notes

`practice_status` is derived presentation data.

It is not a mastery score.

## POST `/pieces`

Creates a piece without requiring an immediate upload.

### Request

```json
{
  "title": "Cello Suite No. 1",
  "composer": "J. S. Bach",
  "arranger": null,
  "instrument_profile_id": "uuid"
}
```

### Response

`201 Created`

## GET `/pieces/{piece_id}`

Returns Piece Home data.

### Response Includes

- metadata
- active score source
- movements
- recent sessions
- current practice-map summary
- active recommendations
- active assignment when available
- current progress narrative

## PATCH `/pieces/{piece_id}`

Updates metadata.

## POST `/pieces/{piece_id}/archive`

Archives a piece.

## POST `/pieces/{piece_id}/restore`

Restores an archived piece.

## DELETE `/pieces/{piece_id}`

Permanently deletes a piece and related content.

### Rules

- permanent deletion requires explicit confirmation
- archive is the default UI action
- deletion should be asynchronous when large file cleanup is required

---

# Score Upload and Parsing

## POST `/pieces/{piece_id}/score-sources`

Uploads a MusicXML or MXL file.

### Content Type

```text
multipart/form-data
```

### Fields

```text
file
copyright_confirmed
copyright_confirmation_version
```

### Example Form Values

```text
copyright_confirmed=true
copyright_confirmation_version=2026-07
```

### Response

```json
{
  "data": {
    "id": "score-source-uuid",
    "piece_id": "piece-uuid",
    "original_filename": "bach-suite-1.mxl",
    "file_type": "mxl",
    "parsing_status": "queued",
    "is_active": false
  }
}
```

### Status

`202 Accepted`

### Rules

- reject upload when copyright confirmation is false or absent
- support `.musicxml`, `.xml`, and `.mxl`
- validate MIME type and file extension
- enforce file-size limits
- calculate checksum
- store file privately
- parsing occurs asynchronously where practical

## GET `/score-sources/{score_source_id}`

Returns upload and parsing status.

## POST `/score-sources/{score_source_id}/parse`

Queues a parse or reparse.

## POST `/score-sources/{score_source_id}/activate`

Marks a ready source as active for the piece.

### Rules

- activation must be atomic
- only one source may be active per piece
- source must be parsed successfully before activation

## DELETE `/score-sources/{score_source_id}`

Deletes an inactive source.

Active-source deletion should require a replacement or explicit piece impact confirmation.

---

# Score Structure

## GET `/pieces/{piece_id}/movements`

Returns movements.

## GET `/movements/{movement_id}/measures`

Returns measure metadata.

### Query Parameters

```text
start_sequence
end_sequence
```

## GET `/pieces/{piece_id}/score-outline`

Returns lightweight score structure for:

- measure navigation
- passage selection
- practice-map rendering

### Response

```json
{
  "data": {
    "piece_id": "uuid",
    "score_source_id": "uuid",
    "movements": [
      {
        "id": "movement-uuid",
        "title": "Prelude",
        "sequence_number": 1,
        "measures": [
          {
            "id": "measure-uuid",
            "internal_sequence": 1,
            "displayed_measure_number": "1"
          }
        ]
      }
    ]
  }
}
```

## GET `/pieces/{piece_id}/score-file`

Returns or redirects to a protected score-file response.

The API must not expose a permanent public URL.

---

# Home

## GET `/home`

Returns the information needed for the Home screen.

### Response

```json
{
  "data": {
    "greeting_name": "Kara",
    "primary_recommendation": {
      "id": "recommendation-uuid",
      "piece_id": "piece-uuid",
      "piece_title": "Cello Suite No. 1",
      "passage_label": "Measures 23–25",
      "focus_category": "intonation",
      "estimated_minutes": 10,
      "reason": "The shift into Measure 24 remained flat across three recordings."
    },
    "teacher_assignments": [],
    "recent_pieces": [],
    "has_music": true
  }
}
```

### Rules

- return no fabricated recommendation when evidence is insufficient
- the client may show a neutral first-practice prompt instead
- this endpoint is a convenience aggregation endpoint

---

# Passage Definitions

## POST `/pieces/{piece_id}/passages`

Creates a passage definition.

### Request: Contiguous Range

```json
{
  "passage_type": "measure_range",
  "display_label": "Measures 23–25",
  "ranges": [
    {
      "movement_id": "uuid",
      "start_measure_id": "uuid",
      "end_measure_id": "uuid"
    }
  ]
}
```

### Request: Non-Contiguous

```json
{
  "passage_type": "non_contiguous_ranges",
  "display_label": "Measures 23–25 and 40–42",
  "ranges": [
    {
      "movement_id": "uuid",
      "start_measure_id": "uuid",
      "end_measure_id": "uuid"
    },
    {
      "movement_id": "uuid",
      "start_measure_id": "uuid",
      "end_measure_id": "uuid"
    }
  ]
}
```

## GET `/pieces/{piece_id}/passages`

Returns saved or recent passage definitions.

## GET `/passages/{passage_id}`

Returns one passage.

## DELETE `/passages/{passage_id}`

Deletes an unused user-created passage definition.

Historical session references must remain understandable.

---

# Practice Sessions

## POST `/practice-sessions`

Starts a new independent session.

### Request

```json
{
  "piece_id": "piece-uuid",
  "instrument_profile_id": "instrument-uuid",
  "practice_source": "musician_choice",
  "initial_passage_id": "passage-uuid",
  "focus_codes": ["intonation"],
  "target_duration_seconds": 1200,
  "goals": [
    {
      "goal_type": "successful_repetitions",
      "description": "Complete 3 successful repetitions",
      "target_value": 3,
      "target_unit": "repetitions",
      "completion_method": "hybrid"
    }
  ]
}
```

### Response

```json
{
  "data": {
    "id": "session-uuid",
    "status": "active",
    "started_at": "2026-07-11T23:00:00Z",
    "current_segment": {
      "id": "segment-uuid",
      "passage_id": "passage-uuid",
      "focus_codes": ["intonation"]
    }
  }
}
```

### Rules

- no setup wizard is required
- omitted optional values receive sensible defaults
- every new session is independent
- completed sessions cannot be resumed

## GET `/practice-sessions/{session_id}`

Returns full workspace state.

### Response Includes

- session timer information
- current segment
- current passage
- focus areas
- goals
- notes
- recordings
- processing statuses

## GET `/practice-sessions`

Returns session history.

### Filters

```text
piece_id
status
started_after
started_before
limit
cursor
```

## PATCH `/practice-sessions/{session_id}`

Updates editable session-level values.

### Example

```json
{
  "target_duration_seconds": 1800,
  "session_notes": "Focus on relaxed shifting."
}
```

## POST `/practice-sessions/{session_id}/complete`

Ends the session.

### Request

```json
{
  "ended_at": "2026-07-11T23:24:00Z"
}
```

### Response

`202 Accepted`

```json
{
  "data": {
    "session_id": "uuid",
    "status": "completed",
    "summary_status": "queued"
  }
}
```

## POST `/practice-sessions/{session_id}/interrupt`

Safely closes an interrupted session.

### Rules

- completing a session closes the active segment
- summary generation may be asynchronous
- completing is idempotent
- a completed session cannot return to active

---

# Practice Segments

## POST `/practice-sessions/{session_id}/segments`

Creates a new segment when passage or focus changes.

### Request

```json
{
  "passage_id": "passage-uuid",
  "focus_codes": ["intonation", "rhythm"],
  "target_tempo_bpm": 60
}
```

### Rules

- close the prior active segment atomically
- create the next sequence number
- do not restart the Practice Session timer

## PATCH `/practice-segments/{segment_id}`

Updates the currently active segment.

Allowed fields may include:

- passage
- focus codes
- target tempo
- notes

Historical completed segments should not be rewritten without explicit correction semantics.

---

# Practice Goals

## POST `/practice-sessions/{session_id}/goals`

Creates a goal.

## PATCH `/practice-goals/{goal_id}`

Updates progress or status.

### Example

```json
{
  "current_value": 2,
  "status": "active"
}
```

## POST `/practice-goals/{goal_id}/complete`

Marks a goal complete.

### Rules

- goals never block continued practice
- completion may be user-confirmed or system-supported
- the API should preserve completion method

---

# Practice Notes

## GET `/pieces/{piece_id}/practice-notes`

Returns active notes.

### Filters

```text
passage_id
session_id
author_type
active
```

## POST `/pieces/{piece_id}/practice-notes`

Creates a note.

### Request

```json
{
  "note_text": "Relax the left thumb during the shift.",
  "passage_id": "uuid",
  "practice_session_id": null
}
```

## PATCH `/practice-notes/{note_id}`

Updates a musician-authored note.

## POST `/practice-notes/{note_id}/archive`

Archives a note.

### Rules

- teacher notes require teacher permission
- application observations should remain distinct from authored notes
- clients should display author type clearly

---

# Recordings

Recording creation should support browser-recorded audio without requiring users to manually upload files through a separate workflow.

## POST `/practice-sessions/{session_id}/recordings`

Creates a recording record before or at upload time.

### Request

```json
{
  "practice_segment_id": "segment-uuid",
  "passage_id": "passage-uuid",
  "client_recording_id": "client-generated-uuid",
  "started_at": "2026-07-11T23:05:00Z"
}
```

### Response

```json
{
  "data": {
    "id": "recording-uuid",
    "recording_number": 3,
    "status": "capturing"
  }
}
```

## POST `/recordings/{recording_id}/audio`

Uploads recorded audio.

### Content Type

```text
multipart/form-data
```

### Fields

```text
file
ended_at
duration_ms
original_mime_type
sample_rate_hz
channel_count
```

### Response

```json
{
  "data": {
    "id": "recording-uuid",
    "status": "saved",
    "analysis_status": "queued"
  }
}
```

### Status

`202 Accepted`

### Rules

- validate session and segment ownership
- preserve neutral recording numbering
- save original audio privately
- normalize audio asynchronously or immediately
- queue analysis after successful persistence
- allow the next recording without waiting

## Alternative Combined Endpoint

A simplified early implementation may use:

```text
POST /practice-sessions/{session_id}/recordings/upload
```

to create metadata and upload the file in one request.

The long-term contract should still preserve idempotency and recording identity.

## GET `/recordings/{recording_id}`

Returns metadata and analysis status.

## GET `/recordings/{recording_id}/audio`

Streams authorized audio.

## GET `/practice-sessions/{session_id}/recordings`

Returns ordered session recordings.

## POST `/recordings/{recording_id}/remove`

Marks a recording removed.

### Request

```json
{
  "reason": "accidental_recording"
}
```

### Rules

- removal is not the same as immediate uncontrolled hard deletion
- removed recordings must not contribute to future analysis
- storage deletion should follow privacy policy
- recording numbers are not reused

---

# Analysis Runs

## POST `/recordings/{recording_id}/analysis-runs`

Queues analysis.

### Request

```json
{
  "engine_version": "0.2.0",
  "configuration_version": "pitch-default-v1",
  "force_reprocess": false
}
```

### Response

```json
{
  "data": {
    "id": "analysis-run-uuid",
    "status": "queued"
  }
}
```

### Status

`202 Accepted`

### Rules

- normal recording upload may automatically create this run
- duplicate requests should be idempotent
- reprocessing creates a new run
- completed runs remain immutable

## GET `/analysis-runs/{analysis_run_id}`

Returns analysis status and component summaries.

### Response

```json
{
  "data": {
    "id": "uuid",
    "recording_id": "uuid",
    "status": "completed",
    "engine_version": "0.2.0",
    "overall_confidence": 0.91,
    "components": {
      "audio_validation": "completed",
      "pitch": "completed",
      "segmentation": "completed",
      "alignment": "not_requested",
      "rhythm": "not_requested",
      "dynamics": "not_requested"
    },
    "warnings": []
  }
}
```

## GET `/recordings/{recording_id}/analysis-runs`

Returns version history.

## POST `/analysis-runs/{analysis_run_id}/prefer`

Marks a completed run as preferred.

### Rules

- update preference atomically
- clear the prior preferred run
- only completed or partially completed runs may be preferred

## POST `/analysis-runs/{analysis_run_id}/retry`

Creates a new run based on the failed run's intended configuration.

---

# Pitch Results

## GET `/analysis-runs/{analysis_run_id}/pitch-observations`

Returns note- or region-level pitch observations.

### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "score_measure_id": "measure-uuid",
      "expected_pitch": "F#3",
      "detected_pitch_center": "F#3",
      "average_cents_deviation": -17.2,
      "pitch_stability_cents": 8.4,
      "vibrato_detected": true,
      "vibrato_width_cents": 31.0,
      "confidence": 0.93,
      "start_ms": 1220,
      "end_ms": 2480
    }
  ]
}
```

### Rules

- raw numeric values are allowed in detailed analysis responses
- the UI should not convert them into a global score
- low-confidence observations must be labeled

---

# Measure Observations

## GET `/analysis-runs/{analysis_run_id}/measure-observations`

Returns interpreted findings.

### Filters

```text
category
minimum_confidence
```

### Response

```json
{
  "data": [
    {
      "id": "uuid",
      "measure_id": "uuid",
      "displayed_measure_number": "18",
      "category": "intonation",
      "observation_code": "pitch_center_flat",
      "confidence_label": "reliable",
      "user_message": "Measure 18: F-sharp centered 17 cents flat.",
      "evidence_count": 1
    }
  ]
}
```

## GET `/pieces/{piece_id}/observations`

Returns aggregated current observations across preferred runs.

### Filters

```text
movement_id
measure_id
category
session_id
recent_only
```

---

# Analysis Diagnostics

## GET `/analysis-runs/{analysis_run_id}/diagnostics`

Returns development-only diagnostics.

This endpoint should be disabled or restricted in production.

Possible response includes:

- pitch trace
- rejected frames
- segmentation boundaries
- alignment path
- preprocessing metadata
- component timing

The API must not expose private file paths or sensitive logs.

---

# Practice Map

## GET `/pieces/{piece_id}/practice-map`

Returns current map states.

### Query Parameters

```text
movement_id
category
```

### Response

```json
{
  "data": {
    "piece_id": "uuid",
    "updated_at": "2026-07-11T23:30:00Z",
    "categories": ["intonation", "rhythm"],
    "states": [
      {
        "measure_id": "uuid",
        "displayed_measure_number": "24",
        "category": "intonation",
        "priority_label": "recommended_focus",
        "explanation": "The shift destination was flat across three recordings.",
        "confidence_label": "reliable"
      }
    ]
  }
}
```

### Rules

- return semantic labels, not only color values
- client decides accessible visual representation
- states should not change while recording is active

## GET `/pieces/{piece_id}/practice-map/history`

Returns historical snapshots.

This may be deferred until snapshot support is implemented.

---

# Recommendations

## GET `/recommendations`

Returns user recommendations.

### Filters

```text
piece_id
status
focus_category
source_type
limit
cursor
```

## GET `/recommendations/{recommendation_id}`

Returns a full explanation.

### Response

```json
{
  "data": {
    "id": "uuid",
    "piece_id": "uuid",
    "passage": {
      "id": "uuid",
      "display_label": "Measures 24–25"
    },
    "focus_category": "intonation",
    "title": "Reinforce the shift into Measure 24",
    "reason": "The F-sharp after the shift averaged 17 cents flat across three recordings.",
    "suggested_method": [
      "Practice the shift separately.",
      "Use a slower tempo.",
      "Remove vibrato for the first three repetitions.",
      "Reconnect Measures 23–26."
    ],
    "estimated_minutes": {
      "minimum": 8,
      "maximum": 10
    },
    "status": "active",
    "evidence": [
      {
        "type": "measure_observation",
        "id": "uuid"
      }
    ]
  }
}
```

## POST `/recommendations/{recommendation_id}/accept`

Marks accepted.

## POST `/recommendations/{recommendation_id}/defer`

### Request

```json
{
  "until": "2026-07-14T12:00:00Z"
}
```

## POST `/recommendations/{recommendation_id}/complete`

Marks completed.

## POST `/recommendations/{recommendation_id}/dismiss`

### Request

```json
{
  "reason": "I am following a different teacher assignment."
}
```

## POST `/recommendations/{recommendation_id}/start-practice`

Creates a new session prepopulated from the recommendation.

### Response

```json
{
  "data": {
    "practice_session_id": "uuid"
  }
}
```

### Rules

- recommendation state never blocks free practice
- evidence remains traceable
- dismissed recommendations may influence future suppression
- completing a recommendation does not imply permanent mastery

---

# Recommendation Generation

## POST `/pieces/{piece_id}/recommendations/generate`

Queues recommendation generation from current preferred evidence.

### Response

`202 Accepted`

This endpoint may be internal-only in production because recommendation generation should normally follow analysis automatically.

## GET `/pieces/{piece_id}/recommendations/primary`

Returns the current primary recommendation for Piece Home.

---

# Session Summaries

## GET `/practice-sessions/{session_id}/summary`

Returns the current summary.

### Response

```json
{
  "data": {
    "id": "uuid",
    "practice_session_id": "uuid",
    "status": "ready",
    "practice_duration_seconds": 1320,
    "recording_count": 6,
    "passages": [
      "Measures 23–25",
      "Measures 40–42"
    ],
    "what_improved": [
      "Rhythm became more consistent in Measures 23–25.",
      "The F-sharp in Measure 24 moved closer to pitch center."
    ],
    "still_needs_attention": [
      "The shift into Measure 24 remained slightly flat."
    ],
    "looking_ahead": {
      "passage_label": "Measures 23–25",
      "reason": "The same tendency appeared in three recordings.",
      "suggested_method": [
        "Practice the shift separately.",
        "Remove vibrato.",
        "Use a slower tempo."
      ],
      "estimated_minutes": {
        "minimum": 8,
        "maximum": 10
      }
    },
    "teacher_reminder": null
  }
}
```

## POST `/practice-sessions/{session_id}/summary/regenerate`

Creates a new summary version after additional analysis completes.

### Rules

- summaries are versioned
- old versions are not silently overwritten
- summary generation must not fabricate missing analysis
- `processing` and `partial` statuses are valid

---

# Progress

## GET `/progress`

Returns musician-level narrative progress.

### Query Parameters

```text
period
```

Example:

```text
period=month
```

### Response

```json
{
  "data": {
    "period": "month",
    "practice_session_count": 14,
    "practice_duration_seconds": 16320,
    "most_improved": {
      "piece_id": "uuid",
      "piece_title": "Cello Suite No. 1",
      "passage_label": "Measures 23–25",
      "message": "Rhythm became more consistent across five sessions."
    },
    "current_focus": {
      "category": "intonation",
      "message": "Fourth-finger notes have tended slightly flat in recent recordings."
    },
    "practice_patterns": [
      "You practiced Cello Suite No. 1 consistently for three weeks."
    ]
  }
}
```

## GET `/pieces/{piece_id}/progress`

Returns piece-level progress.

### Rules

- narrative-first
- charts may be supported with structured trend data
- no daily global score
- comparisons should use compatible analysis versions

---

# Teacher API

Teacher endpoints are future-facing.

## GET `/teacher/relationships`

Returns current teacher connections.

## POST `/teacher/relationships/invite`

Invites or links a teacher.

## DELETE `/teacher/relationships/{relationship_id}`

Ends access.

## GET `/teacher/assignments`

Returns assignments visible to the student.

## POST `/teacher/assignments`

Teacher-only endpoint to create an assignment.

## PATCH `/teacher/assignments/{assignment_id}`

Updates assignment status or details.

## POST `/teacher/assignments/{assignment_id}/start-practice`

Creates a student practice session from an assignment.

### Rules

- teacher permissions must be explicit
- users control sharing
- ended relationships revoke future access
- app recommendations do not rewrite teacher instructions

---

# File Limits

Initial configurable limits should include:

```text
score upload maximum size
recording upload maximum size
maximum recording duration
supported MIME types
```

The API should return:

```text
413 Payload Too Large
```

for oversized uploads.

Limits must be configuration-driven.

---

# Asynchronous Processing

Analysis, parsing, recommendation generation, and summary generation may run asynchronously.

## Status Resources

The client should poll or subscribe to:

- score-source status
- recording status
- analysis-run status
- summary status

## Initial Polling

Example:

```text
GET /api/v1/analysis-runs/{id}
```

## Future Realtime

Possible future mechanisms:

- Server-Sent Events
- WebSockets
- push notifications

The API contract should not require realtime support for Version 0.2.

---

# Event Model

A future event system may emit:

```text
score_source.uploaded
score_source.parsed
recording.saved
recording.removed
analysis_run.queued
analysis_run.completed
analysis_run.failed
practice_map.updated
recommendation.created
recommendation.superseded
practice_session.completed
session_summary.ready
```

Events should contain identifiers rather than raw private content.

---

# API Versioning

Use URL versioning:

```text
/api/v1
```

Breaking changes require a new major API version.

Non-breaking additions may include:

- new optional response fields
- new endpoints
- new enum values when clients tolerate them

Clients should not fail when unknown optional fields are present.

---

# Schema Documentation

FastAPI should expose OpenAPI documentation.

Recommended development routes:

```text
/docs
/redoc
/openapi.json
```

Production exposure may be restricted.

All request and response models should use typed schemas.

---

# Request Validation

Use Pydantic models for:

- required fields
- string lengths
- enum values
- numeric ranges
- UUID formats
- datetime formats
- nested passage ranges
- file metadata
- copyright confirmation

Validation errors should return clear field-level details.

---

# Example Validation Error

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request contains invalid fields.",
    "details": [
      {
        "field": "target_duration_seconds",
        "message": "Value must be greater than zero."
      }
    ],
    "request_id": "uuid"
  }
}
```

---

# Privacy Requirements

The API must:

- scope every private resource to the authenticated user
- avoid public score URLs
- avoid public audio URLs
- avoid exposing storage paths
- avoid returning raw teacher data without permission
- support deletion workflows
- avoid using recordings for training without explicit consent
- record copyright confirmation version and date

---

# Logging

Logs may include:

- request ID
- endpoint
- response status
- processing duration
- authenticated user ID when appropriate
- resource IDs
- analysis version
- error code

Logs must not include:

- raw audio
- full score content
- access tokens
- sensitive personal notes
- storage credentials

---

# Rate Limiting

Future production should rate-limit:

- score uploads
- audio uploads
- analysis submissions
- summary regeneration
- authentication attempts

Local development may disable rate limits.

---

# Caching

Safe cache candidates:

- score outline
- movement list
- static reference data
- completed analysis result
- completed summary version

Do not publicly cache private user content.

Cache keys must include ownership and version context.

---

# Database Transaction Expectations

## Starting a Session

Create session and first segment atomically.

## Changing Passage

Close prior segment and create new segment atomically.

## Finalizing Recording

Save metadata only after file persistence succeeds.

## Preferring Analysis

Switch preferred run atomically.

## Activating Score Source

Clear prior active source and activate new source atomically.

## Completing Session

Close segment and session atomically.

---

# Initial Implementation Priorities

## Already Implemented or Foundation

- piece upload
- piece metadata
- score storage
- MusicXML and MXL parsing
- piece library
- browser recording and replay

## Next API Work

Implement:

```text
POST /practice-sessions
GET /practice-sessions/{id}
POST /practice-sessions/{id}/recordings
POST /recordings/{id}/audio
GET /recordings/{id}
POST /recordings/{id}/analysis-runs
GET /analysis-runs/{id}
GET /analysis-runs/{id}/pitch-observations
POST /practice-sessions/{id}/complete
GET /practice-sessions/{id}/summary
```

This is the minimum useful API path for Version 0.2.

---

# Version 0.2 Minimum API

The first intonation milestone requires:

## Pieces

```text
GET /pieces
GET /pieces/{piece_id}
```

## Sessions

```text
POST /practice-sessions
GET /practice-sessions/{session_id}
POST /practice-sessions/{session_id}/complete
```

## Recordings

```text
POST /practice-sessions/{session_id}/recordings
POST /recordings/{recording_id}/audio
GET /recordings/{recording_id}
GET /recordings/{recording_id}/audio
```

## Analysis

```text
POST /recordings/{recording_id}/analysis-runs
GET /analysis-runs/{analysis_run_id}
GET /analysis-runs/{analysis_run_id}/pitch-observations
```

## Summary

```text
GET /practice-sessions/{session_id}/summary
```

---

# Version 0.2 Acceptance Flow

```text
1. GET /pieces
2. POST /practice-sessions
3. POST /practice-sessions/{session_id}/recordings
4. POST /recordings/{recording_id}/audio
5. GET /analysis-runs/{analysis_run_id}
6. GET /analysis-runs/{analysis_run_id}/pitch-observations
7. POST /practice-sessions/{session_id}/complete
8. GET /practice-sessions/{session_id}/summary
```

Expected user-facing result:

```text
Detected note: A3
Pitch center: 12 cents flat
Vibrato detected
Confidence: sufficient
```

---

# Example End-to-End Request

## Start Session

```http
POST /api/v1/practice-sessions
Content-Type: application/json

{
  "piece_id": "piece-uuid",
  "practice_source": "musician_choice",
  "focus_codes": ["intonation"]
}
```

## Create Recording

```http
POST /api/v1/practice-sessions/session-uuid/recordings
Content-Type: application/json

{
  "practice_segment_id": "segment-uuid",
  "client_recording_id": "client-uuid",
  "started_at": "2026-07-11T23:05:00Z"
}
```

## Upload Audio

```http
POST /api/v1/recordings/recording-uuid/audio
Content-Type: multipart/form-data
```

## Poll Analysis

```http
GET /api/v1/analysis-runs/analysis-run-uuid
```

## Read Pitch Result

```http
GET /api/v1/analysis-runs/analysis-run-uuid/pitch-observations
```

---

# Open API Decisions

The following require implementation decisions:

1. Whether recording creation and upload should remain separate endpoints.
2. Whether large uploads should use presigned object-storage URLs.
3. Whether polling is sufficient through Version 0.3.
4. How much raw pitch-trace data should be returned to the frontend.
5. Whether analysis component results should use separate endpoints or one aggregate response.
6. Whether passage definitions should be created independently or inline with session updates.
7. How archived and deleted resources should appear in history endpoints.
8. Whether recommendation evidence should be exposed by default or only in details.
9. How teacher permissions should be represented.
10. Whether summary regeneration should be automatic only.
11. What upload size and duration limits are appropriate.
12. Whether idempotency records should be stored in the database or application cache.
13. How long failed analysis resources should remain queryable.
14. Whether OpenAPI documentation should be publicly accessible in beta.
15. How API compatibility tests should be maintained.

---

# Recommended Implementation Sequence

## Phase 1: Session and Recording API

Implement:

- create session
- retrieve session
- update current segment
- create recording
- upload audio
- replay audio
- complete session

## Phase 2: Analysis API

Implement:

- queue analysis
- poll status
- retrieve pitch observations
- retrieve measure observations
- retry failed run

## Phase 3: Practice Guidance API

Implement:

- practice map
- recommendations
- recommendation actions
- session summaries
- home aggregation

## Phase 4: Progress API

Implement:

- piece progress
- musician progress
- trend narratives
- compatible-version comparisons

## Phase 5: Teacher API

Implement:

- relationships
- assignments
- permissions
- shared notes
- student-controlled access

---

# Summary

The primary API flow is:

```text
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
Practice Map and Recommendation
  ↓
Session Summary
```

The API should preserve four distinctions:

1. user intent
2. recorded evidence
3. analytical interpretation
4. suggested action

This separation keeps the system testable, explainable, and respectful of the musician's judgment.
