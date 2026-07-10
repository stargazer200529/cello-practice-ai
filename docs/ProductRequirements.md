# Product Requirements

## 1. Purpose

Cello Practice AI is intended to help cellists practice with more structure and
reflection. It should support a musician's judgment rather than position
automated feedback as an authoritative evaluation of artistry or technique.

This document defines the proposed product direction. It does not claim that
the features or outcomes below have been implemented or validated.

## 2. Target users

### Primary users

- Student cellists who want help organizing independent practice.
- Adult learners who need a repeatable practice routine.
- Advancing players who want a searchable record of goals and observations.

### Secondary users

- Teachers who may review practice summaries shared intentionally by a student.

Teachers, institutions, and parents are not assumed to have automatic access to
a musician's data.

## 3. User needs

Users need to be able to:

- decide what to work on before a session;
- divide limited practice time among meaningful activities;
- record what happened without interrupting practice excessively;
- revisit prior goals and observations;
- distinguish measured signals from suggestions and subjective interpretation;
- understand when automated feedback is uncertain or unavailable; and
- control the storage, sharing, export, and deletion of personal recordings.

## 4. Product principles

1. **Musician agency:** The user chooses goals and decides whether advice is
   useful.
2. **Honest feedback:** The product must not present estimates as facts or invent
   measurements when analysis is unavailable.
3. **Practice first:** Interaction should minimize distraction during a session.
4. **Privacy by default:** Recordings and notes are private unless the user
   explicitly shares them.
5. **Accessible foundations:** Core planning and reflection should not depend on
   advanced analysis features.
6. **Incremental validation:** Audio features should be released only with
   documented limitations and appropriate evaluation.

## 5. Proposed core journeys

### Plan a session

1. The user selects or creates practice goals.
2. The user sets the available duration.
3. The product proposes an editable sequence of activities.
4. The user starts the session after reviewing the plan.

### Run and reflect on a session

1. The product displays the current activity and optional timer.
2. The user can pause, skip, extend, or annotate an activity.
3. At the end, the user records a short reflection and next step.
4. The product saves a session summary.

### Review progress

1. The user filters prior sessions by date, piece, technique, or goal.
2. The product displays recorded practice history and user-authored notes.
3. Any future computed metrics identify their source, confidence, and limits.

### Request audio-assisted feedback (later phase)

1. The user explicitly records or uploads a sample.
2. The product explains what will be analyzed and how the recording is handled.
3. The product returns supported observations with uncertainty indicators.
4. The user may reject, annotate, or delete the result and recording.

## 6. Functional requirements

### Initial product foundation

- Create, edit, complete, and archive practice goals.
- Build an editable session plan with a total duration.
- Start, pause, resume, and finish a practice session.
- Add notes and a post-session reflection.
- Review session history.
- Associate sessions with user-defined pieces, excerpts, or techniques.
- Export and delete user data.

### Later audio capabilities

- Capture or upload audio only after explicit user action.
- Preserve the original recording only according to the user's storage choice.
- Track analysis status and handle failure without fabricating a result.
- Show the analysis method or metric category in plain language.
- Display confidence or a clear unavailable/uncertain state.
- Allow users to delete recordings and derived results.

## 7. Non-functional requirements

- **Privacy:** Apply least-privilege access and avoid public recordings by
  default.
- **Security:** Encrypt network traffic and protect stored credentials and user
  data using platform-appropriate controls.
- **Accessibility:** Target WCAG 2.2 AA for user-facing interfaces.
- **Reliability:** Preserve session notes during transient failures and make
  incomplete analysis states explicit.
- **Performance:** Keep common planning and note-taking interactions responsive;
  measurable targets will be set after a delivery platform is selected.
- **Portability:** Provide a documented export format for user-created data.
- **Observability:** Record operational failures without placing private musical
  content in routine logs.

## 8. Out of scope for the initial release

- Claims of diagnosing physical technique or preventing injury.
- Automatic grading of musical quality.
- Replacement of a teacher or medical professional.
- Public social feeds, rankings, or competitive leaderboards.
- Training models on user recordings without separate, informed consent.
- Real-time accompaniment or score-following unless separately specified and
  validated.

## 9. Success criteria to validate

The project should establish baseline research before setting numeric targets.
Candidate measures include:

- users can create and complete a practice plan without assistance;
- users find session history useful when deciding what to practice next;
- users understand the distinction between their notes and computed feedback;
- users can locate recording privacy and deletion controls; and
- the system never displays a successful analysis when processing failed.

No results are reported here because user research and product testing have not
yet been conducted.

## 10. Open questions

- Which cellist experience level should the first release prioritize?
- Is the first delivery target web, mobile, or both?
- Should accounts be required for a local-first initial experience?
- Which practice taxonomies are useful without becoming prescriptive?
- What minimum evidence is required before releasing each audio metric?
- What retention defaults best balance convenience and privacy?
