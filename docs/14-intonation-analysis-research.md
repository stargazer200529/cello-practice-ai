# Intonation Analysis Research

## Status

Working research specification for **Practice with Purpose**.

This document defines the evidence base, research questions, provisional design decisions, and validation plan for bowed-string intonation analysis. It is intentionally more conservative than a generic tuner design because cello pitch contains onset transients, shifts, corrective slides, vibrato, bowing irregularities, resonances, and releases that should not be treated as equivalent evidence.

The first supported instrument remains solo cello.

---

# 1. Core Product Question

The analysis engine must not ask only:

> What frequency was present?

It must ask:

> What happened during the note, where did the player first arrive, did the pitch move intentionally or correctively, where did it settle, how reliable is the estimate, and is the same pattern repeated?

A useful intonation observation should distinguish at least:

- unreliable bow-onset transient
- first reliable finger placement
- corrective movement
- settled pitch center
- vibrato behavior
- release
- uncertainty

---

# 2. Principal Design Finding

## Initial placement and settled pitch are separate measurements

A note that begins 25 cents flat and settles to 3 cents flat should not be summarized as merely “3 cents flat.”

The engine should preserve both facts:

- the player initially landed flat
- the player successfully corrected the note

This supports feedback such as:

> Measure 18: F-sharp initially landed about 24 cents flat, then corrected upward and settled within 5 cents of the target. The same arrival pattern occurred in four of five attempts.

---

# 3. Bowed-String Note Model

The first implementation should model a note as a sequence of evidence regions rather than treating every analysis frame equally.

```text
Pre-onset context
    ↓
Bow-onset transient
    ↓
Initial reliable placement
    ↓
Correction or settling trajectory
    ↓
Settled pitch region
    ↓
Release
```

## 3.1 Pre-onset context

Purpose:

- identify the preceding score note
- detect a shift, string crossing, rest, repeated note, or slur
- estimate whether a pitch glide is plausible before the new note
- detect residual ringing from the prior note or an open string

## 3.2 Bow-onset transient

Characteristics may include:

- aperiodic bow noise
- weak or changing harmonic structure
- pitch-tracker confidence instability
- octave errors
- brief double-slip or irregular stick-slip behavior
- overlapping energy from the preceding note

This region should normally be excluded from intonation scoring, but retained for confidence estimation and later bow-onset analysis. The boundary should be detected from evidence, not a universal fixed duration.

## 3.3 Initial reliable placement

Definition:

> The earliest region after note onset that contains sufficiently reliable, target-relevant pitch evidence for long enough to represent a plausible finger placement rather than an isolated frame.

Candidate measurements:

- initial cents error
- initial confidence
- initial placement duration
- relation to eventual settled center
- repetition across attempts

## 3.4 Correction or settling trajectory

Candidate measurements:

- correction direction
- correction distance in cents
- correction latency
- slope and smoothness
- number of reversals
- whether movement begins before or after stable periodicity
- compatibility with a score-defined shift or expressive portamento

## 3.5 Settled pitch region

Candidate measurements:

- robust center pitch
- signed cents error
- pitch stability
- vibrato rate
- vibrato extent
- percentage of reliable frames
- confidence
- duration of settled evidence

## 3.6 Release

Release pitch should not be part of the main intonation score in Version 0.2. It may later support observations about premature finger release, pitch sag during diminuendo, or unstable note endings.

---

# 4. Pitch-Tracking Algorithms

No algorithm should be selected solely from published aggregate accuracy. The engine must be benchmarked on real cello recordings containing low notes, vibrato, onsets, shifts, weak attacks, and room noise.

## 4.1 YIN

Potential strengths:

- mature and understandable
- computationally manageable
- useful monophonic baseline
- exposes periodicity-related evidence useful for confidence

Potential weaknesses:

- low cello notes require several waveform cycles
- onset and rapid pitch movement may be unreliable
- octave and subharmonic errors can occur
- thresholds affect voiced/unvoiced decisions

Role:

- required baseline
- possible low-latency local tool
- comparison against learned models

## 4.2 pYIN

Potential strengths:

- probabilistic voiced/unvoiced estimation
- temporal decoding suppresses isolated errors
- strong conventional baseline

Potential weaknesses:

- smoothing can conceal exact initial placement timing
- temporal decoding may lag rapid corrections
- parameters may need cello-specific tuning

Role:

- strong offline baseline
- candidate for settled-pitch estimation
- unlikely to be the sole source for attack analysis

## 4.3 CREPE

CREPE is a convolutional neural-network pitch estimator operating directly on waveform frames. Its authors reported performance equal to or better than pYIN on general monophonic benchmarks.

Potential strengths:

- high general monophonic accuracy
- confidence distribution over pitch bins
- open-source Python implementations
- useful robustness in benchmark conditions

Potential weaknesses:

- benchmark success does not establish cello-specific onset accuracy
- confidence calibration may vary by register and articulation
- computational cost is higher than basic YIN
- octave mistakes can still occur

Role:

- primary offline candidate
- benchmark against pYIN and YIN
- not authoritative until cello tests are complete

## 4.4 SWIPE / SWIPE'

Potential strengths:

- harmonic-structure-based estimate
- independent comparison against time-domain and learned methods

Potential weaknesses:

- computational cost
- changing bowed-string timbre may affect estimates
- implementation availability may be less convenient

Role:

- optional benchmark algorithm
- disagreement detector

## 4.5 Ensemble approach

A future production system may use:

- one primary tracker
- one independent verification tracker
- signal-quality checks
- score constraints
- note-phase classification

Disagreement should reduce confidence rather than force a result.

---

# 5. Low Cello Register Constraint

Cello C2 is approximately 65.4 Hz. One period is approximately 15.3 ms. Reliable periodicity estimation generally needs multiple periods, so low-register pitch cannot be established instantly.

Consequences:

- initial reliable placement cannot use the same minimum latency across the full cello range
- lower notes may require longer evidence windows
- correction latency must account for estimator latency
- the engine should distinguish “the player corrected late” from “the detector needed more cycles”

The system should record both acoustic event time estimate and analysis availability time.

---

# 6. Vibrato

Vibrato is structured modulation, not random instability.

The engine should estimate:

- vibrato center
- vibrato rate
- vibrato extent
- regularity
- onset time
- percentage of the note containing vibrato

## 6.1 Center estimation

Candidate estimators:

- confidence-weighted median in cents
- robust local regression trend plus oscillatory residual
- midpoint between upper and lower envelope
- periodic-model center
- trimmed mean after outlier removal

The preferred estimator must be validated against manually annotated examples.

## 6.2 Immediate vibrato

When vibrato begins immediately, the engine must not treat the first upper or lower excursion as the finger’s original placement.

Provisional rule:

- require a persistent region or modeled local center
- never infer initial placement from one extreme frame
- classify early periodic oscillation around a stable center as vibrato onset, not correction

## 6.3 Register dependence

Recent cello-specific research indicates acoustic vibrato extent changes with position on the string even when physical finger motion decreases. Therefore a single global vibrato-width threshold is unlikely to be appropriate.

---

# 7. Corrective Slide Versus Intentional Shift

This is a classification problem, not merely a pitch-slope threshold.

## Evidence suggesting corrective placement

- the new note first forms a short reliable plateau away from target
- motion begins after bow onset
- movement ends near the target
- the same direction repeats across attempts
- settled pitch is materially closer to target than initial pitch

## Evidence suggesting intentional shift or portamento

- glide begins during the preceding note
- movement crosses continuously into the target
- slur or phrase context supports connection
- no distinct out-of-tune arrival plateau exists
- the target stabilizes without a second corrective event

## Evidence suggesting bow-onset artifact

- low periodicity or confidence
- isolated octave jumps
- trackers disagree strongly
- duration is too short to represent placement

## Initial policy

Version 0.2 should use conservative internal labels:

- probable corrective adjustment
- probable connected shift
- insufficient evidence

The application should not claim artistic intent.

---

# 8. Note Segmentation

Frame-level F0 tracking is not the same as identifying note events.

The engine must combine:

- MusicXML expected note sequence
- onset evidence
- pitch contour
- amplitude or spectral change
- temporal continuity
- rests and articulations
- expected duration
- confidence

CREPE Notes and related work show that converting an F0 contour into notes is a separate modeling problem.

For Practice with Purpose:

```text
expected score event
+ local onset evidence
+ F0 contour
+ timing tolerance
= performed note hypothesis
```

---

# 9. Confidence Model

Candidate inputs:

- tracker confidence
- agreement among trackers
- periodicity
- signal-to-noise ratio
- harmonic consistency
- target-note plausibility
- duration of reliable evidence
- stability of estimated center
- score-alignment confidence
- absence of competing pitches
- distance from onset and release

Policy:

- Low confidence: store internally, no corrective feedback.
- Medium confidence: descriptive uncertainty or request another attempt.
- High confidence: eligible for user-facing observation.
- Repeated medium-confidence events may become reportable when the same pattern recurs.

Core principle:

> Silence is preferable to confident-sounding incorrect feedback.

---

# 10. Provisional Metrics

```text
expected_pitch_midi
expected_frequency_hz
onset_time
reliable_pitch_start_time
initial_placement_cents
initial_placement_confidence
settled_pitch_cents
settled_pitch_confidence
correction_detected
correction_direction
correction_distance_cents
correction_latency_ms
settling_time_ms
vibrato_detected
vibrato_rate_hz
vibrato_extent_cents
pitch_stability_cents
release_start_time
overall_measurement_confidence
classification
```

Internal classification candidates:

```text
centered_arrival
initially_flat_corrected
initially_sharp_corrected
settled_flat
settled_sharp
unstable_no_settle
probable_portamento
probable_onset_artifact
insufficient_data
```

---

# 11. Teacher Translation Layer

## Example A

Internal:

```text
initial_placement_cents = -24
settled_pitch_cents = -4
correction_latency_ms = 310
repeat_count = 4 of 5
```

Displayed:

> Measure 18: F-sharp repeatedly begins flat and is corrected upward. The sustained pitch is generally centered.

Suggested practice:

> Practice the arrival without vibrato. Stop on the target note and check the hand position before continuing.

## Example B

Internal:

```text
initial_placement_cents = +3
settled_pitch_cents = +18
vibrato_center_drift = upward
```

Displayed:

> The note begins near center but trends sharp during the sustain.

## Example C

Internal:

```text
tracker_disagreement = high
periodicity = low
duration = short
```

Displayed:

No intonation judgment.

---

# 12. What Should Not Be Scored Yet

Version 0.2 should not provide definitive intonation feedback for:

- double stops
- chords
- accompaniment
- artificial harmonics
- left-hand pizzicato
- notes too short for reliable cycles
- unresolved overlapping strings
- severe wolf-note instability
- highly extended techniques
- recordings with insufficient signal quality

---

# 13. Research Risks and False Positives

## Octave errors

Mitigation:

- score-constrained pitch range
- continuity model
- harmonic plausibility
- tracker ensemble

## Open-string resonance

Mitigation:

- expected-note constraint
- harmonic-energy analysis
- persistence and relative amplitude

## Metronome and room noise

Mitigation:

- pitched periodicity requirement
- spectral rejection
- score timing context

## String crossing

Mitigation:

- crossing-region classification
- persistence requirement
- avoid isolated frames as initial placement

## Wolf behavior

Mitigation:

- lower confidence
- flag instability pattern
- avoid attributing it to finger placement without corroboration

---

# 14. Recommended Benchmark Plan

## Algorithms

Benchmark at least:

- YIN
- pYIN
- CREPE
- one additional independent method if practical

## Recording conditions

Use:

- phone microphone
- tablet microphone
- laptop microphone
- external USB microphone
- quiet room
- moderately reverberant room
- near and normal music-stand distances

## Musical cases

Record:

- open strings
- stopped notes without vibrato
- immediate vibrato
- delayed vibrato
- initially flat then corrected
- initially sharp then corrected
- accurate direct arrival
- slow shifts
- intentional portamento
- repeated notes
- string crossings
- fast scales
- short détaché
- legato
- soft attacks
- strong attacks
- wolf-region notes
- varied releases

## Ground truth

Use a combination of:

- score target
- manually annotated note boundaries
- manually annotated initial placement region
- manually annotated settled region
- expert listening judgment
- controlled reference tones where appropriate

Ground truth should not rely only on another pitch tracker.

## Evaluation metrics

- gross pitch error
- octave error rate
- fine pitch error in cents
- voicing error
- time to first reliable estimate
- initial-placement error
- settled-center error
- correction detection precision and recall
- correction-latency error
- vibrato-center error
- false feedback rate

The false-feedback rate is a primary product metric.

---

# 15. Provisional Engineering Recommendation

## Offline analysis

Begin with:

```text
CREPE or equivalent learned tracker
+
pYIN baseline
+
score constraints
+
confidence gating
+
custom note-phase analysis
```

Do not rely on either tracker alone.

## Live tuner

For a later live tuner, use a lower-latency algorithm and present:

- current pitch center
- cents
- confidence
- stability

The live tuner and post-session analysis do not need identical algorithms.

## Frame representation

Convert frequency to continuous MIDI or cents:

```text
midi = 69 + 12 × log2(frequency / 440)
```

Retain high-resolution frame output internally. Do not expose every frame to the user.

---

# 16. Practice with Purpose Design Decisions

1. Initial placement and settled intonation are separate measurements.
2. Bow-onset transients are not discarded by a universal fixed time window.
3. The first reliable placement is detected from confidence, periodicity, persistence, and score context.
4. A single pitch frame cannot establish initial placement.
5. Vibrato is modeled as structured modulation around a center.
6. Settled intonation uses a robust center, not instantaneous pitch.
7. Correction distance and latency are retained.
8. Probable corrective slides are reported as placement behavior.
9. Intentional portamento is not penalized merely because pitch moves continuously.
10. Release pitch is excluded from primary scoring in Version 0.2.
11. Low-confidence notes produce no corrective judgment.
12. Repeated tendencies matter more than isolated small deviations.
13. Feedback states what happened, where, repetition, significance, and next action.
14. No overall intonation grade or mastery percentage is displayed.
15. The system must be validated on real cello recordings before recommendations use it.

---

# 17. Initial Threshold Policy

Numerical thresholds should not be frozen before benchmark data exists.

Provisional thresholds requiring validation include:

- minimum reliable-frame confidence
- minimum persistence for initial placement
- minimum correction distance
- minimum correction latency
- settled-region duration
- cents tolerance
- vibrato rate and extent ranges
- signal-to-noise requirement
- tracker-agreement tolerance

Thresholds may vary by register, note duration, tempo, articulation, dynamic, microphone, and signal quality.

---

# 18. Next Prototype

The next implementation should be a research sandbox, not a production API.

```text
research/
├── recordings/
├── annotations/
├── notebooks/
├── scripts/
└── reports/
```

The prototype should:

1. load a cello recording
2. run multiple pitch trackers
3. plot confidence and F0
4. convert F0 to cents against a chosen target
5. allow manual annotation of onset, initial placement, settled region, and release
6. compare algorithm output with annotations
7. export a machine-readable result

Do not connect prototype output to recommendations yet.

---

# 19. Required Research Continuation

Additional literature review is still needed in:

- psychoacoustic perception of vibrato center
- bowed-string onset classification
- portamento and expressive pitch modeling
- automatic music-performance assessment
- cello-specific pitch-tracker benchmarks
- pedagogical descriptions of corrective shifting
- confidence calibration

---

# 20. References

1. A. de Cheveigné and H. Kawahara. “YIN, a fundamental frequency estimator for speech and music.” *Journal of the Acoustical Society of America*, 2002.
2. M. Mauch and S. Dixon. “pYIN: A Fundamental Frequency Estimator Using Probabilistic Threshold Distributions.” *IEEE ICASSP*, 2014.
3. A. Camacho and J. G. Harris. “A Sawtooth Waveform Inspired Pitch Estimator for Speech and Music.” *Journal of the Acoustical Society of America*, 2008.
4. J. W. Kim et al. “CREPE: A Convolutional Representation for Pitch Estimation.” *IEEE ICASSP*, 2018. https://arxiv.org/abs/1802.06182
5. X. Riley and S. Dixon. “CREPE Notes: A New Method for Segmenting Pitch Contours into Discrete Notes.” 2023. https://arxiv.org/abs/2311.08884
6. E. Bavu et al. “Rotational and Translational Waves in a Bowed String.” 2005. https://arxiv.org/abs/physics/0505058
7. R. Bader and R. Mores. “Cochlear Detection of Double-Slip Motion in Cello Bowing.” 2018. https://arxiv.org/abs/1804.05695
8. S. Hu et al. “Influence of String Register Locations on Vibratos among Violoncellists.” 2025. https://arxiv.org/abs/2512.18162

---

# 21. Current Conclusion

The most important design conclusion is not which pitch tracker wins a benchmark.

It is this:

> Cello intonation must be analyzed as a time-evolving performance behavior, not as a single average frequency.

A useful system must identify when reliable pitch begins, distinguish initial placement from later correction, estimate the center of vibrato, avoid judging unreliable transitions, and report repeated technical tendencies conservatively.
