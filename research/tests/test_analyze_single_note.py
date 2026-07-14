from __future__ import annotations

import csv
import wave
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from research.scripts.analyze_single_note import (
    CSV_FIELDNAMES,
    DEFAULT_RELIABILITY_THRESHOLD,
    analyze,
    build_frame_masks,
    calculate_statistics,
    cents_from_target,
    create_analysis_plot,
    create_argument_parser,
    export_frame_csv,
    print_statistics,
    validate_reliability_threshold,
    validate_target_midi,
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

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def test_configurable_threshold_controls_reliable_classification() -> None:
    f0 = np.array([220.0, 221.0, 222.0, np.nan])
    voiced = np.array([True, True, True, False])
    probabilities = np.array([0.49, 0.5, 0.9, np.nan])

    valid, reliable = build_frame_masks(
        f0,
        voiced,
        probabilities,
        reliability_threshold=0.5,
    )

    assert valid.tolist() == [True, True, True, False]
    assert reliable.tolist() == [False, True, True, False]


@pytest.mark.parametrize("threshold", [-0.01, 1.01, float("nan")])
def test_invalid_reliability_threshold_is_rejected(threshold: float) -> None:
    with pytest.raises(ValueError, match="from 0 to 1"):
        validate_reliability_threshold(threshold)


@pytest.mark.parametrize("target_midi", [-0.01, 127.01, float("inf")])
def test_invalid_target_midi_is_rejected(target_midi: float) -> None:
    with pytest.raises(ValueError, match="from 0 to 127"):
        validate_target_midi(target_midi)


def test_cli_uses_default_threshold_and_canonical_csv_argument(
    tmp_path: Path,
) -> None:
    wav_path = tmp_path / "note.wav"
    write_pcm_sine_wave(wav_path)
    csv_path = tmp_path / "frames.csv"

    args = create_argument_parser().parse_args(
        [
            str(wav_path),
            "--target-midi",
            "57",
            "--csv-output",
            str(csv_path),
        ]
    )

    assert args.reliability_threshold == DEFAULT_RELIABILITY_THRESHOLD
    assert args.csv_output == csv_path


def test_first_plot_panel_is_waveform_and_all_panels_share_time_axis() -> None:
    audio = np.array([0.0, 0.5, -0.5, 0.0])
    times = np.array([0.0, 0.01, 0.02])
    cents = np.array([0.0, 3.0, np.nan])
    probability = np.array([0.9, 0.85, 0.1])
    valid = np.array([True, True, False])
    reliable = np.array([True, True, False])

    figure = create_analysis_plot(
        audio,
        4,
        times,
        cents,
        probability,
        valid,
        reliable,
        "synthetic.wav",
        57,
        0.8,
    )

    try:
        axes = figure.axes
        assert len(axes) == 3
        assert [axis.get_ylabel() for axis in axes] == [
            "Amplitude",
            "Cents from target",
            "Voiced probability",
        ]
        assert axes[2].get_xlabel() == "Time (seconds)"
        np.testing.assert_allclose(axes[0].lines[0].get_ydata(), audio)
        assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])
        assert axes[0].get_shared_x_axes().joined(axes[0], axes[2])
        confidence_label = axes[2].get_legend().get_texts()[1].get_text()
        assert "provisional cutoff (0.80)" in confidence_label
    finally:
        plt.close(figure)


def test_csv_has_canonical_schema_and_blank_unvoiced_pitch_values(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "nested" / "frames.csv"
    times = np.array([0.0, 0.01, 0.02])
    f0 = np.array([220.0, np.nan, 221.0])
    voiced = np.array([True, False, True])
    probabilities = np.array([0.9, 0.1, 0.6])
    cents = np.array([0.0, np.nan, cents_from_target(np.array([221.0]), 57)[0]])

    export_frame_csv(
        csv_path,
        times,
        f0,
        voiced,
        probabilities,
        cents,
        reliability_threshold=0.7,
    )

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert tuple(reader.fieldnames or ()) == CSV_FIELDNAMES
    assert list(reader.fieldnames or ()) == [
        "time_seconds",
        "frequency_hz",
        "midi_pitch",
        "cents_from_target",
        "voiced",
        "voiced_probability",
        "reliable",
    ]
    assert len(rows) == len(f0)
    assert rows[0]["frequency_hz"] == "220"
    assert rows[0]["reliable"] == "true"
    assert rows[1]["frequency_hz"] == ""
    assert rows[1]["midi_pitch"] == ""
    assert rows[1]["cents_from_target"] == ""
    assert rows[1]["voiced"] == "false"
    assert rows[2]["reliable"] == "false"


def test_complete_confidence_statistics_are_printed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cents = np.array([-5.0, 5.0, 15.0, np.nan])
    probability = np.array([0.4, 0.8, 0.9, 0.1])
    valid = np.array([True, True, True, False])
    reliable = np.array([False, True, True, False])
    statistics = calculate_statistics(
        1.25,
        cents,
        probability,
        valid,
        reliable,
        reliability_threshold=0.8,
    )

    print_statistics(statistics)
    output = capsys.readouterr().out

    assert "Total audio duration: 1.250 seconds" in output
    assert "Total analysis frames: 4" in output
    assert "Valid voiced frames: 3 (75.0% of analysis frames)" in output
    assert "Minimum voiced probability among valid voiced frames: 0.400" in output
    assert "Maximum voiced probability among valid voiced frames: 0.900" in output
    assert "Median voiced probability among valid voiced frames: 0.800" in output
    assert "Selected reliability threshold (provisional): 0.800" in output
    assert "Reliable frames: 2 (50.0% of analysis frames)" in output
    assert "Median cents among all voiced frames: +5.0 cents" in output
    assert "Median cents among reliable frames: +10.0 cents" in output


def test_no_probability_or_pitch_summary_when_no_valid_voiced_frames(
    capsys: pytest.CaptureFixture[str],
) -> None:
    statistics = calculate_statistics(
        0.5,
        np.array([np.nan, np.nan]),
        np.array([0.1, 0.2]),
        np.array([False, False]),
        np.array([False, False]),
        reliability_threshold=0.8,
    )

    print_statistics(statistics)
    output = capsys.readouterr().out

    assert "Valid voiced frames: 0 (0.0% of analysis frames)" in output
    assert "Reliable frames: 0 (0.0% of analysis frames)" in output
    assert "No valid voiced frames were detected" in output
    assert "Minimum voiced probability" not in output
    assert "Median cents among all voiced frames" not in output


def test_generated_pcm_wav_runs_end_to_end_and_creates_directories(
    tmp_path: Path,
) -> None:
    wav_path = tmp_path / "input" / "synthetic-a3.wav"
    plot_path = tmp_path / "results" / "plots" / "analysis.png"
    csv_path = tmp_path / "results" / "csv" / "frames.csv"
    write_pcm_sine_wave(wav_path)

    statistics = analyze(
        wav_path,
        57,
        plot_path,
        csv_path,
        reliability_threshold=0.6,
    )

    assert plot_path.is_file()
    assert plot_path.stat().st_size > 0
    assert csv_path.is_file()
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == statistics.total_frames
    assert statistics.total_frames > 0
    assert statistics.audio_duration_seconds == pytest.approx(0.75, abs=0.001)
