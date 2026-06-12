#!/usr/bin/env node
// check-status-drift — flag spec docs whose Status still says "unbuilt" after the deliverable shipped.
//
// The problem: agents in this repo implement FROM specs (AGENTS.md § The flow), so a spec that
// misreports built-ness invites a duplicate build or a wrong scoping decision. A naive "flag any
// unbuilt-status doc" is unshippable — most unbuilt specs are CORRECTLY unbuilt. So this is OPT-IN:
// a spec declares its deliverable in a machine-readable HTML comment, and the lint flags a doc ONLY
// IF (a) it carries such a marker, (b) the deliverable now exists, AND (c) the Status line still
// reads unbuilt. Un-marked docs are never flagged — zero false positives by construction.
//
//   <!-- built-when: <repo-relative-path> -->
//   <!-- built-when: <repo-relative-path> contains "<literal>" -->
//
// Standalone (not a validate.sh validator) so it touches neither the self-testable count nor the
// dual-script mirror; same class as assemble-changelog.mjs. Detection only — never auto-fixes.
//
//   node scripts/check-status-drift.mjs [--check]   scan docs/**/*.md; exit 0 clean / 1 stale-or-error
//   node scripts/check-status-drift.mjs --root <dir> override scan root (self-test seam)
//   node scripts/check-status-drift.mjs --self-test  hermetic fixture suite; exit 0 only if all pass
//
// Spec: docs/qol-status-drift-lint.md.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// Status-line unbuilt patterns (case-insensitive; matched against the Status line only). Each is
// attested by a real doc in docs/ — see the spec's table.
const UNBUILT = [
  /\bunbuilt\b/i,
  /\bnot yet built\b/i,
  /\bnot built\b/i,
  /\bnot yet implemented\b/i,
  /\bready for build\b/i,
];
// The "spec → review → build" arrow form needs all three tokens + an arrow on the Status line.
function specArrowForm(s) {
  return /\bspec\b/i.test(s) && /(→|->)/.test(s) && /\breview\b/i.test(s) && /\bbuild\b/i.test(s);
}
// Built-guard: a Status that ALSO says built/shipped/implemented (outside the unbuilt span) is a
// partially-built doc (e.g. "Increments 1–3 built; increment 5 not yet built") — conservatively
// NOT flagged. Word-boundaried so "buildable" never trips it.
const BUILT_GUARD = /\b(built|shipped|implemented)\b/i;

const MARKER_ATTEMPT = /<!--\s*built-when:/i;
const MARKER_FULL = /^<!--\s*built-when:\s*(.+?)\s*-->$/i;
const MARKER_TAIL = /^(\S+)(?:\s+contains\s+"([^"]*)")?$/;

function listMarkdown(dir) {
  const out = [];
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...listMarkdown(p));
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}

// Return non-fenced lines only (line-based ``` toggle), so markers/Status quoted inside fenced
// code blocks — including this lint's own spec — are never parsed.
function unfencedLines(text) {
  const out = [];
  let fenceChar = null; // '`' or '~' while inside a fence, else null
  for (const line of text.split("\n")) {
    const t = line.trim();
    if (fenceChar === null) {
      if (t.startsWith("```") || t.startsWith("~~~")) {
        fenceChar = t[0];
        continue;
      }
      out.push(line);
    } else {
      // inside a fence: skip everything until a close line of the SAME fence char
      if (t.startsWith(fenceChar.repeat(3))) fenceChar = null;
    }
  }
  return out;
}

function badPath(p) {
  if (!p) return "empty path";
  if (/[*?[\]]/.test(p)) return "glob characters not allowed";
  if (p.startsWith("/")) return "absolute path not allowed";
  if (p.split("/").includes("..")) return "'..' segment not allowed";
  return null;
}

// Parse one doc → { markers:[{path,literal}], errors:[...], statusLine:string|null }
function parseDoc(text) {
  const lines = unfencedLines(text);
  const markers = [];
  const errors = [];
  let statusLine = null;
  for (const line of lines) {
    const t = line.trim();
    if (MARKER_ATTEMPT.test(t)) {
      const m = t.match(MARKER_FULL);
      if (!m) {
        errors.push(`malformed built-when marker (not a single \`<!-- built-when: … -->\` comment): ${t}`);
        continue;
      }
      const tail = m[1].match(MARKER_TAIL);
      if (!tail) {
        errors.push(`unparseable built-when tail: ${m[1]}`);
        continue;
      }
      const bp = badPath(tail[1]);
      if (bp) {
        errors.push(`bad built-when path (${bp}): ${tail[1]}`);
        continue;
      }
      markers.push({ path: tail[1], literal: tail[2] });
    }
    if (statusLine === null) {
      const s = line.replace(/^\s+/, "").replace(/^[*_]+/, "").replace(/^\s+/, "");
      if (/^Status:/i.test(s)) statusLine = s;
    }
  }
  return { markers, errors, statusLine };
}

function markerTrue(marker, root) {
  const target = path.join(root, marker.path);
  if (!fs.existsSync(target)) return false;
  if (marker.literal === undefined) return true;
  try {
    return fs.readFileSync(target, "utf8").includes(marker.literal);
  } catch {
    return false;
  }
}

function statusIsUnbuilt(statusLine) {
  let residual = statusLine;
  let matched = false;
  for (const re of UNBUILT) {
    if (re.test(statusLine)) {
      matched = true;
      residual = residual.replace(new RegExp(re.source, "gi"), " ");
    }
  }
  if (specArrowForm(statusLine)) {
    matched = true;
    residual = residual.replace(/\bbuild\b/gi, " ");
  }
  if (!matched) return false;
  // Built-guard: a built/shipped/implemented token surviving outside the unbuilt span → partial → skip.
  if (BUILT_GUARD.test(residual)) return false;
  return true;
}

// Engine. Returns { stale:[...], errors:[...], markerCount, scanned }.
function scan(root) {
  const docsDir = path.join(root, "docs");
  const files = listMarkdown(docsDir);
  const stale = [];
  const errors = [];
  let markerCount = 0;
  for (const file of files) {
    const rel = path.relative(root, file);
    let text;
    try {
      text = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }
    const { markers, errors: pErr, statusLine } = parseDoc(text);
    for (const e of pErr) errors.push(`${rel}: ${e}`);
    markerCount += markers.length;
    if (markers.length === 0) continue;
    if (statusLine === null) {
      errors.push(`${rel}: carries a built-when marker but has no detectable Status line`);
      continue;
    }
    if (!statusIsUnbuilt(statusLine)) continue;
    const hit = markers.find((m) => markerTrue(m, root));
    if (hit) {
      const cond = hit.literal === undefined ? hit.path : `${hit.path} contains "${hit.literal}"`;
      const excerpt = statusLine.replace(/\*/g, "").slice(0, 80);
      stale.push(`${rel}: Status says "${excerpt}" but deliverable exists: ${cond}`);
    }
  }
  return { stale, errors, markerCount, scanned: files.length };
}

function runScan(root) {
  const { stale, errors, markerCount, scanned } = scan(root);
  const problems = [];
  for (const s of stale) problems.push(`STALE: ${s}`);
  for (const e of errors) problems.push(`ERROR: ${e}`);
  if (markerCount === 0) problems.push("ERROR: no built-when markers found in scope — the lint would pass vacuously (seeding regressed?)");
  if (problems.length) {
    console.error("check-status-drift failed:");
    for (const p of problems) console.error(`  ${p}`);
    return 1;
  }
  console.log(`check-status-drift: ok (${scanned} docs scanned, ${markerCount} built-when marker(s), no stale status)`);
  return 0;
}

// ---------------------------------------------------------------- self-test
function selfTest() {
  let rc = 0;
  const made = [];
  const mk = (files) => {
    const dir = fs.mkdtempSync(path.join(process.env.TMPDIR || "/tmp", "csd-"));
    made.push(dir);
    for (const [rel, body] of Object.entries(files)) {
      const fp = path.join(dir, rel);
      fs.mkdirSync(path.dirname(fp), { recursive: true });
      fs.writeFileSync(fp, body);
    }
    return dir;
  };
  const check = (name, cond) => {
    console.log(`  ${name}: ${cond ? "OK" : "FAIL"}`);
    if (!cond) rc = 1;
  };
  // run scan on a root, return {code, stale, errors}
  const run = (root) => scan(root);

  // 1. marker + existing path + unbuilt status → STALE (names the doc + path)
  let r = run(mk({
    "docs/a.md": "# A\n**Status:** Proposed (unbuilt)\n<!-- built-when: scripts/a.py -->\n",
    "scripts/a.py": "x\n",
  }));
  check("stale_fires", r.stale.length === 1 && r.stale[0].includes("docs/a.md") && r.stale[0].includes("scripts/a.py"));

  // 2. marker + missing path + unbuilt status → clean
  r = run(mk({ "docs/b.md": "**Status:** Proposed (unbuilt)\n<!-- built-when: scripts/missing.py -->\n" }));
  check("missing_path_clean", r.stale.length === 0 && r.errors.length === 0 && r.markerCount === 1);

  // 3. no marker + unbuilt status → clean (but vacuous → the runner would ERROR; engine reports 0 markers)
  r = run(mk({ "docs/c.md": "**Status:** Proposed (unbuilt)\n" }));
  check("no_marker_not_flagged", r.stale.length === 0 && r.errors.length === 0 && r.markerCount === 0);

  // 4. marker + existing path + Built status → clean
  r = run(mk({
    "docs/d.md": "**Status:** **Built**\n<!-- built-when: scripts/d.py -->\n",
    "scripts/d.py": "x\n",
  }));
  check("built_status_clean", r.stale.length === 0 && r.errors.length === 0);

  // 5. contains form: literal present → STALE; literal absent → clean
  r = run(mk({
    "docs/e.md": '**Status:** Proposed (unbuilt)\n<!-- built-when: scripts/v.sh contains "check-mirror" -->\n',
    "scripts/v.sh": "case check-mirror)\n",
  }));
  check("contains_present_stale", r.stale.length === 1);
  r = run(mk({
    "docs/e.md": '**Status:** Proposed (unbuilt)\n<!-- built-when: scripts/v.sh contains "check-mirror" -->\n',
    "scripts/v.sh": "nothing here\n",
  }));
  check("contains_absent_clean", r.stale.length === 0 && r.markerCount === 1);

  // 6. partial status (built-guard) + true marker → clean
  r = run(mk({
    "docs/f.md": "**Status:** Increments 1–3 built. Increment 5 not yet built.\n<!-- built-when: scripts/f.py -->\n",
    "scripts/f.py": "x\n",
  }));
  check("built_guard_partial_clean", r.stale.length === 0);

  // 7. marker inside a fenced block + existing path + unbuilt status → clean (fence immunity)
  r = run(mk({
    "docs/g.md": "**Status:** Proposed (unbuilt)\n```\n<!-- built-when: scripts/g.py -->\n```\n",
    "scripts/g.py": "x\n",
  }));
  check("fence_immunity", r.stale.length === 0 && r.markerCount === 0);

  // 7b. marker inside a ~~~ fenced block → also ignored (tilde fences)
  r = run(mk({
    "docs/g2.md": "**Status:** Proposed (unbuilt)\n~~~\n<!-- built-when: scripts/g2.py -->\n~~~\n",
    "scripts/g2.py": "x\n",
  }));
  check("fence_immunity_tilde", r.stale.length === 0 && r.markerCount === 0);

  // 8. malformed markers → ERROR (glob / .. / absolute / unparseable tail)
  for (const [label, body] of [
    ["glob", "**Status:** x\n<!-- built-when: scripts/*.py -->\n"],
    ["dotdot", "**Status:** x\n<!-- built-when: ../etc/passwd -->\n"],
    ["absolute", "**Status:** x\n<!-- built-when: /etc/passwd -->\n"],
    ["tail", '**Status:** x\n<!-- built-when: a b c -->\n'],
  ]) {
    r = run(mk({ "docs/h.md": body }));
    check(`malformed_${label}_error`, r.errors.length === 1);
  }

  // 9. marker-bearing doc with no Status line → ERROR
  r = run(mk({
    "docs/i.md": "# No status here\n<!-- built-when: scripts/i.py -->\n",
    "scripts/i.py": "x\n",
  }));
  check("no_status_error", r.errors.length === 1 && r.errors[0].includes("no detectable Status line"));

  // 10. zero markers in scope → runner ERRORs via the vacuity guard (engine reports markerCount 0)
  const vroot = mk({ "docs/j.md": "**Status:** Active\nsome prose, no markers.\n" });
  check("vacuity_guard", run(vroot).markerCount === 0);

  for (const d of made) fs.rmSync(d, { recursive: true, force: true });
  console.log(rc === 0 ? "Self-test: PASS" : "Self-test: FAIL");
  return rc;
}

function main(argv) {
  if (argv.includes("--self-test")) return selfTest();
  let root = repoRoot;
  const ri = argv.indexOf("--root");
  if (ri !== -1 && argv[ri + 1]) root = path.resolve(argv[ri + 1]);
  return runScan(root);
}

process.exit(main(process.argv.slice(2)));
