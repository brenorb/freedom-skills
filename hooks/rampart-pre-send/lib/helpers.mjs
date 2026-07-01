import fs from "node:fs";
import path from "node:path";

export function readJsonFile(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export function writeJsonFileAtomic(filePath, value) {
  const tempPath = `${filePath}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(value, null, 2)}\n`);
  fs.renameSync(tempPath, filePath);
}

export function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

export function parseBool(value, fallback = false) {
  if (value === undefined || value === null || value === "") {
    return fallback;
  }
  if (typeof value === "boolean") {
    return value;
  }
  const normalized = String(value).trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) {
    return true;
  }
  if (["0", "false", "no", "off"].includes(normalized)) {
    return false;
  }
  return fallback;
}

export function parseList(value) {
  if (value === undefined || value === null || value === "") {
    return [];
  }
  if (Array.isArray(value)) {
    return value.map((entry) => String(entry)).filter(Boolean);
  }
  return String(value)
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export function countPlaceholders(text) {
  const matches = String(text).match(/\[[A-Z][A-Z_]*_\d+\]/g);
  return matches ? matches.length : 0;
}

export function summarizeChange(original, transformed) {
  return {
    changed: original !== transformed,
    placeholders: countPlaceholders(transformed)
  };
}

export function parseAliasEntries(entries) {
  const out = {};
  for (const entry of entries) {
    const index = entry.indexOf("=");
    if (index === -1) {
      continue;
    }
    const key = entry.slice(0, index).trim();
    const value = entry.slice(index + 1).trim();
    if (key && value) {
      out[key] = value;
    }
  }
  return out;
}

export function parseAliasesValue(value) {
  if (!value) {
    return {};
  }
  if (typeof value === "object" && !Array.isArray(value)) {
    return value;
  }
  return JSON.parse(String(value));
}

export function resolveMaybeRelative(baseDir, targetPath) {
  if (!targetPath) {
    return targetPath;
  }
  if (path.isAbsolute(targetPath)) {
    return targetPath;
  }
  return path.resolve(baseDir, targetPath);
}

export function sanitizeSessionId(sessionId) {
  return encodeURIComponent(String(sessionId || "default"));
}

export function parseToken(token) {
  const match = /^\[([A-Z][A-Z_]*)_(\d+)\]$/.exec(token);
  if (!match) {
    return null;
  }
  return {
    displayName: match[1],
    index: Number(match[2])
  };
}
