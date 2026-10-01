import fs from "node:fs";
import path from "node:path";

// Additive producer contract. Legacy card paths remain identifiers; this
// catalog binds each identifier to one owning skill's actual resource.
export function buildAuditCatalog(registry, root) {
  const families = registry.auditFamilies;
  const referenceAliases = registry.auditReferenceAliases;
  if (!Array.isArray(families) || families.length === 0 ||
      !referenceAliases || typeof referenceAliases !== "object" || Array.isArray(referenceAliases)) {
    throw new Error("Missing audit-family ownership or reference aliases");
  }
  const ids = new Set();
  for (const family of families) {
    if (!/^[a-z][a-z0-9-]*$/.test(family.id) || family.id === "specialized-audits" || ids.has(family.id)) {
      throw new Error(`Invalid/duplicate audit family: ${family.id}`);
    }
    ids.add(family.id);
    const skill = `plugins/apodictic/skills/${family.id}/SKILL.md`;
    if (!registry.paths.skillFiles.includes(skill) || !fs.existsSync(path.join(root, skill))) {
      throw new Error(`Unregistered or missing owning skill: ${skill}`);
    }
  }
  const targets = new Set();
  for (const [legacy, canonical] of Object.entries(referenceAliases)) {
    if (!legacy.startsWith("specialized-audits/references/") ||
        !ids.has(canonical.split("/")[0]) ||
        canonical.split("/")[1] !== "references" ||
        [legacy, canonical].some((p) => p.startsWith("/") || p.includes("\\") ||
          p.split("/").some((part) => !part || part === "." || part === ".."))) {
      throw new Error(`Unsafe audit reference alias: ${legacy}`);
    }
    if (targets.has(canonical)) throw new Error(`Ambiguous audit reference: ${canonical}`);
    targets.add(canonical);
    if (!fs.existsSync(path.join(root, "plugins/apodictic/skills", canonical))) {
      throw new Error(`Missing audit reference target: ${canonical}`);
    }
  }
  // A new reference must have a stable migration identifier too. This catches
  // accidental omission from runtime discovery even when its card is present.
  for (const family of families) {
    const base = path.join(root, "plugins/apodictic/skills", family.id, "references");
    function visit(directory) {
      for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const file = path.join(directory, entry.name);
        if (entry.isDirectory()) visit(file);
        else if (entry.isFile()) {
          const canonical = path.relative(path.join(root, "plugins/apodictic/skills"), file).split(path.sep).join("/");
          if (!targets.has(canonical)) throw new Error(`Unmapped audit resource: ${canonical}`);
        }
      }
    }
    visit(base);
  }
  return { schemaVersion: 1, families, referenceAliases };
}
