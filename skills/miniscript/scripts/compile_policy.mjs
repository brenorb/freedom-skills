#!/usr/bin/env node

import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { analyzeMiniscript, compileMiniscript, satisfier } from "@bitcoinerlab/miniscript";
import { compilePolicy, compilePolicyTaproot, ready } from "@bitcoinerlab/miniscript-policies";

function usage() {
  console.error(
    [
      "Usage:",
      "  node scripts/compile_policy.mjs --policy '<policy>' [--context p2wsh|taproot] [--out result.json]",
      "  node scripts/compile_policy.mjs --miniscript '<miniscript>' [--context p2wsh|taproot] [--out result.json]"
    ].join("\n")
  );
}

function parseArgs(argv) {
  const args = {
    context: "p2wsh",
    out: null,
    policy: null,
    miniscript: null
  };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--policy") {
      args.policy = argv[++index] ?? null;
    } else if (token === "--miniscript") {
      args.miniscript = argv[++index] ?? null;
    } else if (token === "--context") {
      args.context = argv[++index] ?? "p2wsh";
    } else if (token === "--out") {
      args.out = argv[++index] ?? null;
    } else if (token === "--help" || token === "-h") {
      usage();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }
  if (Boolean(args.policy) === Boolean(args.miniscript)) {
    throw new Error("Provide exactly one of --policy or --miniscript");
  }
  if (!["p2wsh", "taproot"].includes(args.context)) {
    throw new Error(`Unsupported context: ${args.context}`);
  }
  return args;
}

function makeResultSkeleton(args) {
  return {
    compiler:
      "bitcoinerlab/miniscript-policies (reference C++ policy compiler from sipa/miniscript)",
    context: args.context,
    inputType: args.policy ? "policy" : "miniscript",
    input: args.policy ?? args.miniscript,
    ok: false
  };
}

function sliceWitnesses(items) {
  return items.slice(0, 5);
}

function analyzeCompiledMiniscript(miniscript, context) {
  const tapscript = context === "taproot";
  const compiled = compileMiniscript(miniscript, { tapscript });
  const analysis = analyzeMiniscript(miniscript, { tapscript });
  let satisfactions = null;
  if (analysis.valid && analysis.issane) {
    const sats = satisfier(miniscript, { tapscript });
    satisfactions = {
      nonMalleableSats: sliceWitnesses(sats.nonMalleableSats ?? []),
      malleableSats: sliceWitnesses(sats.malleableSats ?? []),
      nonMalleableCount: sats.nonMalleableSats?.length ?? 0,
      malleableCount: sats.malleableSats?.length ?? 0
    };
  }
  return { compiled, analysis, satisfactions };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(error.message);
    usage();
    process.exit(2);
  }

  await ready;

  const result = makeResultSkeleton(args);

  try {
    if (args.policy) {
      const policyResult =
        args.context === "taproot"
          ? compilePolicyTaproot(args.policy)
          : compilePolicy(args.policy);
      result.policy = policyResult;

      if (!policyResult.issane || !policyResult.miniscript || policyResult.miniscript.startsWith("[")) {
        result.error = "Policy compilation failed or produced an insane policy.";
      } else {
        result.miniscript = policyResult.miniscript;
        result.ok = true;
      }
    } else {
      result.miniscript = args.miniscript;
      result.ok = true;
    }

    if (result.ok && result.miniscript) {
      const analysis = analyzeCompiledMiniscript(result.miniscript, args.context);
      result.compiled = analysis.compiled;
      result.analysis = analysis.analysis;
      result.satisfactions = analysis.satisfactions;
      result.ok =
        result.analysis.valid &&
        result.analysis.issane &&
        result.compiled.issane &&
        result.compiled.issanesublevel;
      if (!result.ok && !result.error) {
        result.error = result.analysis.error || result.compiled.error || "Compiled miniscript is not sane.";
      }
    }
  } catch (error) {
    result.ok = false;
    result.error = error instanceof Error ? error.message : String(error);
  }

  const output = JSON.stringify(result, null, 2);
  if (args.out) {
    writeFileSync(resolve(args.out), output);
  }
  console.log(output);
  process.exit(result.ok ? 0 : 1);
}

await main();
