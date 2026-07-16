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

// --- release-registry coverage of shipped specialized-audit references --------
//
// The Gemini website is generated from release-registry.json, so a specialized
// audit that ships a reference file but is NEVER carded in the registry's
// categories[].items[].files is invisible downstream — exactly the v2.6.0 gap
// where content-advisory.md and craft/persona-divergence.md shipped uncarded.
// PRIMARY-REFERENCE BINDING (Codex PR #146 P1). Gemini renders ONE card per
// registry item, from that item's PRIMARY reference = files[0]. So a reference
// must be the files[0] of its OWN card; merely occurring somewhere in another
// card's files[] (e.g. demoted to a non-primary files[1:] sub-reference of an
// unrelated item, with its own card removed) leaves the audit with no card
// downstream — the exact regression this gate exists to prevent. The check is
// therefore: every shipped reference `.md` must be the files[0] primary of
// exactly one card (across categories[].items[] + researchModes +
// argumentCompanions) OR be explicitly listed in NOT_CARDED. File-path based,
// to sidestep the inventory-display-name vs. registry-name mismatch.
const REGISTRY_FILE = "release-registry.json";
const SPECIALIZED_REFS_DIR =
  "plugins/apodictic/skills/specialized-audits/references";

// NOT_CARDED — reference files that are legitimately NOT the files[0] primary of
// their own card. A NEW specialized-audit reference must become a card's files[0]
// primary OR be listed here; doing neither FAILS this check (the v2.6.0 gap where
// content-advisory/persona-divergence shipped uncarded, now guarded).
// Paths are relative to SPECIALIZED_REFS_DIR (matching the files[] convention).
const NOT_CARDED = new Set([
  // (1) Sub-references (files[1:]) of an already-carded audit — level-setting /
  //     computational / stub companions that ride along with a card's primary.
  "craft/ai-prose-calibration-distributional.md",
  "craft/ai-prose-calibration-level-setting.md",
  "craft/argument-persuasion-level-setting.md",
  "craft/argument-red-team-level-setting.md",
  "craft/compression-audit-expansion-stub.md",
  "craft/compression-audit-level-setting.md",
  "craft/decision-pressure-level-setting.md",
  "craft/dialectical-clarity-level-setting.md",
  "craft/rhetorical-stance-triage.md",
  "craft/female-interiority-level-setting.md",
  "craft/force-architecture-level-setting.md",
  "craft/literary-craft-level-setting.md",
  "craft/reception-risk-level-setting.md",
  "craft/series-continuity-level-setting.md",
  "craft/stakes-system-level-setting.md",
  "genre/grimdark-level-setting.md",
  "genre/horror-craft-level-setting.md",
  "genre/mystery-thriller-architecture-level-setting.md",
  "genre/sff-worldbuilding-level-setting.md",
  "genre/supernatural-horror-level-setting.md",
  "tag/cozy-tag-level-setting.md",
  // (2) Pre-existing standalone audits not carded in any registry section —
  //     advisory/opt-in surfaces that predate this gate. Carding them (if they
  //     should be web-marketed) is tracked separately; allowlisted so the gate
  //     is green today and only catches NEWLY added uncarded references.
  "craft/idiolect-preservation.md",
  "craft/pov-voice-profile.md",
  "craft/punctuation-cadence.md",
  // (3) Position-Pair Register (stance-consistency consumer) — a `handoff:
  //     experimental`, uncalibrated SETEC-consumer surface. Its sibling
  //     Argument-Decision (ArgScope) is carded, but web-marketing an
  //     experimental/uncalibrated surface is deferred until it graduates
  //     (same posture as category (2)); allowlisted, not carded, meanwhile.
  //     The worked example is a fixture (wired into `--check-all`), never a card.
  "craft/position-pair-register.md",
  "example-position-pair-register/Example_Position_Pair_Register_run.md",
]);

// Recursively collect every `*.md` under `dir`, returned as POSIX-style paths
// relative to `dir` (matching the registry's files[] convention).
function collectReferenceFiles(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  const walk = (abs, rel) => {
    for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
      const childAbs = path.join(abs, entry.name);
      const childRel = rel ? `${rel}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        walk(childAbs, childRel);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        out.push(childRel);
      }
    }
  };
  walk(dir, "");
  return out;
}

// Collect each card's PRIMARY reference = files[0], across every registry section
// Gemini renders as a card (categories[].items[] + researchModes + argumentCompanions).
// Returns { primaries, duplicates } — a file bound as files[0] of two cards is
// itself a misconfiguration (one card per reference).
function collectPrimaryReferenceFiles(registry) {
  const counts = new Map(); // files[0] -> number of cards claiming it as primary
  const sections = [
    ...(registry.categories || []).flatMap((c) => c.items || []),
    ...(registry.researchModes || []),
    ...(registry.argumentCompanions || []),
  ];
  for (const item of sections) {
    const primary = (item.files || [])[0];
    if (primary) counts.set(primary, (counts.get(primary) || 0) + 1);
  }
  return {
    primaries: new Set(counts.keys()),
    duplicates: [...counts.entries()].filter(([, n]) => n > 1).map(([f]) => f),
  };
}

// Returns an array of problem strings (empty => clean). Asserts that every
// shipped specialized-audit reference is the files[0] PRIMARY of its own card in
// release-registry.json OR explicitly allowlisted in NOT_CARDED.
function checkRegistryReferenceCoverage(root, { notCarded = NOT_CARDED } = {}) {
  const refsDir = path.join(root, SPECIALIZED_REFS_DIR);
  const registryPath = path.join(root, REGISTRY_FILE);
  if (!fs.existsSync(registryPath)) {
    return [
      `MISSING-REGISTRY: ${REGISTRY_FILE} not found at repo root; cannot verify reference coverage.`,
    ];
  }
  let registry;
  try {
    registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
  } catch (e) {
    return [`BAD-REGISTRY: ${REGISTRY_FILE} is not valid JSON (${e.message}).`];
  }
  const shipped = collectReferenceFiles(refsDir);
  const { primaries, duplicates } = collectPrimaryReferenceFiles(registry);
  const problems = [];
  for (const dup of duplicates.sort()) {
    problems.push(
      `DUPLICATE-PRIMARY: ${dup} is the files[0] primary of more than one card in ` +
        `${REGISTRY_FILE} — each reference must bind to exactly one card.`
    );
  }
  for (const rel of shipped.sort()) {
    if (primaries.has(rel)) continue; // it is its own card's files[0] primary
    if (notCarded.has(rel)) continue; // a declared sub-reference / non-card
    problems.push(
      `UNCARDED-REFERENCE: ${SPECIALIZED_REFS_DIR}/${rel} is a shipped ` +
        `specialized-audit reference but is NOT the files[0] PRIMARY of any card in ` +
        `${REGISTRY_FILE} (categories[].items[] + researchModes + argumentCompanions) ` +
        `and is NOT in NOT_CARDED. Gemini renders one card per item from its files[0], ` +
        `so a reference that is only a non-primary files[1:] of another card (or dropped ` +
        `entirely) has no card downstream. Make it a card's files[0] primary OR add it to ` +
        `scripts/check-inventory-parity.mjs's NOT_CARDED — this is the gate that catches ` +
        `the v2.6.0 gap where content-advisory/persona-divergence shipped uncarded.`
    );
  }
  return problems;
}

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

  // Second, independent check: every shipped specialized-audit reference must be
  // carded in release-registry.json or explicitly allowlisted (NOT_CARDED).
  problems.push(...checkRegistryReferenceCoverage(root));

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
    // Seed a clean release-registry.json + a fully-carded references tree so the
    // registry-coverage check (wired into runCheck) is a no-op for the marker
    // cases below — those cases assert problems.length===0 and must not be
    // tripped by an unrelated coverage problem. (The coverage check has its own
    // dedicated cases (h)/(i) below.)
    fs.writeFileSync(
      path.join(root, REGISTRY_FILE),
      JSON.stringify(
        {
          categories: [
            {
              name: "Craft",
              items: [{ name: "Alpha", slug: "alpha", files: ["alpha.md"] }],
            },
          ],
        },
        null,
        2
      )
    );
    const refsDir = path.join(root, SPECIALIZED_REFS_DIR);
    fs.mkdirSync(refsDir, { recursive: true });
    fs.writeFileSync(path.join(refsDir, "alpha.md"), "# carded ref\n");
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

  // --- registry-coverage check (the new release-registry.json guard) ---------
  //
  // Hermetic, non-vacuous proof: a fixtured reference file that is neither carded
  // in release-registry.json nor allowlisted must FAIL; the SAME file once carded
  // (or once allowlisted) must PASS. We call checkRegistryReferenceCoverage()
  // directly so the assertion is structural (a non-empty/empty problems array),
  // mirroring the marker-case style above.
  function makeCoverageRoot({ registry, refFiles }) {
    caseN++;
    const root = path.join(tmpBase, `cov-${caseN}`);
    fs.mkdirSync(root, { recursive: true });
    fs.writeFileSync(
      path.join(root, REGISTRY_FILE),
      JSON.stringify(registry, null, 2)
    );
    const refsDir = path.join(root, SPECIALIZED_REFS_DIR);
    fs.mkdirSync(refsDir, { recursive: true });
    for (const rel of refFiles) {
      const abs = path.join(refsDir, rel);
      fs.mkdirSync(path.dirname(abs), { recursive: true });
      fs.writeFileSync(abs, `# ${rel}\n`);
    }
    return root;
  }

  // (h) an uncarded, un-allowlisted reference -> FAIL (non-vacuous: catches the
  //     exact v2.6.0 class of bug).
  {
    const root = makeCoverageRoot({
      registry: {
        categories: [
          {
            name: "Craft",
            items: [
              { name: "Carded", slug: "carded", files: ["craft/carded.md"] },
            ],
          },
        ],
      },
      refFiles: ["craft/carded.md", "craft/orphan.md"],
    });
    const problems = checkRegistryReferenceCoverage(root, { notCarded: new Set() });
    const flagged = problems.some(
      (p) => p.startsWith("UNCARDED-REFERENCE:") && p.includes("craft/orphan.md")
    );
    log(
      !!flagged && problems.length > 0,
      "(h) uncarded+unallowlisted reference -> FAIL",
      flagged ? "" : "did not flag the orphan reference"
    );
  }

  // (i-card) the SAME orphan, now CARDED in the registry -> PASS.
  {
    const root = makeCoverageRoot({
      registry: {
        categories: [
          {
            name: "Craft",
            items: [
              { name: "Carded", slug: "carded", files: ["craft/carded.md"] },
              { name: "Orphan", slug: "orphan", files: ["craft/orphan.md"] },
            ],
          },
        ],
      },
      refFiles: ["craft/carded.md", "craft/orphan.md"],
    });
    const problems = checkRegistryReferenceCoverage(root, { notCarded: new Set() });
    log(problems.length === 0, "(i-card) same reference, now carded -> PASS");
  }

  // (i-allow) the SAME orphan, now ALLOWLISTED in NOT_CARDED -> PASS.
  {
    const root = makeCoverageRoot({
      registry: {
        categories: [
          {
            name: "Craft",
            items: [
              { name: "Carded", slug: "carded", files: ["craft/carded.md"] },
            ],
          },
        ],
      },
      refFiles: ["craft/carded.md", "craft/orphan.md"],
    });
    const problems = checkRegistryReferenceCoverage(root, {
      notCarded: new Set(["craft/orphan.md"]),
    });
    log(
      problems.length === 0,
      "(i-allow) same reference, now allowlisted -> PASS"
    );
  }

  // (j) the orphan attached as a NON-PRIMARY files[1] of the WRONG card, its own
  //     card removed -> must FAIL. Under the old union-coverage check this PASSED
  //     (the path occurs in some files[]), while Gemini renders one card per item
  //     from files[0] and drops it — the exact misattribution Codex PR #146 P1
  //     flagged. This is the regression test for the primary-binding fix.
  {
    const root = makeCoverageRoot({
      registry: {
        categories: [
          {
            name: "Craft",
            items: [
              {
                name: "Carded",
                slug: "carded",
                files: ["craft/carded.md", "craft/orphan.md"],
              },
            ],
          },
        ],
      },
      refFiles: ["craft/carded.md", "craft/orphan.md"],
    });
    const problems = checkRegistryReferenceCoverage(root, { notCarded: new Set() });
    const flagged = problems.some(
      (p) => p.startsWith("UNCARDED-REFERENCE:") && p.includes("craft/orphan.md")
    );
    log(
      !!flagged && problems.length > 0,
      "(j) reference demoted to a non-primary files[1] of the wrong card -> FAIL",
      flagged ? "" : "did not flag the misattributed (non-primary) reference"
    );
  }

  // (k) the same reference as files[0] primary of TWO cards -> DUPLICATE-PRIMARY.
  {
    const root = makeCoverageRoot({
      registry: {
        categories: [
          {
            name: "Craft",
            items: [
              { name: "A", slug: "a", files: ["craft/dup.md"] },
              { name: "B", slug: "b", files: ["craft/dup.md"] },
            ],
          },
        ],
      },
      refFiles: ["craft/dup.md"],
    });
    const problems = checkRegistryReferenceCoverage(root, { notCarded: new Set() });
    const flagged = problems.some(
      (p) => p.startsWith("DUPLICATE-PRIMARY:") && p.includes("craft/dup.md")
    );
    log(
      !!flagged,
      "(k) reference as files[0] of two cards -> DUPLICATE-PRIMARY FAIL",
      flagged ? "" : "did not flag the duplicate primary"
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
