# Information Architecture

## Purpose

This document defines the conceptual organization of Practice with Purpose.

It describes how information is structured throughout the application rather than how it is displayed.

The goal is to ensure every piece of information has a logical home and that navigation remains intuitive as the application grows.

This document is independent of implementation details such as databases, APIs, or frontend frameworks.

---

# Design Philosophy

The application is organized around the musician's practice journey.

Information should be easy to find because it naturally belongs where musicians expect it to be.

The hierarchy follows:

Application

↓

Music

↓

Piece

↓

Practice Session

↓

Recording

↓

Analysis

Rather than organizing around files or recordings, the application organizes around musical works and the musician's long-term progress.

---

# Top-Level Navigation

The application consists of six primary areas.

```
Home

My Music

Progress

Teacher

Settings

Help
```

Each area answers a different question.

| Area | Question |
|--------|----------|
| Home | What should I practice today? |
| My Music | What music do I have? |
| Progress | How am I improving? |
| Teacher | What has my teacher assigned? |
| Settings | How should the application behave? |
| Help | How do I use the application? |

---

# Home

Purpose

The Home screen is the musician's starting point.

It should surface only information that helps begin practicing quickly.

Contains

- Resume Your Progress
- Teacher Assignments
- Recommended Practice
- Recent Pieces
- Add Piece

The Home screen should never become a dashboard filled with statistics.

---

# My Music

Purpose

The musician's personal library.

Contains

- Pieces
- Collections (future)
- Favorites
- Search

Selecting a piece opens that piece's home.

---

# Piece

Every musical work has its own information space.

Each piece contains:

```
Piece

├── Metadata

├── Practice Sessions

├── Heat Map

├── Recommendations

├── Teacher Assignments

├── Progress

├── Reference Score

└── Files
```

The Piece is the application's primary organizational object.

Everything related to one musical work belongs here.

---

# Metadata

Contains information describing the music.

Examples

- Title
- Composer
- Instrument
- Difficulty
- Time Signature
- Key Signature
- Number of Measures
- Movements
- Source File

---

# Practice Sessions

A Piece contains many Practice Sessions.

```
Piece

↓

Practice Sessions

↓

July 12

↓

July 15

↓

July 18
```

Each Practice Session is independent.

Previous sessions inform recommendations but are never resumed.

---

# Practice Session

A Practice Session represents one period of focused practice.

Contains

- Date
- Duration
- Current Focus
- Goals
- Recordings
- Summary
- Observations

The Practice Session is the application's primary working object.

---

# Recordings

Each Practice Session contains one or more recordings.

```
Practice Session

├── Recording 1

├── Recording 2

├── Recording 3

└── Recording 4
```

Recordings exist to document learning.

They should not become a collection of only perfect performances.

---

# Analysis

Each Recording produces one Analysis.

Analysis contains:

- Intonation
- Rhythm
- Timing
- Dynamics
- Tempo
- Technical observations

Analysis exists to understand performance.

It does not assign a global grade.

---

# Heat Map

Each Piece maintains a Heat Map.

The Heat Map is updated over time using information from multiple Practice Sessions.

It represents practice priorities rather than musical ability.

The Heat Map belongs to the Piece rather than an individual Practice Session because it reflects long-term learning.

---

# Recommendations

Recommendations belong to a Piece.

Examples

- Practice Measures 23–25.
- Focus on intonation.
- Review dynamics before your lesson.

Recommendations are generated using:

- recent practice sessions
- teacher assignments
- recurring technical patterns
- long-term progress

---

# Progress

Progress exists at two levels.

## Piece Progress

Examples

- Heat Map evolution
- Intonation trends
- Rhythm trends
- Practice frequency
- Passage mastery

## Musician Progress

Examples

- Weekly practice time
- Practice consistency
- Repertoire growth
- Teacher assignments completed
- Overall learning trends

Progress focuses on growth rather than comparison.

---

# Teacher

Teacher information exists independently of Pieces.

Contains

- Active assignments
- Completed assignments
- Teacher notes
- Lesson history (future)

Assignments may reference multiple Pieces.

---

# Settings

Contains user preferences.

Examples

General

Recording

Metronome

Tuner

Theme

Accessibility

Notifications

Teacher Connection

Privacy

---

# Relationships

```
User

├── Pieces

│      ├── Metadata

│      ├── Practice Sessions

│      │      ├── Recordings

│      │      │      └── Analysis

│      │      └── Summary

│      │
│      ├── Heat Map

│      ├── Recommendations

│      ├── Progress

│      └── Teacher Assignments

│
├── Global Progress

├── Teacher

└── Settings
```

---

# Information Ownership

Every object has a clear owner.

| Information | Owner |
|-------------|-------|
| Piece Title | Piece |
| Composer | Piece |
| Heat Map | Piece |
| Practice History | Piece |
| Recording | Practice Session |
| Analysis | Recording |
| Session Summary | Practice Session |
| Recommendation | Piece |
| Assignment | Teacher |
| Practice Timer | Practice Session |
| User Preferences | Settings |

This prevents duplicate information and simplifies future development.

---

# Navigation Principles

Navigation should always move naturally between levels.

```
Home

↓

My Music

↓

Piece

↓

Practice Session

↓

Recording
```

The musician should always understand where they are.

No screen should require more than three interactions to begin practicing.

---

# Future Expansion

The architecture should support future capabilities without restructuring the application.

Examples include:

- Additional instruments
- Multiple teachers
- Ensembles
- Practice groups
- Cloud synchronization
- PDF annotation
- AI lesson planning
- Shared recordings
- Teacher review
- Practice challenges

The organizational hierarchy should remain stable as these capabilities are introduced.

---

# Summary

The application is organized around one central idea:

```
Musician

↓

Music

↓

Piece

↓

Practice Session

↓

Recording

↓

Analysis

↓

Guidance
```

Every piece of information should have one logical home.

The architecture should support how musicians think about practice rather than how software stores data.

When in doubt, ask:

> **Where would a musician naturally expect to find this information?**
