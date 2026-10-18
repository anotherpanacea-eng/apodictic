#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createZipArchive, listZipEntryMetadata } from "./zip-archive.mjs";

const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "apodictic-zip-test-"));
try {
  const source = path.join(tempRoot, "source.txt");
  const archive = path.join(tempRoot, "archive.zip");
  fs.writeFileSync(source, "fixture\n", "utf8");
  createZipArchive(archive, [
    { sourcePath: source, archiveName: "regular.txt", mode: 0o644 },
    { sourcePath: source, archiveName: "executable.sh", mode: 0o755 }
  ]);
  assert.deepEqual(listZipEntryMetadata(archive), [
    { name: "executable.sh", mode: 0o755 },
    { name: "regular.txt", mode: 0o644 }
  ]);
  assert.throws(
    () => createZipArchive(archive, [
      { sourcePath: source, archiveName: "unsafe", mode: 0o777 }
    ]),
    /must be 0644 or 0755/
  );
  console.log("zip-archive modes: OK");
} finally {
  fs.rmSync(tempRoot, { recursive: true, force: true });
}
