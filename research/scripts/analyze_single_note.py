from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import librosa
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

try:  # Support both repository imports and direct execution from research/.
    from research.scripts.note_phases import (  # noqa: E402
        DEFAULT_PHASE_HEURISTICS,
        PHASE_ATTACK,
        PHASE_CORRECTION,
        PHASE_RELEASE,
        PHASE_SUSTAIN,
        PHASE_UNVOICED,
        PhaseDetectionResult,
        PhaseHeuristics,
        calculate_frame_rms,
        detect_note_phases,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised by local CLI runs
    from note_phases import (  # type: ignore[no-redef]  # noqa: E402
        DEFAULT_PHASE_HEURISTICS,
        PHASE_ATTACK,
        PHASE_CORRECTION,
        PHASE_RELEASE,
        PHASE_SUSTAIN,
        PHASE_UNVOICED,
        PhaseDetectionResult,
        PhaseHeuristics,
        calculate_frame_rms,
        detect_note_phases,
    )


A4_HZ = 440.0
FRAME_LENGTH = 2048
HOP_LENGTH = 256
DEFAULT_RELIABILITY_THRESHOLD = 0.8
CSV_FIELDNAMES = (
    "time_seconds",
    "frequency_hz",
    "midi_pitch",
    "cents_from_target",
    "voiced",
    "voiced_probability",
    "reliable",
    "phase",
)


@dataclass(frozen=True)
class AnalysisStatistics:
    audio_duration_seconds: float
    total_frames: int
    voiced_frames: int
    voiced_frame_percentage: float
    minimum_voiced_probability: float | None
    maximum_voiced_probability: float | None
    median_voiced_probability: float | None
    reliability_threshold: float
    reliable_frames: int
    reliable_frame_percentage: float
    median_voiced_cents: float | None
    median_reliable_cents: float | None
    phase_detection: PhaseDetectionResult | None = None


def validate_audio_path(value: str | Path) -> Path:
    audio_path = Path(value)
    if not audio_path.is_file():
        raise ValueError(f"Audio file not found: {audio_path}")
    return audio_path


def validate_target_midi(value: str | float) -> float:
    try:
        target_midi = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Target MIDI must be a finite number from 0 to 127.") from exc

    if not math.isfinite(target_midi) or not 0 <= target_midi <= 127:
        raise ValueError("Target MIDI must be a finite number from 0 to 127.")
    return target_midi


def validate_reliability_threshold(value: str | float) -> float:
    try:
        threshold = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Reliability threshold must be a finite number from 0 to 1."
        ) from exc

    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError(
            "Reliability threshold must be a finite number from 0 to 1."
        )
    return threshold


def _audio_path_argument(value: str) -> Path:
    try:
        return validate_audio_path(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _target_midi_argument(value: str) -> float:
    try:
        return validate_target_midi(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _reliability_threshold_argument(value: str) -> float:
    try:
        return validate_reliability_threshold(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def frequency_to_midi(frequency_hz: np.ndarray) -> np.ndarray:
    """Convert frequency values to continuous MIDI note numbers."""
    return 69.0 + 12.0 * np.log2(frequency_hz / A4_HZ)


def cents_from_target(
    frequency_hz: np.ndarray,
    target_midi: float,
) -> np.ndarray:
    """Calculate signed cents relative to a target MIDI pitch."""
    midi = frequency_to_midi(frequency_hz)
    return 100.0 * (midi - target_midi)


def build_frame_masks(
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probability: np.ndarray,
    reliability_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Identify valid voiced frames and frames meeting a provisional cutoff."""
    threshold = validate_reliability_threshold(reliability_threshold)
    valid = (
        np.asarray(voiced_flag, dtype=bool)
        & np.isfinite(f0)
        & np.isfinite(voiced_probability)
    )
    reliable = valid & (voiced_probability >= threshold)
    return valid, reliable


def _percentage(count: int, total: int) -> float:
    return 100.0 * count / total if total else 0.0


def calculate_statistics(
    audio_duration_seconds: float,
    cents: np.ndarray,
    voiced_probability: np.ndarray,
    valid: np.ndarray,
    reliable: np.ndarray,
    reliability_threshold: float,
    phase_detection: PhaseDetectionResult | None = None,
) -> AnalysisStatistics:
    """Summarize pYIN confidence and cents without validating the cutoff."""
    threshold = validate_reliability_threshold(reliability_threshold)
    total_frames = int(cents.size)
    voiced_frames = int(valid.sum())
    reliable_frames = int(reliable.sum())

    if voiced_frames:
        valid_probabilities = voiced_probability[valid]
        minimum_probability = float(np.min(valid_probabilities))
        maximum_probability = float(np.max(valid_probabilities))
        median_probability = float(np.median(valid_probabilities))
        median_voiced_cents = float(np.median(cents[valid]))
    else:
        minimum_probability = None
        maximum_probability = None
        median_probability = None
        median_voiced_cents = None

    median_reliable_cents = (
        float(np.median(cents[reliable])) if reliable_frames else None
    )

    return AnalysisStatistics(
        audio_duration_seconds=float(audio_duration_seconds),
        total_frames=total_frames,
        voiced_frames=voiced_frames,
        voiced_frame_percentage=_percentage(voiced_frames, total_frames),
        minimum_voiced_probability=minimum_probability,
        maximum_voiced_probability=maximum_probability,
        median_voiced_probability=median_probability,
        reliability_threshold=threshold,
        reliable_frames=reliable_frames,
        reliable_frame_percentage=_percentage(reliable_frames, total_frames),
        median_voiced_cents=median_voiced_cents,
        median_reliable_cents=median_reliable_cents,
        phase_detection=phase_detection,
    )


def create_analysis_plot(
    audio: np.ndarray,
    sample_rate: int,
    times: np.ndarray,
    cents: np.ndarray,
    voiced_probability: np.ndarray,
    valid: np.ndarray,
    reliable: np.ndarray,
    audio_name: str,
    target_midi: float,
    reliability_threshold: float,
    phase_detection: PhaseDetectionResult | None = None,
) -> plt.Figure:
    """Create waveform, pitch-deviation, and confidence inspection panels."""
    threshold = validate_reliability_threshold(reliability_threshold)
    figure, axes = plt.subplots(
        3,
        1,
        figsize=(12, 10),
        sharex=True,
        constrained_layout=True,
    )

    waveform_times = np.arange(audio.size, dtype=float) / sample_rate
    axes[0].plot(waveform_times, audio, linewidth=0.6, color="tab:gray")
    axes[0].set_ylabel("Amplitude")
    axes[0].set_title(f"{audio_name} — target MIDI {target_midi:g}")
    axes[0].grid(alpha=0.2)

    display_cents = np.where(valid, cents, np.nan)
    axes[1].plot(
        times,
        display_cents,
        linewidth=1,
        color="0.65",
        label="Valid voiced frame",
    )
    axes[1].scatter(
        times[reliable],
        cents[reliable],
        s=8,
        color="tab:blue",
        label=f"Confidence ≥ {threshold:.2f}",
        zorder=3,
    )
    axes[1].axhline(0, linestyle="--", linewidth=1, color="black")
    axes[1].axhline(10, linestyle=":", linewidth=1, color="tab:green")
    axes[1].axhline(-10, linestyle=":", linewidth=1, color="tab:green")
    axes[1].set_ylabel("Cents from target")
    axes[1].set_ylim(-100, 100)
    axes[1].legend(loc="upper right")
    axes[1].grid(alpha=0.2)

    axes[2].plot(
        times,
        voiced_probability,
        linewidth=1,
        color="tab:orange",
        label="pYIN voiced probability",
    )
    axes[2].axhline(
        threshold,
        linestyle="--",
        linewidth=1,
        color="tab:red",
        label=f"Selected provisional cutoff ({threshold:.2f})",
    )
    axes[2].set_xlabel("Time (seconds)")
    axes[2].set_ylabel("Voiced probability")
    axes[2].set_ylim(0, 1.05)
    axes[2].legend(loc="upper right")
    axes[2].grid(alpha=0.2)

    if phase_detection is not None:
        phase_colors = {
            PHASE_ATTACK: "tab:orange",
            PHASE_CORRECTION: "tab:blue",
            PHASE_SUSTAIN: "tab:green",
            PHASE_RELEASE: "tab:red",
        }
        # Contiguous phase spans use the same color on every panel so the
        # waveform, cents contour, and confidence trace remain visually aligned.
        for phase_name, phase_color in phase_colors.items():
            phase_mask = phase_detection.phase_labels == phase_name
            for start, end in _true_runs(phase_mask):
                start_time = times[start]
                end_time = (
                    times[end]
                    if end < len(times)
                    else times[-1] + _analysis_frame_duration(times)
                )
                for axis in axes:
                    axis.axvspan(start_time, end_time, color=phase_color, alpha=0.08)

        marker_colors = {
            "Attack start": "darkorange",
            "First voiced": "purple",
            "Correction start": "royalblue",
            "Sustain start": "forestgreen",
            "Sustain end": "olive",
            "Release start": "firebrick",
            "Release end": "brown",
        }
        # Every detected event receives a vertical marker on all three panels.
        # Labels are attached only to the waveform panel to avoid duplicate keys.
        for event_label, event_index in phase_detection.event_indices():
            event_time = times[event_index]
            for axis_index, axis in enumerate(axes):
                axis.axvline(
                    event_time,
                    color=marker_colors[event_label],
                    linestyle="--",
                    linewidth=0.9,
                    alpha=0.8,
                    label=event_label if axis_index == 0 else None,
                )
        if phase_detection.event_indices():
            axes[0].legend(loc="upper right", fontsize="small", ncol=2)

    return figure


def _true_runs(mask: np.ndarray) -> list[tuple[int, int]]:
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


def _analysis_frame_duration(times: np.ndarray) -> float:
    if len(times) < 2:
        return 0.0
    return float(np.median(np.diff(times)))


def _format_optional_float(value: float) -> str:
    return "" if not np.isfinite(value) else f"{value:.9g}"


def export_frame_csv(
    csv_path: Path,
    times: np.ndarray,
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probability: np.ndarray,
    cents: np.ndarray,
    reliability_threshold: float,
    phase_labels: np.ndarray | None = None,
) -> None:
    """Export exactly one row for every frame returned by pYIN."""
    if phase_labels is None:
        phase_labels = np.full(len(times), PHASE_UNVOICED, dtype="<U10")
    lengths = {
        len(times),
        len(f0),
        len(voiced_flag),
        len(voiced_probability),
        len(cents),
        len(phase_labels),
    }
    if len(lengths) != 1:
        raise ValueError("All pYIN frame arrays must have the same length.")

    valid, reliable = build_frame_masks(
        f0,
        voiced_flag,
        voiced_probability,
        reliability_threshold,
    )
    midi = np.full_like(f0, np.nan, dtype=float)
    midi[valid] = frequency_to_midi(f0[valid])

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for index in range(len(f0)):
            writer.writerow(
                {
                    "time_seconds": _format_optional_float(times[index]),
                    "frequency_hz": (
                        _format_optional_float(f0[index]) if valid[index] else ""
                    ),
                    "midi_pitch": (
                        _format_optional_float(midi[index]) if valid[index] else ""
                    ),
                    "cents_from_target": (
                        _format_optional_float(cents[index]) if valid[index] else ""
                    ),
                    "voiced": str(bool(voiced_flag[index])).lower(),
                    "voiced_probability": _format_optional_float(
                        voiced_probability[index]
                    ),
                    "reliable": str(bool(reliable[index])).lower(),
                    "phase": str(phase_labels[index]),
                }
            )


def print_statistics(statistics: AnalysisStatistics) -> None:
    print(f"Total audio duration: {statistics.audio_duration_seconds:.3f} seconds")
    print(f"Total analysis frames: {statistics.total_frames}")
    print(
        f"Valid voiced frames: {statistics.voiced_frames} "
        f"({statistics.voiced_frame_percentage:.1f}% of analysis frames)"
    )

    if statistics.voiced_frames:
        print(
            "Minimum voiced probability among valid voiced frames: "
            f"{statistics.minimum_voiced_probability:.3f}"
        )
        print(
            "Maximum voiced probability among valid voiced frames: "
            f"{statistics.maximum_voiced_probability:.3f}"
        )
        print(
            "Median voiced probability among valid voiced frames: "
            f"{statistics.median_voiced_probability:.3f}"
        )

    print(
        "Selected reliability threshold (provisional): "
        f"{statistics.reliability_threshold:.3f}"
    )
    print(
        f"Reliable frames: {statistics.reliable_frames} "
        f"({statistics.reliable_frame_percentage:.1f}% of analysis frames)"
    )

    if not statistics.voiced_frames:
        print("No valid voiced frames were detected; pitch statistics unavailable.")
        return

    print(
        "Median cents among all voiced frames: "
        f"{statistics.median_voiced_cents:+.1f} cents"
    )
    if statistics.median_reliable_cents is not None:
        print(
            "Median cents among reliable frames: "
            f"{statistics.median_reliable_cents:+.1f} cents"
        )


def print_phase_detection(phases: PhaseDetectionResult) -> None:
    def format_seconds(value: float | None) -> str:
        return "unavailable" if value is None else f"{value:.3f} seconds"

    def format_cents(value: float | None) -> str:
        return "unavailable" if value is None else f"{value:+.1f} cents"

    direction_labels = {
        "flat_to_center": "Flat -> Center",
        "sharp_to_center": "Sharp -> Center",
        "none": "None",
    }
    print("Note phase measurements:")
    print(f"  Attack duration: {format_seconds(phases.attack_duration_seconds)}")
    print(f"  Initial cents offset: {format_cents(phases.initial_cents_offset)}")
    print(f"  Correction direction: {direction_labels[phases.correction_direction]}")
    print(f"  Correction magnitude: {phases.correction_magnitude_cents:.1f} cents")
    print(
        "  Correction duration: "
        f"{phases.correction_duration_seconds:.3f} seconds"
    )
    print(
        "  Settled pitch center: "
        f"{format_cents(phases.settled_pitch_center_cents)}"
    )
    print(f"  Sustain duration: {phases.sustain_duration_seconds:.3f} seconds")
    print(
        "  Sustain pitch stability: "
        + (
            "unavailable"
            if phases.sustain_pitch_stability_cents is None
            else f"{phases.sustain_pitch_stability_cents:.1f} cents"
        )
    )
    print(f"  Release duration: {phases.release_duration_seconds:.3f} seconds")


def analyze(
    audio_path: Path,
    target_midi: float,
    output_path: Path,
    csv_output_path: Path,
    reliability_threshold: float = DEFAULT_RELIABILITY_THRESHOLD,
    phase_heuristics: PhaseHeuristics = DEFAULT_PHASE_HEURISTICS,
) -> AnalysisStatistics:
    audio_path = validate_audio_path(audio_path)
    target_midi = validate_target_midi(target_midi)
    threshold = validate_reliability_threshold(reliability_threshold)

    audio, sample_rate = librosa.load(audio_path, sr=None, mono=True)
    audio_duration_seconds = audio.size / sample_rate

    f0, voiced_flag, voiced_probability = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sample_rate,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH,
    )

    times = librosa.times_like(
        f0,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
    )
    valid, reliable = build_frame_masks(
        f0,
        voiced_flag,
        voiced_probability,
        threshold,
    )

    cents = np.full_like(f0, np.nan, dtype=float)
    cents[valid] = cents_from_target(f0[valid], target_midi)
    frame_energy = calculate_frame_rms(
        audio,
        FRAME_LENGTH,
        HOP_LENGTH,
        len(times),
    )
    phase_detection = detect_note_phases(
        times,
        cents,
        valid,
        voiced_probability,
        frame_energy,
        phase_heuristics,
    )
    statistics = calculate_statistics(
        audio_duration_seconds,
        cents,
        voiced_probability,
        valid,
        reliable,
        threshold,
        phase_detection,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = create_analysis_plot(
        audio,
        sample_rate,
        times,
        cents,
        voiced_probability,
        valid,
        reliable,
        audio_path.name,
        target_midi,
        threshold,
        phase_detection,
    )
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    export_frame_csv(
        csv_output_path,
        times,
        f0,
        voiced_flag,
        voiced_probability,
        cents,
        threshold,
        phase_detection.phase_labels,
    )

    print_statistics(statistics)
    print_phase_detection(phase_detection)
    print(f"Plot saved to: {output_path}")
    print(f"Frame CSV saved to: {csv_output_path}")
    return statistics


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect pYIN frames for one sustained cello note."
    )
    parser.add_argument("audio", type=_audio_path_argument)
    parser.add_argument(
        "--target-midi",
        type=_target_midi_argument,
        required=True,
        help="Finite target MIDI pitch from 0 to 127. A3 is 57.",
    )
    parser.add_argument(
        "--reliability-threshold",
        type=_reliability_threshold_argument,
        default=DEFAULT_RELIABILITY_THRESHOLD,
        help=(
            "Provisional pYIN voiced-probability cutoff from 0 to 1 "
            f"(default: {DEFAULT_RELIABILITY_THRESHOLD})."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/pitch_plot.png"),
        help="Path for the three-panel PNG plot.",
    )
    parser.add_argument(
        "--csv-output",
        "--csv",
        dest="csv_output",
        type=Path,
        help="Path for frame CSV (defaults to the plot path with .csv).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = create_argument_parser()
    args = parser.parse_args(argv)
    csv_output_path = args.csv_output or args.output.with_suffix(".csv")
    analyze(
        args.audio,
        args.target_midi,
        args.output,
        csv_output_path,
        args.reliability_threshold,
    )


if __name__ == "__main__":
    main()
