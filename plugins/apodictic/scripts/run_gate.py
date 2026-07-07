#!/usr/bin/env python3
"""APODICTIC execution-gate engine (Runner-Governed Execution, increments 1-5).

`validate.sh gate ...` shells out here. Reads the declarative gate manifest
(plugins/apodictic/schemas/execution-gates.v1.json), resolves a phase's required
artifacts in <run_folder> by output-structure.md naming globs, runs the mechanical
checks via `validate.sh <validator> <file>...` (capturing exit code AND stdout, so a
WARN-level blocker isn't lost), prints the attested checklist, and records the gate
decision as an append-only event in the sidecar's execution.gate_events[] log.

Increment 5 (gate_events model, state_version 2):
  gate <phase> <run_folder> [--strict-warnings]   run mechanical checks; append the
                                                  mechanical outcome (mechanical-passed
                                                  for a gate with attested items, else a
                                                  clearing passed; or pass-with-warn /
                                                  blocked)
  gate --attest <phase> <run_folder>              re-run the mechanical checks and, only
                                                  if still clean, append a CLEARING passed
                                                  (attested_items + attested_contract +
                                                  fresh checks + artifact_digests)
  gate --skip  <phase> <run_folder> --reason ...  append a skipped event (reason required)
  gate --defer <phase> <run_folder> --reason ... [--until ...]   append a deferred event
  gate --check-state <sidecar> [--strict]         gate-state: validate the log + invariants
                                                  (pointer==fold, attestation coverage,
                                                  migration-prefix integrity, ...); --strict
                                                  is nonzero while any open exception remains
  gate --self-test

Exit: 0 permitted, 1 blocked / invalid / (--strict) open exceptions, 2 usage/config error.
See docs/runner-governed-execution.md Increment 5.
"""
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

HERE = os.path.dirname(os.path.abspath(__file__))

# Finding-ID lifecycle: a CLEARING gate advances each ledger finding's state
# (forward-only). run_synthesis -> locked and run_spot_check -> delivered mark
# ALL ledger findings; revision_round -> revised marks ONLY the resolved subset
# (the <!-- resolved: F-… --> ids in the run folder) — see _finding_deltas.
# Finding DISPOSITIONS (declined/deferred, docs/finding-dispositions.md) are an
# OVERLAY, never a lifecycle state: revision_round clears additionally freeze the
# run's disposition markers into event.disposition_deltas (full records), folded
# into execution.finding_dispositions last-event-wins — see _disposition_deltas.
_PHASE_FINDING_STATE = {"run_synthesis": "locked", "run_spot_check": "delivered",
                        "revision_round": "revised"}
_STATE_RANK = {"locked": 1, "delivered": 2, "revised": 3}

_RESULTS = ("passed", "mechanical-passed", "pass-with-warn", "blocked", "skipped", "deferred")
_STATE_VERSION = 2


# ---------------------------------------------------------------- manifest / fs

def _manifest_path():
    env = os.environ.get("APODICTIC_GATES_MANIFEST")
    if env and os.path.exists(env):
        return env
    candidates = []
    if art is not None and art.schema_dir():
        candidates.append(os.path.join(str(art.schema_dir()), "execution-gates.v1.json"))
    candidates += [os.path.join(HERE, "..", "schemas", "execution-gates.v1.json"),
                   os.path.join(HERE, "..", "plugins", "apodictic", "schemas", "execution-gates.v1.json")]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _load_manifest():
    mp = _manifest_path()
    if not mp:
        return None
    with open(mp, encoding="utf-8") as fh:
        return json.load(fh)


def _attested_entries(phase_spec):
    """Normalize entry_requires.attested to [{id, text}, ...] (accepts legacy bare strings)."""
    out = []
    for i, a in enumerate(phase_spec.get("entry_requires", {}).get("attested", []) or []):
        if isinstance(a, dict) and a.get("id"):
            out.append({"id": a["id"], "text": a.get("text", a["id"])})
        elif isinstance(a, str):
            out.append({"id": "att-%d" % (i + 1), "text": a})
    return out


def _attested_ids(phase_spec):
    return [e["id"] for e in _attested_entries(phase_spec)]


def _find_sidecar(run_folder):
    """Walk up from the run folder to the project-root Diagnostic_State.meta.json."""
    d = os.path.abspath(run_folder)
    for _ in range(4):
        sc = os.path.join(d, "Diagnostic_State.meta.json")
        if os.path.exists(sc):
            return sc
        d = os.path.dirname(d)
    return None


def _runlabel(run_folder):
    sc = _find_sidecar(run_folder)
    if not sc:
        return None
    try:
        with open(sc, encoding="utf-8") as fh:
            return (json.load(fh).get("last_session") or {}).get("runlabel")
    except (OSError, ValueError):
        return None


def _ledger_finding_ids(ledger_path):
    """Lifecycle IDs of the apodictic.finding blocks in the ledger."""
    if not ledger_path or art is None:
        return []
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return []
    return [obj["id"] for bt, obj, _e in art.parse_blocks(text)
            if bt == "finding" and isinstance(obj, dict) and obj.get("id")]


def _resolve(run_folder, patterns, runlabel):
    pats = [patterns] if isinstance(patterns, str) else list(patterns or [])
    matches = []
    for p in pats:
        matches.extend(glob.glob(os.path.join(run_folder, p)))
    if not matches:
        return None
    if runlabel:
        for m in matches:
            if runlabel in os.path.basename(m):
                return m
    return max(matches, key=os.path.getmtime)


def _project_and_runlabel(run_folder, keys, runlabel):
    project, rl = None, runlabel
    led = _resolve(run_folder, keys.get("findings_ledger", ""), runlabel)
    if led and "_Findings_Ledger_" in os.path.basename(led):
        pre, _, post = os.path.basename(led).partition("_Findings_Ledger_")
        project = pre
        rl = rl or (post[:-3] if post.endswith(".md") else post)
    return project or "Project", rl or "run"


def _digest(path):
    try:
        with open(path, "rb") as fh:
            return "sha256:" + hashlib.sha256(fh.read()).hexdigest()[:16]
    except OSError:
        return None


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- mechanical run

def run_checks(phase, run_folder, manifest, strict_warnings=False, validate_sh=None):
    """Run the manifest's mechanical checks for a phase against a run folder.

    Returns (status, lines, checks, resolved, digests) where status in
    'ok' | 'warn' | 'fail' and checks is [{validator, result: ok|warn|error}, ...].
    """
    phase_spec = manifest.get("phases", {}).get(phase)
    keys = manifest.get("artifact_keys", {})
    runlabel = _runlabel(run_folder)
    project, runlabel_val = _project_and_runlabel(run_folder, keys, runlabel)
    validate_sh = validate_sh or os.path.join(HERE, "validate.sh")
    er = phase_spec.get("entry_requires", {})
    lines, checks, fail, warn = [], [], 0, 0

    resolved = {}
    for key in er.get("artifacts", []):
        path = _resolve(run_folder, keys.get(key, ""), runlabel)
        if path:
            resolved[key] = path
            lines.append("  artifact %-22s ok (%s)" % (key, os.path.basename(path)))
        else:
            lines.append("  artifact %-22s MISSING" % key)
            fail = 1

    for chk in er.get("checks", []):
        v = chk["validator"]
        files, ok = [], True
        for t in chk.get("targets", []):
            if t == "run_folder":
                files.append(run_folder)
            elif t == "$project":
                files.append(project)
            elif t == "$runlabel":
                files.append(runlabel_val)
            else:
                p = resolved.get(t) or _resolve(run_folder, keys.get(t, ""), runlabel)
                if not p:
                    lines.append("  check    %-22s MISSING target (%s)" % (v, t))
                    ok = False
                    break
                files.append(p)
        if not ok:
            fail = 1
            checks.append({"validator": v, "result": "error"})
            continue
        proc = subprocess.run(["bash", validate_sh, v] + files, capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            lines.append("  check    %-22s ERROR (exit %d)" % (v, proc.returncode))
            checks.append({"validator": v, "result": "error"})
            fail = 1
        elif "WARN" in out:
            lines.append("  check    %-22s GATE-WARN" % v)
            checks.append({"validator": v, "result": "warn"})
            warn = 1
        else:
            lines.append("  check    %-22s ok" % v)
            checks.append({"validator": v, "result": "ok"})

    for e in _attested_entries(phase_spec):
        lines.append("  ATTEST   [%s] %s" % (e["id"], e["text"]))

    digests = {}
    for key, p in resolved.items():
        d = _digest(p)
        if d:
            digests[key] = d

    if fail:
        status = "fail"
    elif warn:
        status = "warn"
    else:
        status = "ok"
    return status, lines, checks, resolved, digests


# ---------------------------------------------------------------- fold (pointer)

def _ev(e):
    """A gate_event as a dict — a non-dict / malformed element becomes {} so the fold helpers never
    traceback; check_state separately reports it as 'not an object' (Review fix — Codex #28 P2)."""
    return e if isinstance(e, dict) else {}


def _prefix_len(events):
    n = 0
    for e in events:
        if _ev(e).get("migrated"):
            n += 1
        else:
            break
    return n


def _has_real_event(events):
    """True if the log contains any non-migrated event (evidence of real upgrade work)."""
    return any(not _ev(e).get("migrated") for e in events)


def _grandfathered(events, idx):
    # A migrated seed is grandfathered (required_ids = ∅, exempt from attestation/freshness) ONLY as
    # part of a genuine upgrade baseline: a contiguous prefix (idx < prefix_len) AND followed by real
    # work — the non-migrated event the engine appends atomically with the upgrade. A log of *only*
    # migrated events is a hand-authored clearing bypass, not a migration, so its migrated `passed`
    # is NOT grandfathered: it then needs a real attested_contract and is rejected as malformed.
    # (Review fix — Codex #28 P1: prefix position alone was a bypass.)
    return (bool(_ev(events[idx]).get("migrated")) and idx < _prefix_len(events)
            and _has_real_event(events))


def _required_ids(events, idx):
    if _grandfathered(events, idx):
        return set()
    return set(_ev(events[idx]).get("attested_contract") or [])


def _attested_items(e):
    return set(_ev(e).get("attested_items") or [])


def is_clearing(events, idx):
    """clearing_pass(e): a passed that authorizes a transition (see spec Open exceptions)."""
    e = _ev(events[idx])
    if e.get("result") != "passed":
        return False
    if not _grandfathered(events, idx) and "attested_contract" not in e:
        return False  # non-grandfathered passed with no contract is malformed -> not clearing
    return _attested_items(e) >= _required_ids(events, idx)


def fold_pointer(events, manifest):
    """Derive (phase, allowed_next, pending_gate, finding_states) from the event log."""
    phases = manifest.get("phases", {})
    order = list(phases.keys())

    frontier = None
    for idx in range(len(events)):
        if is_clearing(events, idx):
            frontier = _ev(events[idx]).get("gate")  # last clearing wins (highest index)

    latest_idx = {}
    for idx, e in enumerate(events):
        g = _ev(e).get("gate")
        if g is not None:
            latest_idx[g] = idx
    open_gates = {g for g, idx in latest_idx.items() if not is_clearing(events, idx)}

    pending = None
    for g in order:
        if g in open_gates:
            pending = g
            break

    if pending or frontier is None:
        allowed_next = []
    else:
        allowed_next = list(phases.get(frontier, {}).get("allowed_next", []))

    finding_states = {}
    for e in events:
        for fid, st in (_ev(e).get("finding_deltas") or {}).items():
            if _STATE_RANK.get(st, 0) >= _STATE_RANK.get(finding_states.get(fid), 0):
                finding_states[fid] = st

    # Finding dispositions (docs/finding-dispositions.md): an OVERLAY beside finding_states, never a
    # lifecycle state — the rank-monotonic fold above is untouched. Last-event-wins per id (a later
    # disposition overwrites an earlier one); supersedence by `revised` is a READ-time precedence
    # rule (consumers check finding_states first), so a superseded record is kept here, not dropped.
    finding_dispositions = {}
    for e in events:
        dd = _ev(e).get("disposition_deltas")
        if isinstance(dd, dict):
            for fid, rec in dd.items():
                finding_dispositions[fid] = rec

    return {"phase": frontier, "allowed_next": allowed_next, "pending_gate": pending,
            "finding_states": finding_states, "finding_dispositions": finding_dispositions}


# ---------------------------------------------------------------- write / migrate

def _seed_migration(ex, manifest):
    """If a legacy gates map needs upgrading, seed a grandfathered baseline prefix
    (one event per legacy entry, in MANIFEST PHASE ORDER) so the v2 fold reconstructs
    the correct frontier. Returns True if seeding occurred."""
    if ex.get("state_version", 1) >= _STATE_VERSION or ex.get("gate_events"):
        return False
    legacy = ex.get("gates") or {}
    seeds = []
    today = datetime.date.today().isoformat()
    for g in manifest.get("phases", {}):  # manifest order is authoritative
        if g not in legacy:
            continue
        val = legacy[g]
        if val == "attested":
            result, prov = "passed", "attested"
        elif val in ("passed", "pass-with-warn", "blocked"):
            result, prov = val, "mechanical"
        else:
            continue
        seeds.append({"gate": g, "result": result, "provenance": prov, "ts": today,
                      "migrated": True, "attested_items": [],
                      "note": "migrated from legacy gates map"})
    ex["gate_events"] = seeds
    return True


def append_event(sidecar, event, manifest):
    """Seed migration if needed, append the event, recompute the pointer, write. Returns True."""
    try:
        with open(sidecar, encoding="utf-8") as fh:
            meta = json.load(fh)
    except (OSError, ValueError):
        return False
    ex = meta.setdefault("execution", {})
    _seed_migration(ex, manifest)
    ex.setdefault("gate_events", []).append(event)
    ex["state_version"] = _STATE_VERSION
    ex.pop("gates", None)  # deprecated; gate_events is canonical

    # Write the pointer EXACTLY as the fold computes it — clear stale phase / finding_states when the
    # fold no longer supports them, so the recomputable pointer never lags the log (Codex #28 P2).
    ptr = fold_pointer(ex["gate_events"], manifest)
    if ptr["phase"] is not None:
        ex["phase"] = ptr["phase"]
    else:
        ex.pop("phase", None)
    ex["allowed_next"] = ptr["allowed_next"]
    if ptr["pending_gate"]:
        ex["pending_gate"] = ptr["pending_gate"]
    else:
        ex.pop("pending_gate", None)  # omitted when none (never null)
    if ptr["finding_states"]:
        ex["finding_states"] = ptr["finding_states"]
    else:
        ex.pop("finding_states", None)
    # finding_dispositions mirrors finding_states handling exactly: written as the fold computes it,
    # cleared when the fold no longer supports it. A pointer write leaves SUPERSEDED records
    # untouched (supersedence is read-time precedence, never a write-time deletion or rewrite).
    if ptr["finding_dispositions"]:
        ex["finding_dispositions"] = ptr["finding_dispositions"]
    else:
        ex.pop("finding_dispositions", None)
    if event.get("run_folder"):
        ex["run_folder"] = event["run_folder"]

    # Atomic write: serialize to a temp file in the same directory, then os.replace() — so an
    # interrupted write can never leave a half-written / corrupt Diagnostic_State.meta.json
    # (the rolling state a project can't afford to lose). os.replace is atomic on the same fs.
    try:
        d = os.path.dirname(sidecar) or "."
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".Diagnostic_State.meta.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                json.dump(meta, fh, indent=2)
                fh.write("\n")
            os.replace(tmp, sidecar)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return True
    except OSError:
        return False


def _rel_run_folder(run_folder, sidecar):
    try:
        return os.path.relpath(run_folder, os.path.dirname(sidecar))
    except ValueError:
        return run_folder


def _finding_deltas(phase, run_folder, manifest, resolved):
    if phase not in _PHASE_FINDING_STATE:
        return {}
    keys = manifest.get("artifact_keys", {})
    if phase == "revision_round":
        # revised marks ONLY the resolved subset — the <!-- resolved: F-… --> ids in the gate's
        # required revision_report artifact (a narrow *_Revision_Report_*.md, so a Revision
        # Calendar or other *_Revision_*.md can't satisfy the gate or contribute deltas), never
        # every ledger finding. Lazy import keeps run_gate free of a hard finding_trace dependency.
        try:
            import finding_trace as _ft
        except ImportError:
            return {}
        report = resolved.get("revision_report") or _resolve(run_folder, keys.get("revision_report", ""), _runlabel(run_folder))
        if not report:
            return {}
        resolved_ids = _ft.resolved_cited_ids(_ft._read(report) or "")
        # Intersect with the ledger inventory so a typo'd/stale marker can't write a phantom
        # finding_states key — the same self-consistency every other phase has (it only ever
        # marks _ledger_finding_ids). finding-trace E2 is the post-hoc backstop; this is the
        # write-time guard so the gate clear itself never emits an off-ledger id.
        led = resolved.get("findings_ledger") or _resolve(run_folder, keys.get("findings_ledger", ""), _runlabel(run_folder))
        ledger_ids = set(_ledger_finding_ids(led))
        return {fid: "revised" for fid in resolved_ids & ledger_ids}
    led = resolved.get("findings_ledger") or _resolve(run_folder, keys.get("findings_ledger", ""), _runlabel(run_folder))
    return {fid: _PHASE_FINDING_STATE[phase] for fid in _ledger_finding_ids(led)}


def _disposition_valid(rec):
    """Write-time record-shape gate: schema-valid + the trigger-iff-deferred conditional the stdlib
    subset checker cannot express + non-empty reason. Same rules check_state re-asserts log-side."""
    schema = art.load_schema("apodictic.finding_disposition.v1") if art else None
    if schema is None or art.validate_obj(rec, schema, "<disposition>"):
        return False
    if rec.get("disposition") == "deferred":
        if not (isinstance(rec.get("trigger"), str) and rec["trigger"].strip()):
            return False
    elif "trigger" in rec:
        return False
    return bool(rec.get("reason", "").strip())


def _disposition_deltas(phase, run_folder, manifest, resolved, sidecar, exclude_ids=()):
    """disposition_deltas for a clearing event — {F-id: full apodictic.finding_disposition.v1
    record}, frozen from the run's pinned disposition markers (docs/finding-dispositions.md) so
    fold_pointer recomputes execution.finding_dispositions from the log alone. Sibling of
    _finding_deltas; active for the revision_round phase only.

    Marker homes scanned, in precedence order (a later home wins per id, and within a home the
    last marker wins): any *_Feedback_Triage_*.md in the run folder (source: triage), the project
    Diagnostic_State.md Coaching Log — the SIBLING of the sidecar JSON _find_sidecar locates,
    derived from its dirname (source: author) — then the gate's revision_report artifact
    (source: author; the round's freshest decision). The grammar is the apodictic_artifacts SSoT
    (parse_disposition_markers), never a local copy.

    Write-time guards (mirroring _finding_deltas' phantom-id filter): a marker is frozen only when
    it names a LEDGER finding whose sidecar lifecycle state is 'delivered' (the write
    precondition; 'revised' is supersedence — a no-op here), is NOT in this clear's resolved
    subset (`exclude_ids` — the same-event revise+disclaim launder check_state rejects), and its
    record validates (_disposition_valid). A skipped marker is surfaced as marker/sidecar lag by
    disposition-check DP2.5 — never frozen into a poisoned append-only event."""
    if phase != "revision_round" or art is None or not hasattr(art, "parse_disposition_markers"):
        return {}
    keys = manifest.get("artifact_keys", {})
    runlabel = _runlabel(run_folder)
    led = resolved.get("findings_ledger") or _resolve(run_folder, keys.get("findings_ledger", ""), runlabel)
    ledger_ids = set(_ledger_finding_ids(led))
    if not ledger_ids:
        return {}
    session, states = 0, {}
    if sidecar:
        try:
            with open(sidecar, encoding="utf-8") as fh:
                meta = json.load(fh)
            session = meta.get("session_count") or 0
            states = (meta.get("execution") or {}).get("finding_states") or {}
        except (OSError, ValueError):
            pass
    sources = []  # (path, source) in precedence order — later wins
    for p in sorted(glob.glob(os.path.join(run_folder, "*_Feedback_Triage_*.md"))):
        sources.append((p, "triage"))
    if sidecar:
        state_md = os.path.join(os.path.dirname(sidecar), "Diagnostic_State.md")
        if os.path.exists(state_md):
            sources.append((state_md, "author"))
    report = resolved.get("revision_report") or _resolve(run_folder, keys.get("revision_report", ""), runlabel)
    if report:
        sources.append((report, "author"))
    deltas = {}
    for path, source in sources:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for m in art.parse_disposition_markers(text):
            fid = m["id"]
            if fid not in ledger_ids or fid in exclude_ids or states.get(fid) != "delivered":
                continue
            rec = {"schema": "apodictic.finding_disposition.v1", "id": fid,
                   "disposition": m["kind"], "reason": m["reason"], "source": source,
                   "session": int(session) if isinstance(session, int) else 0,
                   "ts": _now_iso(), "artifact": os.path.basename(path)}
            if m["trigger"] is not None:
                rec["trigger"] = m["trigger"]
            if _disposition_valid(rec):
                deltas[fid] = rec
    return deltas


# ---------------------------------------------------------------- clearing report (M1b/M1d)

def _clearing_report_lines(run_folder):
    """Display-only trace lines appended to a CLEARING gate output (M1b) plus the T4-watch
    marker-count line (M1d). No state written, no event fields, no schema touched — a pure read of
    the run folder. Never raises: any failure to import/resolve degrades to an empty list (a broken
    trace must not brick a legitimate clear).

    M1b: the per-ID `severity · sidecar state · cited? · rev=` journey (finding_trace's own report,
    reused — not re-implemented). M1d: `T4-watch: N deferred orchestrator-pull-interface marker(s)`,
    the CR-6-detectable surface for defer-trigger T4."""
    lines = []
    try:
        import re as _re
        import finding_trace as _ft
    except ImportError:
        return lines

    # M1b — reuse finding_trace's cross-artifact report (the same lines `validate.sh finding-trace`
    # prints), so the clearing output and the standalone validator never drift.
    try:
        ledger, letter, sidecar, revisions, completions, retcons = _ft.resolve_run_folder(run_folder)
        if ledger:
            sidecar_text = None
            if sidecar:
                sidecar_text = _ft._read(sidecar)
                if sidecar_text is None:
                    sidecar_text = ""
            revision_texts = [t for t in (_ft._read(r) for r in revisions) if t is not None]
            completion_texts = [t for t in (_ft._read(c) for c in completions) if t is not None]
            retcon_texts = [t for t in (_ft._read(r) for r in retcons) if t is not None]
            ev_adv = (_ft.event_advanced_revised_ids(sidecar_text, run_folder, sidecar)
                      if sidecar else set())
            _code, ft_lines = _ft.trace(_ft._read(ledger),
                                        _ft._read(letter) if letter else None,
                                        sidecar_text, revision_texts=revision_texts,
                                        completion_texts=completion_texts,
                                        retcon_texts=retcon_texts, event_advanced=ev_adv)
            lines.append("  finding-ID trace (display only; the gate row already enforced integrity):")
            for ln in ft_lines:
                lines.append("  " + ln)
    except Exception:
        pass  # display-only; never block a legitimate clear on a trace-report failure

    # M1d — T4-watch marker count. Whole-run-folder scan (OQ #5: the marker rides the coverage
    # note / manifest whose exact filename varies), comment-body scoped.
    try:
        marker_re = _re.compile(r"<!--\s*deferred:\s*orchestrator-pull-interface\b", _re.IGNORECASE)
        n = 0
        for name in sorted(os.listdir(run_folder)):
            p = os.path.join(run_folder, name)
            if not os.path.isfile(p):
                continue
            text = _ft._read(p)
            if text:
                n += len(marker_re.findall(text))
        lines.append("  T4-watch: %d deferred orchestrator-pull-interface marker(s) in this run" % n)
    except OSError:
        pass

    return lines


# ---------------------------------------------------------------- commands

def cmd_gate(phase, run_folder, manifest, strict_warnings=False, write=False, validate_sh=None):
    """Run the mechanical checks and append the mechanical-outcome event."""
    phase_spec = manifest.get("phases", {}).get(phase)
    if not phase_spec:
        return 2, ["gate: unknown phase %r (known: %s)" % (phase, ", ".join(sorted(manifest.get("phases", {}))))]
    if not os.path.isdir(run_folder):
        return 2, ["gate: run_folder not found: %s" % run_folder]

    status, lines, checks, resolved, digests = run_checks(
        phase, run_folder, manifest, strict_warnings, validate_sh)
    attested = _attested_ids(phase_spec)

    if status == "fail" or (status == "warn" and strict_warnings):
        result, code = "blocked", 1
    elif status == "warn":
        result, code = "pass-with-warn", 0
    elif attested:
        result, code = "mechanical-passed", 0  # checks green; attestation still owed
    else:
        result, code = "passed", 0             # no attested items -> clears directly

    if write:
        sidecar = _find_sidecar(run_folder)
        if sidecar:
            event = {"gate": phase, "result": result, "provenance": "mechanical",
                     "ts": _now_iso(), "run_folder": _rel_run_folder(run_folder, sidecar),
                     "checks": checks}
            if digests:
                event["artifact_digests"] = digests
            if result == "passed":
                event["attested_contract"] = []  # no-attest gate; explicit empty contract
                event["attested_items"] = []
                event["finding_deltas"] = _finding_deltas(phase, run_folder, manifest, resolved)
                dd = _disposition_deltas(phase, run_folder, manifest, resolved, sidecar,
                                         exclude_ids=set(event["finding_deltas"]))
                if dd:
                    event["disposition_deltas"] = dd
            if append_event(sidecar, event, manifest):
                lines.append("  (recorded execution.gate_events += %s/%s in %s)"
                             % (phase, result, os.path.basename(sidecar)))

    if code == 1:
        lines.append("gate %s: BLOCKED%s" % (phase, " (--strict-warnings: unresolved WARN)"
                                             if (status == "warn" and strict_warnings) else ""))
        return 1, lines
    if result == "mechanical-passed":
        lines.append("gate %s: MECHANICAL-PASS — confirm the %d ATTEST item(s) then run `gate --attest %s <run_folder>` to clear"
                     % (phase, len(attested), phase))
    elif result == "pass-with-warn":
        lines.append("gate %s: PASS-WITH-WARN — resolve or acknowledge each GATE-WARN before transitioning" % phase)
    else:
        # result == "passed": a no-attest gate clears directly. Append the finding-ID trace + T4-watch
        # report (M1b/M1d) — the clearing outputs only, never the mechanical-passed intermediate
        # (attestation still owed there; a trace then reports pre-advance state and invites misreading).
        lines.append("gate %s: PASS (no attested items; cleared)" % phase)
        lines.extend(_clearing_report_lines(run_folder))
    return 0, lines


def cmd_attest(phase, run_folder, manifest, write=False, validate_sh=None):
    """Re-run the mechanical checks; only if still clean, append a CLEARING passed."""
    phase_spec = manifest.get("phases", {}).get(phase)
    if not phase_spec:
        return 2, ["gate --attest: unknown phase %r" % phase]
    if not os.path.isdir(run_folder):
        return 2, ["gate --attest: run_folder not found: %s" % run_folder]

    status, lines, checks, resolved, digests = run_checks(phase, run_folder, manifest, False, validate_sh)
    contract = _attested_ids(phase_spec)  # the gate's CURRENT manifest attested IDs

    if status != "ok":
        # files changed since mechanical-passed (or never passed): record the current
        # mechanical outcome, do NOT clear.
        result = "blocked" if status == "fail" else "pass-with-warn"
        code = 1 if status == "fail" else 0
        if write:
            sidecar = _find_sidecar(run_folder)
            if sidecar:
                ev = {"gate": phase, "result": result, "provenance": "mechanical",
                      "ts": _now_iso(), "run_folder": _rel_run_folder(run_folder, sidecar), "checks": checks}
                if digests:
                    ev["artifact_digests"] = digests
                append_event(sidecar, ev, manifest)
        lines.append("gate --attest %s: NOT CLEARED — mechanical checks regressed (%s); resolve and retry" % (phase, result))
        return code, lines

    # mechanical clean -> clearing pass; --attest confirms the full current checklist
    if write:
        sidecar = _find_sidecar(run_folder)
        if sidecar:
            event = {"gate": phase, "result": "passed", "provenance": "mechanical",
                     "ts": _now_iso(), "run_folder": _rel_run_folder(run_folder, sidecar),
                     "checks": checks, "attested_items": list(contract),
                     "attested_contract": list(contract),
                     "finding_deltas": _finding_deltas(phase, run_folder, manifest, resolved)}
            dd = _disposition_deltas(phase, run_folder, manifest, resolved, sidecar,
                                     exclude_ids=set(event["finding_deltas"]))
            if dd:
                event["disposition_deltas"] = dd
            if digests:
                event["artifact_digests"] = digests
            if append_event(sidecar, event, manifest):
                lines.append("  (recorded execution.gate_events += %s/passed [cleared %d attest item(s)] in %s)"
                             % (phase, len(contract), os.path.basename(sidecar)))
    lines.append("gate --attest %s: CLEARED (mechanical checks fresh + %d attest item(s) confirmed)" % (phase, len(contract)))
    # M1b/M1d — the clearing --attest output carries the per-ID finding trace + the T4-watch line.
    lines.extend(_clearing_report_lines(run_folder))
    return 0, lines


def cmd_exception(phase, run_folder, manifest, kind, reason, until=None, write=False):
    """Append a skipped / deferred event (reason required). Recording IS the point of an exception,
    so a no-write is an ERROR, never a silent success — a caller must not believe a bypass is
    auditable when no gate_events[] entry exists (Review fix — Codex #28 P2)."""
    if phase not in manifest.get("phases", {}):
        return 2, ["gate --%s: unknown phase %r" % (kind, phase)]
    if not reason:
        return 2, ["gate --%s: --reason is required" % kind]
    if not os.path.isdir(run_folder):
        return 2, ["gate --%s: run_folder not found: %s — NOTHING RECORDED" % (kind, run_folder)]
    result = "skipped" if kind == "skip" else "deferred"
    if not write:
        return 0, ["gate --%s %s: --no-write set — NOTHING RECORDED (dry run)" % (kind, phase)]
    sidecar = _find_sidecar(run_folder)
    if not sidecar:
        return 2, ["gate --%s: no Diagnostic_State.meta.json found under %s — NOTHING RECORDED "
                   "(an exception must be auditable; create the sidecar first)" % (kind, run_folder)]
    event = {"gate": phase, "result": result, "provenance": "attested",
             "ts": _now_iso(), "run_folder": _rel_run_folder(run_folder, sidecar), "reason": reason}
    if until and kind == "defer":
        event["until"] = until
    if not append_event(sidecar, event, manifest):
        return 2, ["gate --%s: failed to write %s event to %s — NOTHING RECORDED"
                   % (kind, result, os.path.basename(sidecar))]
    note = " — record a blind-spot line in the Audit Invocation Log" if result == "skipped" else ""
    return 0, ["gate --%s %s: recorded %s in %s (reason: %s)%s"
               % (kind, phase, result, os.path.basename(sidecar), reason, note)]


# ---------------------------------------------------------------- gate-state check

def check_state(sidecar, manifest, strict=False):
    """gate-state: validate gate_events[] structurally + the semantic invariants the
    subset schema cannot express, and assert pointer == fold. Returns (code, lines)."""
    try:
        with open(sidecar, encoding="utf-8") as fh:
            meta = json.load(fh)
    except (OSError, ValueError) as exc:
        return 2, ["check-state: cannot read %s (%s)" % (sidecar, exc)]
    ex = meta.get("execution", {})
    errs, lines = [], []

    if ex.get("state_version", 1) < _STATE_VERSION and "gate_events" not in ex:
        return 0, ["check-state: legacy sidecar (state_version<2, no gate_events) — nothing to check"]

    events = ex.get("gate_events", [])
    if not isinstance(events, list):
        return 1, ["check-state: execution.gate_events must be an array"]

    phases = manifest.get("phases", {})
    phase_order = list(phases.keys())
    gate_event_schema = art.load_schema("apodictic.gate_event.v1") if art else None
    prefix = _prefix_len(events)
    seen_migrated_gates = set()
    last_mig_order = -1  # manifest-order index of the previous migrated gate

    # A migration prefix must be followed by real work — the engine seeds the baseline atomically
    # with the first real v2 event. A migrated-only log is a forged clearing baseline, not an
    # upgrade (Review fix — Codex #28 P1).
    if prefix and prefix == len(events):
        errs.append("migration prefix of %d migrated event(s) is not followed by any real event "
                    "— a migrated-only log is not a valid upgrade baseline" % prefix)

    for i, e in enumerate(events):
        where = "gate_events[%d]" % i
        if not isinstance(e, dict):
            errs.append("%s: not an object" % where)
            continue
        # structural (reuse the shared per-object subset validator)
        if gate_event_schema is not None:
            errs.extend(art.validate_obj(e, gate_event_schema, where))
        # gate enum == manifest phases keys
        if e.get("gate") not in phases:
            errs.append("%s: gate %r not in manifest phases %s" % (where, e.get("gate"), list(phases)))
        # migration-prefix integrity (Codex P1/P2): migrated only as a contiguous head, <=1/gate,
        # in MANIFEST PHASE ORDER (a shuffled prefix would reconstruct the wrong frontier, since the
        # fold takes the last clearing event in append order).
        if e.get("migrated"):
            if i >= prefix:
                errs.append("%s: migrated:true outside the contiguous migration prefix" % where)
            g = e.get("gate")
            if g in seen_migrated_gates:
                errs.append("%s: second migrated event for gate %r" % (where, g))
            seen_migrated_gates.add(g)
            if g in phase_order:
                gi = phase_order.index(g)
                if gi <= last_mig_order:
                    errs.append("%s: migrated prefix not in manifest phase order "
                                "(gate %r out of order)" % (where, g))
                last_mig_order = gi
        # reason iff skipped/deferred; provenance attested for them
        if e.get("result") in ("skipped", "deferred"):
            if not e.get("reason"):
                errs.append("%s: result %s requires a 'reason'" % (where, e.get("result")))
            if e.get("provenance") != "attested":
                errs.append("%s: result %s must have provenance 'attested'" % (where, e.get("result")))
        elif e.get("reason"):
            errs.append("%s: 'reason' only valid on skipped/deferred" % where)
        # finding_deltas clearing-only + inner shapes
        if e.get("finding_deltas"):
            if not is_clearing(events, i):
                errs.append("%s: finding_deltas only on a clearing passed" % where)
            for fid, st in e["finding_deltas"].items():
                if st not in _STATE_RANK:
                    errs.append("%s: finding_deltas[%s]=%r not a lifecycle state" % (where, fid, st))
        # disposition_deltas (docs/finding-dispositions.md): clearing-only, full-record shapes (the
        # log-side twin of disposition-check DP0), and the no-simultaneous-launder rule — one event
        # cannot both revise and disclaim the same finding.
        if e.get("disposition_deltas"):
            dd = e["disposition_deltas"]
            if not isinstance(dd, dict):
                errs.append("%s: disposition_deltas must be an object" % where)
            else:
                if not is_clearing(events, i):
                    errs.append("%s: disposition_deltas only on a clearing passed" % where)
                dispo_schema = art.load_schema("apodictic.finding_disposition.v1") if art else None
                for fid, rec in dd.items():
                    dwhere = "%s: disposition_deltas[%s]" % (where, fid)
                    if not isinstance(rec, dict):
                        errs.append("%s: not a disposition record object" % dwhere)
                        continue
                    if dispo_schema is not None:
                        errs.extend(art.validate_obj(rec, dispo_schema, dwhere))
                    if rec.get("id") != fid:
                        errs.append("%s: record id %r does not match its map key" % (dwhere, rec.get("id")))
                    # trigger iff deferred — the cross-field rule the subset schema cannot express
                    if rec.get("disposition") == "deferred":
                        if not (isinstance(rec.get("trigger"), str) and rec["trigger"].strip()):
                            errs.append("%s: deferred requires a non-empty 'trigger'" % dwhere)
                    elif "trigger" in rec:
                        errs.append("%s: 'trigger' only valid on a deferred disposition" % dwhere)
                    if not (isinstance(rec.get("reason"), str) and rec["reason"].strip()):
                        errs.append("%s: 'reason' must be non-empty" % dwhere)
                    if (e.get("finding_deltas") or {}).get(fid) == "revised":
                        errs.append("%s: same-event launder — the event both revises and "
                                    "dispositions %s (a finding cannot be revised and disclaimed "
                                    "by the same clear)" % (dwhere, fid))
        # checks[] inner shape
        for j, c in enumerate(e.get("checks") or []):
            if not (isinstance(c, dict) and isinstance(c.get("validator"), str)
                    and c.get("result") in ("ok", "warn", "error")):
                errs.append("%s: checks[%d] must be {validator, result: ok|warn|error}" % (where, j))
        # attestation coverage (non-grandfathered clearing passed must carry+cover its contract)
        if e.get("result") == "passed" and not _grandfathered(events, i):
            if "attested_contract" not in e:
                errs.append("%s: non-grandfathered clearing passed must carry 'attested_contract'" % where)
            elif not (_attested_items(e) >= set(e.get("attested_contract") or [])):
                errs.append("%s: attested_items do not cover attested_contract %s"
                            % (where, e.get("attested_contract")))
            # freshness: a MECHANICAL-provenance clearing pass must carry green checks[]. This is the
            # ENFORCED freshness invariant: `gate --attest` re-runs the checks and writes the clearing
            # pass only if they are still clean, so green checks[] proves the mechanical half was fresh
            # at clear time. (artifact_digests are an INFORMATIONAL audit breadcrumb only — NOT a
            # gate-state-enforced equality: a clean --attest re-run on legitimately-edited files
            # produces new digests, so a mechanical-passed -> passed digest *mismatch* is not an error.
            # Review fix — Codex #28 P2: the spec/PR over-claimed digest binding; it is now informational.)
            # Attested-provenance (degrade) and grandfathered seeds are exempt.
            if e.get("provenance") == "mechanical":
                cks = e.get("checks") or []
                if not cks or any(isinstance(c, dict) and c.get("result") == "error" for c in cks):
                    errs.append("%s: mechanical clearing passed must carry green checks[] (freshness)" % where)

    # pointer == fold (the index must match the canonical log)
    # pointer == fold (compare ABSENCE as well as value, for every pointer field — /start treats
    # this block as the recomputable pointer, so a stale value the fold no longer supports is drift;
    # Review fix — Codex #28 P2: phase was skipped when the fold was None, and finding_states was
    # never compared at all). "" / absent normalize to None for phase.
    ptr = fold_pointer(events, manifest)
    if (ex.get("phase") or None) != ptr["phase"]:
        errs.append("pointer drift: execution.phase=%r but fold=%r" % (ex.get("phase"), ptr["phase"]))
    if ex.get("allowed_next", []) != ptr["allowed_next"]:
        errs.append("pointer drift: execution.allowed_next=%r but fold=%r" % (ex.get("allowed_next"), ptr["allowed_next"]))
    if ex.get("pending_gate") != ptr["pending_gate"]:
        errs.append("pointer drift: execution.pending_gate=%r but fold=%r" % (ex.get("pending_gate"), ptr["pending_gate"]))
    if (ex.get("finding_states") or {}) != ptr["finding_states"]:
        errs.append("pointer drift: execution.finding_states=%r but fold=%r" % (ex.get("finding_states"), ptr["finding_states"]))
    if (ex.get("finding_dispositions") or {}) != ptr["finding_dispositions"]:
        errs.append("pointer drift: execution.finding_dispositions=%r but fold=%r"
                    % (ex.get("finding_dispositions"), ptr["finding_dispositions"]))

    open_gates = sorted(g for g in {_ev(e).get("gate") for e in events}
                        if g is not None
                        and not is_clearing(events, max(i for i, e in enumerate(events) if _ev(e).get("gate") == g)))

    # T2 defer-trigger surface (M1 — CR-6 detectable): a count line broken down by the LATEST
    # non-clearing result per open gate. Same open-exception fold as `open_gates` above; the number
    # (N > 0 at release time on a governed project, recurring) is the T2 watch condition made
    # mechanical (docs/runner-governed-execution.md open-exceptions). Read-only; no state written.
    _latest_idx = {}
    for _i, _e in enumerate(events):
        _g = _ev(_e).get("gate")
        if _g is not None:
            _latest_idx[_g] = _i
    _breakdown = {"skipped": 0, "deferred": 0, "pass-with-warn": 0, "mechanical-passed": 0, "blocked": 0}
    for _g in open_gates:
        _res = _ev(events[_latest_idx[_g]]).get("result")
        if _res in _breakdown:
            _breakdown[_res] += 1

    for e in errs:
        lines.append("  ERROR: %s" % e)
    if errs:
        lines.append("check-state: FAIL (%d error(s))" % len(errs))
        return 1, lines
    lines.append("check-state: OK (%d event(s); frontier=%s; open=%s)"
                 % (len(events), ptr["phase"], ",".join(open_gates) or "none"))
    lines.append("open exceptions: %d (skipped %d · deferred %d · pass-with-warn %d · "
                 "mechanical-passed %d · blocked %d)"
                 % (len(open_gates), _breakdown["skipped"], _breakdown["deferred"],
                    _breakdown["pass-with-warn"], _breakdown["mechanical-passed"], _breakdown["blocked"]))
    if strict and open_gates:
        lines.append("check-state: STRICT FAIL — open exception(s): %s" % ", ".join(open_gates))
        return 1, lines
    return 0, lines


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def check(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 ledger: _ledger_finding_ids must degrade to the no-ids path ([]),
    # never a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    _fd, _nu = tempfile.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    check("non_utf8_ledger_ids_empty", _ledger_finding_ids(_nu) == [])
    os.unlink(_nu)

    manifest = _load_manifest()
    vs = os.path.join(HERE, "validate.sh")

    valid_block = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01",'
                   '"mechanism":"protagonist never chooses","severity":"Must-Fix","confidence":"HIGH",'
                   '"evidence_refs":["Ch. 12"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    ledger_ok = ("## Pass 5 — Ledger Entry\n### Notable Findings\n1. **Agency collapse.** Severity: Must-Fix.\n"
                 + valid_block + "\n\n### Data Artifacts for Letter Reference\n- none\n\n"
                 "### Cross-Pass Connections\n- none\n\n### Unresolved Questions\n- none\n\n"
                 "### Audit Triggers\n| Trigger | Evidence | Recommendation |\n|---|---|---|\n")
    ledger_bad = "## Pass 5 — Ledger Entry\n### Notable Findings\n1. **Agency collapse.** Severity: Must-Fix.\n"

    def folder(ledger_text, with_log=True, sidecar=None):
        d = tempfile.mkdtemp()
        made.append(d)
        with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(ledger_text)
        if with_log:
            with open(os.path.join(d, "Proj_Audit_Invocation_Log_run.md"), "w", encoding="utf-8", newline="") as fh:
                fh.write("## Audit Invocation Log\n")
        with open(os.path.join(d, "Diagnostic_State.meta.json"), "w", encoding="utf-8", newline="") as fh:
            json.dump(sidecar if sidecar is not None else {"project": "Proj", "execution": {}}, fh)
        return d

    def read_ex(d):
        with open(os.path.join(d, "Diagnostic_State.meta.json")) as fh:
            return json.load(fh).get("execution", {})

    # --- core gate run: run_synthesis has attested items -> mechanical-passed (not cleared)
    d = folder(ledger_ok)
    code, _ = cmd_gate("run_synthesis", d, manifest, write=True, validate_sh=vs)
    ex = read_ex(d)
    evs = ex.get("gate_events", [])
    check("synthesis_mechanical_passed",
          code == 0 and len(evs) == 1 and evs[0]["result"] == "mechanical-passed"
          and ex.get("state_version") == 2 and "gates" not in ex)
    check("mechanical_passed_does_not_clear",
          ex.get("phase") is None and ex.get("allowed_next") == [] and ex.get("pending_gate") == "run_synthesis")

    # --attest re-runs checks and clears
    code, _ = cmd_attest("run_synthesis", d, manifest, write=True, validate_sh=vs)
    ex = read_ex(d)
    last = ex["gate_events"][-1]
    check("attest_clears",
          code == 0 and last["result"] == "passed" and set(last["attested_items"]) == {"syn-a1", "syn-a2", "syn-a3"}
          and last.get("attested_contract") == last["attested_items"])
    check("attest_advances_frontier",
          ex.get("phase") == "run_synthesis" and "run_spot_check" in ex.get("allowed_next", [])
          and ex.get("pending_gate") is None)
    check("clearing_advances_finding_lifecycle", ex.get("finding_states", {}).get("F-P5-01") == "locked")
    check("check_state_clean", check_state(os.path.join(d, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    # --- missing artifact -> blocked
    db = folder(ledger_ok, with_log=False)
    code, _ = cmd_gate("run_synthesis", db, manifest, write=True, validate_sh=vs)
    check("missing_artifact_blocks", code == 1 and read_ex(db)["gate_events"][-1]["result"] == "blocked")

    # --- failing check -> blocked
    df = folder(ledger_bad)
    code, _ = cmd_gate("run_synthesis", df, manifest, write=True, validate_sh=vs)
    check("failing_check_blocks", code == 1 and read_ex(df)["gate_events"][-1]["result"] == "blocked")

    # --- unknown phase -> usage error
    check("unknown_phase_usage", cmd_gate("nope", folder(ledger_ok), manifest, validate_sh=vs)[0] == 2)

    # --- skip requires reason; records skipped + open exception
    ds = folder(ledger_ok)
    check("skip_requires_reason", cmd_exception("run_synthesis", ds, manifest, "skip", "", write=True)[0] == 2)
    cmd_exception("run_synthesis", ds, manifest, "skip", "time pressure", write=True)
    exs = read_ex(ds)
    check("skip_recorded_open",
          exs["gate_events"][-1]["result"] == "skipped" and exs.get("pending_gate") == "run_synthesis")

    # --- pending_gate tracks the non-cleared gate, not the last passed one (Codex P1#2
    # scenario): synthesis cleared, spot_check runs and does NOT clear. run_spot_check now
    # also requires the Step 6b Refutation Record (finding-disconfirmation), so stage a
    # green snapshot + record for the ledger's F-P5-01 (Must-Fix HIGH; survived, sha-bound)
    # — the three refutation checks stay green and the scenario's original check surface
    # (the minimal letter's own non-green checks) is what keeps the gate un-cleared.
    dw = folder(ledger_ok)
    cmd_gate("run_synthesis", dw, manifest, write=True, validate_sh=vs)
    cmd_attest("run_synthesis", dw, manifest, write=True, validate_sh=vs)
    with open(os.path.join(dw, "Proj_Core_DE_Synthesis_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Edit\n## What Needs Work\nTheo's arc could perhaps be strengthened (Chapter 34).\n"
                 "## Appendix B: Severity Calibration\nTheo arc: Severity held at Must-Fix.\n")
    snap_text = "Chapter 34\n\nTheo watches the harbor and never chooses, and the chapter ends unchanged.\n"
    with open(os.path.join(dw, "Proj_Manuscript_Snapshot_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(snap_text)
    with open(os.path.join(dw, "Proj_Refutation_Record_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write('# Refutation Record\n\n<!-- apodictic:refutation\n'
                 '{"schema":"apodictic.refutation.v1","id":"F-P5-01","attempted":true,'
                 '"outcome":"survived","counter_evidence_quotes":'
                 '["Theo watches the harbor and never chooses, and the chapter ends unchanged."],'
                 '"alternative_explanations":["Stillness could be the design — Ch. 34 frames it as watching, but no choice is paid for there either."],'
                 '"rationale":"A scene where Theo chooses under pressure would refute this; none found.",'
                 '"confidence_after":"HIGH","snapshot_path":"Proj_Manuscript_Snapshot_run.md",'
                 '"snapshot_sha256":"%s"}\n-->\n\n<!-- apodictic:refutation_budget\n'
                 '{"schema":"apodictic.refutation_budget.v1","cap":15,"eligible":1,"processed":1,"bound":false}\n-->\n'
                 % hashlib.sha256(snap_text.encode("utf-8")).hexdigest())
    code, _ = cmd_gate("run_spot_check", dw, manifest, write=True, validate_sh=vs)
    exw = read_ex(dw)
    check("warn_pending_is_spot_check",
          exw.get("phase") == "run_synthesis" and exw.get("pending_gate") == "run_spot_check"
          and exw.get("allowed_next") == [])

    # --- M1a: finding-trace is now a run_spot_check gate row (referential integrity, NOT ordering).
    # Isolate the row's contribution via run_checks (the other letter-shape checks fail on the
    # minimal fixture; asserting the whole gate clears would need a full canonical letter — the
    # docs/revision-round-gate.md:7 route). We assert the finding-trace CHECK's own result.
    def _ftrace_result(rf):
        _s, _l, cks, _r, _d = run_checks("run_spot_check", rf, manifest, validate_sh=vs)
        for c in cks:
            if c.get("validator") == "finding-trace":
                return c.get("result")
        return None

    def _spot_folder(sidecar_ex, letter_body):
        """A run_spot_check-shaped folder: ledger + editorial letter + governed sidecar."""
        dd = tempfile.mkdtemp()
        made.append(dd)
        with open(os.path.join(dd, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(ledger_ok)
        with open(os.path.join(dd, "Proj_Core_DE_Synthesis_run.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(letter_body)
        with open(os.path.join(dd, "Diagnostic_State.meta.json"), "w", encoding="utf-8", newline="") as fh:
            json.dump({"project": "Proj", "execution": sidecar_ex}, fh)
        return dd

    # sidecar shapes for the M1a matrix
    _synth_cleared_ex = {"state_version": 2, "phase": "run_synthesis",
                         "finding_states": {"F-P5-01": "locked"},
                         "gate_events": [{"gate": "run_synthesis", "result": "passed",
                                          "provenance": "mechanical", "run_folder": ".",
                                          "attested_contract": [], "attested_items": [],
                                          "checks": [{"validator": "x", "result": "ok"}],
                                          "finding_deltas": {"F-P5-01": "locked"}}]}
    _letter_clean = ("# Edit\n<!-- finding: F-P5-01 -->\nThe pacing collapses (Ch 9).\n")
    _letter_phantom = _letter_clean + "Typo'd ref <!-- finding: F-XX-99 -->\n"

    # (a) E1 dangling letter ref -> the finding-trace row ERRORS (would block the clear, exit 1)
    check("m1a_e1_phantom_blocks",
          _ftrace_result(_spot_folder(_synth_cleared_ex, _letter_phantom)) == "error")

    # (b) clean letter + coherent sidecar -> the row is green (ok)
    check("m1a_clean_row_ok",
          _ftrace_result(_spot_folder(_synth_cleared_ex, _letter_clean)) == "ok")

    # (c) OUT-OF-ORDER HONESTY (spec §0 P1): run_spot_check with NO prior run_synthesis clear ->
    # the folded phase is un-advanced, so finding-trace's W1 SELF-SKIPS and the row contributes NO
    # order signal (clean letter -> ok). The E-checks still bind: the SAME out-of-order sidecar with
    # a planted phantom id still ERRORS. Ordering is NOT enforced by this row.
    _ungoverned_ex = {}  # no execution block at all -> phase un-advanced, finding_states empty
    check("m1a_out_of_order_no_signal",
          _ftrace_result(_spot_folder(_ungoverned_ex, _letter_clean)) == "ok")
    check("m1a_out_of_order_e1_still_binds",
          _ftrace_result(_spot_folder(_ungoverned_ex, _letter_phantom)) == "error")

    # (d) POST-LOCK LEDGER ADDITION: the folded phase is run_synthesis (synth cleared) but a
    # Must-Fix ledger id has NO finding_states entry -> W1 fires -> the row is a GATE-WARN
    # (pass-with-warn, exit 0). Ledger carries F-P5-01 AND F-PL-02; sidecar only knows F-P5-01.
    _ledger_two = ledger_ok.rstrip() + "\n" + (
        '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-PL-02",'
        '"mechanism":"added after the lock","severity":"Must-Fix","confidence":"HIGH",'
        '"evidence_refs":["Ch. 3"],"fix_class":"x","risk_if_fixed":"y"}\n-->\n')
    dpl = tempfile.mkdtemp()
    made.append(dpl)
    with open(os.path.join(dpl, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(_ledger_two)
    with open(os.path.join(dpl, "Proj_Core_DE_Synthesis_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(_letter_clean)
    with open(os.path.join(dpl, "Diagnostic_State.meta.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump({"project": "Proj", "execution": _synth_cleared_ex}, fh)
    check("m1a_post_lock_addition_warns",
          _ftrace_result(dpl) == "warn")

    # (e) STALE/UNGOVERNED POINTER: (i) an ungoverned sidecar makes W1 inactive but E1 still binds
    # (covered by m1a_out_of_order_*); (ii) a governed pointer hand-set to run_spot_check with empty
    # finding_states -> the row surfaces W1 warns (the pointer/fold discrepancy itself is
    # gate-state's to catch, not this row's).
    _handset_ex = {"state_version": 2, "phase": "run_spot_check", "finding_states": {}}
    check("m1a_handset_pointer_warns",
          _ftrace_result(_spot_folder(_handset_ex, _letter_clean)) == "warn")

    # (f) M1b/M1d: the CLEARING output carries the trace + T4-watch; mechanical-passed carries
    # neither. run_spot_check has attest items, so its clear is via --attest; but the minimal letter
    # can't clear it. Exercise the surfaces on a NO-ATTEST clearing path instead — a temp manifest
    # phase with only the finding-trace row (so cmd_gate takes the `passed` clearing branch) — which
    # is exactly the code path M1b hooks. (Real-gate coverage: the --check-all spot-check arm.)
    ft_only_manifest = {"artifact_keys": manifest.get("artifact_keys", {}),
                        "phases": {"ft_only": {"entry_requires": {
                            "artifacts": ["findings_ledger"],
                            "checks": [{"validator": "finding-trace", "targets": ["run_folder"]}],
                            "attested": []}, "allowed_next": []}}}
    dclr = _spot_folder(_synth_cleared_ex, _letter_clean)
    # plant a deferred pull-interface marker so T4-watch counts 1
    with open(os.path.join(dclr, "Proj_Coverage_Note_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Coverage\n<!-- deferred: orchestrator-pull-interface (Runner-Governed Execution Increment 4) -->\n")
    ccode, clines = cmd_gate("ft_only", dclr, ft_only_manifest, write=True, validate_sh=vs)
    check("m1b_clearing_carries_trace",
          ccode == 0 and any("finding-ID trace" in ln for ln in clines)
          and any("F-P5-01" in ln and "sev=" in ln for ln in clines))
    check("m1d_clearing_carries_t4watch",
          any("T4-watch: 1 deferred orchestrator-pull-interface" in ln for ln in clines))

    # mechanical-passed carries NEITHER: a phase WITH an attest item stops at mechanical-passed.
    ft_attest_manifest = {"artifact_keys": manifest.get("artifact_keys", {}),
                          "phases": {"ft_att": {"entry_requires": {
                              "artifacts": ["findings_ledger"],
                              "checks": [{"validator": "finding-trace", "targets": ["run_folder"]}],
                              "attested": [{"id": "a1", "text": "confirm"}]}, "allowed_next": []}}}
    dmp = _spot_folder(_synth_cleared_ex, _letter_clean)
    mcode, mlines = cmd_gate("ft_att", dmp, ft_attest_manifest, write=True, validate_sh=vs)
    check("m1b_mechanical_passed_no_trace",
          mcode == 0 and read_ex(dmp)["gate_events"][-1]["result"] == "mechanical-passed"
          and not any("finding-ID trace" in ln for ln in mlines)
          and not any("T4-watch" in ln for ln in mlines))

    # (mid-run upgrade boundary, spec §4-Fixtures item 4): a mechanical-passed recorded under a
    # PRE-M1a manifest (finding-trace row absent), then --attest under the NEW manifest with a
    # phantom id planted -> --attest re-runs against the LIVE manifest and records `blocked` (a clean
    # block, not a crash, not a false clear). Modeled with the ft_att manifest as "new": record a
    # mechanical-passed with the clean letter, then swap in a phantom letter and --attest.
    dmu = _spot_folder(_synth_cleared_ex, _letter_clean)
    cmd_gate("ft_att", dmu, ft_attest_manifest, write=True, validate_sh=vs)  # mechanical-passed (clean)
    with open(os.path.join(dmu, "Proj_Core_DE_Synthesis_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(_letter_phantom)  # phantom planted before the attest re-check
    ucode, _ = cmd_attest("ft_att", dmu, ft_attest_manifest, write=True, validate_sh=vs)
    check("m1a_mid_upgrade_attest_blocks",
          ucode == 1 and read_ex(dmu)["gate_events"][-1]["result"] == "blocked")

    # (T2 count line): check_state prints an `open exceptions: N (...)` line. Reuse `ds` (a folder
    # with a recorded `skipped` run_synthesis event — pointer written fold-consistently by
    # append_event) so no pointer-drift error short-circuits the OK path: N == 1, skipped 1.
    _tc, t2lines = check_state(os.path.join(ds, "Diagnostic_State.meta.json"), manifest)
    check("t2_open_exceptions_line",
          any(ln.startswith("open exceptions: 1 ") and "skipped 1" in ln for ln in t2lines))
    # zero open exceptions on a cleanly-cleared folder -> `open exceptions: 0 (...)`
    _tc0, t2lines0 = check_state(os.path.join(d, "Diagnostic_State.meta.json"), manifest)
    check("t2_open_exceptions_zero",
          any(ln.startswith("open exceptions: 0 ") for ln in t2lines0))

    # --- gate-state catches a migrated bypass injected after real work (Codex P1)
    bypass = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "mechanical-passed", "provenance": "mechanical", "ts": "t0"},
        {"gate": "run_synthesis", "result": "passed", "provenance": "attested", "ts": "t1", "migrated": True},
    ]}}
    dbz = folder(ledger_ok, sidecar=bypass)
    code, lines = check_state(os.path.join(dbz, "Diagnostic_State.meta.json"), manifest)
    check("migrated_bypass_rejected",
          code == 1 and any("outside the contiguous migration prefix" in ln for ln in lines))

    # --- non-grandfathered passed without contract is rejected
    nocontract = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "mechanical", "ts": "t0"},
    ], "phase": "run_synthesis", "allowed_next": ["run_spot_check"]}}
    dnc = folder(ledger_ok, sidecar=nocontract)
    code, lines = check_state(os.path.join(dnc, "Diagnostic_State.meta.json"), manifest)
    check("passed_without_contract_rejected",
          code == 1 and any("must carry 'attested_contract'" in ln for ln in lines))

    # --- migration: legacy gates map seeds a grandfathered baseline in manifest order
    legacy = {"project": "Proj", "execution": {"gates": {"run_spot_check": "blocked", "run_synthesis": "attested"},
                                               "phase": "run_synthesis", "allowed_next": ["run_spot_check"]}}
    dl = folder(ledger_ok, sidecar=legacy)
    # trigger upgrade by recording a real event (re-run synthesis)
    cmd_gate("run_synthesis", dl, manifest, write=True, validate_sh=vs)
    exl = read_ex(dl)
    seeds = [e for e in exl["gate_events"] if e.get("migrated")]
    check("migration_seeds_manifest_order",
          len(seeds) == 2 and seeds[0]["gate"] == "run_synthesis" and seeds[1]["gate"] == "run_spot_check"
          and exl.get("state_version") == 2 and "gates" not in exl)
    check("migration_seeds_grandfathered_valid",
          check_state(os.path.join(dl, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    # --- --strict is nonzero while an open exception remains
    code_strict, _ = check_state(os.path.join(ds, "Diagnostic_State.meta.json"), manifest, strict=True)
    check("strict_red_on_open_exception", code_strict == 1)

    # --- freshness: a mechanical clearing passed with an errored/empty checks[] is rejected
    stale = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "mechanical", "ts": "t0",
         "attested_contract": ["syn-a1", "syn-a2", "syn-a3"], "attested_items": ["syn-a1", "syn-a2", "syn-a3"],
         "checks": [{"validator": "ledger-check", "result": "error"}]},
    ], "phase": "run_synthesis", "allowed_next": ["run_spot_check"]}}
    dstale = folder(ledger_ok, sidecar=stale)
    code, lines = check_state(os.path.join(dstale, "Diagnostic_State.meta.json"), manifest)
    check("stale_mechanical_pass_rejected",
          code == 1 and any("freshness" in ln for ln in lines))

    # --- a degrade-path (attested-provenance) clearing pass needs NO checks[] (exempt)
    degrade = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "attested", "ts": "2026-06-03",
         "attested_contract": ["syn-a1", "syn-a2", "syn-a3"], "attested_items": ["syn-a1", "syn-a2", "syn-a3"]},
    ], "phase": "run_synthesis", "allowed_next": ["run_spot_check"]}}
    ddeg = folder(ledger_ok, sidecar=degrade)
    check("degrade_attested_pass_exempt_from_checks",
          check_state(os.path.join(ddeg, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    # --- pointer-drift detection (stale phase while the fold cleared run_synthesis)
    drift = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "mechanical", "ts": "t0",
         "attested_contract": ["syn-a1", "syn-a2", "syn-a3"], "attested_items": ["syn-a1", "syn-a2", "syn-a3"],
         "checks": [{"validator": "ledger-check", "result": "ok"}]},
    ], "phase": "run_spot_check", "allowed_next": ["run_spot_check"]}}
    dd = folder(ledger_ok, sidecar=drift)
    code, lines = check_state(os.path.join(dd, "Diagnostic_State.meta.json"), manifest)
    check("pointer_drift_detected", code == 1 and any("pointer drift" in ln for ln in lines))

    # --- (Codex #28 P1) a migrated-ONLY log (no real event) is a forged baseline -> rejected,
    # and its migrated `passed` is not grandfathered (so it cannot clear the frontier)
    migonly = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "attested", "ts": "t0", "migrated": True},
    ]}}
    dmo = folder(ledger_ok, sidecar=migonly)
    code, lines = check_state(os.path.join(dmo, "Diagnostic_State.meta.json"), manifest)
    check("migrated_only_log_rejected",
          code == 1 and any("not followed by any real event" in ln for ln in lines))
    check("migrated_only_does_not_clear",
          fold_pointer(migonly["execution"]["gate_events"], manifest)["phase"] is None)

    # --- (Codex #28 P2) a SHUFFLED migrated prefix (wrong manifest order) is rejected — it would
    # otherwise reconstruct the wrong frontier (fold takes the last clearing event in append order)
    shuffled = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_spot_check", "result": "passed", "provenance": "mechanical", "ts": "t0", "migrated": True, "attested_items": []},
        {"gate": "run_synthesis", "result": "passed", "provenance": "mechanical", "ts": "t1", "migrated": True, "attested_items": []},
        {"gate": "run_spot_check", "result": "blocked", "provenance": "mechanical", "ts": "t2"},
    ]}}
    dsh = folder(ledger_ok, sidecar=shuffled)
    code, lines = check_state(os.path.join(dsh, "Diagnostic_State.meta.json"), manifest)
    check("shuffled_migrated_prefix_rejected",
          code == 1 and any("manifest phase order" in ln for ln in lines))

    # --- (Codex #28 P2) a malformed (non-dict) gate_events entry is a CLEAN validation failure,
    # not a Python traceback — the fold helpers tolerate non-dicts
    malformed = {"project": "Proj", "execution": {"state_version": 2, "gate_events": ["not an object"]}}
    dmf = folder(ledger_ok, sidecar=malformed)
    try:
        code, lines = check_state(os.path.join(dmf, "Diagnostic_State.meta.json"), manifest)
        ok = code == 1 and any("not an object" in ln for ln in lines)
    except Exception:
        ok = False
    check("malformed_event_no_traceback", ok)

    # --- (Codex #28 P2) stale execution.phase accepted when the fold cleared nothing
    stalephase = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "mechanical-passed", "provenance": "mechanical", "ts": "t0",
         "checks": [{"validator": "x", "result": "ok"}]},
    ], "phase": "run_synthesis", "allowed_next": []}}
    dsp = folder(ledger_ok, sidecar=stalephase)
    code, lines = check_state(os.path.join(dsp, "Diagnostic_State.meta.json"), manifest)
    check("stale_phase_with_empty_fold_drift",
          code == 1 and any("execution.phase" in ln and "drift" in ln for ln in lines))

    # --- (Codex #28 P2) finding_states never compared: clearing deltas vs ex finding_states {}
    fsdrift = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "run_synthesis", "result": "passed", "provenance": "mechanical", "ts": "t0",
         "attested_contract": ["syn-a1", "syn-a2", "syn-a3"], "attested_items": ["syn-a1", "syn-a2", "syn-a3"],
         "checks": [{"validator": "x", "result": "ok"}], "finding_deltas": {"F-P5-01": "locked"}},
    ], "phase": "run_synthesis", "allowed_next": ["run_spot_check"], "finding_states": {}}}
    dfs = folder(ledger_ok, sidecar=fsdrift)
    code, lines = check_state(os.path.join(dfs, "Diagnostic_State.meta.json"), manifest)
    check("finding_states_drift_detected",
          code == 1 and any("finding_states" in ln and "drift" in ln for ln in lines))

    # --- (Codex #28 P2) --skip/--defer never report success without writing
    check("skip_nonexistent_folder_errors",
          cmd_exception("run_synthesis", "/nonexistent/xyz", manifest, "skip", "r", write=True)[0] == 2)
    nosc = tempfile.mkdtemp()
    made.append(nosc)
    with open(os.path.join(nosc, "Proj_Findings_Ledger_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(ledger_ok)  # ledger present but NO Diagnostic_State.meta.json
    check("skip_no_sidecar_errors",
          cmd_exception("run_synthesis", nosc, manifest, "skip", "r", write=True)[0] == 2)

    # --- revision_round (Increment 4a): folds ONLY the resolved subset to "revised" ---
    rev_block2 = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-02",'
                  '"mechanism":"stakes stay abstract","severity":"Should-Fix","confidence":"HIGH",'
                  '"evidence_refs":["Ch. 3"],"fix_class":"x","risk_if_fixed":"y"}\n-->')
    ledger2 = ("## Pass 5 — Ledger Entry\n### Notable Findings\n"
               "1. **Agency collapse.** Severity: Must-Fix.\n" + valid_block + "\n"
               "2. **Abstract stakes.** Severity: Should-Fix.\n" + rev_block2 + "\n\n"
               "### Data Artifacts for Letter Reference\n- none\n\n"
               "### Cross-Pass Connections\n- none\n\n### Unresolved Questions\n- none\n\n"
               "### Audit Triggers\n| Trigger | Evidence | Recommendation |\n|---|---|---|\n")

    def _ev_passed(gate, deltas):
        return {"gate": gate, "result": "passed", "provenance": "mechanical", "ts": "t",
                "attested_contract": [], "attested_items": [],
                "checks": [{"validator": "x", "result": "ok"}], "finding_deltas": deltas}

    # prior gate log: synthesis + spot_check cleared -> both findings at "delivered"
    prior = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        _ev_passed("run_synthesis", {"F-P5-01": "locked", "F-P5-02": "locked"}),
        _ev_passed("run_spot_check", {"F-P5-01": "delivered", "F-P5-02": "delivered"}),
    ]}}
    drev = folder(ledger2, sidecar=prior)
    # sanity: the prior log folds to both findings at delivered (materialized only by append_event,
    # so check the fold directly here, not the as-written sidecar)
    check("rev_prior_delivered",
          fold_pointer(prior["execution"]["gate_events"], manifest)["finding_states"]
          == {"F-P5-01": "delivered", "F-P5-02": "delivered"})
    # revision report resolves ONLY F-P5-01 (F-P5-02 stays present, no marker)
    with open(os.path.join(drev, "Proj_Revision_Report_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags resolved: F-P5-01\n<!-- resolved: F-P5-01 -->\n"
                 "- Flags still present: F-P5-02\n")
    code, _ = cmd_gate("revision_round", drev, manifest, write=True, validate_sh=vs)
    check("rev_mechanical_passed",
          code == 0 and read_ex(drev)["gate_events"][-1]["result"] == "mechanical-passed")
    code, _ = cmd_attest("revision_round", drev, manifest, write=True, validate_sh=vs)
    exr = read_ex(drev)
    check("rev_clears", code == 0 and exr["gate_events"][-1]["result"] == "passed")
    # (a) ONLY the resolved subset advances to revised; still-present finding stays delivered
    check("rev_subset_only",
          exr.get("finding_states", {}) == {"F-P5-01": "revised", "F-P5-02": "delivered"})
    # (b) pointer == fold holds with a revised delta present
    check("rev_check_state_clean",
          check_state(os.path.join(drev, "Diagnostic_State.meta.json"), manifest)[0] == 0)
    check("rev_frontier",
          exr.get("phase") == "revision_round" and exr.get("allowed_next") == ["run_synthesis"])

    # (d) backward frontier + terminal-revised (spec-review §4 / Blocker 2): a fresh run_synthesis
    # clearing after revision_round regresses the frontier (last-clearing wins) yet F-P5-01 stays
    # revised (monotonic — a re-locked delta can't lower it). Tested at the fold (pure function).
    back_events = exr["gate_events"] + [_ev_passed("run_synthesis", {"F-P5-01": "locked", "F-P5-02": "locked"})]
    ptr = fold_pointer(back_events, manifest)
    check("rev_backward_frontier",
          ptr["phase"] == "run_synthesis" and ptr["allowed_next"] == ["run_spot_check"]
          and ptr["pending_gate"] is None)
    check("rev_revised_terminal",
          ptr["finding_states"].get("F-P5-01") == "revised" and ptr["finding_states"].get("F-P5-02") == "delivered")

    # (c) zero resolved markers -> no-op on finding_states (empty subset)
    drev0 = folder(ledger2, sidecar=prior)
    with open(os.path.join(drev0, "Proj_Revision_Report_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags still present: F-P5-01, F-P5-02\n")  # no resolved markers
    cmd_gate("revision_round", drev0, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", drev0, manifest, write=True, validate_sh=vs)
    check("rev_zero_resolved_noop",
          read_ex(drev0).get("finding_states", {}) == {"F-P5-01": "delivered", "F-P5-02": "delivered"})

    # (S1) an off-ledger resolved marker is filtered at write time — no phantom finding_states key
    drevp = folder(ledger2, sidecar=prior)
    with open(os.path.join(drevp, "Proj_Revision_Report_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags resolved: F-P5-01, F-ZZ-99\n"
                 "<!-- resolved: F-P5-01 -->\n<!-- resolved: F-ZZ-99 -->\n")
    cmd_gate("revision_round", drevp, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", drevp, manifest, write=True, validate_sh=vs)
    fsp = read_ex(drevp).get("finding_states", {})
    check("rev_phantom_id_filtered", fsp.get("F-P5-01") == "revised" and "F-ZZ-99" not in fsp)

    # (P1) a Revision *Calendar* (not a Report) does NOT satisfy the revision_report artifact —
    # even one carrying a resolved marker — so the gate blocks rather than clearing with empty deltas
    drevc = folder(ledger2, sidecar=prior)
    with open(os.path.join(drevc, "Proj_Revision_Calendar_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Calendar\n<!-- resolved: F-P5-01 -->\n")
    code, _ = cmd_gate("revision_round", drevc, manifest, write=True, validate_sh=vs)
    check("rev_calendar_not_report_blocks",
          code == 1 and read_ex(drevc)["gate_events"][-1]["result"] == "blocked")

    # --- Finding dispositions (docs/finding-dispositions.md) — governed write path ---
    # (a) a revision_round clear with a declined marker in the revision report folds the FULL
    # record into finding_dispositions; pointer == fold.
    ddis = folder(ledger2, sidecar=prior)
    rep_path = os.path.join(ddis, "Proj_Revision_Report_run.md")
    with open(rep_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags resolved: F-P5-01\n<!-- resolved: F-P5-01 -->\n"
                 "- Flags set aside: F-P5-02\n"
                 "<!-- declined: F-P5-02 — abstraction is the register, a deliberate pass -->\n")
    cmd_gate("revision_round", ddis, manifest, write=True, validate_sh=vs)
    code, _ = cmd_attest("revision_round", ddis, manifest, write=True, validate_sh=vs)
    exd = read_ex(ddis)
    recd = exd.get("finding_dispositions", {}).get("F-P5-02", {})
    check("dispo_full_record_folds",
          code == 0 and recd.get("schema") == "apodictic.finding_disposition.v1"
          and recd.get("disposition") == "declined" and recd.get("source") == "author"
          and recd.get("reason") == "abstraction is the register, a deliberate pass"
          and isinstance(recd.get("session"), int) and recd.get("ts")
          and recd.get("artifact") == "Proj_Revision_Report_run.md")
    check("dispo_lifecycle_untouched",
          exd.get("finding_states", {}) == {"F-P5-01": "revised", "F-P5-02": "delivered"})
    check("dispo_check_state_clean",
          check_state(os.path.join(ddis, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    # (b) last-write-wins — deferred then declined for one id across two clears (same report file
    # rewritten, so artifact resolution stays stable).
    dlw = folder(ledger2, sidecar=prior)
    rep_lw = os.path.join(dlw, "Proj_Revision_Report_run.md")
    with open(rep_lw, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n<!-- deferred: F-P5-02 until: 2026-09 — waiting on the POV decision -->\n")
    cmd_gate("revision_round", dlw, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", dlw, manifest, write=True, validate_sh=vs)
    first = read_ex(dlw).get("finding_dispositions", {}).get("F-P5-02", {})
    with open(rep_lw, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n<!-- declined: F-P5-02 — POV decided; the stakes stay as-is -->\n")
    cmd_gate("revision_round", dlw, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", dlw, manifest, write=True, validate_sh=vs)
    exlw = read_ex(dlw)
    second = exlw.get("finding_dispositions", {}).get("F-P5-02", {})
    check("dispo_last_write_wins",
          first.get("disposition") == "deferred" and first.get("trigger") == "2026-09"
          and second.get("disposition") == "declined" and "trigger" not in second)
    check("dispo_lww_check_state_clean",
          check_state(os.path.join(dlw, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    # (c) supersedence — a later clear resolves the dispositioned id: the revised delta lands, the
    # disposition record is RETAINED (history; read-time precedence), pointer still == fold.
    with open(rep_lw, "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags resolved: F-P5-02\n<!-- resolved: F-P5-02 -->\n")
    cmd_gate("revision_round", dlw, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", dlw, manifest, write=True, validate_sh=vs)
    exsup = read_ex(dlw)
    check("dispo_superseded_record_retained",
          exsup.get("finding_states", {}).get("F-P5-02") == "revised"
          and exsup.get("finding_dispositions", {}).get("F-P5-02", {}).get("disposition") == "declined")
    check("dispo_supersede_check_state_clean",
          check_state(os.path.join(dlw, "Diagnostic_State.meta.json"), manifest)[0] == 0)

    def _dispo_rec(fid, kind="declined", **kw):
        rec = {"schema": "apodictic.finding_disposition.v1", "id": fid, "disposition": kind,
               "reason": "r", "source": "author", "session": 1, "ts": "t"}
        rec.update(kw)
        return rec

    # (d) disposition_deltas on a NON-clearing event -> check_state ERROR
    nonclear = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        {"gate": "revision_round", "result": "mechanical-passed", "provenance": "mechanical", "ts": "t0",
         "checks": [{"validator": "x", "result": "ok"}],
         "disposition_deltas": {"F-P5-01": _dispo_rec("F-P5-01")}},
    ], "finding_dispositions": {"F-P5-01": _dispo_rec("F-P5-01")}, "pending_gate": "revision_round",
        "allowed_next": []}}
    dnc2 = folder(ledger2, sidecar=nonclear)
    code, lines = check_state(os.path.join(dnc2, "Diagnostic_State.meta.json"), manifest)
    check("dispo_nonclearing_rejected",
          code == 1 and any("disposition_deltas only on a clearing passed" in ln for ln in lines))

    # (e) same-event launder — one event carrying finding_deltas[F-X]=revised AND
    # disposition_deltas[F-X] -> ERROR (revised and disclaimed by the same clear)
    launder_ev = _ev_passed("revision_round", {"F-P5-01": "revised"})
    launder_ev["disposition_deltas"] = {"F-P5-01": _dispo_rec("F-P5-01")}
    launder = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [launder_ev],
               "phase": "revision_round", "allowed_next": ["run_synthesis"],
               "finding_states": {"F-P5-01": "revised"},
               "finding_dispositions": {"F-P5-01": _dispo_rec("F-P5-01")}}}
    dla = folder(ledger2, sidecar=launder)
    code, lines = check_state(os.path.join(dla, "Diagnostic_State.meta.json"), manifest)
    check("dispo_same_event_launder_rejected",
          code == 1 and any("same-event launder" in ln for ln in lines))

    # (f) malformed record — deferred with no trigger -> ERROR (trigger-iff-deferred, log-side)
    badrec_ev = _ev_passed("revision_round", {})
    badrec_ev["disposition_deltas"] = {"F-P5-01": _dispo_rec("F-P5-01", kind="deferred")}
    badrec = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [badrec_ev],
              "phase": "revision_round", "allowed_next": ["run_synthesis"],
              "finding_dispositions": {"F-P5-01": _dispo_rec("F-P5-01", kind="deferred")}}}
    dbr = folder(ledger2, sidecar=badrec)
    code, lines = check_state(os.path.join(dbr, "Diagnostic_State.meta.json"), manifest)
    check("dispo_deferred_without_trigger_rejected",
          code == 1 and any("deferred requires a non-empty 'trigger'" in ln for ln in lines))

    # (g) a marker in a Feedback Triage artifact folds with source: triage
    dtg = folder(ledger2, sidecar=prior)
    with open(os.path.join(dtg, "Proj_Feedback_Triage_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Feedback Triage\n<!-- declined: F-P5-02 — reader claim refuted by Pass 5 -->\n")
    with open(os.path.join(dtg, "Proj_Revision_Report_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n- Flags resolved: F-P5-01\n<!-- resolved: F-P5-01 -->\n")
    cmd_gate("revision_round", dtg, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", dtg, manifest, write=True, validate_sh=vs)
    rect = read_ex(dtg).get("finding_dispositions", {}).get("F-P5-02", {})
    check("dispo_triage_marker_source",
          rect.get("source") == "triage" and rect.get("artifact") == "Proj_Feedback_Triage_run.md")

    # (h) write-time guards: an off-ledger id and a not-yet-delivered (locked) id are NOT frozen —
    # the same self-consistency _finding_deltas' phantom filter gives finding_states.
    locked_prior = {"project": "Proj", "execution": {"state_version": 2, "gate_events": [
        _ev_passed("run_synthesis", {"F-P5-01": "locked", "F-P5-02": "locked"}),
    ]}}
    dwg = folder(ledger2, sidecar=locked_prior)
    with open(os.path.join(dwg, "Proj_Revision_Report_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Revision Report\n<!-- declined: F-ZZ-99 — off ledger -->\n"
                 "<!-- declined: F-P5-02 — still only locked -->\n")
    cmd_gate("revision_round", dwg, manifest, write=True, validate_sh=vs)
    cmd_attest("revision_round", dwg, manifest, write=True, validate_sh=vs)
    check("dispo_write_guards_filter",
          read_ex(dwg).get("finding_dispositions", {}) == {})

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


# ---------------------------------------------------------------- main

def main(argv):
    if "--self-test" in argv:
        return run_self_test()

    manifest = _load_manifest()
    if not manifest:
        print("gate: could not locate execution-gates.v1.json")
        return 2

    args = argv[1:]
    write = "--no-write" not in args
    flags = [a for a in args if a.startswith("--")]
    pos = [a for a in args if not a.startswith("--")]

    def opt(name):
        if name in args:
            i = args.index(name)
            if i + 1 < len(args):
                return args[i + 1]
        return None

    if "--check-state" in flags:
        sidecar = pos[0] if pos else None
        if not sidecar or not os.path.exists(sidecar):
            print("Usage: run_gate.py --check-state <sidecar> [--strict]")
            return 2
        code, lines = check_state(sidecar, manifest, strict="--strict" in flags)
    elif "--attest" in flags:
        if len(pos) < 2:
            print("Usage: run_gate.py --attest <phase> <run_folder>")
            return 2
        code, lines = cmd_attest(pos[0], pos[1], manifest, write=write)
    elif "--skip" in flags or "--defer" in flags:
        kind = "skip" if "--skip" in flags else "defer"
        if len(pos) < 2:
            print("Usage: run_gate.py --%s <phase> <run_folder> --reason <text>%s"
                  % (kind, " [--until <text>]" if kind == "defer" else ""))
            return 2
        code, lines = cmd_exception(pos[0], pos[1], manifest, kind, opt("--reason"),
                                    until=opt("--until"), write=write)
    else:
        if len(pos) < 2:
            print("Usage: run_gate.py <phase> <run_folder> [--strict-warnings] "
                  "| --attest <phase> <run_folder> | --skip/--defer <phase> <run_folder> --reason ... "
                  "| --check-state <sidecar> [--strict] | --self-test")
            return 2
        code, lines = cmd_gate(pos[0], pos[1], manifest, strict_warnings="--strict-warnings" in flags, write=write)

    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
