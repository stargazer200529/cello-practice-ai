from __future__ import annotations

import csv
import wave
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from research.scripts.analyze_single_note import (
    CSV_FIELDNAMES,
    RELIABLE_CONFIDENCE_THRESHOLD,
    analyze,
    build_frame_masks,
    calculate_statistics,
    cents_from_target,
    create_analysis_plot,
    export_frame_csv,
)


def write_pcm_sine_wave(
    path: Path,
    frequency_hz: float = 220.0,
    duration_seconds: float = 0.75,
    sample_rate: int = 22_050,
) -> None:
    times = np.arange(int(duration_seconds * sample_rate)) / sample_rate
    samples = 0.5 * np.sin(2 * np.pi * frequency_hz * times)
    pcm = np.asarray(samples * np.iinfo(np.int16).max, dtype="<i2")

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def test_masks_and_statistics_preserve_provisional_threshold() -> None:
    f0 = np.array([220.0, 221.0, 222.0, np.nan])
    voiced = np.array([True, True, True, False])
    probabilities = np.array(
        [
            RELIABLE_CONFIDENCE_THRESHOLD - 0.01,
            RELIABLE_CONFIDENCE_THRESHOLD,
            0.95,
            np.nan,
        ]
    )
    valid, reliable = build_frame_masks(f0, voiced, probabilities)
    cents = np.full_like(f0, np.nan)
    cents[valid] = cents_from_target(f0[valid], target_midi=57)

    statistics = calculate_statistics(cents, valid, reliable)

    assert valid.tolist() == [True, True, True, False]
    assert reliable.tolist() == [False, True, True, False]
    assert statistics.total_frames == 4
    assert statistics.voiced_frames == 3
    assert statistics.reliable_frames == 2
    assert statistics.reliable_frame_percentage == pytest.approx(50.0)
    assert statistics.median_reliable_cents is not None
    assert statistics.mean_reliable_cents is not None
    assert statistics.reliable_cents_standard_deviation is not None


def test_csv_exports_one_row_per_pyin_frame(tmp_path: Path) -> None:
    csv_path = tmp_path / "frames.csv"
    times = np.array([0.0, 0.01, 0.02])
    f0 = np.array([220.0, np.nan, 221.0])
    voiced = np.array([True, False, True])
    probabilities = np.array([0.9, 0.1, 0.8])
    cents = np.array([0.0, np.nan, cents_from_target(np.array([221.0]), 57)[0]])
    reliable = np.array([True, False, True])

    export_frame_csv(
        csv_path,
        times,
        f0,
        voiced,
        probabilities,
        cents,
        reliable,
        target_midi=57,
    )

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert tuple(reader.fieldnames or ()) == CSV_FIELDNAMES
    assert len(rows) == len(f0)
    assert rows[0]["frequency_hz"] == "220"
    assert rows[0]["reliable"] == "true"
    assert rows[1]["frequency_hz"] == ""
    assert rows[1]["midi_note"] == ""
    assert rows[1]["cents_from_target"] == ""
    assert rows[1]["voiced_flag"] == "false"


def test_plot_contains_three_time_aligned_panels() -> None:
    times = np.array([0.0, 0.01, 0.02])
    f0 = np.array([220.0, 220.4, np.nan])
    cents = np.array([0.0, 3.0, np.nan])
    probability = np.array([0.9, 0.85, 0.1])
    valid = np.array([True, True, False])
    reliable = np.array([True, True, False])

    figure = create_analysis_plot(
        times,
        f0,
        cents,
        probability,
        valid,
        reliable,
        "synthetic.wav",
        57,
    )

    try:
        assert len(figure.axes) == 3
        assert [axis.get_ylabel() for axis in figure.axes] == [
            "Frequency (Hz)",
            "Cents from target",
            "Voiced probability",
        ]
        assert figure.axes[2].get_xlabel() == "Time (seconds)"
    finally:
        plt.close(figure)


def test_generated_pcm_wav_runs_end_to_end(tmp_path: Path) -> None:
    wav_path = tmp_path / "synthetic-a3.wav"
    plot_path = tmp_path / "analysis.png"
    csv_path = tmp_path / "frames.csv"
    write_pcm_sine_wave(wav_path)

    statistics = analyze(wav_path, 57, plot_path, csv_path)

    assert plot_path.is_file()
    assert plot_path.stat().st_size > 0
    assert csv_path.is_file()
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == statistics.total_frames
    assert statistics.total_frames > 0
