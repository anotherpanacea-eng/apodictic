---
description: Plan revision sessions from diagnostic state
argument-hint: [time] or [deadline DATE] or [stuck SCENE] or no argument
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Post-diagnostic revision coaching. Helps plan revision sessions, work through stuck points, track momentum, and manage deadlines.

Load `../skills/revision-coach/SKILL.md`. Follow the coaching protocol in `../skills/revision-coach/references/coaching-protocol.md`.

**Mode selection:**

1. **No `Diagnostic_State.md` found at the project root** → No-diagnostic fallback. Do not improvise. Route to `/start` or `/diagnose`.

2. **Argument includes "deadline" or a date** → Deadline Coaching. Ask for available hours/week if not provided. Produce revision calendar.

3. **Argument includes "stuck" or names a specific scene/problem** → Stuck-Point Coaching. Read handoff history for context.

4. **Prior session plan exists and writer is returning** → Momentum Tracking. Compare current state against prior plan, then transition to Session Planning.

5. **Otherwise** → Session Planning (default). Ask for available time. Energy/focus level defaults to `mixed` if not stated.

**After synthesis completion** (when invoked by post-synthesis offer): Skip mode detection — enter Session Planning directly.

**State and output locations** (per `../skills/core-editor/references/output-policy.md` §Folder Architecture):
- Read `Diagnostic_State.md`, `SYNTHESIS.md`, and `Argument_State.md` from the **project root**
- Write active `Session_Plan_{NN}.md` to the **project root** (working document while session is in progress)
- On session completion, archive the plan: create `runs/YYYY-MM-DD_{model}_coaching/` and move the completed session plan there, along with any revision calendars or momentum reports
- Update `Diagnostic_State.md` coaching log at the project root
- Append row to `README.md` run archive table
- Never write to the plugin repo

If a project path or time constraint is provided: $ARGUMENTS
