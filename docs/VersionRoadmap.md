# Version Roadmap

## 1. Purpose

This roadmap describes a proposed sequence, not committed dates or completed
work. Each version should advance only after its exit criteria are met. Scope may
change based on user research, technical discovery, accessibility review, and
privacy or security findings.

## 2. Guiding sequence

The project should establish useful practice workflows before adding automated
audio feedback. This creates value without depending on unvalidated analysis and
provides the product context needed to evaluate later features responsibly.

## 3. Phase 0: Discovery and foundations

### Goals

- Validate the primary user group and highest-value practice problems.
- Choose the initial delivery platform.
- Define privacy, accessibility, and data-retention expectations.
- Establish the product vocabulary and core data model.
- Identify candidate audio features without promising their accuracy.

### Deliverables

- User research plan and findings.
- Prioritized initial-release scope.
- Architecture decision records for key technology choices.
- Initial threat model and data inventory.
- Accessibility plan.
- Measurement and evaluation plan.

### Exit criteria

- The initial user and problem statement are supported by research.
- Open product questions that affect platform architecture are resolved.
- Privacy-sensitive data flows are identified and reviewed.
- Initial success measures have baselines or a plan to establish them.

## 4. Version 0.1: Practice planning

### Proposed scope

- Create and manage practice goals.
- Create an editable, time-bounded session plan.
- Run a session with simple activity timing controls.
- Record notes, reflections, and next steps.
- Review a basic session history.
- Export and delete user-created practice data.

### Explicit exclusions

- Automated audio analysis.
- Teacher dashboards.
- Social feeds, rankings, and public profiles.

### Exit criteria

- Critical planning and session journeys pass usability testing.
- Accessibility checks cover the supported interaction paths.
- Authorization, export, and deletion behavior are tested.
- No feature implies that musical performance was analyzed.

## 5. Version 0.2: Practice continuity

### Proposed scope

- Reusable routines and templates.
- Better filtering by repertoire item, technique, goal, and date.
- User-controlled reminders.
- Progress summaries derived from recorded practice activity.
- Reliability improvements for interrupted or offline sessions, as appropriate
  for the chosen platform.

### Exit criteria

- Summary labels clearly distinguish logged activity from musical assessment.
- Reminder behavior is opt-in and controllable.
- Session data survives the documented interruption scenarios.
- Users can understand and use history to plan a subsequent session.

## 6. Version 0.3: Recording foundation

### Proposed scope

- Explicit audio capture or upload.
- Private playback and recording management.
- Configurable retention and deletion controls.
- Asynchronous processing states without musical feedback.
- Internal evaluation tooling separated from user-facing results.

### Exit criteria

- Recording consent, access, retention, export, and deletion flows are reviewed.
- Threat modeling and security testing cover the media pipeline.
- Failed processing never appears as a successful result.
- Supported devices and recording-quality constraints are documented.

## 7. Version 0.4: Limited audio-assisted feedback

### Proposed scope

- One or more narrowly defined metrics selected after evaluation.
- Plain-language explanations of what each metric can and cannot indicate.
- Input-quality checks and uncertainty states.
- User controls to dismiss, annotate, or delete results.
- Versioned analysis results and monitoring for operational failures.

Candidate metrics are intentionally not selected in this roadmap; selection
requires evidence that a method is useful and sufficiently reliable for the
target users and recording conditions.

### Exit criteria

- Each exposed metric has documented datasets, evaluation methods, thresholds,
  and known failure modes.
- Product testing shows users understand the metric's limitations.
- Privacy, accessibility, security, and deletion requirements remain satisfied.
- Release communication avoids claims not supported by the evaluation.

## 8. Future possibilities

The following ideas require separate discovery and are not commitments:

- teacher-student sharing with granular permission controls;
- score- or passage-aware practice organization;
- comparison of user-selected takes;
- more responsive feedback during practice; and
- integrations with calendars, notation tools, or learning platforms.

## 9. Release governance

For every version:

1. Confirm scope against the product principles.
2. Document relevant architecture and privacy decisions.
3. Define measurable acceptance criteria before implementation is considered
   complete.
4. Test accessibility and critical user journeys.
5. Record known limitations and unresolved risks.
6. Release behind appropriate safeguards when evidence is incomplete.
7. Review observed outcomes before expanding scope.

The roadmap should be updated when evidence changes priorities; it should not be
used to imply that planned features or outcomes already exist.
