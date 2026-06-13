#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const checkOnly = process.argv.includes("--check");

const registryPath = path.join(repoRoot, "release-registry.json");
if (!fs.existsSync(registryPath)) {
  console.error(`Missing registry: ${registryPath}`);
  process.exit(1);
}

const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
const { paths, counts, categories, tagSummaryNames, commands, passes, researchModes, argumentCompanions, macroBlocks } = registry;

function abs(relPath) {
  return path.resolve(repoRoot, relPath);
}

function mustRead(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing file: ${filePath}`);
  }
  return fs.readFileSync(filePath, "utf8");
}

function writeIfChanged(filePath, nextContent, changedFiles) {
  const current = mustRead(filePath);
  if (current === nextContent) return;
  changedFiles.push(filePath);
  if (!checkOnly) {
    fs.writeFileSync(filePath, nextContent, "utf8");
  }
}

function replaceOrThrow(content, pattern, replacement, label) {
  if (!pattern.test(content)) {
    throw new Error(`Pattern not found for ${label}`);
  }
  return content.replace(pattern, replacement);
}

function updateJsonFile(filePath, mutator, changedFiles) {
  const current = mustRead(filePath);
  const data = JSON.parse(current);
  mutator(data);
  const next = `${JSON.stringify(data, null, 2)}\n`;
  writeIfChanged(filePath, next, changedFiles);
}

function buildAuditStats() {
  const byName = new Map(categories.map((category) => [category.name, category]));
  const universal = byName.get("Universal")?.items.length ?? 0;
  const craft = byName.get("Craft")?.items.length ?? 0;
  const genre = byName.get("Genre")?.items.length ?? 0;
  const tag = byName.get("Tag")?.items.length ?? 0;
  const available = categories.reduce((sum, category) => sum + category.items.length, 0);
  const specialized = available - universal;
  const primaryTag = tagSummaryNames.length;
  const companionTag = tag - primaryTag;

  return {
    byName,
    universal,
    craft,
    genre,
    tag,
    available,
    specialized,
    primaryTag,
    companionTag
  };
}

function ensureCountMatches(field, actual) {
  if (typeof counts[field] !== "number") return;
  if (counts[field] !== actual) {
    throw new Error(`Registry count mismatch: counts.${field}=${counts[field]} but derived value is ${actual}`);
  }
}

function validateRegistry(stats) {
  if (!stats.byName.has("Universal")) {
    throw new Error("Registry missing Universal category.");
  }
  if (!stats.byName.has("Tag")) {
    throw new Error("Registry missing Tag category.");
  }
  if (stats.companionTag < 0) {
    throw new Error(
      `Registry mismatch: tagSummaryNames has ${stats.primaryTag} entries but Tag category has ${stats.tag} items.`
    );
  }

  const tagNames = new Set();
  for (const item of stats.byName.get("Tag")?.items || []) {
    const normalizedName = item.name.trim().toLowerCase();
    tagNames.add(normalizedName);
    tagNames.add(item.slug.trim().toLowerCase());
    if (normalizedName.endsWith(" tag")) {
      tagNames.add(normalizedName.replace(/ tag$/, ""));
    }
  }
  const unknownSummaryTags = tagSummaryNames.filter(
    (name) => !tagNames.has(name.trim().toLowerCase())
  );
  if (unknownSummaryTags.length > 0) {
    throw new Error(
      `Registry mismatch: tagSummaryNames contains unknown tag names: ${unknownSummaryTags.join(", ")}`
    );
  }

  ensureCountMatches("availableAudits", stats.available);
  ensureCountMatches("specializedAudits", stats.specialized);
  ensureCountMatches("universalAudits", stats.universal);
  ensureCountMatches("tagAudits", stats.tag);
  ensureCountMatches("primaryTagAudits", stats.primaryTag);
  ensureCountMatches("tagCompanionAudits", stats.companionTag);
}

function buildPluginDescription(stats) {
  return [
    "APODICTIC Development Editor. Developmental editing that listens before diagnosing.",
    "Provides structural diagnosis, genre calibration, tag audits, plot architecture analysis, revision coaching, partial manuscript diagnostic, fragment synthesis, nonfiction argument engine (Dialectical Clarity + Red Team, Persuasion, Evidence, and Coaching companions), pre-writing pathway, and intake routing",
    `across ${counts.corePasses} core passes, ${stats.available} available audits (${stats.universal} universal, ${stats.craft} craft, ${stats.genre} genre, ${stats.tag} tag), ${counts.researchModes} research modes, ${counts.preWritingPathways} pre-writing pathway, and ${counts.intakeRouters} intake router.`,
    "Includes contract-driven and finding-driven audit integration pipeline."
  ].join(" ");
}

function buildCommandAuditList() {
  return categories
    .map((category) => {
      const header = `### ${category.commandHeading}`;
      const bullets = category.items
        .map((item) => `- **${item.slug}** — ${item.name}: ${item.summary}`)
        .join("\n");
      return `${header}\n${bullets}`;
    })
    .join("\n\n");
}

function buildReadmeSpecializedLine(stats) {
  return `- **Specialized Audits** — ${stats.available} available audits (${stats.universal} universal, ${stats.craft} craft, ${stats.genre} genre, ${stats.tag} tag), including ${stats.primaryTag} primary tags (${tagSummaryNames.join(", ")}) and ${stats.companionTag} companion intimacy audits; plus ${counts.researchModes} internet-enabled research modes`;
}

function buildReadmeAuditCountLine(stats) {
  return `Run a named audit or list all ${stats.available} available audits.`;
}

function buildReadmeCapabilitiesLine(stats) {
  return [
    "Current version is in `.claude-plugin/plugin.json`.",
    `Capabilities: ${counts.plotSpines} plot spines across ${counts.plotFamilies} families, ${stats.available} available audits (${stats.universal} universal, ${stats.craft} craft, ${stats.genre} genre, ${stats.tag} tag), ${counts.researchModes} research modes, ${counts.corePasses} core passes, the evaluative Pass 11 gate, the pre-writing pathway, and the intake router.`,
    "Includes contract-driven and finding-driven audit integration pipeline."
  ].join(" ");
}

function buildRootReadmePlotLine() {
  return `- **Plot coach** with ${counts.plotSpines} structural spines across ${counts.plotFamilies} families (not just three-act)`;
}

function buildRootReadmeAuditsLine(stats) {
  return `- **${stats.available} available audits** (${stats.universal} universal, ${stats.craft} craft, ${stats.genre} genre, ${stats.tag} tag) including scene function, shelf positioning, emotional craft, AI-prose detection, worldbuilding integration, force architecture, reception risk, and intimacy/consent coverage`;
}

function buildGroupedCommandList() {
  if (!commands || !Array.isArray(commands)) return null;

  const groups = {
    entry: { heading: "Start here:", items: [] },
    diagnostic: { heading: "Diagnostic workflows:", items: [] },
    focused: { heading: "Focused tools:", items: [] },
    setup: { heading: "Setup:", items: [] }
  };

  const aliases = [];

  for (const cmd of commands) {
    if (cmd.status === "compat_alias") {
      aliases.push(cmd);
      continue;
    }
    const group = groups[cmd.category];
    if (group) {
      group.items.push(`- \`${cmd.command}\` — ${cmd.writerQuestion}`);
    }
  }

  const sections = Object.values(groups)
    .filter((g) => g.items.length > 0)
    .map((g) => `**${g.heading}**\n${g.items.join("\n")}`)
    .join("\n\n");

  const aliasLines = aliases
    .map((a) => `\`${a.command}\` is a compatibility alias for \`${a.routerEquivalent}\`.`)
    .join("\n");

  return aliasLines ? `${sections}\n\n${aliasLines}` : sections;
}

function main() {
  const changedFiles = [];
  const auditStats = buildAuditStats();
  validateRegistry(auditStats);

  const pluginJsonPath = abs(paths.pluginJson);
  const pluginDescription = buildPluginDescription(auditStats);

  updateJsonFile(pluginJsonPath, (data) => {
    data.description = pluginDescription;
  }, changedFiles);

  updateJsonFile(abs(paths.rootPluginJson), (data) => {
    data.description = pluginDescription;
  }, changedFiles);

  updateJsonFile(abs(paths.rootMarketplaceJson), (data) => {
    if (Array.isArray(data.plugins) && data.plugins.length > 0) {
      data.plugins[0].description = pluginDescription;
    }
  }, changedFiles);

  updateJsonFile(abs(paths.claudeMarketplaceJson), (data) => {
    if (Array.isArray(data.plugins) && data.plugins.length > 0) {
      data.plugins[0].description = pluginDescription;
    }
  }, changedFiles);

  {
    const readmePath = abs(paths.pluginReadme);
    let content = mustRead(readmePath);
    content = replaceOrThrow(
      content,
      /^- \*\*(?:specialized-audits|Specialized Audits)\*\* — .*$/m,
      buildReadmeSpecializedLine(auditStats),
      "README specialized line"
    );
    content = replaceOrThrow(
      content,
      /Run a named audit or list all \d+ available audits\./,
      buildReadmeAuditCountLine(auditStats),
      "README available audits line"
    );
    content = replaceOrThrow(
      content,
      /Current version is in `\.claude-plugin\/plugin\.json`\. Capabilities: .*Includes contract-driven and finding-driven audit integration pipeline\./,
      buildReadmeCapabilitiesLine(auditStats),
      "README capabilities line"
    );
    writeIfChanged(readmePath, content, changedFiles);
  }

  if (paths.rootReadme) {
    const rootReadmePath = abs(paths.rootReadme);
    let content = mustRead(rootReadmePath);
    content = replaceOrThrow(
      content,
      /^- \*\*Plot coach\*\* with .*$/m,
      buildRootReadmePlotLine(),
      "root README plot-coach line"
    );
    content = replaceOrThrow(
      content,
      /^- \*\*(?:\d+ specialized audits|\d+ available audits)\*\*.*$/m,
      buildRootReadmeAuditsLine(auditStats),
      "root README audits line"
    );
    writeIfChanged(rootReadmePath, content, changedFiles);
  }

  {
    const auditCommandPath = abs(paths.auditCommand);
    let content = mustRead(auditCommandPath);
    const generated = buildCommandAuditList();
    content = replaceOrThrow(
      content,
      /### Universal Audits[\s\S]*?### Plot Architecture/,
      `${generated}\n\n### Plot Architecture`,
      "commands/audit generated list"
    );
    writeIfChanged(auditCommandPath, content, changedFiles);
  }

  // NOTE: App.tsx / LandingPage.tsx generation moved to APODICTIC-Gemini, which
  // now PULLS this registry (vendored as apodictic-registry.json) and runs its own
  // scripts/generate-ui.mjs. apodictic no longer reaches into the private sibling.

  if (commands && Array.isArray(commands)) {
    const groupedCommandList = buildGroupedCommandList();

    if (groupedCommandList) {
      // Each regex below replaces the WHOLE command block — from the "Start
      // here:" group up to the next section heading (## Key Terms / ### Selection
      // Guide). Consequences for future edits: prose inserted between the command
      // list and that heading is overwritten on regen, and renaming the heading
      // breaks replaceOrThrow. Keep added prose after the heading. (The end anchor
      // is the heading because the previous terminator — the `/revision-plan`
      // compatibility-alias sentence — no longer renders once that alias was retired.)
      {
        const rootReadmePath = abs(paths.rootReadme);
        let content = mustRead(rootReadmePath);
        content = replaceOrThrow(
          content,
          /## Commands\n\n\*\*Start here:\*\*[\s\S]*?(?=\n\n## Key Terms)/,
          `## Commands\n\n${groupedCommandList}`,
          "root README grouped command list"
        );
        writeIfChanged(rootReadmePath, content, changedFiles);
      }

      {
        const pluginReadmePath = abs(paths.pluginReadme);
        let content = mustRead(pluginReadmePath);
        content = replaceOrThrow(
          content,
          /### Commands\n\n\*\*Start here:\*\*[\s\S]*?(?=\n\n### Selection Guide)/,
          `### Commands\n\n${groupedCommandList}`,
          "plugin README grouped command list"
        );
        writeIfChanged(pluginReadmePath, content, changedFiles);
      }
    }
  }

  if (checkOnly) {
    if (changedFiles.length > 0) {
      console.error("release-generate check failed. Out-of-date files:");
      changedFiles.forEach((file) => console.error(`  - ${path.relative(repoRoot, file)}`));
      process.exit(1);
    }
    console.log("release-generate check passed.");
    return;
  }

  if (changedFiles.length === 0) {
    console.log("release-generate: no changes needed.");
    return;
  }

  console.log("release-generate updated files:");
  changedFiles.forEach((file) => console.log(`  - ${path.relative(repoRoot, file)}`));
}

try {
  main();
} catch (error) {
  console.error(`release-generate failed: ${error.message}`);
  process.exit(1);
}
