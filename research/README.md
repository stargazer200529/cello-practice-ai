# Pitch Analysis Research Tool

This research-only script exposes frame-level pYIN output for a single sustained
note. It does not perform note segmentation, correction detection, score
alignment, or produce recommendations.

Run commands from this `research` directory using the local `.venv` environment:

```powershell
.\.venv\Scripts\python.exe scripts\analyze_single_note.py `
  recordings\note.wav `
  --target-midi 57 `
  --output output\note.png `
  --csv output\note.csv
```

The plot contains three time-aligned panels:

1. pYIN frequency estimate
2. cents from the requested target pitch
3. pYIN voiced probability

The reliability cutoff remains the existing provisional value of `0.8`. This
tool makes the cutoff visible for research; it does not validate it or recommend
changing it.

The CSV contains one row per pYIN frame with these columns:

```text
frame_index,time_seconds,frequency_hz,voiced_flag,voiced_probability,midi_note,target_midi,cents_from_target,reliable
```

Numeric pitch fields are blank when pYIN does not produce a finite estimate.
Recordings and generated output remain local and are excluded by the repository
`.gitignore`.

Run the focused research tests from the repository root:

```powershell
research\.venv\Scripts\python.exe -m pytest research\tests `
  --basetemp research\.pytest-tmp
```
