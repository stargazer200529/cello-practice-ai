# Architecture

## 1. Status

This document describes a proposed architecture for planning purposes. No
application components or analysis pipeline are implemented yet. Technology
choices remain open until product requirements and delivery constraints are
validated.

## 2. Architectural goals

- Keep core practice planning usable independently of audio analysis.
- Isolate private recordings from routine application data and logs.
- Support asynchronous analysis without implying that pending or failed work
  succeeded.
- Make analysis outputs traceable to a method and version.
- Allow components to evolve without requiring a premature distributed system.
- Support deletion across source recordings, derived artifacts, and metadata.

## 3. Proposed system context

The system may contain the following logical boundaries:

1. **Client application** for goals, session plans, timers, notes, history, and
   explicit recording controls.
2. **Application API** for authenticated operations and product rules.
3. **Primary data store** for users, goals, sessions, consent records, and
   analysis metadata.
4. **Private object storage** for recordings and derived media artifacts.
5. **Analysis worker** for asynchronous, versioned audio processing.
6. **Job queue** connecting analysis requests to workers with retry and failure
   handling.
7. **Operational telemetry** for service health, excluding raw recordings and
   sensitive note content by default.

These are logical responsibilities, not a requirement to deploy seven separate
services. A modular monolith plus a background worker is the preferred starting
shape unless scale or isolation requirements demonstrate otherwise.

## 4. Component responsibilities

### Client application

- Present practice planning and session workflows.
- Make offline or interrupted-session behavior understandable.
- Request microphone or file access only in context.
- Clearly label user-entered information, generated suggestions, and computed
  observations.
- Provide export and deletion controls.

### Application API

- Authenticate users and authorize access to each resource.
- Validate session, goal, and recording metadata.
- Issue short-lived upload and download permissions when object storage is used.
- Create analysis jobs and expose explicit queued, running, completed, failed,
  and deleted states.
- Coordinate user data export and deletion.

### Analysis worker

- Consume immutable job inputs.
- Validate media before processing.
- Produce structured observations with method version, units, confidence or
  quality indicators, and failure details.
- Avoid converting a failed or unsupported measurement into a placeholder
  success value.
- Keep experimentation separate from production-facing analysis versions.

## 5. Conceptual data model

- **User:** identity, preferences, and privacy settings.
- **PracticeGoal:** user-defined objective, status, and optional associations.
- **RepertoireItem:** a user-defined piece, movement, excerpt, exercise, or
  technique label.
- **PracticeSession:** planned and actual timing plus lifecycle state.
- **SessionActivity:** ordered unit within a session plan.
- **Reflection:** user-authored notes and next steps.
- **Recording:** ownership, storage reference, retention choice, and capture
  metadata.
- **AnalysisJob:** processing state, input reference, method version, and error
  category.
- **AnalysisResult:** structured observations and uncertainty information.
- **ConsentRecord:** the user's decision for an optional use of recording data.

Identifiers should be non-guessable. Ownership must be checked server-side for
every user resource.

## 6. Key data flows

### Save a practice session

1. The client creates or updates an in-progress session.
2. The API validates ownership and lifecycle transitions.
3. Structured session data and reflections are stored.
4. The client receives the authoritative saved state.

### Analyze a recording

1. The user explicitly initiates capture or upload.
2. The API records the user's storage and processing choices.
3. The recording is stored privately and an analysis job is queued.
4. A worker validates and processes the recording using a versioned method.
5. The result or failure state is stored without overwriting the source record.
6. The client displays the outcome and relevant limitations.

### Delete recording data

1. The user requests deletion.
2. The API revokes access and marks the resource unavailable.
3. Source and derived objects are deleted according to the documented process.
4. Related results are deleted or irreversibly de-identified as policy permits.
5. Completion or an actionable failure is surfaced to the user.

Backup expiration and legal retention constraints must be documented before
launch.

## 7. Security and privacy baseline

- Use established identity and session-management libraries.
- Enforce authorization at the API boundary rather than relying on client UI.
- Encrypt transport and use managed encryption for stored data.
- Separate object identifiers from publicly accessible URLs.
- Use short-lived, narrowly scoped access for recording transfer.
- Exclude recordings, access tokens, and free-form practice notes from normal
  logs.
- Audit administrative access and sensitive data operations.
- Document retention, export, deletion, and incident-response procedures.
- Perform threat modeling before enabling recording uploads in production.

## 8. Analysis integrity

Every production-facing result should include enough metadata to determine:

- the analysis method and version;
- when the analysis ran;
- the units and interpretation of each value;
- whether input quality was sufficient;
- the confidence or known limitations, where applicable; and
- whether the result was superseded or invalidated.

Model or algorithm evaluation datasets, acceptance thresholds, and known failure
modes must be documented before an analysis feature is represented as reliable.

## 9. Deployment approach

The first implementation should favor a small number of deployable units:

- a client;
- an application/API service; and
- a background worker introduced only when asynchronous processing is needed.

Managed relational storage, object storage, and queueing are reasonable default
categories, but providers and frameworks are intentionally undecided. Separate
development, test, and production environments should use independent secrets
and data.

## 10. Quality strategy

- Unit tests for product rules and state transitions.
- Integration tests for persistence, authorization, upload, and deletion flows.
- Contract tests between the client, API, and worker.
- End-to-end tests for critical practice and privacy journeys.
- Evaluation suites for each audio method before product exposure.
- Accessibility, security, and recovery checks before release.

## 11. Decisions still required

- Delivery platform and client framework.
- Hosting environment and regional requirements.
- Identity and account model.
- Local-first versus server-synchronized data behavior.
- Recording formats, limits, and retention defaults.
- Initial analysis methods and their validation standards.
- Export schema and deletion service-level objectives.

Significant decisions should be recorded as architecture decision records when
implementation begins.
