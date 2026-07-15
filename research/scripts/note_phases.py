from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# These defaults are experimental controls for this research tool. They are not
# taken from literature, are not validated for cello, and must not be interpreted
# as production thresholds. Keeping them named and grouped makes each rule easy
# to change while comparing the detector with manually inspected recordings.

# An energy frame becomes active at this fraction of the recording's robust
# high-energy reference. A relative value avoids assuming a microphone level.
ENERGY_ACTIVITY_RATIO = 0.08

# The 95th percentile is used instead of the absolute energy peak so one isolated
# impulse does not set the activity scale for the entire recording.
ENERGY_REFERENCE_PERCENTILE = 95.0

# Short moving-average smoothing suppresses frame-to-frame waveform RMS jitter.
ENERGY_SMOOTHING_SECONDS = 0.03

# Pitch estimates farther than two semitones from the requested single-note
# target are treated as pYIN octave/subharmonic artifacts for phase detection.
MAXIMUM_TARGET_DEVIATION_CENTS = 200.0

# Activity islands shorter than this are treated as isolated noise, not a note.
MINIMUM_ACTIVITY_SECONDS = 0.04

# Brief energy gaps shorter than this are joined so a bow transient does not
# split one sustained note into multiple activity components.
MAXIMUM_ACTIVITY_GAP_SECONDS = 0.06

# Attack start is refined to the last upward crossing of this fraction of the
# voiced-region energy, preventing quiet room tone from becoming a long attack.
ATTACK_ENERGY_RATIO = 0.5

# Initial placement uses this much valid pitch evidence after the first voiced
# frame. It is a local measurement window, not an assumed attack duration.
INITIAL_PLACEMENT_SECONDS = 0.06

# The latter half of valid pitch frames supplies a robust candidate settled
# center. This is relative to detected evidence and assumes no note duration.
SETTLED_REFERENCE_FRACTION = 0.5

# Frames within this distance of the candidate center count as locally settled.
SUSTAIN_CENTER_TOLERANCE_CENTS = 8.0

# A stable run normally needs this duration before it becomes the sustain phase.
MINIMUM_SUSTAIN_SECONDS = 0.06

# Short gaps in otherwise settled pitch evidence may be bridged when pYIN briefly
# drops voicing. The detector never fills the underlying pitch values themselves.
MAXIMUM_SETTLED_GAP_SECONDS = 0.03

# If a genuinely short note cannot satisfy the normal sustain duration, at least
# this many stable frames are required for the deterministic short-note fallback.
MINIMUM_SHORT_SUSTAIN_FRAMES = 2

# Initial-to-settled movement must exceed this distance before it is labeled a
# correction. Smaller movement is retained in metrics but classified as none.
MINIMUM_CORRECTION_MAGNITUDE_CENTS = 12.0

# A correction must also reduce absolute target error by this amount, preventing
# arbitrary pitch drift from being mislabeled as movement toward the center.
MINIMUM_CORRECTION_IMPROVEMENT_CENTS = 6.0

# Correction start is the first frame that completes this fraction of the total
# initial-to-settled movement, subject to the absolute movement floor below.
CORRECTION_START_FRACTION = 0.2

# This absolute movement floor prevents tiny contour jitter from starting the
# correction phase when the total detected correction is large.
MINIMUM_CORRECTION_START_MOVEMENT_CENTS = 3.0

# Faster movement is absorbed into the attack because pYIN onset convergence can
# resemble a correction. This duration is an experimental inspection control.
MINIMUM_CORRECTION_DURATION_SECONDS = 0.08

# Release begins when smoothed RMS remains below this fraction of sustain energy.
# This is a relative envelope rule and does not assume a note duration.
RELEASE_ENERGY_RATIO = 0.7

# The release energy condition must persist for this duration so a single noisy
# low-energy frame does not end the sustain.
RELEASE_CONFIRMATION_SECONDS = 0.04

# Release end is the first persistent fall below this fraction of sustain energy,
# preventing post-note room noise from extending the detected release.
RELEASE_END_ENERGY_RATIO = 0.12

# The end threshold may not fall below this multiple of measured pre-note room
# energy, allowing release to end when the signal returns near its own baseline.
RELEASE_BASELINE_MULTIPLIER = 1.5


PHASE_UNVOICED = "unvoiced"
PHASE_ATTACK = "attack"
PHASE_CORRECTION = "correction"
PHASE_SUSTAIN = "sustain"
PHASE_RELEASE = "release"


@dataclass(frozen=True)
class PhaseHeuristics:
    energy_activity_ratio: float = ENERGY_ACTIVITY_RATIO
    energy_reference_percentile: float = ENERGY_REFERENCE_PERCENTILE
    energy_smoothing_seconds: float = ENERGY_SMOOTHING_SECONDS
    maximum_target_deviation_cents: float = MAXIMUM_TARGET_DEVIATION_CENTS
    minimum_activity_seconds: float = MINIMUM_ACTIVITY_SECONDS
    maximum_activity_gap_seconds: float = MAXIMUM_ACTIVITY_GAP_SECONDS
    attack_energy_ratio: float = ATTACK_ENERGY_RATIO
    initial_placement_seconds: float = INITIAL_PLACEMENT_SECONDS
    settled_reference_fraction: float = SETTLED_REFERENCE_FRACTION
    sustain_center_tolerance_cents: float = SUSTAIN_CENTER_TOLERANCE_CENTS
    minimum_sustain_seconds: float = MINIMUM_SUSTAIN_SECONDS
    maximum_settled_gap_seconds: float = MAXIMUM_SETTLED_GAP_SECONDS
    minimum_short_sustain_frames: int = MINIMUM_SHORT_SUSTAIN_FRAMES
    minimum_correction_magnitude_cents: float = (
        MINIMUM_CORRECTION_MAGNITUDE_CENTS
    )
    minimum_correction_improvement_cents: float = (
        MINIMUM_CORRECTION_IMPROVEMENT_CENTS
    )
    correction_start_fraction: float = CORRECTION_START_FRACTION
    minimum_correction_start_movement_cents: float = (
        MINIMUM_CORRECTION_START_MOVEMENT_CENTS
    )
    minimum_correction_duration_seconds: float = (
        MINIMUM_CORRECTION_DURATION_SECONDS
    )
    release_energy_ratio: float = RELEASE_ENERGY_RATIO
    release_confirmation_seconds: float = RELEASE_CONFIRMATION_SECONDS
    release_end_energy_ratio: float = RELEASE_END_ENERGY_RATIO
    release_baseline_multiplier: float = RELEASE_BASELINE_MULTIPLIER


DEFAULT_PHASE_HEURISTICS = PhaseHeuristics()


@dataclass(frozen=True)
class PhaseDetectionResult:
    phase_labels: np.ndarray
    frame_energy: np.ndarray
    smoothed_energy: np.ndarray
    attack_start_index: int | None
    first_voiced_index: int | None
    correction_start_index: int | None
    sustain_start_index: int | None
    sustain_end_index: int | None
    release_start_index: int | None
    release_end_index: int | None
    attack_duration_seconds: float | None
    initial_cents_offset: float | None
    correction_direction: str
    correction_magnitude_cents: float
    correction_duration_seconds: float
    settled_pitch_center_cents: float | None
    sustain_duration_seconds: float
    sustain_pitch_stability_cents: float | None
    release_duration_seconds: float

    def event_indices(self) -> tuple[tuple[str, int], ...]:
        events = (
            ("Attack start", self.attack_start_index),
            ("First voiced", self.first_voiced_index),
            ("Correction start", self.correction_start_index),
            ("Sustain start", self.sustain_start_index),
            ("Sustain end", self.sustain_end_index),
            ("Release start", self.release_start_index),
            ("Release end", self.release_end_index),
        )
        return tuple((label, index) for label, index in events if index is not None)


def calculate_frame_rms(
    audio: np.ndarray,
    frame_length: int,
    hop_length: int,
    frame_count: int,
) -> np.ndarray:
    """Calculate centered waveform RMS aligned with the pYIN frame grid."""
    if frame_count == 0:
        return np.array([], dtype=float)

    # Center padding mirrors the frame alignment used by librosa's default pYIN
    # analysis, allowing waveform energy and pitch evidence to share indices.
    half_frame = frame_length // 2
    padded = np.pad(np.asarray(audio, dtype=float), (half_frame, half_frame))
    rms = np.empty(frame_count, dtype=float)
    for index in range(frame_count):
        start = index * hop_length
        frame = padded[start : start + frame_length]
        if frame.size < frame_length:
            frame = np.pad(frame, (0, frame_length - frame.size))
        rms[index] = float(np.sqrt(np.mean(np.square(frame))))
    return rms


def _frame_duration(times: np.ndarray) -> float:
    if times.size < 2:
        return 1.0
    positive_differences = np.diff(times)
    positive_differences = positive_differences[positive_differences > 0]
    if not positive_differences.size:
        return 1.0
    return float(np.median(positive_differences))


def _seconds_to_frames(seconds: float, frame_duration: float) -> int:
    if seconds <= 0:
        return 1
    return max(1, int(np.ceil(seconds / frame_duration)))


def _smooth(values: np.ndarray, window_frames: int) -> np.ndarray:
    if values.size == 0 or window_frames <= 1:
        return np.asarray(values, dtype=float).copy()
    window_frames = min(window_frames, values.size)
    left = window_frames // 2
    right = window_frames - 1 - left
    padded = np.pad(values, (left, right), mode="edge")
    kernel = np.full(window_frames, 1.0 / window_frames)
    return np.convolve(padded, kernel, mode="valid")


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Return true runs as half-open (start, end) index pairs."""
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(mask):
        if value and start is None:
            start = index
        elif not value and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(mask)))
    return runs


def _fill_internal_gaps(mask: np.ndarray, maximum_gap_frames: int) -> np.ndarray:
    filled = mask.copy()
    inverse_runs = _runs(~mask)
    for start, end in inverse_runs:
        # Only internal gaps are joined; leading and trailing silence remains
        # available for attack and release boundary detection.
        if (
            start > 0
            and end < len(mask)
            and end - start <= maximum_gap_frames
        ):
            filled[start:end] = True
    return filled


def _remove_short_runs(mask: np.ndarray, minimum_frames: int) -> np.ndarray:
    cleaned = mask.copy()
    for start, end in _runs(mask):
        if end - start < minimum_frames:
            cleaned[start:end] = False
    return cleaned


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    finite = np.isfinite(values) & np.isfinite(weights)
    values = values[finite]
    weights = np.maximum(weights[finite], 0.0)
    if not values.size:
        raise ValueError("A weighted median requires at least one finite value.")
    if float(weights.sum()) == 0:
        return float(np.median(values))
    order = np.argsort(values)
    ordered_values = values[order]
    cumulative = np.cumsum(weights[order])
    midpoint = cumulative[-1] / 2
    return float(ordered_values[np.searchsorted(cumulative, midpoint, side="left")])


def _select_note_component(
    activity_mask: np.ndarray,
    valid: np.ndarray,
) -> tuple[int, int] | None:
    components = _runs(activity_mask)
    if not components:
        valid_indices = np.flatnonzero(valid)
        if not valid_indices.size:
            return None
        return int(valid_indices[0]), int(valid_indices[-1] + 1)

    # A component containing pYIN evidence outranks an isolated energy-only
    # component. Length breaks ties deterministically.
    return max(
        components,
        key=lambda run: (int(valid[run[0] : run[1]].sum()), run[1] - run[0]),
    )


def _empty_result(
    phase_labels: np.ndarray,
    frame_energy: np.ndarray,
    smoothed_energy: np.ndarray,
    component: tuple[int, int] | None,
) -> PhaseDetectionResult:
    attack_start = component[0] if component else None
    release_end = component[1] - 1 if component else None
    if component:
        phase_labels[component[0] : component[1]] = PHASE_ATTACK
    return PhaseDetectionResult(
        phase_labels=phase_labels,
        frame_energy=frame_energy,
        smoothed_energy=smoothed_energy,
        attack_start_index=attack_start,
        first_voiced_index=None,
        correction_start_index=None,
        sustain_start_index=None,
        sustain_end_index=None,
        release_start_index=None,
        release_end_index=release_end,
        attack_duration_seconds=None,
        initial_cents_offset=None,
        correction_direction="none",
        correction_magnitude_cents=0.0,
        correction_duration_seconds=0.0,
        settled_pitch_center_cents=None,
        sustain_duration_seconds=0.0,
        sustain_pitch_stability_cents=None,
        release_duration_seconds=0.0,
    )


def detect_note_phases(
    times: np.ndarray,
    cents: np.ndarray,
    valid: np.ndarray,
    voiced_probability: np.ndarray,
    frame_energy: np.ndarray,
    heuristics: PhaseHeuristics = DEFAULT_PHASE_HEURISTICS,
) -> PhaseDetectionResult:
    """Deterministically segment one sustained note from research evidence."""
    lengths = {
        len(times),
        len(cents),
        len(valid),
        len(voiced_probability),
        len(frame_energy),
    }
    if len(lengths) != 1:
        raise ValueError("All phase-detection frame arrays must have equal length.")

    frame_count = len(times)
    phase_labels = np.full(frame_count, PHASE_UNVOICED, dtype="<U10")
    if frame_count == 0:
        return _empty_result(
            phase_labels,
            np.asarray(frame_energy, dtype=float),
            np.asarray(frame_energy, dtype=float),
            None,
        )

    times = np.asarray(times, dtype=float)
    cents = np.asarray(cents, dtype=float)
    valid = np.asarray(valid, dtype=bool) & np.isfinite(cents)
    # The script already expresses pitch in cents from the requested target.
    # Target-distant pYIN octave/subharmonic estimates are excluded only from
    # phase inference; they remain intact in the exported frame-level CSV.
    phase_valid = valid & (
        np.abs(cents) <= heuristics.maximum_target_deviation_cents
    )
    voiced_probability = np.asarray(voiced_probability, dtype=float)
    frame_energy = np.asarray(frame_energy, dtype=float)
    frame_duration = _frame_duration(times)

    smoothing_frames = _seconds_to_frames(
        heuristics.energy_smoothing_seconds,
        frame_duration,
    )
    smoothed_energy = _smooth(frame_energy, smoothing_frames)
    energy_reference = float(
        np.percentile(smoothed_energy, heuristics.energy_reference_percentile)
    )
    activity_threshold = energy_reference * heuristics.energy_activity_ratio
    activity_mask = (
        smoothed_energy >= activity_threshold
        if energy_reference > 0
        else np.zeros(frame_count, dtype=bool)
    )

    # The activity mask first joins brief internal gaps, then removes short
    # islands. This preserves one bowed note while rejecting isolated impulses.
    activity_mask = _fill_internal_gaps(
        activity_mask,
        _seconds_to_frames(
            heuristics.maximum_activity_gap_seconds,
            frame_duration,
        ),
    )
    activity_mask = _remove_short_runs(
        activity_mask,
        _seconds_to_frames(
            heuristics.minimum_activity_seconds,
            frame_duration,
        ),
    )
    component = _select_note_component(activity_mask, phase_valid)
    if component is None:
        return _empty_result(
            phase_labels,
            frame_energy,
            smoothed_energy,
            None,
        )

    note_start, note_end = component
    note_valid = phase_valid.copy()
    note_valid[:note_start] = False
    note_valid[note_end:] = False
    valid_indices = np.flatnonzero(note_valid)
    if not valid_indices.size:
        return _empty_result(
            phase_labels,
            frame_energy,
            smoothed_energy,
            component,
        )

    first_voiced = int(valid_indices[0])
    last_voiced = int(valid_indices[-1])

    # Refine the attack boundary with a sustain-relative energy crossing. The
    # activity component remains a guardrail, while the crossing rejects room
    # tone that happens to sit above the global activity threshold.
    voiced_energy_reference = float(np.median(smoothed_energy[valid_indices]))
    attack_threshold = voiced_energy_reference * heuristics.attack_energy_ratio
    pre_voiced_indices = np.arange(note_start, first_voiced)
    below_attack = pre_voiced_indices[
        smoothed_energy[pre_voiced_indices] < attack_threshold
    ]
    if below_attack.size:
        note_start = min(first_voiced, int(below_attack[-1] + 1))

    # The candidate settled center is a voiced-probability-weighted median of
    # the latter fraction of detected pitch evidence. Weighting uses pYIN's
    # probability continuously rather than introducing another confidence gate.
    reference_count = max(
        1,
        int(np.ceil(valid_indices.size * heuristics.settled_reference_fraction)),
    )
    reference_indices = valid_indices[-reference_count:]
    candidate_center = _weighted_median(
        cents[reference_indices],
        voiced_probability[reference_indices],
    )

    stable_mask = note_valid & (
        np.abs(cents - candidate_center)
        <= heuristics.sustain_center_tolerance_cents
    )
    stable_mask = _fill_internal_gaps(
        stable_mask,
        _seconds_to_frames(
            heuristics.maximum_settled_gap_seconds,
            frame_duration,
        ),
    )
    stable_runs = [
        run
        for run in _runs(stable_mask)
        if run[1] > first_voiced and run[0] < note_end
    ]
    minimum_sustain_frames = _seconds_to_frames(
        heuristics.minimum_sustain_seconds,
        frame_duration,
    )
    qualifying_runs = [
        run for run in stable_runs if run[1] - run[0] >= minimum_sustain_frames
    ]
    if qualifying_runs:
        sustain_start = max(first_voiced, qualifying_runs[0][0])
    elif stable_runs:
        # A short-note fallback selects the longest stable run only when it has
        # at least the explicitly configured minimum number of stable frames.
        longest_stable_run = max(stable_runs, key=lambda run: run[1] - run[0])
        if (
            longest_stable_run[1] - longest_stable_run[0]
            >= heuristics.minimum_short_sustain_frames
        ):
            sustain_start = max(first_voiced, longest_stable_run[0])
        else:
            sustain_start = first_voiced
    else:
        sustain_start = first_voiced

    # Release begins only after a sustained region and only when waveform RMS
    # stays below a fraction of the sustain energy for the confirmation window.
    sustain_energy_end = max(sustain_start + 1, last_voiced + 1)
    sustain_energy = smoothed_energy[sustain_start:sustain_energy_end]
    sustain_energy_reference = float(np.median(sustain_energy))
    release_threshold = (
        sustain_energy_reference * heuristics.release_energy_ratio
    )
    release_confirmation_frames = _seconds_to_frames(
        heuristics.release_confirmation_seconds,
        frame_duration,
    )
    # A release must occur on or after the post-sustain energy peak. This avoids
    # treating the naturally quieter front of a crescendo as a release.
    post_sustain_energy = smoothed_energy[sustain_start:note_end]
    post_sustain_peak = sustain_start + int(np.argmax(post_sustain_energy))
    release_search_start = min(
        max(sustain_start + minimum_sustain_frames, post_sustain_peak),
        note_end - 1,
    )
    low_energy = smoothed_energy <= release_threshold
    release_start: int | None = None
    for start, end in _runs(low_energy):
        candidate = max(start, release_search_start)
        if (
            candidate < note_end
            and end - candidate >= release_confirmation_frames
        ):
            release_start = candidate
            break
    if release_start is None:
        # If the energy envelope never crosses the release threshold, the first
        # frame after the last voiced estimate is the conservative fallback.
        release_start = min(max(last_voiced + 1, sustain_start + 1), note_end - 1)

    sustain_end = max(sustain_start, release_start - 1)
    release_end = note_end - 1
    baseline_region = smoothed_energy[:note_start]
    baseline_energy = (
        float(np.median(baseline_region))
        if baseline_region.size
        else float(np.percentile(smoothed_energy, 10))
    )
    release_end_threshold = max(
        sustain_energy_reference * heuristics.release_end_energy_ratio,
        baseline_energy * heuristics.release_baseline_multiplier,
    )
    release_end_low_energy = smoothed_energy <= release_end_threshold
    for start, end in _runs(release_end_low_energy):
        candidate = max(start, release_start)
        if end - candidate >= release_confirmation_frames:
            release_end = min(release_end, max(release_start, candidate))
            break

    initial_window_end_time = (
        times[first_voiced] + heuristics.initial_placement_seconds
    )
    initial_indices = valid_indices[
        (valid_indices >= first_voiced)
        & (times[valid_indices] <= initial_window_end_time)
    ]
    if not initial_indices.size:
        initial_indices = np.array([first_voiced])
    initial_cents = _weighted_median(
        cents[initial_indices],
        voiced_probability[initial_indices],
    )

    sustain_indices = np.flatnonzero(
        note_valid
        & (np.arange(frame_count) >= sustain_start)
        & (np.arange(frame_count) < release_start)
    )
    if sustain_indices.size:
        settled_center = _weighted_median(
            cents[sustain_indices],
            voiced_probability[sustain_indices],
        )
        sustain_stability = float(np.std(cents[sustain_indices]))
    else:
        settled_center = candidate_center
        sustain_stability = None

    movement = settled_center - initial_cents
    movement_magnitude = abs(movement)
    improvement = abs(initial_cents) - abs(settled_center)
    correction_direction = "none"
    if (
        initial_cents < 0
        and movement >= heuristics.minimum_correction_magnitude_cents
        and improvement >= heuristics.minimum_correction_improvement_cents
    ):
        correction_direction = "flat_to_center"
    elif (
        initial_cents > 0
        and -movement >= heuristics.minimum_correction_magnitude_cents
        and improvement >= heuristics.minimum_correction_improvement_cents
    ):
        correction_direction = "sharp_to_center"

    correction_start: int | None = None
    if correction_direction != "none" and sustain_start > first_voiced:
        required_movement = max(
            heuristics.minimum_correction_start_movement_cents,
            movement_magnitude * heuristics.correction_start_fraction,
        )
        for index in valid_indices:
            if index >= sustain_start:
                break
            signed_movement = cents[index] - initial_cents
            if (
                correction_direction == "flat_to_center"
                and signed_movement >= required_movement
            ) or (
                correction_direction == "sharp_to_center"
                and -signed_movement >= required_movement
            ):
                correction_start = int(index)
                break
        if correction_start is None:
            correction_start = max(first_voiced, sustain_start - 1)

    if correction_start is not None:
        detected_correction_duration = float(
            times[sustain_start] - times[correction_start]
        )
        if (
            detected_correction_duration
            < heuristics.minimum_correction_duration_seconds
        ):
            # A movement shorter than the configured persistence is treated as
            # tracker/onset convergence. Its frames remain in the attack phase.
            correction_start = None
            correction_direction = "none"
            initial_cents = settled_center
            movement_magnitude = 0.0

    attack_end = correction_start if correction_start is not None else sustain_start
    phase_labels[note_start:attack_end] = PHASE_ATTACK
    if correction_start is not None:
        phase_labels[correction_start:sustain_start] = PHASE_CORRECTION
    phase_labels[sustain_start:release_start] = PHASE_SUSTAIN
    phase_labels[release_start : release_end + 1] = PHASE_RELEASE

    attack_duration = max(0.0, float(times[first_voiced] - times[note_start]))
    correction_duration = (
        max(0.0, float(times[sustain_start] - times[correction_start]))
        if correction_start is not None
        else 0.0
    )
    sustain_duration = max(
        0.0,
        float(times[release_start] - times[sustain_start]),
    )
    release_duration = max(
        0.0,
        float(times[release_end] + frame_duration - times[release_start]),
    )

    return PhaseDetectionResult(
        phase_labels=phase_labels,
        frame_energy=frame_energy,
        smoothed_energy=smoothed_energy,
        attack_start_index=note_start,
        first_voiced_index=first_voiced,
        correction_start_index=correction_start,
        sustain_start_index=sustain_start,
        sustain_end_index=sustain_end,
        release_start_index=release_start,
        release_end_index=release_end,
        attack_duration_seconds=attack_duration,
        initial_cents_offset=initial_cents,
        correction_direction=correction_direction,
        correction_magnitude_cents=(
            movement_magnitude if correction_direction != "none" else 0.0
        ),
        correction_duration_seconds=correction_duration,
        settled_pitch_center_cents=settled_center,
        sustain_duration_seconds=sustain_duration,
        sustain_pitch_stability_cents=sustain_stability,
        release_duration_seconds=release_duration,
    )
