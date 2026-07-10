# Product Requirements

## 1. Product definition

Cello Practice AI is a score-aware cello performance analysis application. Its
initial target user is a solo cello student who wants concrete feedback about a
recorded passage in relation to an uploaded MusicXML score.

The core experience is score upload, direct microphone recording, recording
playback, and progressively richer score-referenced analysis. General practice
planning, timers, journaling, and goal management are not the primary product.

This document defines intended behavior. It does not claim that any analysis is
implemented or validated.

## 2. Primary user

The first user is a solo cello student practicing an individual part. The
initial product should work without requiring a teacher, accompanist, ensemble,
or manually prepared audio file.

## 3. Core user journey

1. The student uploads a MusicXML file.
2. The application validates the file and displays basic score information.
3. The student selects the relevant passage when selection is supported.
4. The student grants microphone access and records through the device.
5. The application saves the recording and allows immediate replay.
6. In analysis-enabled versions, the application processes the recording and
   aligns it to the uploaded score.
7. The application presents supported observations at note and measure level.
8. Across recordings, the application identifies repeated mistakes and
   recommends specific measures to isolate.

Manual WAV upload is not required for the core experience. Importing external
audio is outside the initial scope.

## 4. Functional requirements

### 4.1 Score handling

- Accept MusicXML uploads in documented supported forms.
- Validate format, size, and parseability.
- Extract basic score information such as title when present, part names,
  measures, time signatures, key signatures, tempo markings, and notated notes.
- Require the student to choose the solo cello part if it cannot be selected
  reliably.
- Preserve a stable reference between analysis results and score locations.
- Surface unsupported notation or ambiguous score data clearly.

### 4.2 Recording and playback

- Request microphone permission only when the student initiates recording.
- Record directly through a supported device microphone.
- Show clear recording, stopped, saved, and failed states.
- Save the recording with its associated score and passage context.
- Replay the saved recording using standard playback controls.
- Permit deletion according to the documented retention policy.
- Do not require manual WAV upload.

### 4.3 Pitch and intonation analysis

Later versions should:

- detect performed pitch over time;
- convert frequency estimates to musical note names;
- express intonation as cents sharp or flat from the relevant reference pitch;
- handle sustained notes without treating every analysis frame as a new note;
- estimate the center of vibrato rather than interpreting normal oscillation as
  alternating intonation mistakes; and
- distinguish insufficient audio from a valid measurement.

Reference tuning and temperament assumptions must be visible and configurable
when appropriate.

### 4.4 Score alignment and recommendations

Later versions should:

- align performed note events to MusicXML notes and measures;
- identify incorrect notes and supported intonation problems;
- highlight measures needing work;
- provide a basic, explainable score without presenting it as a complete measure
  of musical quality;
- track repeated supported mistakes across comparable recordings; and
- recommend specific measures to isolate, with evidence linking the
  recommendation to observed attempts.

### 4.5 Rhythm and timing analysis

Later versions should analyze:

- early and late entrances;
- note duration;
- local timing and tempo drift; and
- deviations while allowing reasonable expressive timing.

The product must avoid treating every expressive deviation as an error.

### 4.6 Dynamic contour analysis

Later versions should support:

- dynamic contour visualization;
- crescendo and diminuendo analysis;
- dynamic contrast observations; and
- phrase-shape observations.

Results must account for the limits of microphone placement, device gain,
automatic gain control, room acoustics, and notation ambiguity.

## 5. Analysis integrity requirements

- Never create or display fake analysis results.
- Use explicit queued, processing, completed, uncertain, unsupported, failed,
  and deleted states.
- Attach analysis method and version to every result.
- Preserve units, reference assumptions, confidence or quality information, and
  score location.
- Avoid numerical scoring when alignment or signal quality is inadequate.
- Make it possible to distinguish measured observations from recommendations.
- Document evaluation datasets, thresholds, and known failure modes before an
  analysis feature is presented as reliable.

## 6. Non-functional requirements

- **Privacy:** Scores and recordings are private by default.
- **Security:** Authorize every score, recording, and result operation; protect
  data in transit and at rest using platform-appropriate controls.
- **Accessibility:** Target WCAG 2.2 AA for user-facing functionality.
- **Reliability:** Do not lose a successfully saved recording after reporting it
  as saved.
- **Traceability:** Link observations to the recording, score version, measure,
  notated event, and analysis version where possible.
- **Performance:** Recording controls must respond promptly; asynchronous
  analysis must expose progress without blocking playback.
- **Observability:** Operational logs must not contain raw audio, full score
  contents, credentials, or fabricated fallbacks.

## 7. Out of scope for the initial release

- Manual WAV upload as a required workflow.
- Ensemble, accompaniment, or multi-instrument analysis.
- Automatic grading of overall musicianship.
- Medical or injury-prevention claims.
- Replacement of a cello teacher.
- Training models on user recordings without separate informed consent.
- Practice timers, journals, and general goal management as primary features.

## 8. First successful milestone

A cellist records a simple passage and the application correctly identifies
notes that are consistently sharp or flat.

Milestone validation requires defined test passages, tuning assumptions,
recording conditions, ground truth, repeat-trial criteria, and acceptable error
thresholds. No milestone result is claimed until that evaluation is completed.

## 9. Open questions

- Which MusicXML versions and notation constructs must be supported first?
- How will the student select a passage and establish the intended start point?
- What reference pitch and temperament defaults should be used?
- Which browsers and devices provide the minimum viable recording quality?
- How many comparable attempts establish a repeated mistake?
- How should confidence and partial alignment be explained to a student?
- What retention defaults should apply to scores, recordings, and results?
