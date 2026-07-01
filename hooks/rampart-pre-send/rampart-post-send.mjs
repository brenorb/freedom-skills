#!/usr/bin/env node

import { cwd, exit, stderr, stdout } from "node:process";

import { parsePostSendOptions } from "./lib/config.mjs";
import { autoMode, summarizeReveal, transformPayload } from "./lib/payload.mjs";
import { createSessionTable } from "./lib/runtime.mjs";
import { deleteSessionState, loadSessionState, restoreSessionTable, sessionStatePath } from "./lib/session-store.mjs";

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

async function main() {
  const rawInput = await readStdin();
  try {
    const parsed = parsePostSendOptions(process.argv.slice(2), cwd());
    if (parsed.help) {
      stdout.write(parsed.help);
      exit(0);
    }

    const options = parsed.options;
    const startedAt = Date.now();
    const stateInfo = loadSessionState(options);

    if ((stateInfo.state.entries || []).length === 0 && options.allowMissingSession) {
      stdout.write(rawInput);
      if (!rawInput.endsWith("\n")) {
        stdout.write("\n");
      }
      if (options.emitStats) {
        stderr.write(
          `[rampart-post-send] session=${options.sessionId} scanned=0 changed=0 revealed=0 elapsed_ms=${Date.now() - startedAt} missing_session=1\n`
        );
      }
      exit(0);
    }

    const table = createSessionTable(options);
    restoreSessionTable(table, stateInfo.state);
    const modeInfo = options.mode === "auto" ? autoMode(rawInput) : { mode: options.mode, parsed: null };
    const payloadMode = modeInfo.mode;
    const parsedJson = payloadMode === "json" ? modeInfo.parsed ?? JSON.parse(rawInput) : null;

    const transformText = async (text) => summarizeReveal(text, table.rehydrate(text));

    let output;
    let stats;
    if (payloadMode === "json") {
      const transformed = await transformPayload(parsedJson, {
        skipKeys: options.responseSkipKeys,
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
        placeholders: 0,
        revealed: result.revealed
      };
      stdout.write(output);
      if (!output.endsWith("\n")) {
        stdout.write("\n");
      }
    }

    if (options.clearSession) {
      deleteSessionState(stateInfo.filePath);
    }

    if (options.emitStats) {
      stderr.write(
        `[rampart-post-send] session=${options.sessionId} scanned=${stats.textsScanned} changed=${stats.textsChanged} revealed=${stats.revealed} elapsed_ms=${Date.now() - startedAt}\n`
      );
    }
  } catch (error) {
    const parsed = (() => {
      try {
        return parsePostSendOptions(process.argv.slice(2), cwd());
      } catch {
        return null;
      }
    })();
    if (parsed?.options?.failOpen) {
      stderr.write(`[rampart-post-send] fail-open: ${error.message}\n`);
      stdout.write(rawInput);
      if (!rawInput.endsWith("\n")) {
        stdout.write("\n");
      }
      exit(0);
    }
    stderr.write(`[rampart-post-send] ${error.message}\n`);
    exit(1);
  }
}

await main();
