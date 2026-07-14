# Pitch Analysis Research Tool

This research-only script exposes frame-level pYIN output for a single sustained
note. It does not perform note segmentation, correction detection, score
alignment, or produce recommendations.

Run commands from this `research` directory using the local `.venv` environment:

```powershell
.\.venv\Scripts\python.exe scripts\analyze_single_note.py `
  recordings\note.wav `
  --target-midi 57 `
  --reliability-threshold 0.8 `
  --output output\note.png `
  --csv-output output\note.csv
```

The plot contains three time-aligned panels:

1. waveform amplitude
2. cents from the requested target pitch
3. pYIN voiced probability

Use `--reliability-threshold` to inspect classification at a selected pYIN
voiced-probability cutoff. Its default remains `0.8`, and every selected value
is provisional. This tool makes a cutoff visible for research; it does not
validate the threshold or recommend lowering it.

The CSV contains one row per pYIN frame with these columns:

```text
time_seconds,frequency_hz,midi_pitch,cents_from_target,voiced,voiced_probability,reliable
```

Numeric pitch fields are blank when pYIN does not produce a finite estimate.
Recordings and generated output remain local and are excluded by the repository
`.gitignore`.

Run the focused research tests from the repository root:

```powershell
research\.venv\Scripts\python.exe -m pytest research\tests `
  --basetemp research\.pytest-tmp
```
