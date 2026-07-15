# Pitch Analysis Research Tool

This research-only script exposes frame-level pYIN output and deterministic
musical phases for one sustained note. It does not match notes, use MusicXML,
perform machine-learning inference, or produce recommendations.

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

Detected attack, correction, sustain, and release regions are color-coded across
all panels. Vertical markers identify attack start, first voiced frame,
correction start when present, sustain start and end, and release start and end.

The phase detector uses only waveform RMS, pYIN pitch estimates, pYIN voicing,
and voiced probability. Its rules are deterministic:

1. find the energy activity component containing the strongest voiced evidence
2. treat the component start as attack start and the first target-relevant valid
   pYIN estimate as the first voiced frame
3. estimate a settled center from the latter valid pitch evidence, weighted by
   voiced probability
4. find the first persistent run close to that center as sustain start, with a
   documented short-note fallback
5. label movement from a materially flat or sharp initial placement toward the
   settled center as correction
6. identify release from a persistent relative drop in waveform RMS

All numeric controls are explicitly named in
`scripts/note_phases.py` and grouped in `PhaseHeuristics`. They are experimental
inspection defaults, not literature-derived or validated cello thresholds.

Use `--reliability-threshold` to inspect classification at a selected pYIN
voiced-probability cutoff. Its default remains `0.8`, and every selected value
is provisional. This tool makes a cutoff visible for research; it does not
validate the threshold or recommend lowering it.

The CSV contains one row per pYIN frame with these columns:

```text
time_seconds,frequency_hz,midi_pitch,cents_from_target,voiced,voiced_probability,reliable,phase
```

Numeric pitch fields are blank when pYIN does not produce a finite estimate.
The `phase` value is one of `unvoiced`, `attack`, `correction`, `sustain`, or
`release`. Console output includes phase boundaries plus attack, correction,
sustain, settled-pitch, pitch-stability, and release measurements.
Recordings and generated output remain local and are excluded by the repository
`.gitignore`.

Run the focused research tests from the repository root:

```powershell
research\.venv\Scripts\python.exe -m pytest research\tests `
  --basetemp research\.pytest-tmp
```
