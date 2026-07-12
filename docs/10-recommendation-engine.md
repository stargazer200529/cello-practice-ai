# Recommendation Engine

## Purpose

This document defines how **Practice with Purpose** converts analysis evidence, practice history, teacher guidance, and musician goals into clear, actionable practice recommendations.

The recommendation engine does not decide what the musician must practice.

It identifies useful next steps and explains why they are being suggested.

The engine should answer:

> **What should I practice next, and why?**

---

# Recommendation Philosophy

Recommendations must be:

- specific
- explainable
- optional
- evidence-based
- appropriately scoped
- actionable
- respectful of musical interpretation
- aligned with the musician's current goals

The application recommends.

Teachers assign.

The musician decides.

The recommendation engine must never behave as though it has authority over the musician or teacher.

---

# Core Principles

## Guide, Do Not Judge

Recommendations should direct attention without assigning grades.

Prefer:

> Practice Measures 24–26 at a slower tempo. The shift into Measure 25 was late in three recordings.

Avoid:

> This passage is poor.

## Explain the Evidence

Every recommendation should state:

- where the issue occurred
- what happened
- how often it happened
- why it matters
- what to try next

## Recommend the Smallest Useful Action

A recommendation should be narrow enough to practice immediately.

Prefer:

> Isolate the shift into Measure 26 and repeat it three times without vibrato.

Avoid:

> Improve intonation.

## Respect Context

The engine should consider:

- current practice focus
- selected passage
- teacher assignments
- target tempo
- recent attempts
- long-term patterns
- signal confidence
- session duration
- whether the musician is learning, reinforcing, or performing

## Preserve Musician Control

Recommendations may be:

- accepted
- modified
- deferred
- dismissed
- ignored

No recommendation should block recording, practicing, or ending a session.

---

# Scope

## Initial Recommendation Scope

The first implementation should recommend:

- passages to isolate
- categories to focus on
- simple practice methods
- when to repeat
- when to slow down
- when to remove vibrato
- when to compare attempts
- where to begin next session

## Future Scope

Later versions may recommend:

- tempo progression
- distributed practice
- repertoire maintenance
- lesson preparation
- warm-up selection
- review scheduling
- mixed-practice strategies
- teacher-approved exercises
- technique-specific drills
- performance run-through timing

---

# Non-Goals

The recommendation engine will not:

- prescribe artistic interpretation as objectively correct
- replace a teacher
- infer physical technique without evidence
- force completion of recommendations
- produce a universal practice score
- create public rankings
- reward excessive repetition
- recommend unsupported medical or physical interventions
- treat every measurable deviation as a problem
- assume one practice method works for every musician

---

# Inputs

The engine may use the following inputs.

## Analysis Evidence

- Measure Observations
- Pitch Observations
- Rhythm Observations
- Timing Observations
- Dynamic Observations
- Technical Patterns
- Analysis confidence
- Signal-quality warnings
- Alignment confidence

## Practice Context

- Piece
- Movement
- Current passage
- Practice focus
- Practice goals
- Target tempo
- Session duration
- Recording count
- Recent attempts
- Practice source

## Long-Term Context

- Practice Map States
- prior sessions
- previous recommendations
- recommendation outcomes
- recurring patterns
- time since last practice
- improvement trends
- regression or retention evidence

## Teacher Context

- active assignments
- teacher notes
- due dates
- teacher-selected passages
- teacher-selected focus areas

## Musician Context

- user-selected goals
- user notes
- dismissed recommendations
- accepted recommendations
- preferred practice methods
- available practice time
- accessibility settings

---

# High-Level Flow

```text
Analysis Evidence
       +
Practice Context
       +
Teacher and Musician Intent
       ↓
Candidate Recommendation Generation
       ↓
Evidence Validation
       ↓
Priority Calculation
       ↓
Conflict Resolution
       ↓
Recommendation Selection
       ↓
Action Wording
       ↓
Presentation
       ↓
Outcome Tracking
```

---

# Recommendation Object

Each recommendation should contain:

```text
Recommendation
├── piece
├── passage
├── focus category
├── title
├── reason
├── supporting evidence
├── suggested method
├── estimated time
├── priority
├── source type
├── status
├── created date
├── expiration
└── supersession link
```

## Example

```text
Title:
Reinforce the shift into Measure 24

Passage:
Measures 23–25

Focus:
Intonation

Reason:
The F-sharp after the shift averaged 18 cents flat in three recordings.

Suggested method:
Practice the shift separately at a slower tempo.
Remove vibrato for the first three repetitions.
Then add vibrato and record one final attempt.

Estimated time:
8 minutes
```

---

# Recommendation Types

## Passage Focus

Identifies a passage that deserves attention.

Example:

> Focus on Measures 24–27.

## Technical Focus

Identifies a measurable category.

Examples:

- intonation
- rhythm
- timing
- dynamics
- tempo stability

## Practice Method

Suggests how to work.

Examples:

- slow tempo
- remove vibrato
- isolate transition
- clap rhythm
- subdivide
- repeat short groups
- record three attempts
- compare first and last attempt

## Review Recommendation

Suggests returning to material that may need reinforcement.

## Maintenance Recommendation

Suggests brief review of previously comfortable material.

## Teacher Assignment Recommendation

Surfaces teacher-provided work.

## Session Start Recommendation

Defines where to begin the next session.

## Stop or Move-On Recommendation

Future versions may suggest moving on when:

- the passage is consistently stable
- practice quality is declining
- repetition is no longer producing useful change
- the planned goal has been met

This must be phrased carefully and never prevent continued practice.

---

# Candidate Generation

The engine should generate multiple candidate recommendations before selecting what to show.

## Candidate Sources

### Analysis-Based

Generated from:

- severe observations
- repeated observations
- high-confidence patterns
- unstable passages
- meaningful within-session regressions
- unresolved prior issues

### Teacher-Based

Generated from:

- active assignment
- upcoming due date
- teacher note
- teacher-selected passage

### Musician-Based

Generated from:

- current focus
- current goal
- selected passage
- personal notes
- manually chosen practice item

### Long-Term

Generated from:

- recurring pattern
- retention decline
- neglected piece
- previously recommended passage
- slow improvement
- repeated incomplete goal

---

# Candidate Eligibility

A candidate should be rejected when:

- confidence is too low
- signal quality is insufficient
- score alignment is ambiguous
- the issue is musically trivial
- the evidence is isolated and minor
- the same recommendation was recently dismissed
- the recommendation duplicates an active one
- the suggested method is unsupported
- the passage is outside the musician's selected scope without strong reason
- the recommendation conflicts with teacher guidance without explanation

---

# Priority Model

Priority should be calculated internally.

The user should not see a numeric score.

## Priority Factors

### Severity

How significant is the issue?

### Frequency

How often has it occurred?

### Recency

How recently did it occur?

### Confidence

How reliable is the evidence?

### Persistence

Has it continued across attempts or sessions?

### Selected Focus

Does it align with the musician's current focus?

### Teacher Relevance

Is it part of an active teacher assignment?

### Dependency

Does the issue cause later problems?

### Practice Efficiency

Can a short focused action produce meaningful improvement?

### Readiness

Is the musician in a position to work on it now?

### Fatigue or Over-Repetition

Has the musician already spent too long on it?

---

# Suggested Internal Priority Formula

A configurable internal model may combine:

```text
priority =
    severity_weight
  × confidence_weight
  × recurrence_weight
  × recency_weight
  × context_weight
  × dependency_weight
```

This is conceptual.

The implementation may use rules rather than a single mathematical formula initially.

Internal priority must never become a user-facing mastery grade.

---

# Recurrence Model

Recurrence should increase priority.

## Evidence Levels

```text
Observed once
Observed repeatedly within one recording
Observed across recordings in one session
Observed across multiple sessions
Long-term tendency
```

## Example

Single event:

> Measure 18 was 14 cents flat once.

Repeated session pattern:

> Measure 18 averaged 17 cents flat across three attempts.

Long-term pattern:

> F-sharps in this passage have trended flat across three sessions.

Long-term repeated evidence should generally rank above one isolated event.

---

# Recency Model

Recent evidence should normally weigh more than old evidence.

However:

- long-term unresolved patterns remain relevant
- old isolated issues should fade
- previously resolved issues should not dominate
- reappearing issues should regain priority

A recommendation may expire when:

- the issue no longer appears
- the score changes
- the assignment ends
- the user dismisses it
- newer evidence supersedes it

---

# Dependency Model

Some problems cause later problems.

Examples:

- late shift causes following notes to rush
- unstable pickup causes phrase tempo drift
- poor bow distribution weakens later crescendo
- misread rhythm disrupts subsequent alignment

The engine may raise priority when an issue is a likely upstream cause.

It should explain this relationship carefully.

Preferred:

> The late shift into Measure 26 also delayed the next two notes.

Avoid:

> Your shift caused the whole passage to fail.

---

# Practice Map Integration

Practice Map States help identify where recommendations should focus.

## Label Meaning

- Comfortable
- Needs reinforcement
- Recommended focus
- Insufficient data

## Rules

- A red visual state does not automatically require a recommendation.
- The engine should avoid showing too many red areas at once.
- Recommendations should select the highest-value passage, not every flagged measure.
- Multiple adjacent measures may be grouped into one passage.
- Different categories may produce separate recommendations for the same measure.
- User-selected focus may determine which category is surfaced first.

---

# Passage Grouping

The engine should group nearby observations into practical passages.

## Example

Individual evidence:

```text
Measure 24: shift late
Measure 25: F-sharp flat
Measure 26: rhythm compressed
```

Possible grouped recommendation:

> Practice Measures 24–26. Isolate the shift first, then reconnect the three measures at a slower tempo.

## Grouping Rules

Group observations when:

- measures are adjacent
- one issue causes the next
- the same method addresses all observations
- the passage remains short enough to practice effectively

Do not group when:

- issues are unrelated
- the passage becomes too long
- different methods are required
- evidence confidence differs substantially

---

# Practice Method Library

Recommendations should draw from a controlled library of practice methods.

Each method should define:

- suitable categories
- prerequisites
- contraindications
- recommended passage length
- suggested repetition range
- explanation
- expected outcome

---

## Slow Practice

### Appropriate For

- unstable rhythm
- difficult shifts
- note accuracy
- coordination
- early learning

### Suggested Wording

> Reduce the tempo until the passage feels controlled, then record three attempts.

### Caution

Slow practice should not be recommended indefinitely.

The engine should eventually support gradual tempo return.

---

## Remove Vibrato

### Appropriate For

- pitch-center work
- shift destination accuracy
- sustained intonation

### Suggested Wording

> Practice the note without vibrato first so the pitch center is easier to hear.

### Caution

Do not imply that vibrato is the problem.

---

## Isolate the Transition

### Appropriate For

- shifts
- string crossings
- entrances
- hand-position changes
- difficult note pairs

### Suggested Wording

> Practice only the transition into Measure 26 before reconnecting the full phrase.

---

## Rhythmic Subdivision

### Appropriate For

- compressed rhythms
- uneven subdivisions
- unstable pulse
- complex rests

### Suggested Wording

> Subdivide the beat and practice the rhythm without worrying about full tempo.

---

## Rhythm-Only Practice

### Appropriate For

- repeated timing errors
- unfamiliar rhythmic patterns

Examples:

- clap
- tap
- speak counts
- play on open strings

### Caution

The engine should not recommend a method the app cannot explain clearly.

---

## Repetition Set

### Appropriate For

- short isolated passages
- comparison across attempts
- measurable correction

### Suggested Wording

> Record three repetitions and compare whether the pitch center becomes more consistent.

### Caution

Avoid encouraging excessive repetition.

A default range of three to five attempts is more appropriate than open-ended repetition.

---

## Compare Attempts

### Appropriate For

- within-session progress
- self-reflection
- consistency work

### Suggested Wording

> Replay the first and most recent attempts and listen for the shift into Measure 24.

---

## Reduce Passage Length

### Appropriate For

- mixed errors across a long passage
- low alignment confidence
- overload
- inconsistent results

### Suggested Wording

> Narrow the passage to Measures 24–25 before reconnecting the larger section.

---

## Reconnect the Phrase

### Appropriate For

- issue improved in isolation
- transition back to context

### Suggested Wording

> Reconnect Measures 23–27 and record one full attempt.

---

# Successful Repetition

A successful repetition must not be defined only by perfection.

It may mean:

- the selected issue improved
- no high-severity error occurred
- rhythm remained within configured tolerance
- pitch center stayed within target range
- the musician manually marked the attempt successful

## Rules

- The success definition should match the current goal.
- The application should explain what counted.
- The user may override or confirm success.
- Success should not require every category to be perfect.
- The threshold should be configurable and evidence-based.

---

# Recommendation Selection

The engine should limit what is shown.

## Home

Show:

- one primary recommendation
- optional teacher assignment
- a small number of recent alternatives

## Piece Home

Show:

- one primary recommendation
- up to two secondary recommendations
- practice-map context

## Practice Workspace

Show:

- current focus
- current passage
- contextual tool
- quiet post-recording suggestion

Do not surface a full recommendation list while the musician is actively playing.

## Session Summary

Show:

- one main continuation recommendation
- supporting method
- optional teacher reminder

---

# Recommendation Diversity

The engine should avoid repeating the same recommendation indefinitely.

## Diversity Rules

- do not repeat identical wording every session
- do not recommend the same method after repeated failure without reconsideration
- rotate between compatible methods when useful
- recognize improvement
- reduce priority when the issue is resolving
- surface a different high-value issue when appropriate

## Example

Session 1:

> Practice the shift without vibrato.

Session 2:

> The pitch center improved. Reconnect the shift to Measures 23–25.

Session 3:

> The passage is now stable at 60 BPM. Increase tempo slightly.

This progression is more useful than repeating the original instruction.

---

# Conflict Resolution

Recommendations may conflict.

## Possible Conflicts

- teacher assignment versus app recommendation
- musician-selected focus versus high-severity issue
- two categories in the same passage
- multiple pieces needing attention
- short available time versus broad assignment
- app recommendation versus dismissed method

## Resolution Order

A reasonable default hierarchy:

1. safety and data integrity
2. explicit musician choice
3. active teacher assignment
4. high-confidence recurring issue
5. current session focus
6. recent recommendation continuity
7. maintenance or review

This hierarchy should not be absolute.

The musician remains free to choose differently.

## Presentation

When a conflict matters, explain it.

Example:

> Your teacher assigned Measures 40–48. The app also detected a repeated intonation issue in Measures 24–25. Start with the assignment, or choose the shorter intonation review.

---

# Teacher Assignment Integration

Teacher assignments are not generated by the recommendation engine.

They are authoritative teacher guidance surfaced by the application.

The engine may:

- prioritize them
- break them into smaller practice steps
- add measurable feedback
- show supporting analysis
- suggest session structure

It must not:

- rewrite teacher intent
- declare an assignment unnecessary
- contradict a teacher without explicit uncertainty
- mark an assignment complete solely from one analysis result

---

# User Preference Learning

The engine may learn from user behavior.

## Signals

- accepted recommendations
- dismissed recommendations
- modified recommendations
- methods used
- time spent
- completed goals
- repeated deferrals
- manual notes

## Rules

- preference learning should improve relevance
- it must not hide important recurring issues
- it must remain transparent
- users should be able to reset preferences
- the engine should not infer personal traits beyond the practice context

---

# Recommendation Outcomes

Each recommendation should track outcome.

## Statuses

- Active
- Accepted
- Deferred
- Completed
- Dismissed
- Expired
- Superseded

## Evidence of Completion

Completion may come from:

- user confirmation
- goal completion
- improved analysis
- teacher confirmation
- passage stability across attempts

## Rules

- completion should not imply permanent mastery
- completed recommendations may inform progress
- recurring issues may create a new recommendation later
- dismissed recommendations should retain the reason when provided

---

# Recommendation Explanation

Every recommendation should provide an explanation layer.

## Minimum Explanation

```text
What:
Shift destination is consistently flat.

Where:
Measure 24.

Evidence:
Three recordings in this session.

Next step:
Practice the shift separately without vibrato.
```

## Expanded Explanation

The user may open details to see:

- supporting recordings
- average deviation
- confidence
- practice-map state
- history
- related teacher note

The default view should remain concise.

---

# Wording Rules

## Tone

Use calm, neutral, teacher-like language.

## Preferred Verbs

- practice
- isolate
- reinforce
- compare
- repeat
- slow
- reconnect
- review
- listen
- observe

## Avoid

- failed
- bad
- poor
- unacceptable
- mastered
- perfect
- wrong overall
- score
- grade

## Evidence-Based Praise

Preferred:

> Rhythm became more consistent across the final three attempts.

Avoid:

> Great job!

unless paired with specific evidence.

---

# Estimated Practice Time

Recommendations may include an estimated time.

## Inputs

- passage length
- method
- number of repetitions
- current tempo
- prior completion time
- user practice history

## Rules

- estimates should be ranges
- estimates are optional
- estimates should not create pressure
- the musician may ignore them
- the engine should not imply certainty

Example:

> Estimated focus time: 8–10 minutes.

---

# Session Planning

The recommendation engine may compose a lightweight session plan.

## Example

```text
1. Measures 24–25
   Intonation
   8 minutes

2. Measures 40–42
   Rhythm
   6 minutes

3. Full passage
   Reconnect
   4 minutes
```

## Rules

- no mandatory setup wizard
- plan should be editable
- plan should not block spontaneous practice
- user may start immediately
- plan should fit available time when known
- teacher assignments should be visible

---

# Home Recommendation Logic

The Home screen should answer:

> What should I practice today?

## Candidate Sources

- recent active piece
- unfinished teacher assignment
- high-priority recurring issue
- piece not practiced recently
- user-pinned piece
- current goal

## Selection Rules

Prefer a recommendation that is:

- relevant
- recent
- actionable
- short enough to begin immediately
- supported by clear evidence

Do not show a recommendation when evidence is insufficient.

In that case, show:

> Practice this piece to begin building personalized guidance.

---

# Piece Home Recommendation Logic

The Piece Home should show:

- primary recommended passage
- focus category
- estimated time
- reason
- practice-map context

## Example

> Measures 23–25  
> Focus: Intonation  
> The shift into Measure 24 averaged flat across three recordings.

The primary action remains:

> Start Practice

---

# Practice Workspace Recommendation Logic

During active practice, the engine should remain quiet.

## After Recording Stops

The engine may show:

- analysis in progress
- one concise observation
- one optional next action

Example:

> The shift into Measure 24 was flatter than the previous attempt. Try one repetition without vibrato.

## Rules

- do not interrupt active recording
- do not update visual heat maps during playing
- do not display multiple competing recommendations
- do not block the next recording
- allow the user to hide guidance

---

# Session Summary Recommendation Logic

The summary should include:

- what improved
- what still needs attention
- where to begin next time
- one suggested method
- optional teacher reminder

## Example

```text
Looking Ahead

Begin next time with Measures 23–25.

Reason:
The shift into Measure 24 remained slightly flat in three attempts.

Suggested method:
Practice the shift separately at a slower tempo without vibrato.

Estimated focus time:
8–10 minutes.
```

---

# Practice Map Update Rules

The recommendation engine should coordinate with the Practice Map update process.

## Suggested State Logic

### Insufficient Data

Use when:

- no usable recording exists
- alignment confidence is too low
- too few observations exist
- category analysis is unavailable

### Comfortable

Use when:

- recent evidence is stable
- no meaningful repeated issue exists
- confidence is sufficient
- performance is retained across attempts

### Needs Reinforcement

Use when:

- one or more moderate issues recur
- improvement is incomplete
- retention is uncertain
- evidence is mixed

### Recommended Focus

Use when:

- issue is significant
- evidence is repeated
- confidence is high
- problem affects later material
- teacher assignment emphasizes the passage

## Rules

- a state should not change from one low-confidence observation
- state changes should be explainable
- one category should not overwrite another
- historical state changes should remain reviewable
- labels should not be shown as grades

---

# Decay and Retention

Practice Map States and recommendations should evolve over time.

## Comfortable Material

Comfortable material may eventually need review.

Possible triggers:

- long time since last practice
- upcoming performance
- teacher request
- prior instability
- user-selected maintenance

## Issue Decay

An old issue should lose priority when:

- no longer observed
- repeatedly corrected
- replaced by more recent evidence
- no longer relevant to the active score

## Reappearance

A resolved issue may return if new evidence supports it.

The engine should treat this as new evidence, not failure.

---

# Avoiding Over-Practice

The engine should eventually detect diminishing returns.

Possible signals:

- increasing error rate
- worsening consistency
- repeated attempts without change
- rising tempo instability
- long time on one passage
- user-reported fatigue

Possible wording:

> This passage has not changed across the last five attempts. Consider moving on and returning later.

This should be optional and cautious.

---

# Confidence and Recommendation Strength

Recommendation strength should reflect evidence quality.

## High Confidence

> Practice Measures 24–25. The shift destination was flat in three recordings.

## Moderate Confidence

> Measures 24–25 may need reinforcement. The shift appeared flat in two attempts.

## Low Confidence

Do not create a strong recommendation.

Use:

> More recordings are needed before the app can identify a reliable pattern.

---

# Recommendation Suppression

Suppress recommendations when:

- user is actively recording
- analysis is incomplete
- confidence is insufficient
- signal quality is poor
- evidence is contradictory
- user dismissed the same recommendation recently
- recommendation would duplicate teacher text without adding value
- issue is below meaningful threshold
- too many recommendations are already active

---

# Maximum Recommendation Counts

To reduce overload:

## Home

- 1 primary
- up to 2 secondary

## Piece Home

- 1 primary
- up to 2 secondary

## Practice Workspace

- 1 immediate suggestion after a recording

## Session Summary

- 1 next-session starting recommendation
- up to 2 additional observations

The app may retain more recommendations internally.

---

# Explainability Requirements

Every recommendation must be traceable to evidence.

## Evidence Links

A recommendation may reference:

- Measure Observations
- Technical Patterns
- Practice Map States
- Teacher Assignments
- Practice Goals
- Session comparisons

## Internal Audit

The system should be able to answer:

- which evidence created this recommendation?
- which engine version produced that evidence?
- why was this recommendation prioritized?
- why was another candidate suppressed?
- when did it expire or change?

---

# Recommendation Versioning

Recommendation rules will change.

Store:

- recommendation engine version
- rule-set version
- source analysis versions
- evidence references
- creation timestamp

A recommendation should not be silently rewritten.

A newer recommendation may supersede an older one.

---

# Testing Strategy

## Unit Tests

Test:

- priority calculations
- recurrence weighting
- recency weighting
- state transitions
- duplicate suppression
- conflict resolution
- passage grouping
- wording templates
- recommendation expiration

## Scenario Tests

### Scenario 1: Repeated Flat Note

Evidence:

- same F-sharp flat in three recordings
- high confidence
- same passage

Expected:

- one intonation recommendation
- narrow passage
- specific practice method
- no global judgment

### Scenario 2: One Isolated Error

Evidence:

- one slightly early note
- otherwise stable

Expected:

- no recommendation
- optional observation only

### Scenario 3: Teacher Assignment Conflict

Evidence:

- active teacher assignment on Measures 40–48
- app issue in Measures 24–25

Expected:

- assignment remains visible
- app issue presented as optional secondary choice
- no override

### Scenario 4: Insufficient Data

Evidence:

- noisy recording
- low alignment confidence

Expected:

- no strong recommendation
- request another recording or better signal

### Scenario 5: Improvement

Evidence:

- three attempts improve from -24 cents to -8 cents

Expected:

- acknowledge measurable improvement
- recommend reconnecting passage
- do not repeat original drill unchanged

### Scenario 6: Diminishing Returns

Evidence:

- six attempts
- no meaningful change
- increasing instability

Expected:

- suggest pausing or changing method
- no punitive language

---

# Product Validation

Recommendations should be reviewed by:

- cello students
- advanced cellists
- teachers

## Validation Questions

- Is the recommendation accurate?
- Is it specific enough?
- Is it actionable?
- Is the passage scope appropriate?
- Is the method musically useful?
- Is the wording discouraging?
- Does the explanation build trust?
- Would a teacher agree with the suggested next step?
- Does the recommendation respect interpretation?

The recommendation engine is successful only when users find the guidance useful in practice.

---

# Initial Rule-Based Implementation

The first version should use transparent rules rather than a complex machine-learning recommender.

## Reasons

- easier to test
- easier to explain
- easier to debug
- lower data requirements
- safer for early user trust
- easier teacher review

## Example Rule

```text
IF
    category = intonation
AND evidence_count >= 3
AND confidence >= configured threshold
AND average_absolute_cents >= meaningful threshold
THEN
    recommend isolated slow practice
    suggest removing vibrato
    passage = smallest passage containing affected note
```

Thresholds remain configurable and require real-world validation.

---

# Initial Recommendation Rules

## Rule 1: Repeated Intonation Deviation

Trigger:

- same expected note or score location
- at least three confident observations
- same direction
- meaningful average cents deviation

Output:

- identify note and measure
- state average deviation
- recommend isolated practice
- suggest no vibrato initially

## Rule 2: Shift Destination Pattern

Trigger:

- repeated pitch deviation immediately after shift
- sufficient alignment confidence
- repeated across attempts

Output:

- isolate transition
- slow tempo
- no vibrato initially
- reconnect phrase after improvement

## Rule 3: Repeated Rhythm Error

Trigger:

- same onset or duration pattern
- repeated across attempts

Output:

- isolate rhythm
- subdivide
- reduce tempo
- reconnect passage

## Rule 4: Tempo Drift

Trigger:

- consistent acceleration or slowing
- not indicated by score
- repeated across passage

Output:

- practice with pulse reference
- shorten passage
- compare starting and ending tempo

## Rule 5: Dynamic Contour Missing

Trigger:

- written contour
- stable microphone gain
- repeated lack of measurable contrast

Output:

- exaggerate contour in isolated practice
- compare waveform or intensity shape

## Rule 6: Improvement Detected

Trigger:

- comparable attempts
- meaningful improvement
- sufficient confidence

Output:

- acknowledge change
- reduce priority
- suggest reconnecting or modest tempo increase

## Rule 7: Insufficient Data

Trigger:

- low confidence
- poor signal
- too few attempts

Output:

- do not diagnose
- suggest another recording
- explain limitation

---

# Version 0.3 Acceptance Criteria

The first useful recommendation engine is successful when it can:

1. consume measure-level intonation observations
2. detect repeated evidence across recordings
3. identify the smallest useful passage
4. generate one actionable recommendation
5. explain the evidence
6. avoid generating recommendations from low-confidence data
7. preserve musician choice
8. store recommendation status
9. update recommendation when new evidence appears
10. avoid a global performance score

## Example Acceptance Output

```text
Recommended Practice

Measures 24–25

Reason:
The F-sharp after the shift averaged 17 cents flat across three recordings.

Suggested practice:
Slow the passage.
Practice the shift separately without vibrato.
Record three repetitions, then reconnect Measures 23–26.

Estimated focus time:
8–10 minutes.
```

---

# Open Decisions

The following require later testing:

1. How many observations are required before a recommendation is created?
2. How should confidence combine across recordings?
3. How should recommendation priority decay over time?
4. How often should repeated recommendations be resurfaced?
5. Which practice methods should be available first?
6. How should user dismissals affect future recommendations?
7. When should an issue be considered resolved?
8. How should teacher assignments affect priority?
9. How should available practice time shape recommendations?
10. Should users be able to pin or manually create recommendations?
11. How should the engine detect diminishing returns?
12. When should Comfortable material be scheduled for maintenance?
13. How should competing recommendations across pieces be ranked?
14. How should future machine learning influence transparent rules?
15. Which recommendation outcomes should be shared with teachers?

---

# Recommended Implementation Sequence

## Phase 1: Recommendation Data Model

Implement:

- recommendation records
- evidence links
- statuses
- version fields
- expiration
- supersession

## Phase 2: Intonation Rules

Implement:

- repeated pitch deviation rule
- shift destination rule
- insufficient-data rule
- passage grouping

## Phase 3: Session Summary Integration

Implement:

- next-session starting point
- suggested method
- estimated time
- improvement acknowledgment

## Phase 4: Practice Map Integration

Implement:

- priority-state updates
- recency
- recurrence
- confidence
- state history

## Phase 5: Teacher Integration

Implement:

- assignment-aware ranking
- teacher-note display
- conflict handling
- permission rules

## Phase 6: Preference and Outcome Learning

Implement:

- accepted methods
- dismissed methods
- recommendation completion
- diversity
- diminishing returns

---

# Summary

The recommendation engine transforms:

```text
Evidence
  ↓
Candidate Actions
  ↓
Prioritized Recommendation
  ↓
Clear Explanation
  ↓
Musician Choice
  ↓
Outcome
```

A successful recommendation is not merely correct.

It must be useful enough that the musician can act on it immediately.

The standard is:

> **Tell the musician what happened, where it happened, why it matters, and what to practice next.**
