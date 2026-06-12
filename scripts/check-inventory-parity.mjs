#!/usr/bin/env node
//
// check-inventory-parity.mjs — guard that display surfaces stay synced with the
// canonical audit/research inventory.
//
// Why: the display surfaces (overview-dashboard.html, AUDIT_SELECTION_MATRIX.md)
// hand-list the audit/research inventory and can silently drift behind the
// canonical registry (the rot PR #81 hand-fixed). This is the #79 status-drift
// pattern applied to inventory: a *sync-marker* + a changed-since signal. It
// catches the drift event (registry changed, a surface wasn't re-synced),
// robustly and with near-zero false positives.
//
// Honest limitation (same as #79's status flip): it verifies the *signal is
// consistent*, not that the surface content is actually correct — a maintainer
// who bumps the marker without re-syncing defeats it. That's an acceptable,
// transparent trade vs. brittle name-by-name matching, and strictly better than
// today's nothing.
//
// Canonical signature: `<count>:<short-hash>` where short-hash = first 8 hex of
// sha256 over the sorted inventory names joined by "\n". Count is human-glanceable;
// the hash catches a rename/swap that keeps the count.
//   - audits:   the `- Name` bullets BETWEEN the registry begin/end markers in
//               plugins/apodictic/skills/core-editor/references/audit-routing-table.md
//   - research: the `- **<mode>**` bullets in plugins/apodictic/commands/research.md
//
// Opted-in surfaces carry:
//   <!-- inventory-synced: audits=<count>:<hash> research=<count>:<hash> -->
// A surface without the marker is SKIPPED (opt-in). A surface whose recorded sig
// != current canonical sig is FLAGGED (exit 1). Zero markers anywhere => vacuity
// ERROR. Markers inside ``` / ~~~ fences are ignored. A malformed marker is a
// loud ERROR.
//
// Modes:
//   node scripts/check-inventory-parity.mjs [--check]   (default) run the gate
//   node scripts/check-inventory-parity.mjs --self-test  hermetic fixtures

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const AUDIT_REGISTRY_FILE =
  "plugins/apodictic/skills/core-editor/references/audit-routing-table.md";
const RESEARCH_FILE = "plugins/apodictic/commands/research.md";
const REGISTRY_BEGIN = "<!-- registry:signal-emitting-audits:begin -->";
const REGISTRY_END = "<!-- registry:signal-emitting-audits:end -->";

const OPTED_IN_SURFACES = [
  "plugins/apodictic/overview-dashboard.html",
  "plugins/apodictic/AUDIT_SELECTION_MATRIX.md",
];

const MARKER_RE =
  /<!--\s*inventory-synced:\s*(.*?)\s*-->/;
// A line that *looks like* the marker (so a malformed one can't be silently skipped).
const MARKER_LOOSE_RE = /<!--\s*inventory-synced\b/;
const SIG_RE = /^(\d+):([0-9a-f]{8})$/;

function fail(message) {
  console.error(`check-inventory-parity ERROR: ${message}`);
  process.exit(1);
}

// --- signature computation -------------------------------------------------

function signatureOf(names) {
  const sorted = [...names].sort();
  const hash = crypto
    .createHash("sha256")
    .update(sorted.join("\n"))
    .digest("hex")
    .slice(0, 8);
  return `${sorted.length}:${hash}`;
}

function parseAuditNames(text, label) {
  const begin = text.indexOf(REGISTRY_BEGIN);
  const end = text.indexOf(REGISTRY_END);
  if (begin === -1 || end === -1 || end < begin) {
    fail(
      `${label}: could not find the registry begin/end markers ` +
        `(${REGISTRY_BEGIN} / ${REGISTRY_END}).`
    );
  }
  const block = text.slice(begin + REGISTRY_BEGIN.length, end);
  // Only `- Name` bullets count; a non-bullet line (blank, prose) is ignored,
  // and a nested/indented bullet is NOT counted (registry entries are flush-left).
  const names = block
    .split("\n")
    .filter((line) => /^- \S/.test(line))
    .map((line) => line.replace(/^- /, "").trim());
  if (names.length === 0) {
    fail(`${label}: no \`- Name\` bullets found between the registry markers.`);
  }
  return names;
}

function parseResearchModes(text, label) {
  // Mode bullets are `- **<mode>** — ...`. Only bold-leading bullets are modes;
  // a plain `- text` bullet (e.g. the numbered principles further down, or prose)
  // is intentionally NOT a mode.
  const names = text
    .split("\n")
    .map((line) => {
      const m = line.match(/^- \*\*(.+?)\*\*/);
      return m ? m[1].trim() : null;
    })
    .filter(Boolean);
  if (names.length === 0) {
    fail(`${label}: no \`- **mode**\` bullets found.`);
  }
  return names;
}

function computeCanonical(root) {
  const auditText = fs.readFileSync(
    path.join(root, AUDIT_REGISTRY_FILE),
    "utf8"
  );
  const researchText = fs.readFileSync(path.join(root, RESEARCH_FILE), "utf8");
  return {
    audits: signatureOf(parseAuditNames(auditText, AUDIT_REGISTRY_FILE)),
    research: signatureOf(parseResearchModes(researchText, RESEARCH_FILE)),
  };
}

// --- marker scanning -------------------------------------------------------

// Strip fenced code blocks (``` and ~~~) so a doc that *documents* the marker
// syntax doesn't self-trip. Lines inside a fence are blanked (kept for line
// numbering) so a marker inside them is invisible to the scan.
function maskFences(text) {
  const lines = text.split("\n");
  let fence = null; // null | "```" | "~~~"
  return lines.map((line) => {
    const m = line.match(/^\s*(`{3,}|~{3,})/);
    if (m) {
      const tick = m[1][0]; // ` or ~
      if (fence === null) {
        fence = tick;
        return ""; // the opening fence line itself
      }
      if (fence === tick) {
        fence = null;
        return ""; // the closing fence line
      }
      // a different fence char inside an open fence: still inside, mask it
      return "";
    }
    return fence === null ? line : "";
  });
}

// Returns { sigs: {audits, research} } on a clean parse,
//   { malformed: <reason> } if a marker is present but unparseable,
//   null if the surface has no marker.
function scanSurface(text, label) {
  const masked = maskFences(text);
  let found = null;
  for (let i = 0; i < masked.length; i++) {
    const line = masked[i];
    if (!MARKER_LOOSE_RE.test(line)) continue;
    const m = line.match(MARKER_RE);
    if (!m) {
      return {
        malformed: `${label}:${i + 1}: an \`inventory-synced\` marker is present but malformed (could not extract its body).`,
      };
    }
    const body = m[1];
    const parsed = parseMarkerBody(body);
    if (parsed.error) {
      return { malformed: `${label}:${i + 1}: ${parsed.error}` };
    }
    if (found) {
      return {
        malformed: `${label}:${i + 1}: more than one \`inventory-synced\` marker in this surface.`,
      };
    }
    found = parsed.sigs;
  }
  if (!found) return null;
  return { sigs: found };
}

function parseMarkerBody(body) {
  // Expect: audits=<count>:<hash> research=<count>:<hash>  (order-independent)
  const fields = {};
  const tokens = body.trim().split(/\s+/);
  for (const tok of tokens) {
    const eq = tok.indexOf("=");
    if (eq === -1) {
      return { error: `malformed marker token '${tok}' (expected key=value).` };
    }
    const key = tok.slice(0, eq);
    const val = tok.slice(eq + 1);
    if (key !== "audits" && key !== "research") {
      return { error: `unknown marker key '${key}' (expected audits/research).` };
    }
    if (!SIG_RE.test(val)) {
      return {
        error: `malformed signature for '${key}': '${val}' (expected <count>:<8-hex>).`,
      };
    }
    fields[key] = val;
  }
  if (!fields.audits || !fields.research) {
    return {
      error: `marker missing required field(s): need both audits= and research=.`,
    };
  }
  return { sigs: fields };
}

// --- the check -------------------------------------------------------------

function runCheck(root, { quiet = false } = {}) {
  const canonical = computeCanonical(root);
  const problems = [];
  let markerCount = 0;
  const checked = [];

  for (const rel of OPTED_IN_SURFACES) {
    const abs = path.join(root, rel);
    if (!fs.existsSync(abs)) continue;
    const text = fs.readFileSync(abs, "utf8");
    const result = scanSurface(text, rel);
    if (result === null) {
      // no marker -> opt-out, skip
      continue;
    }
    if (result.malformed) {
      problems.push(`MALFORMED: ${result.malformed}`);
      markerCount++; // a malformed-but-present marker still counts against vacuity
      continue;
    }
    markerCount++;
    checked.push(rel);
    const { sigs } = result;
    for (const kind of ["audits", "research"]) {
      if (sigs[kind] !== canonical[kind]) {
        problems.push(
          `STALE: ${rel}: ${kind} signature is out of date — ` +
            `expected ${canonical[kind]}, found ${sigs[kind]}. ` +
            `The canonical ${kind === "audits" ? "audit registry" : "research modes"} ` +
            `changed since this surface was last synced — re-verify the surface's ` +
            `inventory and update its \`inventory-synced\` marker to ` +
            `audits=${canonical.audits} research=${canonical.research}.`
        );
      }
    }
  }

  return { canonical, problems, markerCount, checked };
}

function check(root) {
  const { canonical, problems, markerCount, checked } = runCheck(root);

  if (markerCount === 0) {
    fail(
      `vacuity guard: no opted-in surface carries an \`inventory-synced\` marker — ` +
        `the check would be vacuous. Seed at least one surface with ` +
        `<!-- inventory-synced: audits=${canonical.audits} research=${canonical.research} -->.`
    );
  }

  if (problems.length > 0) {
    for (const p of problems) console.error(`check-inventory-parity ${p}`);
    process.exit(1);
  }

  console.log(
    `check-inventory-parity: clean. Canonical signatures: ` +
      `audits=${canonical.audits} research=${canonical.research}.`
  );
  console.log(`  surfaces checked: ${checked.join(", ")}`);
  return true;
}

// --- self-test -------------------------------------------------------------

function selfTest() {
  // Hermetic: build a throwaway repo tree with the canonical source files and
  // synthetic surfaces, then exercise the check via runCheck() so we can assert
  // on the structured result (problems/markerCount) WITHOUT spawning processes.
  // Negative cases must FAIL if the compare were stubbed always-pass — we assert
  // a non-empty `problems`/error per negative case, so a no-op compare is caught.
  const tmpBase = fs.mkdtempSync(
    path.join(process.env.TMPDIR || "/tmp", "inv-parity-")
  );

  let passed = 0;
  let failed = 0;
  const log = (ok, name, detail) => {
    if (ok) {
      passed++;
      console.log(`  ok   ${name}`);
    } else {
      failed++;
      console.log(`  FAIL ${name}${detail ? ` — ${detail}` : ""}`);
    }
  };

  // Canonical sources used by every fixture.
  const auditSrc = [
    "# t",
    REGISTRY_BEGIN,
    "- Alpha",
    "- Beta",
    "- Gamma",
    REGISTRY_END,
    "",
  ].join("\n");
  const researchSrc = [
    "# r",
    "- **mode-one** — first",
    "- **mode-two** — second",
    "",
  ].join("\n");

  const auditSig = signatureOf(["Alpha", "Beta", "Gamma"]);
  const researchSig = signatureOf(["mode-one", "mode-two"]);
  const goodMarker = `<!-- inventory-synced: audits=${auditSig} research=${researchSig} -->`;

  let caseN = 0;
  function makeRoot(surfaces) {
    caseN++;
    const root = path.join(tmpBase, `case-${caseN}`);
    fs.mkdirSync(
      path.join(root, "plugins/apodictic/skills/core-editor/references"),
      { recursive: true }
    );
    fs.mkdirSync(path.join(root, "plugins/apodictic/commands"), {
      recursive: true,
    });
    fs.writeFileSync(path.join(root, AUDIT_REGISTRY_FILE), auditSrc);
    fs.writeFileSync(path.join(root, RESEARCH_FILE), researchSrc);
    // surfaces: map of relpath -> content; only OPTED_IN_SURFACES are scanned.
    for (const [rel, content] of Object.entries(surfaces)) {
      const abs = path.join(root, rel);
      fs.mkdirSync(path.dirname(abs), { recursive: true });
      fs.writeFileSync(abs, content);
    }
    return root;
  }

  const SURF_A = OPTED_IN_SURFACES[0];
  const SURF_B = OPTED_IN_SURFACES[1];

  // Run runCheck and capture any fail() exit by wrapping process.exit.
  function attempt(root) {
    const orig = process.exit;
    let exited = null;
    process.exit = (code) => {
      exited = code;
      throw new Error(`__exit_${code}__`);
    };
    let result = null;
    let errored = false;
    try {
      result = runCheck(root);
      // Replicate check()'s vacuity guard for the self-test classification.
      if (result.markerCount === 0) {
        errored = true; // vacuity error
      }
    } catch (e) {
      errored = true;
    } finally {
      process.exit = orig;
    }
    return { result, errored, exited };
  }

  // (a) matching marker -> clean
  {
    const root = makeRoot({ [SURF_A]: `top\n${goodMarker}\nbody` });
    const { result, errored } = attempt(root);
    log(
      !errored && result && result.problems.length === 0 && result.markerCount === 1,
      "(a) matching marker -> clean"
    );
  }

  // (b) stale audits sig -> flagged (exit 1) naming the surface
  {
    const staleMarker = `<!-- inventory-synced: audits=9:00000000 research=${researchSig} -->`;
    const root = makeRoot({ [SURF_A]: `top\n${staleMarker}\nbody` });
    const { result } = attempt(root);
    const flagged =
      result &&
      result.problems.some(
        (p) => p.startsWith("STALE:") && p.includes(SURF_A) && p.includes("audits")
      );
    log(!!flagged, "(b) stale audits -> flagged", flagged ? "" : "no STALE problem");
  }

  // (c) stale research sig -> flagged
  {
    const staleMarker = `<!-- inventory-synced: audits=${auditSig} research=9:00000000 -->`;
    const root = makeRoot({ [SURF_A]: `top\n${staleMarker}\nbody` });
    const { result } = attempt(root);
    const flagged =
      result &&
      result.problems.some(
        (p) => p.startsWith("STALE:") && p.includes("research")
      );
    log(!!flagged, "(c) stale research -> flagged");
  }

  // (d) no marker on any surface -> vacuity ERROR
  {
    const root = makeRoot({ [SURF_A]: `no marker here`, [SURF_B]: `none either` });
    const { result, errored } = attempt(root);
    const vacuous = errored && result && result.markerCount === 0;
    log(!!vacuous, "(d) no marker anywhere -> vacuity ERROR");
  }

  // (e) marker inside a ``` fence -> ignored (so it's the only "marker" -> vacuity)
  {
    const fenced = `intro\n\`\`\`\n${goodMarker}\n\`\`\`\ntail`;
    const root = makeRoot({ [SURF_A]: fenced });
    const { result, errored } = attempt(root);
    // The fenced marker must NOT be seen; with no real marker -> vacuity error.
    const ignored = errored && result && result.markerCount === 0;
    log(!!ignored, "(e) fenced marker ignored");
  }

  // (f) malformed marker -> ERROR
  {
    const bad = `<!-- inventory-synced: audits=not-a-sig research=${researchSig} -->`;
    const root = makeRoot({ [SURF_A]: `top\n${bad}\nbody` });
    const { result } = attempt(root);
    const malformed =
      result && result.problems.some((p) => p.startsWith("MALFORMED:"));
    log(!!malformed, "(f) malformed marker -> ERROR");
  }

  // (g) one surface marked (current) + another without -> skip the unmarked, clean
  {
    const root = makeRoot({
      [SURF_A]: `top\n${goodMarker}\nbody`,
      [SURF_B]: `no marker on this one`,
    });
    const { result, errored } = attempt(root);
    const clean =
      !errored &&
      result &&
      result.problems.length === 0 &&
      result.markerCount === 1 &&
      result.checked.length === 1 &&
      result.checked[0] === SURF_A;
    log(!!clean, "(g) one marked + one unmarked -> skip unmarked, clean");
  }

  // Self-test integrity: prove the negative cases would FAIL if compare were a
  // no-op (always-pass). Re-run (b) but ignore STALE problems; it must look clean
  // — confirming (b)'s pass above depended on real comparison, not a stub.
  {
    const staleMarker = `<!-- inventory-synced: audits=9:00000000 research=${researchSig} -->`;
    const root = makeRoot({ [SURF_A]: `top\n${staleMarker}\nbody` });
    const { result } = attempt(root);
    const stubbedWouldPass =
      result && result.problems.filter((p) => !p.startsWith("STALE:")).length === 0;
    // If we stubbed the compare (dropped STALE), the case would pass -> the real
    // signal lives entirely in the STALE problems. Good.
    log(
      !!stubbedWouldPass && result.problems.length > 0,
      "(integrity) negative cases fail only because compare is real"
    );
  }

  fs.rmSync(tmpBase, { recursive: true, force: true });

  console.log(
    `\ncheck-inventory-parity self-test: ${passed} passed, ${failed} failed ` +
      `(${passed + failed} cases).`
  );
  if (failed > 0) process.exit(1);
}

// --- main ------------------------------------------------------------------

function main() {
  const args = process.argv.slice(2);
  if (args.includes("--self-test")) {
    selfTest();
    return;
  }
  // --check is the default.
  check(repoRoot);
}

main();
