# Version Roadmap

## 1. Purpose

This roadmap sequences the score-aware cello performance analysis product from
recording foundations through pitch, score alignment, rhythm, and dynamics.
Versions describe intended scope, not completed work or committed dates.

## 2. Version 0.1: Score and recording foundation

### Scope

- User interface for a solo cello student.
- MusicXML upload.
- Basic score information.
- Direct device-microphone recording.
- Save the recording with its score context.
- Replay the saved recording.

Manual WAV upload is not required. Performance analysis is not included in this
version, and the interface must not display placeholder analysis results.

### Exit criteria

- A supported MusicXML file can be validated and its basic information shown.
- A student can grant microphone access, record, stop, and save a passage.
- A confirmed saved recording can be replayed and deleted.
- Unsupported score, permission, recording, storage, and playback failures are
  explicit and recoverable.
- Scores and recordings are private and authorized by ownership.

## 3. Version 0.2: Pitch and intonation foundation

### Scope

- Pitch detection.
- Frequency-to-note conversion.
- Cents sharp/flat calculation.
- Sustained-note handling.
- Vibrato-center estimation.

### Exit criteria

- Evaluation defines supported pitch range, audio conditions, reference tuning,
  ground truth, and error thresholds.
- Sustained notes produce stable note-level observations rather than an event per
  analysis frame.
- Vibrato-center estimation is evaluated separately from instantaneous pitch.
- Low-quality or unsupported audio produces no fabricated intonation result.

### First successful milestone

A cellist records a simple passage and the application correctly identifies
notes that are consistently sharp or flat.

Success must be demonstrated against predefined passages and ground truth across
repeated trials. This roadmap does not claim that the milestone has been met.

## 4. Version 0.3: Score alignment and basic scoring

### Scope

- Align performed notes to MusicXML notes.
- Detect incorrect notes and supported intonation problems.
- Highlight measures needing work.
- Provide basic, explainable scoring.
- Identify repeated supported mistakes across comparable recordings.
- Recommend specific measures to isolate.

### Exit criteria

- Alignment accuracy is evaluated for the supported notation and performance
  conditions.
- Incorrect-note and intonation observations link to notated events and measures.
- Partial, ambiguous, and failed alignment states are visible.
- Basic scores expose their inputs and do not imply a complete assessment of
  musical quality.
- Repeated-mistake rules use documented evidence and minimum attempt counts.
- Measure recommendations link to the observations that support them.

## 5. Version 0.4: Rhythm and timing analysis

### Scope

- Rhythm and timing analysis.
- Early and late entrance detection.
- Note-duration comparison.
- Tempo-drift analysis.
- Allowance for reasonable expressive timing.

### Exit criteria

- Timing is compared using score tempo, meter, and alignment context.
- Tolerances distinguish supported errors from reasonable expressive variation.
- Early/late, duration, and drift observations include units and reference points.
- Rubato, pauses, ties, rests, and tempo changes have documented behavior for the
  supported notation subset.
- Insufficient alignment prevents unsupported rhythm conclusions.

## 6. Version 0.5: Dynamic contour and phrase shape

### Scope

- Dynamic contour visualization.
- Crescendo and diminuendo analysis.
- Dynamic contrast observations.
- Phrase-shape observations.

### Exit criteria

- The system distinguishes relative contour from absolute sound level.
- Evaluation addresses microphone placement, device gain, automatic gain
  control, and room effects.
- Crescendo, diminuendo, and contrast observations link to score locations when
  notation supports the comparison.
- Phrase-shape language remains observational and avoids unsupported judgments.
- Unreliable amplitude input produces an explicit unavailable or uncertain state.

## 7. Cross-version requirements

Every version must:

1. keep MusicXML and recordings private by default;
2. preserve score, recording, and analysis-version traceability;
3. expose processing, unsupported, uncertain, failed, and deleted states;
4. avoid fake analysis results and placeholder measurements;
5. test accessibility and critical user journeys;
6. document supported devices, notation, and known failure modes; and
7. validate analysis claims before presenting them as reliable.

## 8. Release governance

Before advancing a version:

1. Define ground truth, evaluation data, and acceptance thresholds for new
   analysis capabilities.
2. Review privacy, security, and retention impacts.
3. Test layer contracts between the React/Next.js UI, FastAPI backend,
   audio-processing layer, and music-analysis/scoring layer.
4. Review error messages and user-facing limitations with solo cello students.
5. Record unresolved risks and constrain the release accordingly.

The roadmap should change when evidence changes priorities. It must not be used
to imply that a planned capability or result already exists.
