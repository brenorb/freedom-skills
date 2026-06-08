import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const skillDir = dirname(here);

test("compile_policy returns sane output for a valid policy", () => {
  const completed = spawnSync(
    "node",
    [
      "scripts/compile_policy.mjs",
      "--policy",
      "and(pk(user),or(99@pk(service),older(12960)))"
    ],
    { cwd: skillDir, encoding: "utf-8" }
  );

  assert.equal(completed.status, 0, completed.stderr);
  const payload = JSON.parse(completed.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.context, "p2wsh");
  assert.match(payload.miniscript, /and_v|and_b|and_n|andor|or_/);
  assert.equal(payload.analysis.issane, true);
  assert.equal(payload.compiled.issane, true);
  assert.ok(Array.isArray(payload.satisfactions.nonMalleableSats));
});

test("compile_policy reports invalid policies with a non-zero exit", () => {
  const completed = spawnSync(
    "node",
    [
      "scripts/compile_policy.mjs",
      "--policy",
      "or(and(pk(A),pk(B)),and(pk(A),pk(C)))"
    ],
    { cwd: skillDir, encoding: "utf-8" }
  );

  assert.equal(completed.status, 1);
  const payload = JSON.parse(completed.stdout);
  assert.equal(payload.ok, false);
  assert.match(payload.error, /failed|insane/i);
});
