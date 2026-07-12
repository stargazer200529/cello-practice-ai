# UI Specification

## Purpose

The user interface should support deliberate musical practice while remaining as unobtrusive as possible.

The application is not intended to replace printed sheet music.

Instead, it serves as an intelligent companion positioned beside the musician's music stand, providing recording, analysis, guidance, and long-term progress tracking.

The interface should never compete for the musician's attention.

---

# Design Goals

The interface should always be:

- Clean
- Focused
- Fast
- Encouraging
- Non-judgmental

The musician should be able to begin practicing within five seconds of opening the application.

The interface should emphasize music—not software.

---

# Application Navigation

The application consists of the following primary screens.

```
Home

↓

My Music

↓

Piece Home

↓

Practice Workspace

↓

Practice Summary
```

Supporting screens include:

- Progress
- Teacher Assignments
- Settings

---

# Global Navigation

Persistent navigation should remain simple.

Desktop

- Home
- My Music
- Progress
- Teacher
- Settings

Tablet

Collapsible navigation drawer.

Phone

Bottom navigation bar.

The application should avoid deep menu hierarchies.

---

# Home

## Purpose

Help the musician quickly decide what to practice.

## Primary Information

- Resume Your Progress
- Teacher Assignments
- Recommended Focus
- Recent Pieces
- Add Piece

## Primary Actions

- Start Practice
- Open Piece
- Add Music

The Home screen should answer:

> What should I practice today?

---

# My Music

## Purpose

Display the musician's library.

Each piece displays:

- Title
- Composer
- Last practiced
- Teacher assignment indicator
- Practice priority indicator

Selecting a piece opens that piece's home.

The screen should remain uncluttered.

This is a library—not an analysis page.

---

# Piece Home

## Purpose

Provide a complete overview of one musical work.

## Information

- Piece title
- Composer
- Overall practice status
- Practice map
- Practice heat map
- Recent practice sessions
- Teacher assignments
- Suggested focus
- Progress trends
- Reference score

## Primary Action

Start Practice

The Piece Home answers:

> Where am I with this piece?

---

# Practice Workspace

## Purpose

The Practice Workspace is the primary screen of the application.

Most user interaction occurs here.

The musician should rarely leave this screen during practice.

---

## Workspace Layout

Primary sections include:

- Session information
- Recording controls
- Contextual practice tools
- Practice notes
- Reference score (optional)

The musician may practice using printed sheet music.

The digital score is intended primarily as a reference.

---

# Session Information

Always visible.

Displays:

- Piece title
- Current passage
- Practice timer
- Today's focus
- Optional session goals

Everything remains editable.

Changing focus never restarts the session.

---

# Recording Controls

Always available.

Controls include:

- Record
- Stop
- Replay latest recording
- Recording history

Recording should require a single action.

---

# Contextual Practice Tools

The workspace adapts based on the selected practice focus.

Examples:

## Intonation

Display:

- Live tuner
- Pitch stability
- Cents sharp/flat

## Rhythm

Display:

- Tempo
- Beat indicator
- Metronome

## Dynamics

Display:

- Dynamic contour
- Volume history

## Performance

Display:

- Performance notes
- Run-through timer

Only relevant tools should appear.

The application should surface the right tools at the right time.

---

# Reference Score

The score is optional.

It serves as:

- visual reference
- measure selection
- analysis visualization

It is not intended to replace printed music.

Musicians should be able to practice entirely from paper if preferred.

---

# Practice Heat Map

The application visualizes practice priorities directly on the music.

Colors represent recommendations—not grades.

Green

Comfortable

Yellow

Needs reinforcement

Red

Recommended focus

The heat map appears:

- before practice
- after analysis

It should never update while the musician is actively playing.

The application should never distract during performance.

---

# Recording History

Each practice session contains multiple recordings.

Each recording displays:

- timestamp
- duration
- passage
- replay

Recordings document learning.

They should not encourage repeated deletion in pursuit of perfection.
Removing a recording should be a secondary action labeled:

Remove Recording

The application may ask the musician to identify why the recording is being
removed:

- Accidental recording
- Wrong piece or passage
- No usable audio
- Other

Removal should not appear as a prominent action in the normal recording
workflow. Recordings are intended to preserve the learning process rather than
only polished attempts.

---

# Practice Summary

Appears when the musician ends the session.

Displays:

- Practice duration
- Number of recordings
- Passages practiced
- Improvements observed
- Areas for future attention
- Recommended starting point for next practice

Feedback should remain encouraging.

The summary should answer:

What improved today?

What deserves attention tomorrow?

---

# Progress

Progress focuses on long-term learning.

Examples include:

- Practice frequency
- Heat map evolution
- Technique trends
- Intonation trends
- Rhythm trends
- Teacher assignments completed

Avoid emphasizing single-session scores.

Progress should highlight learning over time.

---

# Teacher Assignments

Displays:

- Assigned passages
- Teacher notes
- Due dates
- Completed assignments

Students remain free to practice anything.

Teacher assignments never prevent independent practice.

---

# Add Piece

Supports:

- MusicXML
- MXL
- PDF (future)

Displays metadata before importing.

Allows organization by:

- Composer
- Collection
- Instrument
- Difficulty
- Favorites

---

# Settings

Examples include:

General

Recording

Metronome

Tuner

Theme

Notifications

Teacher Connection

Privacy

Accessibility

---

# Empty States

The application should always guide the musician.

Examples:

No music

Import your first piece.

No recordings

Start your first practice session.

No recommendations

Practice to begin building personalized guidance.

---

# Error States

Errors should explain:

- what happened
- why
- how to fix it

Avoid technical language whenever possible.

---

# Accessibility

Support:

- keyboard navigation
- screen readers
- scalable text
- high contrast mode
- colorblind-friendly indicators

Color should never be the only method of conveying information.

---

# Responsive Design

## Desktop

Optimized for extended practice sessions.

Multiple panels visible simultaneously.

---

## Tablet

Primary practice platform.

Designed to sit beside printed sheet music on a music stand.

Large controls.

Minimal navigation.

---

## Phone

Companion experience.

Supports:

- recording
- practice guidance
- teacher assignments
- progress review

The phone interface should complement—not replace—printed music.

---

# Interaction Principles

The interface should:

- minimize clicks
- minimize interruptions
- preserve context
- remain editable
- avoid unnecessary dialogs

The musician should always remain focused on making music rather than operating software.

---

# Success

A successful interface allows the musician to forget the application exists.

It quietly records, analyzes, and guides while allowing attention to remain on:

- the instrument
- the music
- the sound
- the learning
