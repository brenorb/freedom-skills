#!/usr/bin/env node

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const preHook = path.join(__dirname, "..", "rampart-pre-send.mjs");
const postHook = path.join(__dirname, "..", "rampart-post-send.mjs");
const fakeLlm = path.join(__dirname, "fake-llm.mjs");

function runNode(script, args, input, env) {
  return spawnSync(process.execPath, [script, ...args], {
    encoding: "utf8",
    input,
    env
  });
}

const sessionId = "e2e-transcript";
const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), "rampart-e2e-"));
const env = {
  ...process.env,
  RAMPART_SESSION_ID: sessionId,
  RAMPART_SESSION_DIR: sessionDir
};

const userInput = [
  "My email is alice@example.com.",
  "My phone number is 415-555-1212.",
  "My address is 123 Main Street, Apartment 4B, Austin, Texas 78701.",
  ""
].join("\n");

const pre = runNode(preHook, ["--mode", "text", "--stats"], userInput, env);
assert.equal(pre.status, 0, pre.stderr);

const expectedRedacted = [
  "My email is [EMAIL_1].",
  "My phone number is [PHONE_1].",
  "My address is [BUILDING_NUMBER_1] [STREET_NAME_1], Apartment 4B, Austin, Texas 78701.",
  ""
].join("\n");
assert.equal(pre.stdout, expectedRedacted);

const llm = runNode(fakeLlm, [], pre.stdout, env);
assert.equal(llm.status, 0, llm.stderr);

const expectedLlmOutput = [
  "Acknowledged.",
  "I will email [EMAIL_1].",
  "I will call [PHONE_1].",
  "I will ship the packet to [BUILDING_NUMBER_1] [STREET_NAME_1], Apartment 4B, Austin, Texas 78701.",
  ""
].join("\n");
assert.equal(llm.stdout, expectedLlmOutput);

const post = runNode(postHook, ["--mode", "text", "--stats"], llm.stdout, env);
assert.equal(post.status, 0, post.stderr);

const expectedVisibleReply = [
  "Acknowledged.",
  "I will email alice@example.com.",
  "I will call 415-555-1212.",
  "I will ship the packet to 123 Main Street, Apartment 4B, Austin, Texas 78701.",
  ""
].join("\n");
assert.equal(post.stdout, expectedVisibleReply);

const sessionFile = path.join(sessionDir, `${encodeURIComponent(sessionId)}.json`);
const sessionState = JSON.parse(fs.readFileSync(sessionFile, "utf8"));

process.stdout.write("=== User Input ===\n");
process.stdout.write(userInput);
process.stdout.write("=== Pre Hook Stats ===\n");
process.stdout.write(pre.stderr);
process.stdout.write("=== Redacted Payload Sent To LLM ===\n");
process.stdout.write(pre.stdout);
process.stdout.write("=== Simulated LLM Output ===\n");
process.stdout.write(llm.stdout);
process.stdout.write("=== Post Hook Stats ===\n");
process.stdout.write(post.stderr);
process.stdout.write("=== User Visible Output ===\n");
process.stdout.write(post.stdout);
process.stdout.write("=== Session Entries ===\n");
process.stdout.write(`${JSON.stringify(sessionState.entries, null, 2)}\n`);
