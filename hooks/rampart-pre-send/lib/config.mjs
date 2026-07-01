import path from "node:path";
import { env } from "node:process";

import { DEFAULT_KEEP_LABELS } from "./runtime.mjs";
import { DEFAULT_MODEL, DEFAULT_RESPONSE_SKIP_KEYS, DEFAULT_SKIP_KEYS } from "./constants.mjs";
import {
  parseAliasEntries,
  parseAliasesValue,
  parseBool,
  parseList,
  readJsonFile,
  resolveMaybeRelative
} from "./helpers.mjs";

function findConfigPath(argv) {
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === "--config") {
      return argv[index + 1];
    }
  }
  return env.RAMPART_HOOK_CONFIG || null;
}

function readConfig(configPath, cwd) {
  if (!configPath) {
    return { config: {}, configDir: cwd };
  }
  const absolute = resolveMaybeRelative(cwd, configPath);
  return {
    config: readJsonFile(absolute),
    configDir: path.dirname(absolute)
  };
}

function mergeUnique(...lists) {
  return [...new Set(lists.flat().filter(Boolean))];
}

function baseOptions(kind, cwd, argv) {
  const configPath = findConfigPath(argv);
  const { config, configDir } = readConfig(configPath, cwd);

  const options = {
    configPath,
    configDir,
    mode: env.RAMPART_HOOK_MODE || config.mode || "auto",
    sessionId: env.RAMPART_SESSION_ID || config.sessionId || "default",
    sessionDir: resolveMaybeRelative(
      configDir,
      env.RAMPART_SESSION_DIR || config.sessionDir || ".rampart-sessions"
    ),
    failOpen: parseBool(env.RAMPART_FAIL_OPEN, parseBool(config.failOpen, false)),
    emitStats: false,
    model: env.RAMPART_MODEL || config.model || DEFAULT_MODEL,
    heuristicsOnly: parseBool(
      env.RAMPART_HEURISTICS_ONLY,
      parseBool(config.heuristicsOnly, false)
    ),
    keepLabels: mergeUnique(
      DEFAULT_KEEP_LABELS,
      parseList(config.keepLabels),
      parseList(env.RAMPART_KEEP_LABELS)
    ),
    aliases: {
      ...(config.aliases || {}),
      ...parseAliasesValue(env.RAMPART_ALIASES_JSON || "")
    },
    skipKeys: mergeUnique(
      DEFAULT_SKIP_KEYS,
      parseList(config.skipKeys),
      parseList(env.RAMPART_SKIP_KEYS)
    ),
    responseSkipKeys: mergeUnique(
      DEFAULT_RESPONSE_SKIP_KEYS,
      parseList(config.responseSkipKeys),
      parseList(env.RAMPART_RESPONSE_SKIP_KEYS)
    ),
    allowMissingSession: parseBool(
      env.RAMPART_ALLOW_MISSING_SESSION,
      parseBool(config.allowMissingSession, kind === "post")
    ),
    clearSession: parseBool(
      env.RAMPART_CLEAR_SESSION,
      parseBool(config.clearSession, false)
    ),
    backendCommand: env.RAMPART_BACKEND_CMD || config.backendCommand || ""
  };

  return options;
}

function printCommonHelp(kind) {
  const suffix =
    kind === "pre"
      ? "[--model <id>] [--heuristics-only] [--keep-label <LABEL>] [--skip-key <key>] [--alias LABEL=NAME]"
      : "[--clear-session] [--allow-missing-session] [--response-skip-key <key>]";

  return `Usage:
  cat payload.json | ${kind === "pre" ? "rampart-pre-send" : "rampart-post-send"} [--config <file>] [--session-id <id>] [--session-dir <dir>] [--mode auto|json|text] [--fail-open] [--stats] ${suffix}
`;
}

export function parsePreSendOptions(argv, cwd) {
  const options = baseOptions("pre", cwd, argv);

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--config") {
      index += 1;
      continue;
    }
    if (arg === "--session-id") {
      options.sessionId = argv[index + 1] || options.sessionId;
      index += 1;
      continue;
    }
    if (arg === "--session-dir") {
      options.sessionDir = resolveMaybeRelative(cwd, argv[index + 1] || options.sessionDir);
      index += 1;
      continue;
    }
    if (arg === "--mode") {
      options.mode = argv[index + 1] || options.mode;
      index += 1;
      continue;
    }
    if (arg === "--model") {
      options.model = argv[index + 1] || options.model;
      index += 1;
      continue;
    }
    if (arg === "--heuristics-only") {
      options.heuristicsOnly = true;
      continue;
    }
    if (arg === "--fail-open") {
      options.failOpen = true;
      continue;
    }
    if (arg === "--stats") {
      options.emitStats = true;
      continue;
    }
    if (arg === "--backend-cmd") {
      options.backendCommand = argv[index + 1] || options.backendCommand;
      index += 1;
      continue;
    }
    if (arg === "--keep-label") {
      options.keepLabels = mergeUnique(options.keepLabels, [argv[index + 1]]);
      index += 1;
      continue;
    }
    if (arg === "--skip-key") {
      options.skipKeys = mergeUnique(options.skipKeys, [argv[index + 1]]);
      index += 1;
      continue;
    }
    if (arg === "--alias") {
      options.aliases = {
        ...options.aliases,
        ...parseAliasEntries([argv[index + 1]])
      };
      index += 1;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      return { help: printCommonHelp("pre") };
    }
    throw new Error(`unknown argument: ${arg}`);
  }

  if (!["auto", "text", "json"].includes(options.mode)) {
    throw new Error(`invalid mode: ${options.mode}`);
  }

  return { options };
}

export function parsePostSendOptions(argv, cwd) {
  const options = baseOptions("post", cwd, argv);

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--config") {
      index += 1;
      continue;
    }
    if (arg === "--session-id") {
      options.sessionId = argv[index + 1] || options.sessionId;
      index += 1;
      continue;
    }
    if (arg === "--session-dir") {
      options.sessionDir = resolveMaybeRelative(cwd, argv[index + 1] || options.sessionDir);
      index += 1;
      continue;
    }
    if (arg === "--mode") {
      options.mode = argv[index + 1] || options.mode;
      index += 1;
      continue;
    }
    if (arg === "--fail-open") {
      options.failOpen = true;
      continue;
    }
    if (arg === "--stats") {
      options.emitStats = true;
      continue;
    }
    if (arg === "--clear-session") {
      options.clearSession = true;
      continue;
    }
    if (arg === "--allow-missing-session") {
      options.allowMissingSession = true;
      continue;
    }
    if (arg === "--response-skip-key") {
      options.responseSkipKeys = mergeUnique(options.responseSkipKeys, [argv[index + 1]]);
      index += 1;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      return { help: printCommonHelp("post") };
    }
    throw new Error(`unknown argument: ${arg}`);
  }

  if (!["auto", "text", "json"].includes(options.mode)) {
    throw new Error(`invalid mode: ${options.mode}`);
  }

  return { options };
}
