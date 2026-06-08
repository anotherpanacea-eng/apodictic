#!/usr/bin/env python3
"""registry-check — integrity for the project registry (Project Addressability, Increment 2).

`validate.sh registry-check <registry.json | workspace_dir>` shells out here. The registry
(apodictic.project_registry.v1) is a recomputable index that makes APODICTIC projects
addressable: `/start <project>` and `/projects` resolve against it. Each per-project
Diagnostic_State.meta.json sidecar is canonical; the registry is a denormalized cache, so this
validator's job is to confirm the cache is well-formed and to surface drift (resolved toward the
sidecar — the cache never wins).

  R1 invalid entry    the envelope fails apodictic.project_registry.v1, or a project fails
                      apodictic.project_entry.v1 (bad/duplicate-shaped id pattern, missing
                      required field, bad mode enum, broken JSON).
  R2 missing root     a project's `root` does not resolve to an existing directory (ERROR), or it
                      exists but carries no Diagnostic_State.meta.json sidecar (WARN — a pre-writing
                      project's minimal sidecar may be pending).
  R3 drift            a denormalized field (`mode`, `next_action.key`) disagrees with the project's
                      sidecar (WARN; ERROR --strict). The sidecar is canonical — the registry is
                      a cache and is meant to be rebuilt, so drift is advisory, not fatal.
  R4 duplicate id     two entries share an `id` (ERROR — ids are the resolution handle).

Roots are resolved relative to the WORKSPACE ROOT (the parent of the `.apodictic/` directory that
holds the registry); absolute roots are honored as-is. Reuses apodictic_artifacts for schema
loading + flat-object validation. An empty/absent registry is a no-op. See docs/project-addressability.md.

  registry_check.py registry-check <registry.json | workspace_dir> [--strict]
  registry_check.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import json
import os
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_ENVELOPE_ID = "apodictic.project_registry.v1"
_ENTRY_ID = "apodictic.project_entry.v1"
_REGISTRY_REL = os.path.join(".apodictic", "registry.json")
_SIDECAR = "Diagnostic_State.meta.json"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _load_sidecar(root):
    """Return (sidecar_dict_or_None, present_bool) for a project root."""
    p = os.path.join(root, _SIDECAR)
    if not os.path.isfile(p):
        return None, False
    try:
        return json.loads(_read(p) or ""), True
    except (json.JSONDecodeError, TypeError):
        return None, True  # present but unparseable — treated as drift-unknown


def check_registry(reg_obj, workspace_root, strict=False):
    """Run R1-R4 over a parsed registry object. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    if art is None:
        return 0, ["registry-check: PASS (degraded — apodictic_artifacts unavailable)"]

    envelope_schema = art.load_schema(_ENVELOPE_ID)
    entry_schema = art.load_schema(_ENTRY_ID)
    if envelope_schema is None or entry_schema is None:
        return 2, ["registry-check: schema(s) not found via %s" % art.schema_dir()]

    # R1 — envelope
    for e in art.validate_obj(reg_obj, envelope_schema, "registry"):
        errs.append("R1 invalid entry: %s" % e)
    projects = reg_obj.get("projects")
    if not isinstance(projects, list):
        # envelope R1 already flagged it; nothing more to do
        return _report(lines, errs, warns, 0, strict)
    if not projects:
        return 0, ["registry-check: no projects registered — nothing to check"]

    # R1 — each entry
    valid = []
    for i, entry in enumerate(projects, 1):
        where = "project #%d" % i
        if not isinstance(entry, dict):
            errs.append("R1 invalid entry: %s is not an object" % where)
            continue
        entry_errs = art.validate_obj(entry, entry_schema, where)
        for e in entry_errs:
            errs.append("R1 invalid entry: %s" % e)
        if not entry_errs:
            valid.append(entry)

    # R4 — duplicate id
    seen = {}
    for entry in valid:
        seen.setdefault(entry.get("id"), 0)
        seen[entry.get("id")] += 1
    for pid, n in sorted(seen.items()):
        if n > 1:
            errs.append("R4 duplicate id: %s appears %d times (ids are the resolution handle)" % (pid, n))

    # R2/R3 — resolve roots against the workspace root, cross-check sidecars
    for entry in valid:
        pid, root = entry.get("id"), entry.get("root")
        abs_root = root if os.path.isabs(root) else os.path.join(workspace_root, root)
        if not os.path.isdir(abs_root):
            errs.append("R2 missing root: %s -> %s does not resolve to a directory" % (pid, root))
            continue
        sidecar, present = _load_sidecar(abs_root)
        if not present:
            warns.append("R2 missing sidecar: %s root has no %s (pre-writing minimal sidecar may be "
                         "pending)" % (pid, _SIDECAR))
            continue
        if sidecar is None:
            warns.append("R3 drift: %s sidecar is present but unparseable — cannot confirm cache" % pid)
            continue
        # R3 — denormalized fields vs sidecar (sidecar wins)
        if "mode" in entry and entry.get("mode") != sidecar.get("mode"):
            warns.append("R3 drift: %s mode=%r but sidecar=%r (sidecar wins; rebuild the cache)"
                         % (pid, entry.get("mode"), sidecar.get("mode")))
        reg_key = (entry.get("next_action") or {}).get("key")
        side_key = (sidecar.get("next_action") or {}).get("key")
        if entry.get("next_action") is not None and reg_key != side_key:
            warns.append("R3 drift: %s next_action.key=%r but sidecar=%r (sidecar wins)"
                         % (pid, reg_key, side_key))

    # Report
    lines.append("registry-check: %d project(s)%s"
                 % (len(projects), "" if len(valid) == len(projects)
                    else " (%d well-formed)" % len(valid)))
    for entry in valid:
        lines.append("  %-24s vol=%s mode=%s root=%s"
                     % (entry.get("id"), entry.get("volume", 1), entry.get("mode", "?"), entry.get("root")))
    return _report(lines, errs, warns, 0, strict)


def _report(lines, errs, warns, _code, strict):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("registry-check: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: registry-check: %d advisory drift(s) — rebuild the cache from sidecars" % len(warns))
    else:
        lines.append("registry-check: PASS (envelope + per-entry schema + unique ids + sidecar cross-check)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def resolve(paths):
    """Return (registry_path, workspace_root) or (None, None)."""
    if not paths:
        return None, None
    p = paths[0]
    if os.path.isdir(p):
        # a workspace dir: look for .apodictic/registry.json under it
        cand = os.path.join(p, _REGISTRY_REL)
        if os.path.isfile(cand):
            return cand, p
        return None, None
    if os.path.isfile(p):
        # a registry file: workspace root is the parent of its .apodictic/ dir
        ap_dir = os.path.dirname(os.path.abspath(p))
        workspace = os.path.dirname(ap_dir) if os.path.basename(ap_dir) == ".apodictic" else ap_dir
        return p, workspace
    return None, None


def run(paths, strict=False):
    reg_path, workspace = resolve(paths)
    if not reg_path:
        return 2, ["registry-check: no registry found (need a .apodictic/registry.json or a workspace "
                   "dir containing one)"]
    text = _read(reg_path)
    if text is None:
        return 2, ["registry-check: cannot read %s" % reg_path]
    try:
        reg_obj = json.loads(text)
    except json.JSONDecodeError as ex:
        return 1, ["registry-check: FAIL (1 error(s))", "  ERROR: R1 invalid entry: registry is not "
                   "valid JSON — %s" % ex]
    return check_registry(reg_obj, workspace, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    if art is None or art.load_schema(_ENVELOPE_ID) is None:
        print("  schema_load: FAIL (registry schemas not found)")
        print("Self-test: FAIL")
        return 1
    print("  schema_load: OK (%s)" % art.schema_dir())

    def sidecar(mode="diagnostic", na_key="run_passes"):
        return json.dumps({"schema": "apodictic.diagnostic-state.v1", "mode": mode,
                           "next_action": {"key": na_key, "description": ""}})

    def entry(pid="wolves-of-november", root="Wolves_Of_November", mode="diagnostic",
              na_key="run_passes", **extra):
        e = {"id": pid, "title": "Wolves of November", "root": root, "volume": 1,
             "mode": mode, "next_action": {"key": na_key, "description": ""},
             "last_touched": "2026-06-08"}
        e.update(extra)
        return e

    def workspace(entries, sidecars):
        """Build a temp workspace; sidecars maps root-> sidecar-json-or-None (None = no sidecar)."""
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, ".apodictic"))
        reg = {"schema": _ENVELOPE_ID, "updated": "2026-06-08", "projects": entries}
        with open(os.path.join(d, ".apodictic", "registry.json"), "w") as fh:
            json.dump(reg, fh)
        for root, sc in sidecars.items():
            os.makedirs(os.path.join(d, root), exist_ok=True)
            if sc is not None:
                with open(os.path.join(d, root, _SIDECAR), "w") as fh:
                    fh.write(sc)
        return d

    beds = []

    def ws(entries, sidecars):
        d = workspace(entries, sidecars)
        beds.append(d)
        return d

    try:
        # clean
        d = ws([entry()], {"Wolves_Of_November": sidecar()})
        chk("clean_single", run([d])[0] == 0)
        chk("clean_via_file", run([os.path.join(d, ".apodictic", "registry.json")])[0] == 0)

        # R1 bad id pattern / missing field / bad mode enum
        chk("r1_bad_id", run([ws([entry(pid="Wolves_Of_November")], {"Wolves_Of_November": sidecar()})])[0] == 1)
        bad = entry(); del bad["root"]
        chk("r1_missing_root_field", run([ws([bad], {})])[0] == 1)
        chk("r1_bad_mode", run([ws([entry(mode="archived")], {"Wolves_Of_November": sidecar()})])[0] == 1)

        # R4 duplicate id
        d = ws([entry(), entry(root="Other_Dir")],
               {"Wolves_Of_November": sidecar(), "Other_Dir": sidecar()})
        code, out = run([d])
        chk("r4_duplicate_id", code == 1 and any("R4 duplicate" in ln for ln in out))

        # R2 missing root dir -> ERROR
        code, out = run([ws([entry(root="Does_Not_Exist")], {})])
        chk("r2_missing_root", code == 1 and any("R2 missing root" in ln for ln in out))

        # R2 root exists but no sidecar -> WARN (advisory; clean exit), ERROR --strict
        d = ws([entry()], {"Wolves_Of_November": None})
        code, out = run([d])
        chk("r2_missing_sidecar_warn", code == 0 and any("R2 missing sidecar" in ln for ln in out))
        chk("r2_missing_sidecar_strict", run([d], strict=True)[0] == 1)

        # R3 drift: registry mode disagrees with sidecar -> WARN, sidecar wins
        d = ws([entry(mode="execution")], {"Wolves_Of_November": sidecar(mode="diagnostic")})
        code, out = run([d])
        chk("r3_mode_drift_warn", code == 0 and any("R3 drift" in ln and "mode" in ln for ln in out))
        chk("r3_drift_strict_fails", run([d], strict=True)[0] == 1)

        # R3 drift: next_action.key disagrees
        d = ws([entry(na_key="deliver")], {"Wolves_Of_November": sidecar(na_key="run_passes")})
        chk("r3_next_action_drift", any("R3 drift" in ln and "next_action" in ln for ln in run([d])[1]))

        # empty registry -> no-op
        chk("empty_noop", run([ws([], {})])[0] == 0)

        # broken JSON -> R1 error
        d = tempfile.mkdtemp(); beds.append(d)
        os.makedirs(os.path.join(d, ".apodictic"))
        with open(os.path.join(d, ".apodictic", "registry.json"), "w") as fh:
            fh.write('{"schema": "apodictic.project_registry.v1", ')  # truncated
        code, out = run([d])
        chk("r1_broken_json", code == 1 and any("not valid JSON" in ln for ln in out))

        # missing registry -> usage
        chk("missing_registry_usage", run([tempfile.mkdtemp()])[0] == 2)
    finally:
        for d in beds:
            shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "registry-check"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: registry_check.py registry-check <registry.json | workspace_dir> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
