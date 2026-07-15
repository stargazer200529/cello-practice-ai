from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from research.scripts.analyze_single_note import create_analysis_plot
from research.scripts.note_phases import (
    PHASE_ATTACK,
    PHASE_CORRECTION,
    PHASE_RELEASE,
    PHASE_SUSTAIN,
    PHASE_UNVOICED,
    PhaseHeuristics,
    detect_note_phases,
)


TEST_HEURISTICS = PhaseHeuristics(
    energy_activity_ratio=0.1,
    energy_reference_percentile=90.0,
    energy_smoothing_seconds=0.0,
    maximum_target_deviation_cents=200.0,
    minimum_activity_seconds=0.01,
    maximum_activity_gap_seconds=0.01,
    attack_energy_ratio=0.2,
    initial_placement_seconds=0.03,
    settled_reference_fraction=0.5,
    sustain_center_tolerance_cents=5.0,
    minimum_sustain_seconds=0.03,
    maximum_settled_gap_seconds=0.0,
    minimum_short_sustain_frames=2,
    minimum_correction_magnitude_cents=12.0,
    minimum_correction_improvement_cents=6.0,
    correction_start_fraction=0.2,
    minimum_correction_start_movement_cents=3.0,
    minimum_correction_duration_seconds=0.02,
    release_energy_ratio=0.5,
    release_confirmation_seconds=0.02,
    release_end_energy_ratio=0.1,
    release_baseline_multiplier=1.5,
)


def sustained_note_contour(
    frame_count: int = 30,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = np.arange(frame_count, dtype=float) * 0.01
    energy = np.zeros(frame_count)
    energy[2] = 0.2
    energy[3] = 0.6
    energy[4:24] = 1.0
    energy[24] = 0.6
    energy[25] = 0.3
    energy[26] = 0.1
    valid = np.zeros(frame_count, dtype=bool)
    valid[4:24] = True
    probability = np.full(frame_count, 0.05)
    probability[valid] = 0.9
    cents = np.full(frame_count, np.nan)
    cents[valid] = 0.0
    return times, cents, valid, probability, energy


def test_perfectly_centered_note_has_attack_sustain_and_release() -> None:
    times, cents, valid, probability, energy = sustained_note_contour()

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        TEST_HEURISTICS,
    )

    assert result.attack_start_index == 2
    assert result.first_voiced_index == 4
    assert result.correction_start_index is None
    assert result.sustain_start_index == 4
    assert result.sustain_end_index == 24
    assert result.release_start_index == 25
    assert result.release_end_index == 26
    assert result.initial_cents_offset == pytest.approx(0.0)
    assert result.correction_direction == "none"
    assert result.settled_pitch_center_cents == pytest.approx(0.0)
    assert result.sustain_pitch_stability_cents == pytest.approx(0.0)
    assert result.phase_labels[0] == PHASE_UNVOICED
    assert result.phase_labels[2] == PHASE_ATTACK
    assert result.phase_labels[4] == PHASE_SUSTAIN
    assert result.phase_labels[25] == PHASE_RELEASE


def test_flat_note_corrected_upward_detects_correction() -> None:
    times, cents, valid, probability, energy = sustained_note_contour()
    cents[4:8] = -30.0
    cents[8] = -24.0
    cents[9] = -15.0
    cents[10] = -6.0

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        TEST_HEURISTICS,
    )

    assert result.correction_direction == "flat_to_center"
    assert result.initial_cents_offset == pytest.approx(-30.0)
    assert result.correction_magnitude_cents == pytest.approx(30.0)
    assert result.correction_start_index == 8
    assert result.sustain_start_index == 11
    assert result.correction_duration_seconds == pytest.approx(0.03)
    assert np.all(result.phase_labels[8:11] == PHASE_CORRECTION)


def test_sharp_note_corrected_downward_detects_correction() -> None:
    times, cents, valid, probability, energy = sustained_note_contour()
    cents[4:8] = 30.0
    cents[8] = 24.0
    cents[9] = 15.0
    cents[10] = 6.0

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        TEST_HEURISTICS,
    )

    assert result.correction_direction == "sharp_to_center"
    assert result.initial_cents_offset == pytest.approx(30.0)
    assert result.correction_magnitude_cents == pytest.approx(30.0)
    assert result.correction_start_index == 8
    assert result.sustain_start_index == 11
    assert np.all(result.phase_labels[8:11] == PHASE_CORRECTION)


def test_attack_without_correction_reports_attack_duration() -> None:
    times, cents, valid, probability, energy = sustained_note_contour()
    valid[4:6] = False
    probability[4:6] = 0.05
    cents[4:6] = np.nan

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        TEST_HEURISTICS,
    )

    assert result.attack_start_index == 2
    assert result.first_voiced_index == 6
    assert result.attack_duration_seconds == pytest.approx(0.04)
    assert result.correction_direction == "none"
    assert result.correction_duration_seconds == 0.0


def test_short_sustain_uses_deterministic_stable_run_fallback() -> None:
    frame_count = 14
    times = np.arange(frame_count, dtype=float) * 0.01
    energy = np.zeros(frame_count)
    energy[2:9] = 1.0
    energy[9] = 0.4
    energy[10] = 0.2
    valid = np.zeros(frame_count, dtype=bool)
    valid[4:8] = True
    probability = np.full(frame_count, 0.05)
    probability[valid] = 0.9
    cents = np.full(frame_count, np.nan)
    cents[valid] = 2.0
    short_note_heuristics = replace(
        TEST_HEURISTICS,
        minimum_sustain_seconds=0.08,
    )

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        short_note_heuristics,
    )

    assert result.sustain_start_index == 4
    assert result.sustain_duration_seconds > 0
    assert result.settled_pitch_center_cents == pytest.approx(2.0)
    assert PHASE_SUSTAIN in result.phase_labels


def test_noisy_release_does_not_extend_note_to_isolated_energy_spike() -> None:
    times, cents, valid, probability, energy = sustained_note_contour(35)
    energy[31] = 1.5
    noisy_release_heuristics = replace(
        TEST_HEURISTICS,
        minimum_activity_seconds=0.02,
    )

    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        noisy_release_heuristics,
    )

    assert result.release_end_index == 26
    assert result.phase_labels[31] == PHASE_UNVOICED
    assert result.release_duration_seconds > 0


def test_plot_overlays_all_detected_event_markers() -> None:
    times, cents, valid, probability, energy = sustained_note_contour()
    cents[4:8] = -30.0
    cents[8] = -24.0
    cents[9] = -15.0
    cents[10] = -6.0
    result = detect_note_phases(
        times,
        cents,
        valid,
        probability,
        energy,
        TEST_HEURISTICS,
    )
    audio = np.sin(2 * np.pi * np.arange(300) / 20)
    reliable = valid.copy()

    figure = create_analysis_plot(
        audio,
        1000,
        times,
        cents,
        probability,
        valid,
        reliable,
        "synthetic.wav",
        57,
        0.8,
        result,
    )

    try:
        waveform_legend = figure.axes[0].get_legend()
        marker_labels = {text.get_text() for text in waveform_legend.get_texts()}
        assert marker_labels == {label for label, _ in result.event_indices()}
        assert "Correction start" in marker_labels
        for axis in figure.axes:
            assert len(axis.patches) >= 3
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)
