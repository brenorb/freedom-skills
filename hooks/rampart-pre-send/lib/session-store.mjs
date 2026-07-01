import fs from "node:fs";
import path from "node:path";

import { ensureDir, parseToken, sanitizeSessionId, writeJsonFileAtomic } from "./helpers.mjs";

function sortEntries(entries) {
  return [...entries].sort((left, right) => {
    const leftToken = parseToken(left.token);
    const rightToken = parseToken(right.token);
    if (!leftToken || !rightToken) {
      return left.token.localeCompare(right.token);
    }
    if (leftToken.displayName !== rightToken.displayName) {
      return leftToken.displayName.localeCompare(rightToken.displayName);
    }
    return leftToken.index - rightToken.index;
  });
}

export function sessionStatePath(options) {
  return path.join(options.sessionDir, `${sanitizeSessionId(options.sessionId)}.json`);
}

export function loadSessionState(options) {
  const filePath = sessionStatePath(options);
  if (!fs.existsSync(filePath)) {
    return {
      filePath,
      state: {
        version: 1,
        entries: []
      }
    };
  }
  return {
    filePath,
    state: JSON.parse(fs.readFileSync(filePath, "utf8"))
  };
}

export function restoreSessionTable(table, state) {
  for (const entry of sortEntries(state.entries || [])) {
    table.placeholderFor(entry.label, entry.value);
  }
}

export function mergeSessionEntries(state, entries) {
  const byToken = new Map((state.entries || []).map((entry) => [entry.token, entry]));
  for (const entry of entries) {
    byToken.set(entry.token, entry);
  }
  return {
    version: 1,
    updatedAt: new Date().toISOString(),
    entries: sortEntries([...byToken.values()])
  };
}

export function saveSessionState(filePath, state) {
  ensureDir(path.dirname(filePath));
  writeJsonFileAtomic(filePath, state);
}

export function deleteSessionState(filePath) {
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
  }
}
