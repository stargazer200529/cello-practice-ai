# Analysis Engine

## Purpose

This document defines the functional architecture and analytical rules for the **Practice with Purpose** music-analysis engine.

The engine converts a recorded performance and a parsed score into structured observations that can support:

- intonation feedback
- rhythm feedback
- timing feedback
- dynamic-contour feedback
- repeated-pattern detection
- practice-map updates
- recommendations
- session summaries

The analysis engine measures what can be measured reliably.

It does not judge artistic interpretation, replace a teacher, or assign a single global performance grade.

---

# Analysis Philosophy

The engine must answer five questions:

1. **What happened?**
2. **Where did it happen?**
3. **How significant was it?**
4. **Did it happen repeatedly?**
5. **What should the musician practice next?**

The engine should produce specific observations such as:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

It should avoid vague statements such as:

> Your intonation was poor.

The engine should preserve the difference between:

- raw measurements
- interpreted observations
- long-term patterns
- practice recommendations

These layers must not be collapsed into one opaque score.

---

# Scope

## Version 0.2

Primary goal:

- detect pitch over time
- estimate note pitch center
- convert frequency to note name
- calculate cents sharp or flat
- handle sustained notes
- reduce false penalties from cello vibrato
- store versioned analysis results

## Version 0.3

Add score comparison:

- align performance with MusicXML notes
- identify expected notes
- detect incorrect notes
- detect intonation problems by note and measure
- aggregate repeated tendencies
- create measure-level observations
- update a basic practice map

## Version 0.4

Add rhythm and timing:

- compare performed onset with expected onset
- compare performed duration with written duration
- identify early and late entrances
- identify tempo drift
- identify repeated rhythm problems
- allow reasonable expressive timing

## Version 0.5

Add dynamics:

- measure relative intensity
- identify dynamic contour
- detect crescendos and diminuendos
- compare broad contour with written dynamics
- avoid judging artistic interpretation as objectively wrong

---

# Non-Goals

The initial analysis engine will not attempt to:

- evaluate tone quality as good or bad
- identify emotional expression
- determine whether an interpretation is artistically correct
- assess posture or bow hold from audio alone
- analyze ensembles
- analyze accompaniment
- infer physical technique without supporting evidence
- provide a single overall score
- penalize normal vibrato
- require mechanical timing
- replace teacher judgment

---

# High-Level Pipeline

```text
Recorded Audio
      ↓
Audio Validation
      ↓
Preprocessing
      ↓
Signal Quality Assessment
      ↓
Feature Extraction
      ↓
Pitch Tracking
      ↓
Note Segmentation
      ↓
Score Alignment
      ↓
Category Analysis
      ├── Intonation
      ├── Rhythm
      ├── Timing
      ├── Tempo
      └── Dynamics
      ↓
Measure Observations
      ↓
Repeated Pattern Detection
      ↓
Practice Map Inputs
      ↓
Recommendation Inputs
```

Each stage should produce explicit outputs and confidence values.

A downstream stage should not invent certainty when an upstream stage is unreliable.

---

# Architectural Components

The analysis engine should be separated into the following modules:

```text
analysis/
├── audio_io/
├── preprocessing/
├── quality/
├── pitch/
├── segmentation/
├── score/
├── alignment/
├── intonation/
├── rhythm/
├── timing/
├── dynamics/
├── aggregation/
├── observations/
├── confidence/
└── orchestration/
```

The precise folder structure may differ, but responsibilities should remain separated.

---

# Analysis Run

Every execution of the engine creates an **Analysis Run**.

An Analysis Run records:

- recording identifier
- score source identifier
- engine version
- configuration version
- start time
- completion time
- component statuses
- confidence
- diagnostics
- failure information

Completed Analysis Runs are immutable.

Reprocessing the same recording creates a new Analysis Run.

This is necessary because:

- algorithms will improve
- score parsing may change
- configuration may change
- thresholds may change
- new analysis categories may be added

One completed run may be marked as the preferred current result.

---

# Input Requirements

## Recording Input

The engine accepts an audio recording associated with:

- one user
- one piece
- one practice session
- one practice segment
- one intended passage when known

Preferred normalized analysis format:

- mono
- uncompressed PCM
- consistent sample rate
- floating-point or signed integer samples
- known duration

The browser may record in another format.

The backend may convert that file into the normalized format before analysis.

## Score Input

For score comparison, the engine accepts parsed score data containing:

- movements
- measures
- note events
- rests
- written pitch
- onset position
- duration
- ties
- voices
- tempo markings
- dynamics when available

The engine must know which score source and parse version were used.

## Session Context

Optional context may include:

- selected passage
- selected focus
- target tempo
- practice goal
- instrument profile
- pitch reference
- teacher assignment

Context affects interpretation and emphasis.

It must not alter raw measurements.

---

# Audio Validation

Before analysis begins, validate the recording.

## Required Checks

- file exists
- file can be decoded
- duration is greater than minimum threshold
- sample rate is supported
- audio contains non-silent content
- signal is not fully clipped
- channel configuration is supported
- file is not obviously corrupted

## Invalid Recording Examples

- zero-byte file
- silent recording
- microphone permission failure
- recording shorter than the configured minimum
- undecodable format
- severe clipping across most of the recording

## Output

```text
AudioValidationResult
├── valid
├── duration
├── sample_rate
├── channel_count
├── peak_level
├── clipping_ratio
├── silence_ratio
├── warnings
└── failure_reason
```

Invalid recordings should not proceed into full analysis.

They may remain available for replay if technically possible, but they should be marked as unusable for feedback.

---

# Preprocessing

Preprocessing should prepare audio for consistent analysis without changing musical meaning.

## Initial Steps

- decode audio
- convert to mono
- resample if necessary
- remove DC offset
- normalize analysis level conservatively
- trim only obvious leading and trailing silence
- preserve original timing offsets
- optionally apply light noise reduction
- optionally apply a cello-relevant frequency filter

## Rules

- Do not aggressively denoise the signal.
- Do not use preprocessing that distorts vibrato.
- Do not compress dynamics before dynamic analysis.
- Preserve an unmodified normalized copy for reproducibility.
- Record all preprocessing parameters in the Analysis Run configuration.

Different analysis categories may use different preprocessing branches.

Example:

```text
Normalized Audio
├── Pitch Branch
│   └── light filtering
├── Rhythm Branch
│   └── onset-preserving processing
└── Dynamics Branch
    └── no amplitude normalization after calibration
```

---

# Signal Quality Assessment

The engine should estimate whether the recording is suitable for analysis.

## Quality Factors

- clipping
- background noise
- room reverberation
- microphone distance
- signal-to-noise ratio
- competing sounds
- low recording level
- unstable device gain
- insufficient duration

## Output

```text
SignalQualityResult
├── overall_quality
├── pitch_suitability
├── rhythm_suitability
├── dynamics_suitability
├── warnings
└── confidence_limits
```

A recording may be suitable for one category and unsuitable for another.

Example:

> Pitch analysis available. Dynamic comparison unavailable because automatic microphone gain changed during the recording.

This is preferable to failing the entire analysis.

---

# Instrument Profile

The engine should use an instrument profile.

For Version 1.0, the default profile is solo cello.

## Cello Profile

Expected practical range:

```text
C2 through upper treble register
```

Default open strings:

```text
C2
G2
D3
A3
```

Default pitch reference:

```text
A4 = 440 Hz
```

The profile may define:

- expected frequency range
- open strings
- common clefs
- likely overtone behavior
- expected monophonic texture
- pitch-tracker parameters
- onset thresholds
- vibrato expectations

Instrument-specific assumptions should remain isolated in the profile.

---

# Pitch Tracking

Pitch tracking estimates the fundamental frequency over time.

## Requirements

The pitch tracker should:

- support the cello frequency range
- work with sustained bowed tones
- tolerate vibrato
- reduce octave errors
- identify unvoiced regions
- output confidence
- preserve time resolution sufficient for note segmentation

## Frame-Level Output

```text
PitchFrame
├── timestamp
├── frequency_hz
├── midi_pitch
├── note_name
├── cents_from_nearest_equal_tempered_note
├── voiced
└── confidence
```

## Frequency to MIDI Pitch

```text
midi = 69 + 12 × log2(frequency / reference_frequency)
```

For standard tuning:

```text
reference_frequency = 440 Hz
```

## Cents Difference

For a detected frequency and expected frequency:

```text
cents = 1200 × log2(detected_frequency / expected_frequency)
```

Positive values are sharp.

Negative values are flat.

## Pitch-Tracking Risks

The engine must detect or mitigate:

- octave doubling
- octave halving
- strong overtones
- bow noise
- attacks with unstable pitch
- open-string resonance
- double stops
- environmental sound
- low-frequency rumble

Version 1.0 assumes primarily monophonic solo cello.

Double stops may be marked unsupported or low confidence.

---

# Pitch Smoothing

Raw pitch frames are not suitable for direct feedback.

The engine should apply conservative smoothing.

## Goals

- remove isolated outliers
- preserve genuine pitch movement
- preserve vibrato shape
- avoid flattening expressive slides
- avoid shifting note boundaries

## Suggested Strategy

1. Remove frames below confidence threshold.
2. Correct isolated octave jumps when neighboring evidence is strong.
3. Apply a short median filter.
4. Preserve the unsmoothed trace for diagnostics.
5. Use smoothed frames for segmentation and pitch-center estimation.

Smoothing parameters must be versioned.

---

# Vibrato Handling

Normal cello vibrato must not be penalized.

The engine should estimate the center of the oscillation rather than evaluating each instantaneous frame against the written pitch.

## Vibrato Characteristics

A sustained note may contain:

- periodic pitch movement
- asymmetric oscillation
- changing width
- changing rate
- expressive drift
- unstable attack
- release motion

## Pitch Center

The pitch center should be estimated from the stable portion of the note.

Possible robust estimators include:

- weighted median
- trimmed mean
- modeled oscillation center
- low-frequency trend estimate

The estimator should reduce the influence of:

- note attack
- note release
- portamento
- isolated tracking errors
- low-confidence frames

## Vibrato Outputs

```text
VibratoEstimate
├── pitch_center
├── width_cents
├── rate_hz
├── regularity
├── stable_region
└── confidence
```

## Rules

- Vibrato width is not itself an error.
- Vibrato rate is not itself an error.
- The engine may report instability only when the pitch center or note control is measurably inconsistent.
- The user-facing observation should distinguish:
  - pitch center
  - stability
  - vibrato behavior

Example:

> The note centered 14 cents flat. Vibrato width was normal and was not counted as an intonation error.

---

# Note Segmentation

Note segmentation identifies performed note regions.

## Inputs

- pitch trace
- amplitude envelope
- onset features
- silence regions
- expected score when available

## Segment Boundaries

A boundary may be caused by:

- onset
- silence
- pitch change
- bow rearticulation
- score expectation
- duration change
- strong confidence drop

## Output

```text
PerformedNote
├── start_time
├── end_time
├── pitch_center
├── pitch_trace
├── amplitude_summary
├── onset_strength
├── confidence
└── segmentation_reason
```

## Rules

- Sustained notes should remain one segment despite vibrato.
- Tied notes may remain one performed segment.
- Rearticulated same-pitch notes should be separable when evidence permits.
- Low-confidence segmentation should be marked explicitly.
- Segmentation should not depend entirely on score alignment.

---

# Score Parsing Contract

The analysis engine should not parse raw MusicXML directly during every run.

It should consume a normalized score representation from the score-processing layer.

## Required Note Data

```text
ScoreNote
├── stable_note_id
├── movement_id
├── measure_id
├── voice
├── staff
├── onset_in_measure
├── duration
├── written_pitch
├── sounding_pitch
├── tie_information
├── articulation
└── dynamic_context
```

## Required Measure Data

```text
ScoreMeasure
├── stable_measure_id
├── movement_id
├── displayed_number
├── internal_sequence
├── duration
├── time_signature
├── key_signature
├── tempo_context
└── note_events
```

Stable identifiers are necessary so historical analysis can remain linked to musical locations.

---

# Score Alignment

Score alignment maps performed notes and timing to expected score events.

## Initial Assumptions

Version 0.3 assumes:

- solo instrument
- one principal melodic line
- known piece
- known or estimated starting passage
- limited skipped measures
- limited repeated sections
- no accompaniment

## Alignment Inputs

- performed note segments
- expected score notes
- intended passage
- optional target tempo
- duration estimates
- pitch similarity
- onset similarity

## Alignment Output

```text
AlignmentEvent
├── score_note_id
├── performed_note_id
├── match_type
├── onset_difference
├── duration_difference
├── pitch_difference
└── confidence
```

## Match Types

- matched
- missing expected note
- extra performed note
- ambiguous
- unalignable

## Alignment Strategy

A practical staged approach:

1. Restrict expected score to the selected passage when known.
2. Build performed note sequence.
3. Compare pitch classes and intervals.
4. Estimate tempo scale.
5. align sequences dynamically.
6. refine timing locally.
7. calculate confidence.
8. reject unreliable regions.

## Rules

- Low-confidence alignment must not produce strong user-facing claims.
- The engine should distinguish:
  - incorrect note
  - missing note
  - extra note
  - uncertain alignment
- Repeats and alternate endings require explicit handling.
- A user-selected passage should strongly constrain alignment.
- If the performer begins outside the selected passage, the engine may search nearby measures and report that the passage could not be confirmed.

---

# Intonation Analysis

Intonation analysis compares performed pitch center with expected pitch.

## Note-Level Measurements

For each confidently aligned pitched note:

- expected pitch
- detected pitch center
- average cents deviation
- signed direction
- pitch stability
- vibrato width
- confidence
- note duration
- usable stable-region duration

## Initial Interpretation Bands

Internal thresholds may use configurable bands such as:

```text
within tolerance
slightly sharp or flat
meaningfully sharp or flat
substantially sharp or flat
```

Exact threshold values must be validated with real cello recordings.

They should not be presented as universal musical truth.

## Factors Affecting Interpretation

- note duration
- vibrato
- attack instability
- dynamic level
- register
- open string versus stopped note
- phrase context
- confidence
- tuning system assumptions
- expressive pitch movement

## User-Facing Examples

Preferred:

> Measure 18: F-sharp centered 17 cents flat.

> Measure 24: The same fourth-finger note was flat in three recordings.

Avoid:

> Bad intonation.

## Repeated Intonation Tendencies

Aggregate by:

- expected note
- pitch class
- string when inferable
- finger when explicitly known or reliably inferred
- measure
- shift destination
- register
- passage
- session
- multiple sessions

The engine should not claim:

> Your fourth finger is flat.

unless fingering is known or the inference is sufficiently reliable.

A safer observation is:

> Fourth-finger notes marked in the score have trended flat.

or:

> Repeated notes in this register have trended flat.

---

# Incorrect Note Detection

An incorrect note is not the same as an intonation deviation.

## Possible Outcomes

- correct expected note, slightly sharp or flat
- different pitch from expected
- expected note omitted
- extra performed note
- uncertain due to alignment
- unsupported chord or double stop

## Rules

- A small cents deviation remains the same musical note.
- Enharmonic spelling comes from the score.
- Low-confidence pitch tracking should not be labeled a wrong note.
- Portamento between notes should not create false extra-note detections.
- Grace notes and ornaments require score-aware treatment.

---

# Rhythm Analysis

Rhythm analysis compares performed timing with score structure.

## Measurements

- onset timing
- inter-onset interval
- note duration
- rest duration
- local tempo
- tempo trend
- rhythmic ratio
- repeated-pattern consistency

## Relative Timing

Rhythm should be evaluated relative to the local tempo.

A raw delay in milliseconds is less meaningful than:

- fraction of a beat
- proportion of expected duration
- deviation from surrounding tempo

## Initial Outputs

```text
RhythmObservation
├── expected_onset
├── performed_onset
├── onset_deviation
├── expected_duration
├── performed_duration
├── duration_deviation
├── local_tempo
└── confidence
```

## Expressive Timing

The engine should allow:

- phrase-end lengthening
- cadential broadening
- pickup flexibility
- limited rubato
- tempo changes indicated in the score

The engine should be more cautious when:

- timing deviations are gradual
- multiple notes shift together
- the phrase remains internally consistent
- the score contains expressive tempo markings

## User-Facing Examples

> Measure 12: The second eighth note entered early in three attempts.

> Measures 30–32 gradually slowed by approximately 8 BPM.

Avoid:

> Your timing is bad.

---

# Tempo Analysis

Tempo analysis estimates pace and drift.

## Outputs

- starting tempo
- ending tempo
- median tempo
- local tempo curve
- drift direction
- short-term instability
- confidence

## Distinguish

- intentional accelerando
- intentional ritardando
- score-indicated tempo change
- gradual unplanned drift
- isolated timing error
- unstable pulse

The engine should not classify a written ritardando as a problem.

---

# Dynamic Analysis

Dynamic analysis measures relative acoustic intensity.

## Measurements

- RMS energy
- peak energy
- smoothed loudness contour
- local contrast
- crescendo slope
- diminuendo slope
- phrase-level contour
- device gain stability

## Limitations

Microphone placement and automatic gain control can strongly affect dynamics.

Therefore, dynamic analysis should be:

- relative within one recording
- cautious across devices
- cautious across sessions
- disabled when gain instability is detected

## Score Comparison

The engine may compare broad contour against:

- written dynamic markings
- crescendo hairpins
- diminuendo hairpins
- phrase regions

## User-Facing Examples

> Measures 14–18 showed a clear crescendo.

> The written diminuendo was not visible in the recording's intensity contour.

Avoid:

> Your phrasing was wrong.

---

# Technique-Pattern Analysis

The engine may identify repeated measurable tendencies.

Examples:

- notes after upward shifts tend flat
- entrances after rests tend late
- repeated sixteenth-note groups compress
- long notes lose pitch stability near release
- crescendos begin too late
- tempo increases during difficult passages

These are **patterns**, not diagnoses.

The engine should not state:

> Your thumb is tense.

unless the user or teacher supplied that note.

Audio alone generally cannot prove physical cause.

---

# Measure Observation Generation

Raw measurements should be converted into concise, evidence-based observations.

## Observation Structure

```text
MeasureObservation
├── location
├── category
├── observation_code
├── severity
├── confidence
├── evidence_count
├── explanation
└── supporting_measurements
```

## Required Content

Every user-facing observation should answer:

- what happened
- where it happened
- how often
- how significant it was
- whether confidence is sufficient

## Examples

> Measure 24: F-sharp centered 14 cents flat in this recording.

> Measures 24–25: The shift entrance was late in three of four attempts.

> Measure 32: Insufficient signal quality for reliable pitch analysis.

## Observation Suppression

Do not create user-facing observations when:

- confidence is below threshold
- alignment is ambiguous
- the signal is unusable
- the event is too short
- the deviation is musically trivial
- the same information would create repetitive clutter

---

# Confidence Model

Confidence must be explicit throughout the pipeline.

## Confidence Sources

- signal quality
- pitch-tracker confidence
- segmentation confidence
- alignment confidence
- score certainty
- note duration
- evidence count
- consistency across frames
- consistency across attempts

## Confidence Levels

Internally, the engine may use numeric confidence from 0 to 1.

User-facing language should use descriptive states when needed:

- reliable
- likely
- uncertain
- insufficient data

## Rules

- Confidence is not performance quality.
- Low confidence should reduce claim strength.
- Insufficient data is a valid result.
- A failed component should not force unrelated components to fail.
- The engine must never fabricate a result to avoid an empty screen.

---

# Severity Model

Severity estimates how much an observation should influence practice priority.

Severity may consider:

- magnitude
- duration
- musical location
- repetition
- proximity to phrase boundary
- impact on following notes
- teacher assignment relevance
- selected practice focus
- confidence

Severity is internal.

The user should see clear language, not a numeric penalty.

---

# Repeated Pattern Detection

A repeated pattern requires aggregation across evidence.

## Evidence Levels

```text
single event
repeated within one recording
repeated across recordings in one session
repeated across multiple sessions
long-term tendency
```

## Promotion Rules

A possible progression:

```text
Raw Measurement
      ↓
Single Observation
      ↓
Repeated Session Pattern
      ↓
Long-Term Technical Pattern
```

Exact thresholds must be configurable and validated.

## Example

Recording 1:

> Measure 18 F-sharp: 16 cents flat.

Recording 2:

> Measure 18 F-sharp: 19 cents flat.

Recording 3:

> Measure 18 F-sharp: 17 cents flat.

Aggregated observation:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

Longer-term pattern:

> F-sharps in this passage have trended flat across the last three sessions.

---

# Practice Map Inputs

The analysis engine does not directly decide the final color presentation.

It supplies evidence to the practice-map update process.

## Input Fields

- piece
- measure
- category
- observation severity
- confidence
- evidence count
- recency
- repeated-pattern status
- selected focus
- teacher assignment relevance

## Practice Map Labels

- Comfortable
- Needs reinforcement
- Recommended focus
- Insufficient data

## Rules

- Map state represents practice priority.
- It does not represent ability.
- One measure may have different states by category.
- Map updates should occur after analysis, not during active playing.
- A single weak observation should rarely move a measure directly to highest priority.
- Recent repeated evidence should weigh more than old isolated evidence.

The exact update rules belong in the recommendation-engine specification.

---

# Recommendation Inputs

The analysis engine provides structured facts.

The recommendation engine decides what to suggest.

## Example Analysis Output

```text
Location: Measures 24–25
Category: Intonation
Pattern: Shift destination flat
Average deviation: -18 cents
Evidence count: 3 recordings
Confidence: high
```

## Example Recommendation

> Practice the shift into Measure 24 separately at a slower tempo. Remove vibrato and record three repetitions.

The recommendation is not part of the raw pitch result.

---

# Session Summary Inputs

The engine should provide summary-ready facts:

- passages analyzed
- recordings analyzed
- measurable improvement within session
- repeated issues
- unresolved high-priority observations
- unavailable categories
- confidence warnings

## Improvement Detection

Improvement should compare like with like.

Examples:

- same passage
- same expected note
- similar tempo
- same analysis version
- sufficient signal quality

The engine should avoid claiming improvement when recordings are not comparable.

Preferred:

> The F-sharp moved from 24 cents flat to 9 cents flat across three attempts.

Avoid:

> Your intonation improved.

unless the evidence supports the statement.

---

# Within-Session Comparison

A session may contain multiple recordings of the same passage.

## Comparable Attempt Criteria

Two recordings are comparable when they share enough of the following:

- same piece
- same passage
- similar score alignment
- same analysis version
- similar intended tempo
- sufficient confidence

## Outputs

- trend direction
- change in average deviation
- change in timing consistency
- change in tempo stability
- number of comparable attempts

## Rules

- Do not compare unrelated passages.
- Do not compare a slow isolated exercise directly with a full-tempo run-through without context.
- Do not treat every variation as improvement or regression.
- Preserve neutral wording when results are mixed.

---

# Cross-Session Comparison

Long-term trends should use:

- recent comparable sessions
- stable score locations
- compatible analysis versions
- sufficient evidence
- recency weighting

## Examples

> Rhythm in Measures 23–25 has become more consistent across five sessions.

> Fourth-finger notes in this movement still trend flat.

## Version Compatibility

If an analysis algorithm changes materially:

- prior runs remain stored
- the preferred comparison set should use compatible versions
- old recordings may be reprocessed
- the summary should not silently compare incompatible measurements

---

# Failure Handling

The engine should support partial completion.

## Example

```text
Pitch analysis: completed
Score alignment: completed
Rhythm analysis: failed
Dynamics analysis: unavailable
```

The user may still receive valid intonation feedback.

## Failure Categories

- invalid audio
- unsupported format
- decoding failure
- insufficient signal
- pitch-tracking failure
- segmentation failure
- score unavailable
- alignment failure
- unsupported polyphony
- internal processing error
- timeout

## User-Facing Error Language

Preferred:

> Pitch could not be analyzed reliably because the recording level was too low.

Avoid:

> Analysis pipeline error 0x031.

Internal diagnostics should retain technical details.

---

# Performance Requirements

The musician should not be forced to wait before continuing practice.

## Target Behavior

- recording saves immediately after stop
- analysis begins in background
- next recording can start without waiting
- partial results may appear when ready
- the interface remains usable during processing

## Initial Local Targets

These are engineering goals, not product guarantees:

- short recording validation: near immediate
- pitch-only analysis: faster than or comparable to recording duration where practical
- full score comparison: background processing
- session summary: generated after available analysis completes

Actual targets should be measured on supported devices.

---

# Reproducibility

Every Analysis Run should record enough information to reproduce the result.

## Required Metadata

- engine version
- configuration version
- score source version
- preprocessing parameters
- pitch reference
- instrument profile
- model or algorithm identifiers
- relevant thresholds
- input file checksum

Raw frame-level outputs may be retained during development and selectively retained in production.

---

# Diagnostics

Development diagnostics may include:

- waveform summary
- pitch trace
- voicing confidence
- segmentation boundaries
- alignment path
- rejected frames
- octave corrections
- quality warnings
- component timing

Diagnostics are for development and validation.

They should not clutter the musician-facing interface.

---

# Testing Strategy

The engine must be tested with real cello recordings.

Synthetic signals are useful but insufficient.

## Test Categories

### Unit Tests

- frequency-to-note conversion
- cents calculation
- confidence combination
- vibrato-center estimation
- measure aggregation
- threshold behavior
- score event normalization

### Synthetic Audio Tests

- pure sine tones
- harmonic tones
- controlled vibrato
- known pitch drift
- known timing offsets
- known crescendos
- silence and clipping

### Recorded Cello Tests

- open strings
- scales
- sustained stopped notes
- vibrato notes
- shifts
- repeated passages
- soft dynamics
- loud dynamics
- low and high registers
- intentionally sharp and flat notes
- room noise
- phone and tablet microphones

### Regression Tests

Each bug fix should add a retained test case when legally and practically possible.

---

# Validation Dataset

Create a small internal validation set containing:

- score file
- recording
- intended passage
- known performance conditions
- expert annotation
- expected broad outcome

## Example Case

```text
Piece: C-major scale
Passage: first octave
Recording condition: no vibrato
Known issue: E3 approximately 20 cents flat
Expected result: note identified as flat with high confidence
```

## Annotation Principles

Ground truth may include:

- manually measured pitch center
- score note identity
- approximate onset
- known intentional deviation
- teacher or expert annotation

The dataset should include difficult and ambiguous examples, not only clean recordings.

---

# Evaluation Metrics

## Pitch Tracking

- voiced/unvoiced accuracy
- raw pitch accuracy
- chroma accuracy
- octave-error rate
- pitch-center error
- note-detection precision and recall

## Segmentation

- onset tolerance accuracy
- boundary error
- note-count accuracy

## Alignment

- correct score-note match rate
- measure alignment accuracy
- skipped-note handling
- extra-note handling
- confidence calibration

## Intonation Feedback

- cents error against annotated reference
- correct sharp/flat direction
- repeated-pattern precision
- false-positive rate

## Rhythm Feedback

- onset error
- duration error
- tempo estimation error
- repeated-rhythm-pattern precision

## Product-Level Evaluation

- observations judged useful by cellists
- observations judged accurate by teachers
- false or misleading feedback rate
- time to analysis
- percentage of recordings producing useful feedback

The most important metric is not raw algorithm accuracy alone.

It is whether the feedback helps the musician practice more effectively.

---

# Configuration

All thresholds should be configuration-driven.

## Example Configuration Areas

- minimum recording duration
- silence threshold
- clipping threshold
- pitch confidence threshold
- octave-correction rules
- smoothing window
- stable-note region
- cents interpretation bands
- minimum note duration
- alignment gap penalties
- repeated-pattern evidence count
- confidence suppression threshold
- dynamic smoothing window

Configurations must be versioned.

Changing configuration should create a new Analysis Run when results may differ.

---

# Security and Privacy

The analysis engine processes private user audio and uploaded scores.

## Requirements

- use internal storage identifiers
- do not expose predictable file paths
- avoid logging raw personal audio
- sanitize failure messages
- delete temporary files
- scope analysis jobs to authorized user content
- honor recording and account deletion
- do not use user recordings for model training without explicit consent

Uploaded music must remain private by default.

---

# Initial Implementation Plan

## Phase 1: Audio Foundation

Implement:

- audio decoding
- mono conversion
- validation
- signal-quality checks
- normalized analysis format
- Analysis Run lifecycle

## Phase 2: Pitch Tracking

Implement:

- frame-level pitch estimation
- confidence
- note-name conversion
- cents calculation
- pitch trace diagnostics

## Phase 3: Sustained-Note Analysis

Implement:

- note segmentation
- stable-region detection
- pitch-center estimation
- vibrato width and rate
- pitch stability

## Phase 4: Passage-Level Intonation

Implement:

- recording passage context
- repeated note aggregation
- user-facing pitch observations
- cross-attempt comparisons

## Phase 5: Score Alignment

Implement:

- parsed score-note input
- sequence alignment
- measure mapping
- incorrect and missing note detection

## Phase 6: Practice Guidance Inputs

Implement:

- measure observations
- repeated patterns
- practice-map evidence
- recommendation evidence
- session-summary facts

---

# Version 0.2 Acceptance Criteria

Version 0.2 is successful when the application can:

1. accept a recorded solo-cello passage
2. validate and normalize the audio
3. estimate pitch over time
4. detect sustained-note regions
5. calculate note pitch center
6. calculate average cents sharp or flat
7. avoid treating normal vibrato as repeated intonation error
8. report confidence
9. store the result in a versioned Analysis Run
10. replay the original recording
11. process another recording without waiting for the prior result screen

## Example Acceptance Test

Input:

- sustained A3 on cello
- normal vibrato
- pitch center approximately 12 cents flat

Expected output:

```text
Detected note: A3
Pitch center: approximately 12 cents flat
Vibrato: detected
Confidence: sufficient
```

The engine should not report every vibrato oscillation as a separate sharp or flat error.

---

# Version 0.3 Acceptance Criteria

Version 0.3 is successful when the application can:

1. identify the intended passage from the score
2. align performed notes with expected notes
3. distinguish incorrect notes from intonation deviations
4. link observations to measures
5. identify repeated intonation issues across recordings
6. produce feedback such as:

> Measure 18: F-sharp averaged 17 cents flat across three attempts.

7. update a basic practice map without presenting a global grade

---

# Open Technical Decisions

The following decisions require prototyping and testing:

1. Which pitch-detection algorithm performs best on real cello recordings?
2. What sample rate provides the best accuracy and processing tradeoff?
3. What stable-region method best estimates vibrato center?
4. How should attacks, releases, and portamento be excluded?
5. What minimum note duration is required for reliable intonation analysis?
6. How should octave errors be corrected?
7. How should open-string resonance affect pitch tracking?
8. How should double stops be handled or rejected?
9. What alignment method best handles skipped and repeated notes?
10. What timing tolerance preserves expressive playing?
11. How should automatic microphone gain be detected?
12. Which measurements should be retained long term?
13. What confidence thresholds produce acceptably few false positives?
14. When should recordings be reprocessed after engine updates?
15. How should a teacher or musician flag incorrect analysis?

These decisions should be resolved through experiments with retained test recordings.

---

# Recommended Experiment Sequence

## Experiment 1

Test sustained open strings without vibrato.

Goal:

- establish basic pitch accuracy
- identify octave errors
- calibrate frequency range

## Experiment 2

Test sustained stopped notes without vibrato.

Goal:

- compare pitch center against known tuner measurements
- validate cents calculation

## Experiment 3

Test sustained notes with normal vibrato.

Goal:

- estimate pitch center
- measure vibrato width and rate
- prevent oscillation-based false errors

## Experiment 4

Test scales at slow tempo.

Goal:

- segment notes
- identify note sequence
- compare transitions

## Experiment 5

Test one short MusicXML passage.

Goal:

- align performed notes to score
- generate measure-level observations

## Experiment 6

Repeat the same passage three times with one intentional flat note.

Goal:

- aggregate repeated evidence
- generate the first useful practice recommendation

This sequence directly supports the first successful milestone.

---

# Summary

The analysis engine transforms:

```text
Audio
  ↓
Measurements
  ↓
Aligned Musical Events
  ↓
Observations
  ↓
Repeated Patterns
  ↓
Practice Guidance Inputs
```

The engine must remain:

- measurable
- versioned
- confidence-aware
- explainable
- non-judgmental
- instrument-aware
- respectful of interpretation

The first successful milestone is not a complete musical evaluation.

It is a reliable, evidence-based statement that helps a cellist correct a real problem:

> This note is consistently flat, here is where it occurs, and here is what to practice next.
