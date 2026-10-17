#!/usr/bin/env python3
"""schema-coverage — the drift-kill keystone for Harness Contracts v2.

`python validate.py schema-coverage [<schemas_dir>] [--strict] [--check-docs]` delegates here. The
22 structured-artifact JSON-Schema files in plugins/apodictic/schemas/ already ARE the single
source of truth, and every one is bound to a Python validator. What was missing is the invariant
the whole system rests on: that *every* `*.schema.json` on disk stays bound to a validator and
stays exercised against a real canonical file by `--check-all`. A new (or renamed/orphaned)
schema could land with no validator and no gate teeth, and CI would stay green. This gate proves
disk reality matches the declarative `_coverage.json` binding table.

  C1 manifest validity   _coverage.json parses + validates against apodictic.schema_coverage.v1
                         (and each binding against apodictic.schema_binding.v1).            ERROR
  C2 no orphan schema    every *.schema.json on disk (minus non_artifact[] and the two self
                         schemas schema_coverage/schema_binding) appears in bindings[].     ERROR
  C3 no phantom binding  every bindings[].schema exists on disk as <schema>.schema.json.    ERROR
  C4 binding proven      each bound command has an actual native first-self-test route and the
                         whole schema ID occurs as non-docstring literal data in its primary
                         helper. This establishes source association, not semantic field proof.
  C5 canonical reachable a bound command receives the exact references-relative artifact through
                         a direct native canonical call or one ordered path assignment in an
                         actually called section. Unknown control cannot supply an anchor.
                         self-test-only requires a real aggregate route.                     ERROR
  W1 non_artifact integ. every non_artifact[] entry exists on disk as a *.schema.json file
                         (else the exclusion is dead).                         WARN; ERROR --strict

The closed-key contract is cross-checked too: for each binding, the schema file's
`additionalProperties` must agree with the manifest's `closed_keys` (true -> false-in-file;
false/absent -> not-closed-in-file). A drift between the table and the schema file is an ERROR
under C1' (manifest<->file closed-key agreement).

`--check-docs` runs the advisory docs-no-re-list lint (Harness Contracts v2 §4.4): for the
closed-key set plus finding.v1, scan the author-facing reference docs that opt in by carrying a
defer-marker and WARN if any enumerates a field name the schema does not declare. Narrow by
construction (opt-in docs only); advisory in increment 1.

Reuses apodictic_artifacts for all schema loading (no second schema reader). Stdlib only; shells
nothing (reads files directly). Without apodictic_artifacts, retains the legacy degraded PASS
only if native source checks succeed; this fallback does not verify schemas.

  schema_coverage.py schema-coverage [<schemas_dir>] [--strict] [--check-docs]
  schema_coverage.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import json
import os
import re
import sys
try:
    from validate_source import SourceError, read_aggregate, read_dispatch, read_canonical, schema_literals
except ImportError as exc:
    print("schema-coverage: source-check unavailable: " + str(exc), file=sys.stderr)
    raise SystemExit(2)
from pathlib import Path

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_MANIFEST_NAME = "_coverage.json"
_COVERAGE_ID = "apodictic.schema_coverage.v1"
_BINDING_ID = "apodictic.schema_binding.v1"
# The two manifest-describing schemas are themselves *.schema.json on disk but are NOT artifact
# carriers, so they are excluded from the orphan check (they describe the table, they aren't IN it).
_SELF_SCHEMAS = frozenset({_COVERAGE_ID, _BINDING_ID})
_SELF_TEST_ONLY = "self-test-only"


# --------------------------------------------------------------- location helpers

def _default_scripts_dir():
    return Path(__file__).resolve().parent


def _default_schemas_dir():
    if art is not None:
        d = art.schema_dir()
        if d:
            return Path(d)
    return None


def _disk_schema_ids(schemas_dir):
    """All *.schema.json stems on disk under schemas_dir (sorted)."""
    if not schemas_dir or not Path(schemas_dir).is_dir():
        return []
    return sorted(p.name[: -len(".schema.json")] for p in Path(schemas_dir).glob("*.schema.json"))


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _load_schema_from(schemas_dir, sid):
    """Read <sid>.schema.json directly from schemas_dir (no global id-cache — the gate is
    parameterized on its schemas dir, so it must not pick up art.load_schema's default-dir cache,
    which matters for the hermetic self-test where the same id lives in several tmp dirs)."""
    raw = _read(Path(schemas_dir) / (sid + ".schema.json"))
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _canonical_invoked(calls, validators, token):
    return any(call.command in validators and any(token in parts for parts in call.reference_paths)
               for call in calls)


def _references_dir(scripts_dir):
    """Locate core-editor/references/ from either script-dir copy (canonical files live there)."""
    here = Path(scripts_dir).resolve()
    for cand in (
        here / ".." / "skills" / "core-editor" / "references",
        here / ".." / "plugins" / "apodictic" / "skills" / "core-editor" / "references",
        here / "plugins" / "apodictic" / "skills" / "core-editor" / "references",
    ):
        cand = cand.resolve()
        if cand.is_dir():
            return cand
    return None


# --------------------------------------------------------------- the gate

def run(schemas_dir=None, scripts_dir=None, strict=False):
    """Run C1-C5 + W1 + the closed-key agreement cross-check. Returns (code, lines)."""
    if art is None:
        # Retain the legacy artifact-import fallback only after native source
        # validity is established; unavailable source must never become a PASS.
        source_dir = Path(scripts_dir) if scripts_dir else _default_scripts_dir()
        try:
            dispatcher = source_dir / "validate.py"
            read_dispatch(dispatcher)
            read_aggregate(dispatcher)
            read_canonical(dispatcher, source_dir / "validate_canonical.py")
        except SourceError as exc:
            return 1, ["schema-coverage: C4/C5 source-check: %s" % exc]
        return 0, ["schema-coverage: PASS (degraded — apodictic_artifacts unavailable)"]
    schemas_dir = Path(schemas_dir) if schemas_dir else _default_schemas_dir()
    scripts_dir = Path(scripts_dir) if scripts_dir else _default_scripts_dir()
    if not schemas_dir or not Path(schemas_dir).is_dir():
        return 2, ["schema-coverage: no schemas dir found (need plugins/apodictic/schemas/)"]

    lines, errs, warns = [], [], []
    manifest_path = Path(schemas_dir) / _MANIFEST_NAME

    # C1 — manifest validity.
    raw = _read(manifest_path)
    if raw is None:
        return 1, ["schema-coverage: FAIL (1 error(s))",
                   "  ERROR: C1 manifest missing — %s not found" % manifest_path]
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as ex:
        return 1, ["schema-coverage: FAIL (1 error(s))",
                   "  ERROR: C1 manifest is not valid JSON — %s" % ex]

    cov_schema = _load_schema_from(schemas_dir, _COVERAGE_ID)
    bind_schema = _load_schema_from(schemas_dir, _BINDING_ID)
    if cov_schema is None or bind_schema is None:
        return 1, ["schema-coverage: FAIL (1 error(s))",
                   "  ERROR: C1 coverage/binding schema not found under %s" % schemas_dir]
    for e in art.validate_obj(manifest, cov_schema, _MANIFEST_NAME):
        errs.append("C1 manifest invalid: %s" % e)
    bindings = manifest.get("bindings", []) if isinstance(manifest, dict) else []
    if not isinstance(bindings, list):
        bindings = []
    for i, b in enumerate(bindings):
        for e in art.validate_obj(b, bind_schema, "%s.bindings[%d]" % (_MANIFEST_NAME, i)):
            errs.append("C1 binding invalid: %s" % e)
    if errs:  # a malformed manifest makes the rest unreliable — report C1 and stop.
        return _report(["schema-coverage: %d binding(s) declared" % len(bindings)], errs, warns, strict)

    non_artifact = manifest.get("non_artifact", []) or []
    bound_ids = [b["schema"] for b in bindings]
    disk_ids = _disk_schema_ids(schemas_dir)
    disk_set = set(disk_ids)

    # C2 — no orphan schema. Every artifact *.schema.json appears in bindings[] (or non_artifact[]).
    excluded = set(non_artifact) | _SELF_SCHEMAS
    for sid in disk_ids:
        if sid in excluded:
            continue
        if sid not in bound_ids:
            errs.append("C2 orphan schema: %s.schema.json has no binding row (add it to %s or non_artifact[])"
                        % (sid, _MANIFEST_NAME))

    # C3 — no phantom binding. Every bindings[].schema exists on disk.
    for b in bindings:
        if b["schema"] not in disk_set:
            errs.append("C3 phantom binding: bindings[].schema %s has no %s.schema.json on disk"
                        % (b["schema"], b["schema"]))

    # Finite source guarantees inspect real native routes without importing them.
    try:
        dispatcher = Path(scripts_dir) / "validate.py"
        arms = read_dispatch(dispatcher)
        agg = read_aggregate(dispatcher)
        ca_region = read_canonical(dispatcher, Path(scripts_dir) / "validate_canonical.py")
    except SourceError as exc:
        return _report(lines, errs + ["C4/C5 source-check: %s" % exc], warns, strict)
    refs = _references_dir(scripts_dir)

    for b in bindings:
        sid = b["schema"]
        validators = b.get("validators", [])
        # C4 — a real native route binds a primary helper with the whole schema ID literal.
        proven = False
        real_arm = None
        for arm in validators:
            if arm in arms:
                real_arm = arm
                for scr in arms[arm].helper_files:
                    try:
                        literals = schema_literals(Path(scripts_dir) / scr)
                    except SourceError as exc:
                        errs.append("C4 source-check: %s" % exc)
                        continue
                    if any(re.search(r"(?<![0-9A-Za-z_.])" + re.escape(sid) + r"(?![0-9A-Za-z_.])", text) for text in literals):
                        proven = True
                        break
            if proven:
                break
        if real_arm is None:
            errs.append("C4 binding unproven: %s names no real native dispatch route (%r)" % (sid, validators))
        elif not proven:
            errs.append("C4 binding unproven: %s id literal not found in any .py bound to %r (claimed by %s)"
                        % (sid, validators, real_arm))

        # C5 — canonical-gate reachability.
        gate = b.get("canonical_gate", "")
        if gate == _SELF_TEST_ONLY:
            # exempt from the file check, but the bound arm must run SOME real check (in AGG_VALIDATORS).
            if not any(v in agg and v in arms and arms[v].self_test_kind for v in validators):
                errs.append("C5 self-test-only escape unbacked: %s's validator(s) %r are not in AGG_VALIDATORS"
                            % (sid, validators))
        else:
            if not _canonical_invoked(ca_region, validators, gate):
                errs.append("C5 canonical gate unreached: %s's canonical_gate %r is not passed to a real "
                            "--check-all invocation of its bound validator(s) %r (an echo/comment, or an "
                            "arg to an unrelated validator, does not count)" % (sid, gate, validators))
            if refs is None or not (Path(refs) / gate).exists():
                errs.append("C5 canonical file missing: %s's canonical_gate %r not found under references/"
                            % (sid, gate))

        # C1' — closed-key agreement: the schema file's additionalProperties must match the table.
        want_closed = bool(b.get("closed_keys", False))
        if sid in disk_set:
            sch = _load_schema_from(schemas_dir, sid)
            file_closed = (sch or {}).get("additionalProperties") is False
            if want_closed and not file_closed:
                errs.append("C1' closed-key drift: %s has closed_keys:true but its schema file is not "
                            "additionalProperties:false" % sid)
            if (not want_closed) and file_closed:
                errs.append("C1' closed-key drift: %s has closed_keys:false/absent but its schema file IS "
                            "additionalProperties:false (declare it in the table)" % sid)

    # W1 — non_artifact integrity. Every entry must exist on disk as a *.schema.json file.
    for na in non_artifact:
        if na not in disk_set:
            warns.append("W1 dead non_artifact exclusion: %r is not a *.schema.json on disk" % na)

    head = "schema-coverage: %d schema(s) on disk, %d binding(s), %d non-artifact" % (
        len(disk_ids), len(bindings), len(non_artifact))
    return _report([head], errs, warns, strict)


def _report(lines, errs, warns, strict):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("schema-coverage: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: schema-coverage: %d advisory issue(s)" % len(warns))
    else:
        lines.append("schema-coverage: PASS (no orphan/phantom; every binding proven + canonically reached)")
    return 0, lines


# --------------------------------------------------------------- docs-no-re-list lint (advisory)

# Docs opt in to the lint by carrying a defer-marker — a line that says the field set is canonical
# in the schema, not the prose. We scan only those docs (never arbitrary prose).
_DEFER_MARKER = re.compile(r'canonical in[^\n]*\.schema\.json|canonical in `?schemas/', re.IGNORECASE)
# A backtick-quoted token on a defer-marker doc that LOOKS like a field name (lower_snake / lower).
_FIELDLIKE = re.compile(r'`([a-z][a-z0-9_]{2,})`')
# A line that LABELS a field-set re-listing (`Fields:`, `**Fields (all required):**`, `field set`).
# Only such lines are eligible — prose that merely names a field is not a re-listing.
_FIELD_RELIST_LABEL = re.compile(r'\*\*Fields\b|(?:^|\s)Fields\s*[:(]|\bfield set\b', re.IGNORECASE)
# Per-schema docs whose defer-marker scopes a SPECIFIC schema id (so we know which field set to check).
_SCHEMA_MENTION = re.compile(r'apodictic\.([a-z_]+)\.v1')


def check_docs(scripts_dir=None, refs_dir=None):
    """Advisory docs-no-re-list lint. Returns (code, lines). WARN-only (increment 1).

    refs_dir overrides the references/ location (used by the hermetic self-test)."""
    if art is None:
        return 0, ["schema-coverage --check-docs: PASS (degraded — apodictic_artifacts unavailable)"]
    scripts_dir = Path(scripts_dir) if scripts_dir else _default_scripts_dir()
    refs = Path(refs_dir) if refs_dir else _references_dir(scripts_dir)
    lines, warns = [], []
    if refs is None:
        return 0, ["schema-coverage --check-docs: PASS (no references/ dir found — nothing to lint)"]
    scanned = 0
    for doc in sorted(Path(refs).glob("*.md")):
        text = _read(doc)
        if not text or not _DEFER_MARKER.search(text):
            continue
        scanned += 1
        # Field sets the defer-marker doc points at: every schema id it mentions, restricted to those
        # actually on disk. We check each backtick token against the union of those field sets and
        # WARN only on a token that matches NO mentioned schema's field set but looks like a field name
        # AND collides with the same schema family namespace (a field name pattern, not arbitrary prose).
        mentioned = []
        for m in _SCHEMA_MENTION.finditer(text):
            sid = "apodictic.%s.v1" % m.group(1)
            fields = art.schema_field_names(sid)
            if fields is not None:
                mentioned.append((sid, fields))
        if not mentioned:
            continue
        known_fields = set()
        for _sid, f in mentioned:
            known_fields |= set(f)
        # Fire ONLY on a line that is an explicit field-set RE-LISTING — one carrying a `Fields:` /
        # `**Fields (…):**` / `field set` LABEL. This is the narrow target: the lines that enumerate a
        # schema's properties in prose (findings-ledger-format.md:94/133/134). Prose that merely
        # MENTIONS a field name (e.g. "the finest `quote` rung") carries no such label and is left
        # alone — the honest seam the spec calls out (catch divergence in a re-listing, not arbitrary
        # prose). Advisory in increment 1.
        for ln in text.splitlines():
            if not _FIELD_RELIST_LABEL.search(ln):
                continue
            line_tokens = _FIELDLIKE.findall(ln)
            # only a genuine re-listing: the labelled line must enumerate >=1 REAL field of a
            # mentioned schema (so a stray label with no field list is not flagged).
            if not any(t in known_fields for t in line_tokens):
                continue
            for tok in line_tokens:
                if tok in known_fields:
                    continue
                warns.append("%s: re-lists field %r not declared by any mentioned schema (%s) — "
                             "prose drift" % (doc.name, tok, ", ".join(sorted({s for s, _ in mentioned}))))
    if warns:
        # dedupe
        seen, uniq = set(), []
        for w in warns:
            if w not in seen:
                seen.add(w)
                uniq.append(w)
        warns = uniq
        lines.append("schema-coverage --check-docs: %d advisory prose-drift WARN(s) over %d opt-in doc(s)"
                     % (len(warns), scanned))
        for w in warns:
            lines.append("  WARN: %s" % w)
    else:
        lines.append("schema-coverage --check-docs: ok (%d opt-in doc(s) scanned, no prose drift)" % scanned)
    return 0, lines  # advisory in increment 1 — never fails the gate


# --------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    if art is None:
        print("  apodictic_artifacts: FAIL (unavailable)")
        print("Self-test: FAIL")
        return 1

    beds = []

    def bed():
        d = tempfile.mkdtemp()
        beds.append(d)
        return Path(d)

    def write_schema(sdir, sid, closed=False, props=None):
        props = props or {"schema": {"const": sid}, "a": {"type": "string"}}
        obj = {"$id": sid, "type": "object", "required": ["schema"], "properties": props}
        if closed:
            obj["additionalProperties"] = False
        (sdir / (sid + ".schema.json")).write_text(json.dumps(obj), encoding="utf-8")

    def setup(bindings, non_artifact=None, extra_disk=None, closed_on_disk=None, ca_lines=None):
        """Build a hermetic fixture: a schemas dir + scripts dir + validate.py + references dir.

        bindings: list of dicts for _coverage.json. extra_disk: schema ids to drop on disk with NO
        binding (orphans). closed_on_disk: set of schema ids to write additionalProperties:false.
        ca_lines(bindings) -> list[str]: optional override for the --check-all body (to forge the
        echo-only / unrelated-validator C5 negatives); default emits a real bound invocation per gate
        mirroring the production `if [ "$1" = "--check-all" ]; then ... "$0" <arm> "$CA_BASE/<gate>" ...`."""
        root = bed()
        sdir = root / "schemas"
        scr = root / "scripts"
        refs = root / "skills" / "core-editor" / "references"
        sdir.mkdir()
        scr.mkdir()
        refs.mkdir(parents=True)
        closed_on_disk = closed_on_disk or set()
        # always ship the two self schemas + the cov/bind schemas (copied from the real engine dir)
        real = _default_schemas_dir()
        for sid in (_COVERAGE_ID, _BINDING_ID):
            shutil.copy(str(Path(real) / (sid + ".schema.json")), str(sdir / (sid + ".schema.json")))
        for b in bindings:
            write_schema(sdir, b["schema"], closed=(b["schema"] in closed_on_disk))
        for sid in (extra_disk or []):
            write_schema(sdir, sid)
        arms = sorted({v for b in bindings for v in b.get("validators", [])})
        for b in bindings:
            g = b.get("canonical_gate", "")
            if g and g != _SELF_TEST_ONLY:
                (refs / g).write_text("fixture\n", encoding="utf-8")

        def _default_ca(bs):
            return ["run_validator(%r, references / %r)" % (b["validators"][0], b["canonical_gate"])
                    for b in bs if b.get("canonical_gate") != _SELF_TEST_ONLY]

        ca_body = ca_lines(bindings) if ca_lines else _default_ca(bindings)
        table = {}
        for a in arms:
            scrname = a.replace("-", "_") + ".py"
            table[a] = scrname
            ids = [b["schema"] for b in bindings if a in b.get("validators", [])]
            (scr / scrname).write_text("SCHEMAS = %r\n" % ids, encoding="utf-8")
        vpy = "\n".join([
            "from pathlib import Path", "import sys, subprocess",
            "from validate_canonical import run_canonical",
            "AGG_VALIDATORS = %r" % (tuple(arms),), "_FIXTURE = %r" % table,
            "def _run_helper(script, args):",
            "    result = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / script), *args])",
            "    return result.returncode",
            "def _self_test(command): pass", "def _argument_carve(args): pass",
            "def _fixture(command, args):",
            "    script = _FIXTURE[command]",
            "    return _run_helper(script, args)",
            "def main(argv=None):",
            "    args = list(sys.argv[1:] if argv is None else argv)",
            "    command = args[0]",
            "    if command == '--check-canonical':", "        return run_canonical()",
            "    if command == '--check-all':", "        return run_canonical()",
            "    if command in _FIXTURE:", "        return _fixture(command, args)",
            "if __name__ == '__main__':", "    sys.exit(main())",
        ])
        (scr / "validate.py").write_text(vpy + "\n", encoding="utf-8")
        canonical = "\n".join([
            "from pathlib import Path", "import sys, subprocess",
            "def run_validator(command, *arguments):",
            "    return subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'validate.py'), command, *arguments])",
            "def run_canonical():", "    references = Path(__file__).resolve().parent / '../skills/core-editor/references'",
            *["    " + line for line in ca_body], "    return 0",
        ])
        (scr / "validate_canonical.py").write_text(canonical + "\n", encoding="utf-8")
        manifest = {"schema": _COVERAGE_ID, "non_artifact": non_artifact or [], "bindings": bindings}
        (sdir / _MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
        return sdir, scr

    base = [
        {"schema": "apodictic.alpha.v1", "validators": ["alpha"], "canonical_gate": "example-alpha.md", "closed_keys": False},
        {"schema": "apodictic.beta.v1", "validators": ["beta"], "canonical_gate": "self-test-only", "closed_keys": False},
    ]

    try:
        # clean baseline
        sd, sc = setup([dict(b) for b in base])
        chk("clean", run(sd, sc)[0] == 0)

        # C2 orphan: a schema on disk with no binding row.
        sd, sc = setup([dict(b) for b in base], extra_disk=["apodictic.orphan.v1"])
        code, out = run(sd, sc)
        chk("c2_orphan", code == 1 and any("C2 orphan" in ln and "orphan" in ln for ln in out))

        # C3 phantom: a binding row for a schema not on disk.
        bad = [dict(b) for b in base] + [{"schema": "apodictic.ghost.v1", "validators": ["alpha"],
                                          "canonical_gate": "self-test-only", "closed_keys": False}]
        # ghost has no schema file (setup writes a file per binding) -> simulate by removing it:
        sd, sc = setup(bad)
        os.remove(str(Path(sd) / "apodictic.ghost.v1.schema.json"))
        code, out = run(sd, sc)
        chk("c3_phantom", code == 1 and any("C3 phantom" in ln for ln in out))

        # C4 unproven (no real arm): the named validator is not a real validate.py dispatch arm.
        # setup() materializes an arm per named validator, so strip alpha's arm + AGG entry afterward.
        sd, sc = setup([dict(b) for b in base])
        vpath = Path(sc) / "validate.py"
        vtxt = vpath.read_text(encoding="utf-8")
        vtxt = vtxt.replace("AGG_VALIDATORS = ('alpha', 'beta')", "AGG_VALIDATORS = ('beta',)")
        vtxt = vtxt.replace("'alpha': 'alpha.py', ", "")
        vpath.write_text(vtxt, encoding="utf-8")
        code, out = run(sd, sc)
        chk("c4_no_arm", code == 1 and any("C4 binding unproven" in ln and "no real" in ln for ln in out))

        # C4 unproven (arm real but bound .py lacks the id): clobber the bound script.
        sd, sc = setup([dict(b) for b in base])
        (Path(sc) / "alpha.py").write_text("# unrelated\n", encoding="utf-8")
        code, out = run(sd, sc)
        chk("c4_id_not_in_bound_py", code == 1 and any("C4 binding unproven" in ln and "not found" in ln for ln in out))

        # C5 canonical gate not run by --check-all: rewrite validate.py to drop the token.
        sd, sc = setup([dict(b) for b in base])
        vtxt = (Path(sc) / "validate_canonical.py").read_text(encoding="utf-8").replace("example-alpha.md", "OTHER.md")
        (Path(sc) / "validate_canonical.py").write_text(vtxt, encoding="utf-8")
        code, out = run(sd, sc)
        chk("c5_gate_unreached", code == 1 and any("C5 canonical gate unreached" in ln for ln in out))

        # C5 BIND — Codex round-9 P2: the token must be passed to a REAL invocation of a BOUND
        # validator, not merely occur somewhere in the --check-all text.
        # (a) token present ONLY in an echo/comment -> still on disk, but never exercised -> FAIL.
        def _ca_echo_only(bs):
            out_ = []
            for bb in bs:
                g = bb.get("canonical_gate", "")
                if g and g != _SELF_TEST_ONLY:
                    out_.append('print(%r) # %s' % (g, g))  # echo + comment, no "$0"
            return out_
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_echo_only)
        code, out = run(sd, sc)
        chk("c5_echo_only_fails", code == 1 and any("C5 canonical gate unreached" in ln for ln in out))

        # (b) token passed ONLY to an UNRELATED validator (not in alpha's validators[]) -> FAIL.
        # alpha's gate (example-alpha.md) is handed to `beta`, never to `alpha`.
        def _ca_unrelated(bs):
            return ["run_validator('beta', references / 'example-alpha.md')",
                    "run_validator('beta', references / 'example-beta.md')"]
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_unrelated)
        # beta's own gate is self-test-only so beta needs no file gate; only alpha's C5 should fire.
        code, out = run(sd, sc)
        chk("c5_unrelated_validator_fails",
            code == 1 and any("C5 canonical gate unreached" in ln and "apodictic.alpha.v1" in ln for ln in out))

        # (c) POSITIVE: token reached through ONE HOP of variable indirection (the real CA_RUNDIR
        # pattern) passes; and a sibling token (-extra) handed to an unrelated arm does NOT leak in.
        def _ca_indirect(bs):
            return ["P = references / 'example-alpha.md'",
                    "run_validator('beta', references / 'example-alpha.md-extra')",
                    "run_validator('alpha', P / 'inner.json')"]
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_indirect)
        chk("c5_indirection_passes", run(sd, sc)[0] == 0)

        # (c2) GUARD — Codex round-10 P2: a variable reassigned AFTER the bound invocation must NOT
        # retroactively satisfy C5 via that later value. At the alpha invocation `$P` holds `OTHER.md`
        # (the gate is NOT exercised); the trailing `P="$CA_BASE/example-alpha.md"` is dead w.r.t. the
        # call. A last-assignment-wins resolver would wrongly PASS this -> must FAIL. (beta carries its
        # own gate so only alpha's C5 should fire.)
        def _ca_reassign_after(bs):
            return ["P = references / 'OTHER.md'", "run_validator('alpha', P)",
                    "P = references / 'example-alpha.md'",
                    "run_validator('beta', references / 'example-beta.md')"]
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_reassign_after)
        code, out = run(sd, sc)
        chk("c5_reassign_after_invocation_fails",
            code == 1 and any("C5 canonical gate unreached" in ln and "apodictic.alpha.v1" in ln for ln in out))

        # (c3) POSITIVE companion: the SAME variable assigned to the gate BEFORE the invocation (and
        # only reused/shadowed afterward) still passes — in-scope resolution must accept the prior value.
        def _ca_reassign_before(bs):
            return ["P = references / 'example-alpha.md'", "run_validator('alpha', P)",
                    "P = references / 'OTHER.md'"]
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_reassign_before)
        chk("c5_reassign_before_invocation_passes", run(sd, sc)[0] == 0)

        # (d) GUARD: the component matcher must not let a longer sibling token satisfy a shorter gate.
        # alpha's gate token appears ONLY as `example-alpha.md-r1` (a different component) on alpha's
        # own invocation -> must still FAIL (substring would have wrongly passed).
        def _ca_sibling_substring(bs):
            return ["run_validator('alpha', references / 'example-alpha.md-r1')"]
        sd, sc = setup([dict(b) for b in base], ca_lines=_ca_sibling_substring)
        code, out = run(sd, sc)
        chk("c5_sibling_substring_fails",
            code == 1 and any("C5 canonical gate unreached" in ln and "apodictic.alpha.v1" in ln for ln in out))

        # C5 canonical file missing: remove the canonical file from references/.
        sd, sc = setup([dict(b) for b in base])
        os.remove(str(_references_dir(sc) / "example-alpha.md"))
        code, out = run(sd, sc)
        chk("c5_file_missing", code == 1 and any("C5 canonical file missing" in ln for ln in out))

        # C5 self-test-only escape unbacked: beta's arm not in AGG_VALIDATORS.
        sd, sc = setup([dict(b) for b in base])
        vpath = Path(sc) / "validate.py"
        vtxt = vpath.read_text(encoding="utf-8").replace("AGG_VALIDATORS = ('alpha', 'beta')", "AGG_VALIDATORS = ('alpha',)")
        vpath.write_text(vtxt, encoding="utf-8")
        code, out = run(sd, sc)
        chk("c5_selftest_only_unbacked", code == 1 and any("C5 self-test-only escape unbacked" in ln for ln in out))

        # closed-key drift: table says closed but the schema file is open.
        closed_b = [dict(base[0], closed_keys=True), dict(base[1])]
        sd, sc = setup(closed_b)  # closed_on_disk NOT set -> file stays open -> drift
        code, out = run(sd, sc)
        chk("closed_key_drift_table_vs_file", code == 1 and any("C1' closed-key drift" in ln for ln in out))

        # closed-key agreement clean: table closed AND file closed -> PASS.
        sd, sc = setup(closed_b, closed_on_disk={"apodictic.alpha.v1"})
        chk("closed_key_agreement_clean", run(sd, sc)[0] == 0)

        # closed-key TYPO kill: a closed schema rejects an unknown field via the engine (the §4.3 proof).
        closed_schema = {"$id": "apodictic.alpha.v1", "type": "object", "required": ["schema"],
                         "additionalProperties": False,
                         "properties": {"schema": {"const": "apodictic.alpha.v1"}, "recommendation": {"type": "string"}}}
        typo = art.validate_obj({"schema": "apodictic.alpha.v1", "recomendation": "x"}, closed_schema, "<typo>")
        chk("closed_key_typo_rejected", any("unknown field 'recomendation'" in e for e in typo))

        # W1 dead non_artifact exclusion: a non_artifact entry not on disk -> WARN (ERROR --strict).
        sd, sc = setup([dict(b) for b in base], non_artifact=["does-not-exist"])
        code, out = run(sd, sc)
        chk("w1_dead_exclusion_warn", code == 0 and any("W1 dead non_artifact" in ln for ln in out))
        chk("w1_dead_exclusion_strict", run(sd, sc, strict=True)[0] == 1)

        # C1 manifest invalid: a binding missing required `validators` -> C1 ERROR.
        sd, sc = setup([dict(b) for b in base])
        man = json.loads((Path(sd) / _MANIFEST_NAME).read_text(encoding="utf-8"))
        del man["bindings"][0]["validators"]
        (Path(sd) / _MANIFEST_NAME).write_text(json.dumps(man), encoding="utf-8")
        code, out = run(sd, sc)
        chk("c1_manifest_invalid", code == 1 and any("C1 binding invalid" in ln for ln in out))

        # C1 manifest stray key (closed envelope): an unknown top-level key -> C1 ERROR.
        sd, sc = setup([dict(b) for b in base])
        man = json.loads((Path(sd) / _MANIFEST_NAME).read_text(encoding="utf-8"))
        man["bogus"] = 1
        (Path(sd) / _MANIFEST_NAME).write_text(json.dumps(man), encoding="utf-8")
        code, out = run(sd, sc)
        chk("c1_manifest_stray_key", code == 1 and any("C1 manifest invalid" in ln and "unknown field" in ln for ln in out))

        # docs-no-re-list lint — fires on a drifted re-listing, clean on a faithful one. Uses a real
        # on-disk schema (audit_trigger.v1, fields schema/audit/evidence/recommendation) so
        # schema_field_names() resolves. The lint is advisory (exit 0 either way); assert the WARN text.
        dref = bed()
        # (a) drift: a `Fields:` re-listing that names a field the schema does NOT declare.
        (dref / "drift.md").write_text(
            "Field set canonical in `schemas/apodictic.audit_trigger.v1.schema.json`.\n"
            "**Fields (all required):** `schema`, `audit`, `evidence`, `recommendation`, `bogusfield`.\n",
            encoding="utf-8")
        _, dout = check_docs(refs_dir=dref)
        chk("docs_lint_catches_drift", any("re-lists field 'bogusfield'" in ln for ln in dout))
        # (b) faithful: the same re-listing with only real fields -> no WARN.
        dref2 = bed()
        (dref2 / "faithful.md").write_text(
            "Field set canonical in `schemas/apodictic.audit_trigger.v1.schema.json`.\n"
            "**Fields (all required):** `schema`, `audit`, `evidence`, `recommendation`.\n",
            encoding="utf-8")
        _, dout2 = check_docs(refs_dir=dref2)
        chk("docs_lint_clean_on_faithful", not any("re-lists field" in ln for ln in dout2))
        # (c) honest seam: prose that MENTIONS a non-field token but carries NO Fields-label -> no WARN.
        dref3 = bed()
        (dref3 / "prose.md").write_text(
            "Field set canonical in `schemas/apodictic.audit_trigger.v1.schema.json`.\n"
            "When present the `recommendation` lets the note anchor to the finest `quote` rung.\n",
            encoding="utf-8")
        _, dout3 = check_docs(refs_dir=dref3)
        chk("docs_lint_ignores_unlabeled_prose", not any("re-lists field" in ln for ln in dout3))

    finally:
        for d in beds:
            shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


# --------------------------------------------------------------- entrypoint

def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "schema-coverage"]
    strict = "--strict" in args
    do_docs = "--check-docs" in args
    positionals = [a for a in args if not a.startswith("--")]
    schemas_dir = positionals[0] if positionals else None
    if do_docs:
        code, lines = check_docs()
        for ln in lines:
            print(ln)
        if not _docs_only(args):
            code2, lines2 = run(schemas_dir, strict=strict)
            for ln in lines2:
                print(ln)
            code = code or code2
        return code
    code, lines = run(schemas_dir, strict=strict)
    for ln in lines:
        print(ln)
    return code


def _docs_only(args):
    """--check-docs alone (no schemas-dir positional, no other gate flag) runs only the docs lint."""
    return all(a in ("--check-docs",) for a in args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
