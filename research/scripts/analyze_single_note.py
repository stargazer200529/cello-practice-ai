from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import librosa
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


A4_HZ = 440.0
FRAME_LENGTH = 2048
HOP_LENGTH = 256
RELIABLE_CONFIDENCE_THRESHOLD = 0.8
CSV_FIELDNAMES = (
    "frame_index",
    "time_seconds",
    "frequency_hz",
    "voiced_flag",
    "voiced_probability",
    "midi_note",
    "target_midi",
    "cents_from_target",
    "reliable",
)


@dataclass(frozen=True)
class AnalysisStatistics:
    total_frames: int
    voiced_frames: int
    reliable_frames: int
    reliable_frame_percentage: float
    median_reliable_cents: float | None
    mean_reliable_cents: float | None
    reliable_cents_standard_deviation: float | None


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
) -> tuple[np.ndarray, np.ndarray]:
    """Identify valid voiced frames and frames meeting the provisional cutoff."""
    valid = (
        np.asarray(voiced_flag, dtype=bool)
        & np.isfinite(f0)
        & np.isfinite(voiced_probability)
    )
    reliable = valid & (
        voiced_probability >= RELIABLE_CONFIDENCE_THRESHOLD
    )
    return valid, reliable


def calculate_statistics(
    cents: np.ndarray,
    valid: np.ndarray,
    reliable: np.ndarray,
) -> AnalysisStatistics:
    """Summarize pYIN frames without treating the cutoff as validated."""
    total_frames = int(cents.size)
    reliable_cents = cents[reliable]

    if reliable_cents.size:
        median_cents = float(np.median(reliable_cents))
        mean_cents = float(np.mean(reliable_cents))
        standard_deviation = float(np.std(reliable_cents))
    else:
        median_cents = None
        mean_cents = None
        standard_deviation = None

    return AnalysisStatistics(
        total_frames=total_frames,
        voiced_frames=int(valid.sum()),
        reliable_frames=int(reliable.sum()),
        reliable_frame_percentage=(
            100.0 * float(reliable.sum()) / total_frames
            if total_frames
            else 0.0
        ),
        median_reliable_cents=median_cents,
        mean_reliable_cents=mean_cents,
        reliable_cents_standard_deviation=standard_deviation,
    )


def create_analysis_plot(
    times: np.ndarray,
    f0: np.ndarray,
    cents: np.ndarray,
    voiced_probability: np.ndarray,
    valid: np.ndarray,
    reliable: np.ndarray,
    audio_name: str,
    target_midi: float,
) -> plt.Figure:
    """Create frequency, pitch-deviation, and confidence inspection panels."""
    figure, axes = plt.subplots(
        3,
        1,
        figsize=(12, 10),
        sharex=True,
        constrained_layout=True,
    )

    display_f0 = np.where(valid, f0, np.nan)
    axes[0].plot(
        times,
        display_f0,
        linewidth=1,
        color="tab:purple",
    )
    axes[0].set_ylabel("Frequency (Hz)")
    axes[0].set_title(f"{audio_name} — target MIDI {target_midi:g}")
    axes[0].grid(alpha=0.2)

    axes[1].plot(
        times,
        cents,
        linewidth=1,
        color="0.65",
        label="Valid voiced frame",
    )
    axes[1].scatter(
        times[reliable],
        cents[reliable],
        s=8,
        color="tab:blue",
        label=f"Confidence ≥ {RELIABLE_CONFIDENCE_THRESHOLD:.2f}",
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
        RELIABLE_CONFIDENCE_THRESHOLD,
        linestyle="--",
        linewidth=1,
        color="tab:red",
        label=(
            "Provisional reliability cutoff "
            f"({RELIABLE_CONFIDENCE_THRESHOLD:.2f})"
        ),
    )
    axes[2].set_xlabel("Time (seconds)")
    axes[2].set_ylabel("Voiced probability")
    axes[2].set_ylim(0, 1.05)
    axes[2].legend(loc="upper right")
    axes[2].grid(alpha=0.2)

    return figure


def _format_optional_float(value: float) -> str:
    return "" if not np.isfinite(value) else f"{value:.9g}"


def export_frame_csv(
    csv_path: Path,
    times: np.ndarray,
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probability: np.ndarray,
    cents: np.ndarray,
    reliable: np.ndarray,
    target_midi: float,
) -> None:
    """Export exactly one row for every frame returned by pYIN."""
    lengths = {
        len(times),
        len(f0),
        len(voiced_flag),
        len(voiced_probability),
        len(cents),
        len(reliable),
    }
    if len(lengths) != 1:
        raise ValueError("All pYIN frame arrays must have the same length.")

    midi = np.full_like(f0, np.nan, dtype=float)
    finite_f0 = np.isfinite(f0)
    midi[finite_f0] = frequency_to_midi(f0[finite_f0])

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for index in range(len(f0)):
            writer.writerow(
                {
                    "frame_index": index,
                    "time_seconds": _format_optional_float(times[index]),
                    "frequency_hz": _format_optional_float(f0[index]),
                    "voiced_flag": str(bool(voiced_flag[index])).lower(),
                    "voiced_probability": _format_optional_float(
                        voiced_probability[index]
                    ),
                    "midi_note": _format_optional_float(midi[index]),
                    "target_midi": f"{target_midi:.9g}",
                    "cents_from_target": _format_optional_float(cents[index]),
                    "reliable": str(bool(reliable[index])).lower(),
                }
            )


def print_statistics(statistics: AnalysisStatistics) -> None:
    print(f"Total pYIN frames: {statistics.total_frames}")
    print(f"Valid voiced frames: {statistics.voiced_frames}")
    print(
        "Reliable frames at provisional confidence "
        f">= {RELIABLE_CONFIDENCE_THRESHOLD:.2f}: "
        f"{statistics.reliable_frames} "
        f"({statistics.reliable_frame_percentage:.1f}%)"
    )

    if statistics.median_reliable_cents is None:
        print("No sufficiently reliable pitch frames were detected.")
        return

    print(
        "Median reliable pitch: "
        f"{statistics.median_reliable_cents:+.1f} cents"
    )
    print(
        "Mean reliable pitch: "
        f"{statistics.mean_reliable_cents:+.1f} cents"
    )
    print(
        "Reliable pitch standard deviation: "
        f"{statistics.reliable_cents_standard_deviation:.1f} cents"
    )


def analyze(
    audio_path: Path,
    target_midi: float,
    output_path: Path,
    csv_path: Path,
) -> AnalysisStatistics:
    audio, sample_rate = librosa.load(audio_path, sr=None, mono=True)

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
    )

    cents = np.full_like(f0, np.nan, dtype=float)
    cents[valid] = cents_from_target(f0[valid], target_midi)
    statistics = calculate_statistics(cents, valid, reliable)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = create_analysis_plot(
        times,
        f0,
        cents,
        voiced_probability,
        valid,
        reliable,
        audio_path.name,
        target_midi,
    )
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    export_frame_csv(
        csv_path,
        times,
        f0,
        voiced_flag,
        voiced_probability,
        cents,
        reliable,
        target_midi,
    )

    print_statistics(statistics)
    print(f"Plot saved to: {output_path}")
    print(f"Frame CSV saved to: {csv_path}")
    return statistics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect pYIN frames for one sustained cello note."
    )
    parser.add_argument("audio", type=Path)
    parser.add_argument(
        "--target-midi",
        type=float,
        required=True,
        help="Target MIDI pitch. A3 is 57.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/pitch_plot.png"),
        help="Path for the three-panel PNG plot.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Path for frame CSV (defaults to the plot path with .csv).",
    )
    args = parser.parse_args()

    if not args.audio.is_file():
        raise FileNotFoundError(f"Audio file not found: {args.audio}")

    csv_path = args.csv or args.output.with_suffix(".csv")
    analyze(args.audio, args.target_midi, args.output, csv_path)


if __name__ == "__main__":
    main()
