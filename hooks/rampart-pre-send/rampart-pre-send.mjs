#!/usr/bin/env node

import { cwd, exit, stderr, stdout } from "node:process";

import { parsePreSendOptions } from "./lib/config.mjs";
import { autoMode, summarizeRedaction, transformPayload } from "./lib/payload.mjs";
import { buildDetector, createSessionTable, redactTextWithTable } from "./lib/runtime.mjs";
import { loadSessionState, mergeSessionEntries, restoreSessionTable, saveSessionState } from "./lib/session-store.mjs";

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

function splitCommand(command) {
  const parts = command.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
  return parts.map((part) => part.replace(/^"(.*)"$/, "$1"));
}

async function redactWithExternalBackend(texts, options) {
  const { spawnSync } = await import("node:child_process");
  const parts = splitCommand(options.backendCommand);
  if (parts.length === 0) {
    throw new Error("empty backend command");
  }
  const result = spawnSync(parts[0], parts.slice(1), {
    encoding: "utf8",
    input: JSON.stringify({
      texts,
      model: options.model,
      heuristicsOnly: options.heuristicsOnly,
      keepLabels: options.keepLabels,
      aliases: options.aliases
    })
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || "").trim() || `backend exited with status ${result.status}`);
  }
  const parsed = JSON.parse(result.stdout || "{}");
  if (!Array.isArray(parsed.texts) || parsed.texts.length !== texts.length) {
    throw new Error("backend returned an invalid texts payload");
  }
  const mappings = Array.isArray(parsed.mappings) ? parsed.mappings : texts.map(() => []);
  return parsed.texts.map((text, index) => ({
    text,
    mappings: Array.isArray(mappings[index]) ? mappings[index] : []
  }));
}

async function main() {
  const rawInput = await readStdin();
  try {
    const parsed = parsePreSendOptions(process.argv.slice(2), cwd());
    if (parsed.help) {
      stdout.write(parsed.help);
      exit(0);
    }

    const options = parsed.options;
    const startedAt = Date.now();
    const stateInfo = loadSessionState(options);
    const table = createSessionTable(options);
    restoreSessionTable(table, stateInfo.state);
    const detector = await buildDetector(options);
    const modeInfo = options.mode === "auto" ? autoMode(rawInput) : { mode: options.mode, parsed: null };
    const payloadMode = modeInfo.mode;
    const parsedJson = payloadMode === "json" ? modeInfo.parsed ?? JSON.parse(rawInput) : null;
    const newEntries = [];

    const transformText = async (text) => {
      if (options.backendCommand) {
        const [result] = await redactWithExternalBackend([text], options);
        for (const mapping of result.mappings) {
          newEntries.push(mapping);
        }
        return summarizeRedaction(text, result.text, result.mappings.length);
      }
      const result = await redactTextWithTable(text, table, detector, options.keepLabels);
      for (const mapping of result.mappings) {
        newEntries.push(mapping);
      }
      return summarizeRedaction(text, result.text, result.mappings.length);
    };

    let output;
    let stats;
    if (payloadMode === "json") {
      const transformed = await transformPayload(parsedJson, {
        skipKeys: options.skipKeys,
        transformText
      });
      output = transformed.payload;
      stats = transformed.stats;
      stdout.write(`${JSON.stringify(output, null, 2)}\n`);
    } else {
      const result = await transformText(rawInput);
      output = result.text;
      stats = {
        textsScanned: 1,
        textsChanged: result.changed ? 1 : 0,
        placeholders: result.placeholders,
        revealed: 0
      };
      stdout.write(output);
      if (!output.endsWith("\n")) {
        stdout.write("\n");
      }
    }

    const nextState = mergeSessionEntries(stateInfo.state, newEntries);
    saveSessionState(stateInfo.filePath, nextState);

    if (options.emitStats) {
      stderr.write(
        `[rampart-pre-send] session=${options.sessionId} scanned=${stats.textsScanned} changed=${stats.textsChanged} placeholders=${stats.placeholders} elapsed_ms=${Date.now() - startedAt}\n`
      );
    }
  } catch (error) {
    const parsed = (() => {
      try {
        return parsePreSendOptions(process.argv.slice(2), cwd());
      } catch {
        return null;
      }
    })();
    if (parsed?.options?.failOpen) {
      stderr.write(`[rampart-pre-send] fail-open: ${error.message}\n`);
      stdout.write(rawInput);
      if (!rawInput.endsWith("\n")) {
        stdout.write("\n");
      }
      exit(0);
    }
    stderr.write(`[rampart-pre-send] ${error.message}\n`);
    exit(1);
  }
}

await main();
