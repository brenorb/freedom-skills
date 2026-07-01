import { countPlaceholders, summarizeChange } from "./helpers.mjs";

export async function transformPayload(value, options) {
  const {
    skipKeys,
    transformText
  } = options;
  const skipKeySet = new Set(skipKeys || []);
  const stats = {
    textsScanned: 0,
    textsChanged: 0,
    placeholders: 0,
    revealed: 0
  };

  async function visit(current, key = null) {
    if (typeof current === "string") {
      if (key && skipKeySet.has(key)) {
        return current;
      }
      stats.textsScanned += 1;
      const transformed = await transformText(current);
      if (transformed.changed) {
        stats.textsChanged += 1;
        stats.placeholders += transformed.placeholders || 0;
        stats.revealed += transformed.revealed || 0;
      }
      return transformed.text;
    }

    if (Array.isArray(current)) {
      const out = [];
      for (const entry of current) {
        out.push(await visit(entry, key));
      }
      return out;
    }

    if (current && typeof current === "object") {
      const out = {};
      for (const [childKey, childValue] of Object.entries(current)) {
        out[childKey] = await visit(childValue, childKey);
      }
      return out;
    }

    return current;
  }

  return {
    payload: await visit(value),
    stats
  };
}

export function autoMode(rawInput) {
  const trimmed = rawInput.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      return {
        mode: "json",
        parsed: JSON.parse(rawInput)
      };
    } catch {
      return {
        mode: "text",
        parsed: null
      };
    }
  }
  return {
    mode: "text",
    parsed: null
  };
}

export function summarizeRedaction(original, redacted, mappingCount = 0) {
  const summary = summarizeChange(original, redacted);
  return {
    text: redacted,
    changed: summary.changed,
    placeholders: mappingCount || summary.placeholders,
    revealed: 0
  };
}

export function summarizeReveal(original, revealed) {
  const before = countPlaceholders(original);
  const after = countPlaceholders(revealed);
  return {
    text: revealed,
    changed: original !== revealed,
    placeholders: 0,
    revealed: Math.max(0, before - after)
  };
}
