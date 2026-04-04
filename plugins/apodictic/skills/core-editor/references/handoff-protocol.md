# Scene-Level Handoff Protocol

**Status:** Implementation-ready
**For:** APODICTIC Development Editor v0.5
**Last updated:** 2026-02-22

This file defines the mechanism for transitioning between diagnostic mode (DE skill active, Firewall active) and execution mode (DE constraints suspended, the assistant works directly with the writer on prose).

All references to `Diagnostic_State.md` in this protocol mean the file at the **project root** (see `references/output-policy.md` §Folder Architecture). For legacy projects that used an `Outputs/` sibling, treat that folder as the project root. Never read from or write to the plugin repo or installed plugin cache.

---

## §1. The Problem

After diagnosis, the DE skill stays loaded. Its Firewall rules prevent the assistant from helping with prose execution, dialogue drafting, or scene-level revision. The writer has to manually exit the skill context — which means knowing that the skill context exists, which newcomers don't.

The handoff protocol makes this transition explicit, preserving diagnostic state across the boundary.

---

## §2. Mode States

The project's `Diagnostic_State.md` tracks the current mode:

```
## Mode
**Current:** [diagnostic | execution]
**Last transition:** [date, direction, trigger]
```

### `diagnostic` mode (default)
- Core-editor skill is loaded.
- Firewall is active: no content invention, no prose generation, no dialogue drafting.
- All pass execution, synthesis, and audit logic applies.
- Output follows output-policy.md.

### `execution` mode
- Core-editor constraints are explicitly suspended (behavior-contract switch).
- Firewall is not active: the assistant can help with prose, dialogue, scene drafting, revision.
- The active handoff context (see §6) provides diagnostic background but does not constrain the assistant's behavior.
- Output follows the assistant's standard conversational behavior, not DE output policy.

---

## §3. Entering Execution Mode

### Trigger conditions

Offer handoff when any of these are true:

1. **Diagnosis identifies a scene-level problem with clear scope.** The synthesis or a pass report names a specific scene (or small set of scenes) with an actionable diagnosis. The writer's next step is execution, not further diagnosis.

2. **The writer asks for help executing a fix.** After reading the editorial letter, the writer says something like "can you help me rewrite this scene?" or "help me fix the dialogue in chapter 3."

3. **Revision round identifies a scene that needs rewriting.** During delta scan, a specific scene is flagged as unresolved and the writer wants to work on it.

### Handoff procedure

1. **Present the handoff offer and get explicit confirmation:**

> **Diagnosis complete for [scene name / chapter / section reference].**
>
> **What I found:** [1-2 sentence summary of the diagnosis for this scene]
>
> **What it needs:** [1-2 sentence summary of the intervention class — not specific content, just the structural requirement]
>
> **Scope:** I'll switch to execution mode for this scene. The Firewall deactivates — I can help with prose, dialogue, and revision. The rest of the diagnostic stays saved.
>
> **Switch to execution mode for [scene reference]?** (yes / no — or name a different scene)

**Do not switch modes until the writer confirms.** If the writer says no, remain in diagnostic mode. If the writer names a different scene, adjust the handoff context accordingly.

2. **After confirmation, write the handoff context to the Handoff History in `Diagnostic_State.md` (see §6).**

3. **Set mode to `execution` in `Diagnostic_State.md`. Record the scene scope lock:**

```
## Mode
**Current:** execution
**Last transition:** [date], diagnostic → execution, [trigger description]
**Active scene scope:** [scene reference — what the writer confirmed]
```

4. **Suspend core-editor constraints.** The Firewall, pass logic, and output policy no longer govern the conversation.

---

## §4. During Execution Mode

While in execution mode:

- The assistant operates with DE constraints suspended.
- The active handoff context in `Diagnostic_State.md` provides background but does not constrain behavior.
- The assistant can draft prose, write dialogue, suggest specific imagery, rewrite scenes — all things the Firewall would normally prohibit.
- The writer and the assistant work together on the scene as they normally would in a standard writing conversation.
- If the writer asks a diagnostic question ("is this working?", "does this fix the pacing problem?"), the assistant can offer informal assessment but should note: "For a formal check, say 'back to editor' and I'll run it through the diagnostic."

---

## §5. Returning to Diagnostic Mode

### Trigger phrases

All re-entry is phrase-based. No new command is introduced — this avoids adding to the command surface during a release that's trying to simplify it.

Any of these re-enter diagnostic mode:

- "back to editor"
- "resume editor"
- "check this fix"
- Any explicit request for diagnostic analysis ("run the passes on this," "does this fix the problem?")

`/start` also triggers re-entry, but with a resume check (see §5a).

### §5a. `/start` resume check

When `/start` fires and `Diagnostic_State.md` exists with the Mode section showing `**Current:** execution`:

1. **Do not run the router question flow.** Instead, present:

> I see you were working on [scene reference] in execution mode. Want to:
>
> - **Check the fix** — I'll reload the editor and run a delta check on what you changed
> - **Keep working** — stay in execution mode on this scene
> - **Start fresh** — run the full intake router (this won't lose your diagnostic history)

2. If the writer picks "Check the fix" → proceed with re-entry (§5b).
3. If the writer picks "Keep working" → remain in execution mode.
4. If the writer picks "Start fresh" → run the router normally. Diagnostic state persists in the file but a new run begins.

### §5b. Re-entry procedure

1. **Re-enable core-editor constraints.** Firewall reactivates. Output policy applies.

2. **Read existing project state from `Diagnostic_State.md`.** Contract, prior findings, root causes, triage — all persist. No re-intake needed.

3. **Check what changed.** If the writer revised the scene during execution mode:
   - Run a targeted delta check on the revised scene against the original diagnosis.
   - Report: what's resolved, what's still present, any new issues introduced.
   - Update `Diagnostic_State.md` with revision progress.

4. **Close the active handoff entry in Handoff History (see §6).** Record outcome.

5. **Set mode to `diagnostic` in `Diagnostic_State.md`.**

6. **Resume normal workflow.** The writer is back in the diagnostic context with full state preserved.

---

## §6. Handoff History

Handoff context is **appended**, not overwritten. Each handoff/return cycle gets its own entry. This preserves auditability across multiple scene fixes in a single session.

### Schema in `Diagnostic_State.md`:

```
## Handoff History

### Handoff 1
**Scene:** [scene reference — chapter, page range, or scene number from reverse outline]
**Entered execution:** [date]
**Diagnosis:** [the specific findings for this scene from the relevant pass(es)]
**Intervention class:** [the structural requirement — e.g., "needs irreversible choice," "needs value reversal," "dialogue must differentiate voices"]
**Contract excerpt:** [relevant contract fields — genre promise, reader expectation for this beat]
**Severity:** [Must-Fix / Should-Fix / Could-Fix]
**Relevant pass findings:** [brief excerpts from pass reports that informed this diagnosis]
**Returned to diagnostic:** [date, or "still in execution"]
**Outcome:** [resolved / partially resolved / unresolved / new issues found]
**Delta notes:** [what changed, what persists — filled on re-entry]

### Handoff 2
...
```

### Active handoff

The most recent entry with `Returned to diagnostic: still in execution` is the active handoff. Its `Scene` field defines the scope lock for execution mode.

### Typical multi-handoff session

1. Run diagnostic → find 3 scene-level problems
2. Handoff 1: scene A → writer revises → return to editor → delta check → close entry
3. Handoff 2: scene B → writer revises → return to editor → delta check → close entry
4. Handoff 3: scene C → writer revises → return to editor → delta check → close entry → final synthesis update

Each handoff entry is preserved. The writer (and any future diagnostic run) can see the full revision history.

---

## §7. Edge Cases

**Writer asks for prose help without a prior diagnosis.** If no diagnostic state exists, there's nothing to hand off from. The assistant works in its normal mode — no handoff protocol needed. If the writer later wants a diagnostic, `/start` runs the router normally.

**Writer asks for a full rewrite, not a scene fix.** Handoff is designed for scene-level work. If the writer wants to rewrite large sections, the handoff context may be too narrow to be useful. In this case, offer the handoff for the first scene and note: "We can do this scene by scene — I'll check each fix as we go."

**Writer forgets to return to editor.** No harm done. The diagnostic state persists in `Diagnostic_State.md` in the active project output context. When the writer eventually says "back to editor" or `/start` fires the resume check, the state is still there. Execution mode has no timeout.

**Diagnostic state doesn't exist.** If `Diagnostic_State.md` hasn't been initialized (no prior diagnostic run), handoff isn't available — there's nothing to hand off from. Prompt the writer to run a diagnostic first.

**Writer wants to change scene scope mid-execution.** If the writer says "actually, let me work on chapter 5 instead," close the current handoff entry as "unresolved" and open a new one for the new scene. Requires the same explicit confirmation as §3.

---

*This file is a runtime reference. For design rationale, see the v0.5 UX Overhaul spec.*
