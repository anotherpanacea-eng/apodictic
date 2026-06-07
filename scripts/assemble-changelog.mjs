#!/usr/bin/env node
//
// assemble-changelog.mjs — cut a release section from changelog.d/ fragments.
//
// Why: the canonical changelog is one large append-only file that every
// release-touching change edits, which collides during parallel branch waves.
// Instead, each change drops an independent `changelog.d/<slug>.md` fragment;
// the release pipeline assembles them into one dated section. (GitHub #51.)
//
// Modes:
//   node scripts/assemble-changelog.mjs <version> [date]
//       Assemble every changelog.d/*.md fragment into a new
//       "## vX.Y.Z - YYYY-MM-DD" section, prepend it above the newest existing
//       "## v" section in the canonical changelog, and DELETE the consumed
//       fragments. No fragments => no-op. date defaults to today (UTC).
//   node scripts/assemble-changelog.mjs --check
//       Validate that every fragment parses (CI gate). No writes.
//   node scripts/assemble-changelog.mjs --section <version>
//       Print the "## vX.Y.Z ..." section from the canonical changelog (used by
//       the release workflow to set the GitHub release notes from the changelog).
//
// Fragment format (apodictic house style): the first non-blank line is a single
// freeform thematic "### " header (e.g. "### Validators"), followed by prose.
// One thematic section per fragment. Malformed fragments fail loudly.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const fragmentsDir = path.join(repoRoot, "changelog.d");
const changelogPath = path.join(
  repoRoot,
  "plugins/apodictic/skills/core-editor/references/changelog.md"
);

function fail(message) {
  console.error(`assemble-changelog failed: ${message}`);
  process.exit(1);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeVersion(value) {
  return String(value).replace(/^v/, "");
}

function listFragmentFiles() {
  if (!fs.existsSync(fragmentsDir)) return [];
  return fs
    .readdirSync(fragmentsDir)
    .filter((name) => name.endsWith(".md"))
    .filter((name) => name.toLowerCase() !== "readme.md")
    .sort()
    .map((name) => path.join(fragmentsDir, name));
}

function parseFragment(filePath) {
  const rel = path.relative(repoRoot, filePath);
  const raw = fs.readFileSync(filePath, "utf8");
  const lines = raw.split("\n");

  const firstNonBlank = lines.findIndex((line) => line.trim() !== "");
  if (firstNonBlank === -1) {
    fail(`${rel}: empty fragment (needs a '### ' header + body).`);
  }

  const headerIndices = lines
    .map((line, i) => (/^### /.test(line) ? i : -1))
    .filter((i) => i !== -1);
  if (headerIndices.length === 0) {
    fail(`${rel}: no '### ' header (the first non-blank line must be a '### ' thematic header).`);
  }
  if (headerIndices.length > 1) {
    fail(`${rel}: multiple '### ' headers — use one thematic section per fragment.`);
  }
  if (headerIndices[0] !== firstNonBlank) {
    fail(`${rel}: prose before the '### ' header — the header must be the first non-blank line.`);
  }

  const body = lines.slice(headerIndices[0] + 1).join("\n").trim();
  if (body === "") {
    fail(`${rel}: '### ' header has an empty body.`);
  }

  return { file: filePath, slug: path.basename(filePath), text: raw.trim() };
}

function assemble(version, date) {
  const files = listFragmentFiles();
  if (files.length === 0) {
    console.log("assemble-changelog: no fragments in changelog.d/ — nothing to cut.");
    return;
  }
  const fragments = files.map(parseFragment);

  let changelog = fs.readFileSync(changelogPath, "utf8");
  const versionHeader = new RegExp(`^## v${escapeRegExp(version)}(?:\\s|$)`, "m");
  if (versionHeader.test(changelog)) {
    fail(`changelog already has a '## v${version}' section — refusing to double-cut.`);
  }

  const sectionBody = fragments.map((fragment) => fragment.text).join("\n\n");
  const newSection = `## v${version} - ${date}\n\n${sectionBody}\n\n`;

  const firstReleaseIdx = changelog.search(/^## v/m);
  if (firstReleaseIdx === -1) {
    changelog = `${changelog.replace(/\s*$/, "")}\n\n${newSection.replace(/\s*$/, "")}\n`;
  } else {
    changelog =
      changelog.slice(0, firstReleaseIdx) + newSection + changelog.slice(firstReleaseIdx);
  }
  fs.writeFileSync(changelogPath, changelog, "utf8");

  for (const fragment of fragments) {
    fs.rmSync(fragment.file, { force: true });
  }

  console.log(`assemble-changelog: cut ## v${version} - ${date} from ${fragments.length} fragment(s):`);
  for (const fragment of fragments) {
    console.log(`  - consumed ${path.relative(repoRoot, fragment.file)}`);
  }
}

function printSection(version) {
  if (!fs.existsSync(changelogPath)) fail(`missing changelog: ${changelogPath}`);
  const changelog = fs.readFileSync(changelogPath, "utf8");
  const blocks = changelog.split(/^(?=## v)/m);
  const matcher = new RegExp(`^## v${escapeRegExp(version)}(?:\\s|-|$)`);
  const block = blocks.find((b) => matcher.test(b));
  if (!block) fail(`no '## v${version}' section found in changelog.`);
  process.stdout.write(`${block.trim()}\n`);
}

function checkFragments() {
  const files = listFragmentFiles();
  files.forEach(parseFragment); // exits via fail() on the first malformed fragment
  console.log(`assemble-changelog check: ${files.length} fragment(s) valid.`);
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--check")) {
    checkFragments();
    return;
  }

  const sectionIdx = args.indexOf("--section");
  if (sectionIdx !== -1) {
    const version = args[sectionIdx + 1];
    if (!version) fail("--section requires a <version> argument.");
    printSection(normalizeVersion(version));
    return;
  }

  const version = args.find((arg) => !arg.startsWith("-"));
  if (!version) {
    fail("usage: assemble-changelog.mjs <version> [date] | --check | --section <version>");
  }
  const normalized = normalizeVersion(version);
  if (!/^\d+\.\d+\.\d+$/.test(normalized)) {
    fail(`invalid version '${version}' (expected X.Y.Z).`);
  }
  const date = args[args.indexOf(version) + 1];
  const resolvedDate =
    date && !date.startsWith("-") ? date : new Date().toISOString().slice(0, 10);
  assemble(normalized, resolvedDate);
}

main();
