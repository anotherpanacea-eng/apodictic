#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const checkSync = process.argv.includes("--check-sync");

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

function checkRsyncParity(sourceDir, targetDir) {
  const raw = execFileSync(
    "rsync",
    [
      "-ain",
      "--delete",
      "--exclude",
      ".git/",
      "--exclude",
      ".DS_Store",
      `${sourceDir}/`,
      `${targetDir}/`
    ],
    { encoding: "utf8" }
  );

  const lines = raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => !line.startsWith("sending incremental file list"))
    .filter((line) => !line.startsWith("sent "))
    .filter((line) => !line.startsWith("total size is"));

  return lines;
}

function main() {
  const errors = [];

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

  try {
    execFileSync(
      process.execPath,
      [path.join(repoRoot, "scripts/build-codex.mjs"), "--check"],
      { stdio: "inherit" }
    );
  } catch {
    errors.push("Codex workspace or package inputs are stale. Run scripts/build-codex.mjs.");
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

  const appTsxPath = abs(paths.appTsx);
  mustExist(appTsxPath);
  const appTsx = read(appTsxPath);
  const aboutMatch = appTsx.match(/Based on APODICTIC plugin v(\d+\.\d+\.\d+)/);
  if (!aboutMatch) {
    errors.push("Could not find About version string in src/App.tsx.");
  } else if (aboutMatch[1] !== expected) {
    errors.push(`Version mismatch: App.tsx About string is ${aboutMatch[1]}, expected ${expected}.`);
  }

  // 3) Optional: verify plugin/public mirror parity.
  if (checkSync) {
    const pluginDir = abs("plugins/apodictic");
    const geminiPublicDir = abs(paths.geminiPublicPlugin);
    mustExist(pluginDir);
    mustExist(geminiPublicDir);
    const rsyncDiff = checkRsyncParity(pluginDir, geminiPublicDir);
    if (rsyncDiff.length > 0) {
      errors.push(
        [
          "Gemini public plugin mirror is out of sync with plugins/apodictic.",
          "Run release sync step or: rsync -a --delete --exclude '.git/' plugins/apodictic/ ../APODICTIC-Gemini/public/apodictic-plugin/",
          "Diff:",
          ...rsyncDiff.slice(0, 40).map((line) => `  ${line}`),
          rsyncDiff.length > 40 ? `  ... (${rsyncDiff.length - 40} more)` : ""
        ].join("\n")
      );
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
