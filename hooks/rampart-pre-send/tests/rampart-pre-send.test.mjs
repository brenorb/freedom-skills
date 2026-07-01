import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const preHook = path.join(__dirname, "..", "rampart-pre-send.mjs");
const postHook = path.join(__dirname, "..", "rampart-post-send.mjs");
const fakeBackend = path.join(__dirname, "fake-redactor.mjs");
const e2eTranscript = path.join(__dirname, "e2e-transcript.mjs");
const fixturesDir = path.join(__dirname, "fixtures");

function makeSessionEnv(extraEnv = {}) {
  return {
    ...process.env,
    RAMPART_SESSION_ID: extraEnv.RAMPART_SESSION_ID || `test-${Math.random().toString(36).slice(2)}`,
    RAMPART_SESSION_DIR:
      extraEnv.RAMPART_SESSION_DIR || fs.mkdtempSync(path.join(os.tmpdir(), "rampart-hooks-")),
    ...extraEnv
  };
}

function runPreHook(input, args = [], extraEnv = {}) {
  const env = makeSessionEnv(extraEnv);
  return spawnSync(
    process.execPath,
    [preHook, "--backend-cmd", `${process.execPath} ${fakeBackend}`, ...args],
    {
      encoding: "utf8",
      input,
      env
    }
  );
}

function runPostHook(input, args = [], extraEnv = {}) {
  const env = makeSessionEnv(extraEnv);
  return spawnSync(process.execPath, [postHook, ...args], {
    encoding: "utf8",
    input,
    env
  });
}

function runRealPreHook(input, args = [], extraEnv = {}) {
  const env = makeSessionEnv(extraEnv);
  return spawnSync(process.execPath, [preHook, ...args], {
    encoding: "utf8",
    input,
    env
  });
}

function runRealPostHook(input, args = [], extraEnv = {}) {
  const env = makeSessionEnv(extraEnv);
  return spawnSync(process.execPath, [postHook, ...args], {
    encoding: "utf8",
    input,
    env
  });
}

function readFixture(name) {
  return fs.readFileSync(path.join(fixturesDir, name), "utf8");
}

test("redacts a plain user turn text payload", () => {
  const result = runPreHook("Send this to alice@example.com and mention SSN 123-45-6789");
  assert.equal(result.status, 0);
  assert.match(result.stdout, /\[EMAIL_1\]/);
  assert.match(result.stdout, /\[SSN_1\]/);
});

test("redacts a realistic OpenAI Chat Completions payload", () => {
  const result = runPreHook(readFixture("openai-chat-completions.json"), ["--mode", "json"]);
  assert.equal(result.status, 0);
  const output = JSON.parse(result.stdout);
  assert.equal(output.model, "gpt-4.1");
  assert.equal(output.messages[0].role, "system");
  assert.match(output.messages[1].content[0].text, /\[EMAIL_1\]/);
  assert.match(output.messages[1].content[0].text, /\[PHONE_1\]/);
  assert.equal(
    output.messages[1].content[1].image_url.url,
    "https://example.com/uploads/alice@example.com.png"
  );
  assert.equal(output.messages[2].tool_calls[0].id, "call_123");
  assert.match(output.messages[2].tool_calls[0].function.arguments, /\[EMAIL_1\]/);
  assert.match(output.messages[2].tool_calls[0].function.arguments, /\[SSN_1\]/);
  assert.equal(output.tools[0].function.name, "lookup_contact");
});

test("auto mode detects a realistic OpenAI Responses payload", () => {
  const result = runPreHook(readFixture("openai-responses.json"));
  assert.equal(result.status, 0);
  const output = JSON.parse(result.stdout);
  assert.equal(output.model, "gpt-5");
  assert.match(output.input[0].content[0].text, /\[EMAIL_1\]/);
  assert.match(output.input[0].content[0].text, /\[SSN_1\]/);
  assert.equal(
    output.input[0].content[1].image_url,
    "https://example.com/screenshots/alice@example.com.png"
  );
  assert.match(output.input[1].content[0].text, /\[PHONE_1\]/);
  assert.equal(output.previous_response_id, "resp_123456");
  assert.equal(output.reasoning.effort, "medium");
});

test("redacts a realistic Anthropic Messages payload", () => {
  const result = runPreHook(readFixture("anthropic-messages.json"), ["--mode", "json"]);
  assert.equal(result.status, 0);
  const output = JSON.parse(result.stdout);
  assert.equal(output.model, "claude-sonnet-4");
  assert.match(output.messages[0].content[0].text, /\[PHONE_1\]/);
  assert.match(output.messages[0].content[0].text, /\[EMAIL_1\]/);
  assert.equal(output.messages[0].content[1].source.data, "YWxpY2VAZXhhbXBsZS5jb20=");
  assert.match(output.messages[1].content[0].input.query, /\[EMAIL_1\]/);
  assert.match(output.messages[1].content[0].input.notes, /\[SSN_1\]/);
  assert.equal(output.messages[1].content[0].id, "toolu_01");
  assert.equal(output.metadata.user_id, "user_123");
});

test("auto mode falls back to text when payload only looks like broken JSON", () => {
  const input = '{"message":"Email alice@example.com"';
  const result = runPreHook(input);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /\[EMAIL_1\]/);
  assert.doesNotThrow(() => {
    assert.equal(typeof result.stdout, "string");
  });
});

test("stats mode emits operational summary on stderr", () => {
  const result = runPreHook("Email alice@example.com", ["--stats"]);
  assert.equal(result.status, 0);
  assert.match(result.stderr, /\[rampart-pre-send\] session=.* scanned=1 changed=1 placeholders=1 elapsed_ms=\d+/);
});

test("environment variables can supply backend, mode, heuristics, and model", () => {
  const input = JSON.stringify({
    input: [
      {
        role: "user",
        content: [
          {
            type: "input_text",
            text: "Email alice@example.com"
          }
        ]
      }
    ]
  });
  const env = makeSessionEnv({
    RAMPART_BACKEND_CMD: `${process.execPath} ${fakeBackend}`,
    RAMPART_HOOK_MODE: "json",
    RAMPART_HEURISTICS_ONLY: "1",
    RAMPART_MODEL: "custom/local-model"
  });
  const result = spawnSync(process.execPath, [preHook], {
    encoding: "utf8",
    input,
    env
  });
  assert.equal(result.status, 0);
  const output = JSON.parse(result.stdout);
  assert.match(output.input[0].content[0].text, /^\[HEURISTICS\]\[MODEL:custom\/local-model\]/);
  assert.match(output.input[0].content[0].text, /\[EMAIL_1\]/);
});

test("fail-open returns original payload on pre-hook backend failure", () => {
  const result = spawnSync(process.execPath, [preHook, "--backend-cmd", `${process.execPath} /no/such/file.mjs`, "--fail-open"], {
    encoding: "utf8",
    input: "Email alice@example.com"
  });
  assert.equal(result.status, 0);
  assert.match(result.stderr, /fail-open/);
  assert.equal(result.stdout.trim(), "Email alice@example.com");
});

test("fail-closed exits non-zero on pre-hook backend failure", () => {
  const result = spawnSync(process.execPath, [preHook, "--backend-cmd", `${process.execPath} /no/such/file.mjs`], {
    encoding: "utf8",
    input: "Email alice@example.com"
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /rampart-pre-send/);
});

test("invalid mode exits non-zero with a clear error", () => {
  const result = runPreHook("Email alice@example.com", ["--mode", "xml"]);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /invalid mode: xml/);
});

test("real model redacts a deterministic plain-text payload", { timeout: 120000 }, () => {
  const result = runRealPreHook(
    "My email is alice@example.com and my SSN is 123-45-6789.\n",
    ["--mode", "text", "--stats"]
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, "My email is [EMAIL_1] and my SSN is [SSN_1].\n");
  assert.match(result.stderr, /\[rampart-pre-send\] session=.* scanned=1 changed=1 placeholders=2 elapsed_ms=\d+/);
});

test("real model redacts a realistic OpenAI Chat Completions payload", { timeout: 120000 }, () => {
  const result = runRealPreHook(readFixture("openai-chat-completions.json"), ["--mode", "json", "--stats"]);
  assert.equal(result.status, 0, result.stderr);

  const output = JSON.parse(result.stdout);
  assert.equal(output.model, "gpt-4.1");
  assert.equal(output.messages[0].content, "You are a privacy-preserving assistant.");
  assert.equal(output.messages[1].content[0].type, "text");
  assert.equal(output.messages[1].content[0].text, "My email is [EMAIL_1] and my phone is [PHONE_1].");
  assert.equal(
    output.messages[1].content[1].image_url.url,
    "https://example.com/uploads/alice@example.com.png"
  );
  assert.equal(output.messages[2].tool_calls[0].id, "call_123");
  assert.equal(
    output.messages[2].tool_calls[0].function.arguments,
    "{\"email\":\"[EMAIL_1]\",\"notes\":\"SSN [SSN_1]\"}"
  );
  assert.equal(output.tools[0].function.name, "lookup_contact");
  assert.match(result.stderr, /\[rampart-pre-send\] session=.* scanned=4 changed=2 placeholders=4 elapsed_ms=\d+/);
});

test("real model redacts supported-language name patterns across all published Latin-script languages", { timeout: 120000 }, () => {
  const cases = [
    {
      language: "en",
      input: "My name is Alice Rivera and I live in London.\n",
      expected: "My name is [GIVEN_NAME_1] [SURNAME_1] and I live in London.\n"
    },
    {
      language: "es",
      input: "Me llamo Ana García y vivo en Madrid.\n",
      expected: "Me llamo [GIVEN_NAME_1] [SURNAME_1] y vivo en Madrid.\n"
    },
    {
      language: "fr",
      input: "Je m'appelle Claire Martin et j'habite a Paris.\n",
      expected: "Je m'appelle [GIVEN_NAME_1] et j'habite a Paris.\n"
    },
    {
      language: "de",
      input: "Ich heisse Anna Mueller und ich wohne in Berlin.\n",
      expected: "Ich heisse [GIVEN_NAME_1] [SURNAME_1] und ich wohne in Berlin.\n"
    },
    {
      language: "it",
      input: "Mi chiamo Giulia Rossi e vivo a Roma.\n",
      expected: "Mi chiamo [GIVEN_NAME_1] [SURNAME_1] e vivo a Roma.\n"
    },
    {
      language: "pt",
      input: "Meu nome e Ana Silva e moro em Lisboa.\n",
      expected: "Meu nome e [GIVEN_NAME_1] e moro em Lisboa.\n"
    },
    {
      language: "nl",
      input: "Ik heet Eva de Vries en ik woon in Amsterdam.\n",
      expected: "Ik heet [GIVEN_NAME_1] de Vries en ik woon in Amsterdam.\n"
    }
  ];

  for (const testCase of cases) {
    const result = runRealPreHook(testCase.input, ["--mode", "text"]);
    assert.equal(result.status, 0, `${testCase.language}: ${result.stderr}`);
    assert.equal(result.stdout, testCase.expected, testCase.language);
  }
});

test("real model covers the declared taxonomy with redaction and keep-policy checks", { timeout: 180000 }, () => {
  const exactCases = [
    {
      label: "SSN",
      input: "My SSN is 123-45-6789.\n",
      expected: "My SSN is [SSN_1].\n"
    },
    {
      label: "CREDIT_CARD",
      input: "My card number is 4111 1111 1111 1111.\n",
      expected: "My card number is [CREDIT_CARD_1].\n"
    },
    {
      label: "EMAIL",
      input: "My email is alice@example.com.\n",
      expected: "My email is [EMAIL_1].\n"
    },
    {
      label: "URL",
      input: "Visit https://example.com/private/alice\n",
      expected: "Visit [URL_1]\n"
    },
    {
      label: "IP_ADDRESS",
      input: "My IP address is 198.51.100.42.\n",
      expected: "My IP address is [IP_ADDRESS_1].\n"
    },
    {
      label: "PHONE",
      input: "My phone number is 415-555-1212.\n",
      expected: "My phone number is [PHONE_1].\n"
    },
    {
      label: "TAX_ID_CPF",
      input: "Meu numero de CPF e 123.456.789-09.\n",
      expected: "Meu numero de CPF e [TAX_ID_1].\n"
    },
    {
      label: "ROUTING_NUMBER",
      input: "Bank routing code 021000021.\n",
      expected: "Bank routing code [ROUTING_NUMBER_1].\n"
    },
    {
      label: "GOVERNMENT_ID",
      input: "My national ID number is AB1234567.\n",
      expected: "My national ID number is [GOVERNMENT_ID_1].\n"
    },
    {
      label: "PASSPORT",
      input: "Passport: X1234567.\n",
      expected: "Passport: [PASSPORT_1].\n"
    },
    {
      label: "DRIVERS_LICENSE",
      input: "Driver license: D1234567.\n",
      expected: "Driver license: [DRIVERS_LICENSE_1].\n"
    },
    {
      label: "BUILDING_STREET",
      input: "I live at 123 Main Street.\n",
      expected: "I live at [BUILDING_NUMBER_1] [STREET_NAME_1].\n"
    },
    {
      label: "SECONDARY_ADDRESS",
      input: "Apartment 4B.\n",
      expected: "[SECONDARY_ADDRESS_1][BUILDING_NUMBER_1].\n"
    },
    {
      label: "FULL_ADDRESS_KEEP_GEO",
      input: "My address is 123 Main Street, Apartment 4B, Austin, Texas 78701.\n",
      expected: "My address is [BUILDING_NUMBER_1] [STREET_NAME_1], [SECONDARY_ADDRESS_1], Austin, Texas 78701.\n"
    }
  ];

  for (const testCase of exactCases) {
    const result = runRealPreHook(testCase.input, ["--mode", "text"]);
    assert.equal(result.status, 0, `${testCase.label}: ${result.stderr}`);
    assert.equal(result.stdout, testCase.expected, testCase.label);
  }

  const bankAccountDiagnostic = runRealPreHook(
    "The beneficiary account identifier is 987654321234.\n",
    ["--mode", "text"]
  );
  assert.equal(bankAccountDiagnostic.status, 0, bankAccountDiagnostic.stderr);
  assert.equal(
    bankAccountDiagnostic.stdout,
    "The beneficiary account identifier is [GOVERNMENT_ID_1].\n"
  );
});

test("pre and post hooks round-trip placeholders through shared session state", () => {
  const env = makeSessionEnv();
  const pre = runPreHook("Email alice@example.com and phone 415-555-1212", [], env);
  assert.equal(pre.status, 0, pre.stderr);
  assert.equal(pre.stdout.trim(), "Email [EMAIL_1] and phone [PHONE_1]");

  const post = runPostHook("I will use [EMAIL_1] and [PHONE_1].", [], env);
  assert.equal(post.status, 0, post.stderr);
  assert.equal(post.stdout.trim(), "I will use alice@example.com and 415-555-1212.");
});

test("real model keeps placeholder identity stable across turns in one session", { timeout: 120000 }, () => {
  const env = makeSessionEnv();
  const first = runRealPreHook("My email is alice@example.com.\n", ["--mode", "text"], env);
  const second = runRealPreHook("Use alice@example.com for the follow-up.\n", ["--mode", "text"], env);
  assert.equal(first.status, 0, first.stderr);
  assert.equal(second.status, 0, second.stderr);
  assert.equal(first.stdout, "My email is [EMAIL_1].\n");
  assert.equal(second.stdout, "Use [EMAIL_1] for the follow-up.\n");
});

test("real model post-hook rehydrates a provider reply using saved session state", { timeout: 120000 }, () => {
  const env = makeSessionEnv();
  const pre = runRealPreHook(
    "My email is alice@example.com and my SSN is 123-45-6789.\n",
    ["--mode", "text"],
    env
  );
  assert.equal(pre.status, 0, pre.stderr);

  const post = runRealPostHook(
    "I will send the documents to [EMAIL_1] and note [SSN_1].\n",
    ["--mode", "text", "--stats"],
    env
  );
  assert.equal(post.status, 0, post.stderr);
  assert.equal(
    post.stdout,
    "I will send the documents to alice@example.com and note 123-45-6789.\n"
  );
  assert.match(post.stderr, /\[rampart-post-send\] session=.* scanned=1 changed=1 revealed=2 elapsed_ms=\d+/);
});

test("config can keep URL visible while still redacting other supported classes", { timeout: 120000 }, () => {
  const env = makeSessionEnv();
  const configPath = path.join(env.RAMPART_SESSION_DIR, "hook-config.json");
  fs.writeFileSync(
    configPath,
    `${JSON.stringify({
      keepLabels: ["CITY", "STATE", "ZIP_CODE", "URL"]
    }, null, 2)}\n`
  );
  const result = runRealPreHook(
    "Visit https://example.com/private/alice and email alice@example.com.\n",
    ["--mode", "text", "--config", configPath],
    env
  );
  assert.equal(result.status, 0, result.stderr);
  assert.equal(
    result.stdout,
    "Visit https://example.com/private/alice and email [EMAIL_1].\n"
  );
});

test("post-hook can clear session state after reveal", () => {
  const env = makeSessionEnv();
  const pre = runPreHook("Email alice@example.com", [], env);
  assert.equal(pre.status, 0, pre.stderr);

  const post = runPostHook("Reply to [EMAIL_1].", ["--clear-session"], env);
  assert.equal(post.status, 0, post.stderr);

  const replay = runPostHook("Reply to [EMAIL_1].", [], env);
  assert.equal(replay.status, 0, replay.stderr);
  assert.equal(replay.stdout.trim(), "Reply to [EMAIL_1].");
});

test("records a complete end-to-end transcript from user text to visible reply", { timeout: 120000 }, () => {
  const result = spawnSync(process.execPath, [e2eTranscript], {
    encoding: "utf8"
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /=== User Input ===/);
  assert.match(result.stdout, /=== Redacted Payload Sent To LLM ===/);
  assert.match(result.stdout, /My email is \[EMAIL_1\]\./);
  assert.match(result.stdout, /=== Simulated LLM Output ===/);
  assert.match(result.stdout, /I will email \[EMAIL_1\]\./);
  assert.match(result.stdout, /=== User Visible Output ===/);
  assert.match(result.stdout, /I will email alice@example\.com\./);
  assert.match(result.stdout, /I will call 415-555-1212\./);
  assert.match(result.stdout, /I will ship the packet to 123 Main Street, Apartment 4B, Austin, Texas 78701\./);
});
