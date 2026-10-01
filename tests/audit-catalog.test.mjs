import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { buildAuditCatalog } from "../scripts/audit-catalog.mjs";

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "audit-catalog-producer-"));
  const family = "narrative-craft-audits";
  const skill = `plugins/apodictic/skills/${family}/SKILL.md`;
  const target = `${family}/references/craft/character.md`;
  const reference = path.join(root, "plugins/apodictic/skills", target);
  fs.mkdirSync(path.dirname(reference), { recursive: true });
  fs.writeFileSync(reference, "# Synthetic character protocol");
  fs.writeFileSync(path.join(root, skill), "# Character audits");
  return { root, registry: { paths: { skillFiles: [skill] }, auditFamilies: [{ id: family }], auditReferenceAliases: { "specialized-audits/references/craft/character.md": target } } };
}

test("binds legacy identifiers to registered owning resources", () => {
  const { root, registry } = fixture();
  try {
    const catalog = buildAuditCatalog(registry, root);
    assert.equal(catalog.schemaVersion, 1);
    assert.equal(catalog.referenceAliases["specialized-audits/references/craft/character.md"], "narrative-craft-audits/references/craft/character.md");
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test("rejects unsafe, absent, ambiguous and unregistered resources", () => {
  const { root, registry } = fixture();
  try {
    for (const target of ["../private.md", "narrative-craft-audits/references/../../private.md", "unknown/references/missing.md", "narrative-craft-audits/references/missing.md"]) {
      assert.throws(() => buildAuditCatalog({ ...registry, auditReferenceAliases: { "specialized-audits/references/craft/character.md": target } }, root));
    }
    assert.throws(() => buildAuditCatalog({ ...registry, paths: { skillFiles: [] } }, root));
    assert.throws(() => buildAuditCatalog({ ...registry, auditReferenceAliases: { ...registry.auditReferenceAliases, "specialized-audits/references/craft/duplicate.md": Object.values(registry.auditReferenceAliases)[0] } }, root));
    fs.writeFileSync(path.join(root, "plugins/apodictic/skills/narrative-craft-audits/references/craft/unmapped.md"), "New protocol");
    assert.throws(() => buildAuditCatalog(registry, root), /Unmapped/);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
