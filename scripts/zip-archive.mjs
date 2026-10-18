#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";

const LOCAL_FILE_HEADER = 0x04034b50;
const CENTRAL_FILE_HEADER = 0x02014b50;
const END_OF_CENTRAL_DIRECTORY = 0x06054b50;
const UTF8_FLAG = 0x0800;
const DEFLATE_METHOD = 8;
const MAX_UINT16 = 0xffff;
const MAX_UINT32 = 0xffffffff;
const REGULAR_FILE_MODE = 0o100000;
const ALLOWED_FILE_MODES = new Set([0o644, 0o755]);

const crcTable = Array.from({ length: 256 }, (_, index) => {
  let value = index;
  for (let bit = 0; bit < 8; bit += 1) {
    value = (value & 1) !== 0 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
  }
  return value >>> 0;
});

function crc32(buffer) {
  let value = 0xffffffff;
  for (const byte of buffer) {
    value = crcTable[(value ^ byte) & 0xff] ^ (value >>> 8);
  }
  return (value ^ 0xffffffff) >>> 0;
}

function canonicalArchiveName(rawName) {
  if (typeof rawName !== "string" || rawName.length === 0 || rawName.includes("\0")) {
    throw new Error("ZIP entry name must be a non-empty string without NUL bytes.");
  }
  if (rawName.includes("\\")) {
    throw new Error(`ZIP entry name must use forward slashes: ${rawName}`);
  }
  const normalized = path.posix.normalize(rawName);
  if (
    normalized !== rawName ||
    normalized.startsWith("/") ||
    normalized === ".." ||
    normalized.startsWith("../")
  ) {
    throw new Error(`Unsafe or non-canonical ZIP entry name: ${rawName}`);
  }
  return normalized;
}

function dosDateTime(date) {
  const year = Math.min(2107, Math.max(1980, date.getUTCFullYear()));
  const month = date.getUTCMonth() + 1;
  const day = date.getUTCDate();
  const hours = date.getUTCHours();
  const minutes = date.getUTCMinutes();
  const seconds = Math.floor(date.getUTCSeconds() / 2);
  return {
    date: ((year - 1980) << 9) | (month << 5) | day,
    time: (hours << 11) | (minutes << 5) | seconds
  };
}

function requireClassicZipLimit(value, label) {
  if (!Number.isSafeInteger(value) || value < 0 || value > MAX_UINT32) {
    throw new Error(`${label} exceeds the supported classic-ZIP limit.`);
  }
}

export function createZipArchive(archivePath, entries) {
  if (!Array.isArray(entries) || entries.length === 0) {
    throw new Error("Refusing to create an empty ZIP archive.");
  }
  if (entries.length > MAX_UINT16) {
    throw new Error("ZIP entry count exceeds the supported classic-ZIP limit.");
  }

  const seen = new Set();
  const localChunks = [];
  const centralChunks = [];
  let localOffset = 0;

  for (const entry of [...entries].sort((left, right) =>
    left.archiveName < right.archiveName ? -1 : left.archiveName > right.archiveName ? 1 : 0
  )) {
    const archiveName = canonicalArchiveName(entry.archiveName);
    if (seen.has(archiveName)) {
      throw new Error(`Duplicate ZIP entry name: ${archiveName}`);
    }
    seen.add(archiveName);

    const sourcePath = path.resolve(entry.sourcePath);
    const fileMode = entry.mode ?? 0o644;
    if (!ALLOWED_FILE_MODES.has(fileMode)) {
      throw new Error(`ZIP entry mode must be 0644 or 0755: ${archiveName}`);
    }
    const stat = fs.statSync(sourcePath);
    if (!stat.isFile()) {
      throw new Error(`ZIP source is not a regular file: ${sourcePath}`);
    }

    const source = fs.readFileSync(sourcePath);
    const compressed = zlib.deflateRawSync(source, { level: 9 });
    const name = Buffer.from(archiveName, "utf8");
    if (name.length > MAX_UINT16) {
      throw new Error(`ZIP entry name is too long: ${archiveName}`);
    }
    requireClassicZipLimit(source.length, `Uncompressed size for ${archiveName}`);
    requireClassicZipLimit(compressed.length, `Compressed size for ${archiveName}`);
    requireClassicZipLimit(localOffset, `Local-header offset for ${archiveName}`);

    const checksum = crc32(source);
    const stamp = dosDateTime(stat.mtime);
    const localHeader = Buffer.alloc(30 + name.length);
    localHeader.writeUInt32LE(LOCAL_FILE_HEADER, 0);
    localHeader.writeUInt16LE(20, 4);
    localHeader.writeUInt16LE(UTF8_FLAG, 6);
    localHeader.writeUInt16LE(DEFLATE_METHOD, 8);
    localHeader.writeUInt16LE(stamp.time, 10);
    localHeader.writeUInt16LE(stamp.date, 12);
    localHeader.writeUInt32LE(checksum, 14);
    localHeader.writeUInt32LE(compressed.length, 18);
    localHeader.writeUInt32LE(source.length, 22);
    localHeader.writeUInt16LE(name.length, 26);
    localHeader.writeUInt16LE(0, 28);
    name.copy(localHeader, 30);
    localChunks.push(localHeader, compressed);

    const centralHeader = Buffer.alloc(46 + name.length);
    centralHeader.writeUInt32LE(CENTRAL_FILE_HEADER, 0);
    centralHeader.writeUInt16LE(0x0314, 4);
    centralHeader.writeUInt16LE(20, 6);
    centralHeader.writeUInt16LE(UTF8_FLAG, 8);
    centralHeader.writeUInt16LE(DEFLATE_METHOD, 10);
    centralHeader.writeUInt16LE(stamp.time, 12);
    centralHeader.writeUInt16LE(stamp.date, 14);
    centralHeader.writeUInt32LE(checksum, 16);
    centralHeader.writeUInt32LE(compressed.length, 20);
    centralHeader.writeUInt32LE(source.length, 24);
    centralHeader.writeUInt16LE(name.length, 28);
    centralHeader.writeUInt16LE(0, 30);
    centralHeader.writeUInt16LE(0, 32);
    centralHeader.writeUInt16LE(0, 34);
    centralHeader.writeUInt16LE(0, 36);
    centralHeader.writeUInt32LE(((REGULAR_FILE_MODE | fileMode) << 16) >>> 0, 38);
    centralHeader.writeUInt32LE(localOffset, 42);
    name.copy(centralHeader, 46);
    centralChunks.push(centralHeader);

    localOffset += localHeader.length + compressed.length;
  }

  const centralDirectory = Buffer.concat(centralChunks);
  requireClassicZipLimit(localOffset, "Central-directory offset");
  requireClassicZipLimit(centralDirectory.length, "Central-directory size");
  const end = Buffer.alloc(22);
  end.writeUInt32LE(END_OF_CENTRAL_DIRECTORY, 0);
  end.writeUInt16LE(0, 4);
  end.writeUInt16LE(0, 6);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(centralDirectory.length, 12);
  end.writeUInt32LE(localOffset, 16);
  end.writeUInt16LE(0, 20);

  const output = Buffer.concat([...localChunks, centralDirectory, end]);
  fs.mkdirSync(path.dirname(archivePath), { recursive: true });
  const tempPath = `${archivePath}.tmp-${process.pid}`;
  fs.writeFileSync(tempPath, output);
  fs.rmSync(archivePath, { force: true });
  fs.renameSync(tempPath, archivePath);
}

export function listZipEntries(archivePath) {
  return listZipEntryMetadata(archivePath).map(({ name }) => name);
}

export function listZipEntryMetadata(archivePath) {
  const archive = fs.readFileSync(archivePath);
  const minimumOffset = Math.max(0, archive.length - (MAX_UINT16 + 22));
  let endOffset = -1;
  for (let offset = archive.length - 22; offset >= minimumOffset; offset -= 1) {
    if (
      archive.readUInt32LE(offset) === END_OF_CENTRAL_DIRECTORY &&
      offset + 22 + archive.readUInt16LE(offset + 20) === archive.length
    ) {
      endOffset = offset;
      break;
    }
  }
  if (endOffset < 0) {
    throw new Error(`ZIP end-of-central-directory record not found: ${archivePath}`);
  }
  if (archive.readUInt16LE(endOffset + 4) !== 0 || archive.readUInt16LE(endOffset + 6) !== 0) {
    throw new Error("Multi-disk ZIP archives are not supported.");
  }

  const entryCount = archive.readUInt16LE(endOffset + 10);
  const centralSize = archive.readUInt32LE(endOffset + 12);
  const centralOffset = archive.readUInt32LE(endOffset + 16);
  if (centralOffset + centralSize !== endOffset) {
    throw new Error("ZIP central-directory bounds are invalid.");
  }

  const entries = [];
  let offset = centralOffset;
  for (let index = 0; index < entryCount; index += 1) {
    if (offset + 46 > archive.length || archive.readUInt32LE(offset) !== CENTRAL_FILE_HEADER) {
      throw new Error(`Invalid ZIP central-file header at entry ${index}.`);
    }
    const nameLength = archive.readUInt16LE(offset + 28);
    const extraLength = archive.readUInt16LE(offset + 30);
    const commentLength = archive.readUInt16LE(offset + 32);
    const nameStart = offset + 46;
    const nameEnd = nameStart + nameLength;
    if (nameEnd > archive.length) {
      throw new Error(`Truncated ZIP entry name at entry ${index}.`);
    }
    entries.push({
      name: archive.subarray(nameStart, nameEnd).toString("utf8"),
      mode: (archive.readUInt32LE(offset + 38) >>> 16) & 0o7777
    });
    offset = nameEnd + extraLength + commentLength;
  }
  if (offset !== centralOffset + centralSize) {
    throw new Error("ZIP central-directory size does not match its entries.");
  }
  return entries;
}
