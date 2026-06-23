#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const registryPath = path.join(repoRoot, "release-registry.json");
if (!fs.existsSync(registryPath)) {
  console.error(`Missing registry: ${registryPath}`);
  process.exit(1);
}

const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
const { paths } = registry;

function abs(relPath) {
  return path.resolve(repoRoot, relPath);
}

function read(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function mustExist(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing file: ${filePath}`);
  }
}

function readJson(filePath) {
  mustExist(filePath);
  return JSON.parse(read(filePath));
}

function extractFrontmatterVersion(filePath) {
  const content = read(filePath);
  const match = content.match(/^version:\s*(.+)$/m);
  if (!match) return null;
  return match[1].trim();
}

function readMarketplaceMetadataVersion(data) {
  if (typeof data.version === "string") return data.version;
  if (data && data.metadata && typeof data.metadata.version === "string") {
    return data.metadata.version;
  }
  return null;
}

function main() {
  const errors = [];

  // --versions-only: run ONLY the cross-manifest version-parity check (section 2),
  // skipping the generate-check / build self-checks / validate.sh --check-all steps.
  // CI uses this — those heavy gates already run as their own ci.yml steps, so the
  // version-parity gate (the one thing CI was NOT checking) is added without
  // double-running them. The full `release-verify` (no flag) still runs everything.
  const versionsOnly = process.argv.includes("--versions-only");

  if (!versionsOnly) {
    // 1) Ensure generated files are up to date.
    try {
      execFileSync(
        process.execPath,
        [path.join(repoRoot, "scripts/release-generate.mjs"), "--check"],
        { stdio: "inherit" }
      );
    } catch {
      errors.push("Generated files are stale. Run scripts/release-generate.mjs.");
    }

    // Host trees are no longer committed (GitHub #52) — regenerate fresh and
    // validate internal consistency (incl. the release archive) instead of
    // diffing against a committed copy.
    try {
      execFileSync(
        process.execPath,
        [path.join(repoRoot, "scripts/build-codex.mjs"), "--self-check"],
        { stdio: "inherit" }
      );
    } catch {
      errors.push("Codex workspace failed self-check. Run scripts/build-codex.mjs.");
    }

    try {
      execFileSync(
        process.execPath,
        [path.join(repoRoot, "scripts/build-antigravity.mjs"), "--self-check"],
        { stdio: "inherit" }
      );
    } catch {
      errors.push("Antigravity workspace failed self-check. Run scripts/build-antigravity.mjs.");
    }

    // 1.5) Aggregate real-file gate: self-tests + registry-vs-§4e + structured-findings
    // on the shipped templates (validate.sh --check-all). Closes the gap where the
    // standard verification path skipped real-file invariants.
    try {
      execFileSync(
        "bash",
        [path.join(repoRoot, "plugins/apodictic/scripts/validate.sh"), "--check-all"],
        { stdio: "inherit" }
      );
    } catch {
      errors.push("validate.sh --check-all failed (self-tests or real-file invariants). Run plugins/apodictic/scripts/validate.sh --check-all.");
    }
  }

  // 2) Verify version parity across canonical files.
  const pluginVersion = readJson(abs(paths.pluginJson)).version;
  const codexPluginVersion = readJson(abs("plugins/apodictic/.codex-plugin/plugin.json")).version;
  const rootPluginVersion = readJson(abs(paths.rootPluginJson)).version;
  const rootMarketplace = readJson(abs(paths.rootMarketplaceJson));
  const claudeMarketplace = readJson(abs(paths.claudeMarketplaceJson));

  const expected = pluginVersion;
  if (codexPluginVersion !== expected) {
    errors.push(`Version mismatch: plugins/apodictic/.codex-plugin/plugin.json is ${codexPluginVersion}, expected ${expected}.`);
  }
  if (rootPluginVersion !== expected) {
    errors.push(`Version mismatch: root plugin.json is ${rootPluginVersion}, expected ${expected}.`);
  }
  const rootMarketplaceVersion = readMarketplaceMetadataVersion(rootMarketplace);
  if (!rootMarketplaceVersion) {
    errors.push("Version mismatch: marketplace.json is missing metadata version.");
  } else if (rootMarketplaceVersion !== expected) {
    errors.push(`Version mismatch: marketplace.json metadata.version is ${rootMarketplaceVersion}, expected ${expected}.`);
  }
  if (!Array.isArray(rootMarketplace.plugins) || rootMarketplace.plugins.length === 0) {
    errors.push("marketplace.json has no plugins entries.");
  } else if (rootMarketplace.plugins[0].version !== expected) {
    errors.push(`Version mismatch: marketplace.json plugins[0].version is ${rootMarketplace.plugins[0].version}, expected ${expected}.`);
  }

  const claudeMarketplaceVersion = readMarketplaceMetadataVersion(claudeMarketplace);
  if (!claudeMarketplaceVersion) {
    errors.push("Version mismatch: .claude-plugin/marketplace.json is missing metadata version.");
  } else if (claudeMarketplaceVersion !== expected) {
    errors.push(`Version mismatch: .claude-plugin/marketplace.json metadata.version is ${claudeMarketplaceVersion}, expected ${expected}.`);
  }
  if (!Array.isArray(claudeMarketplace.plugins) || claudeMarketplace.plugins.length === 0) {
    errors.push(".claude-plugin/marketplace.json has no plugins entries.");
  } else if (claudeMarketplace.plugins[0].version !== expected) {
    errors.push(`Version mismatch: .claude-plugin/marketplace.json plugins[0].version is ${claudeMarketplace.plugins[0].version}, expected ${expected}.`);
  }

  for (const skillRelPath of paths.skillFiles) {
    const skillPath = abs(skillRelPath);
    mustExist(skillPath);
    const skillVersion = extractFrontmatterVersion(skillPath);
    if (!skillVersion) {
      errors.push(`Missing frontmatter version in ${skillRelPath}.`);
      continue;
    }
    if (skillVersion !== expected) {
      errors.push(`Version mismatch: ${skillRelPath} has ${skillVersion}, expected ${expected}.`);
    }
  }

  if (errors.length > 0) {
    console.error("release-verify failed:");
    for (const err of errors) {
      console.error(`- ${err}`);
    }
    process.exit(1);
  }

  console.log("release-verify passed.");
}

try {
  main();
} catch (error) {
  console.error(`release-verify failed: ${error.message}`);
  process.exit(1);
}
