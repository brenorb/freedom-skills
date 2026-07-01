import {
  SessionEntityTable,
  applyPolicy,
  detectHeuristics,
  detectNer,
  premask,
  projectMaskedSpan,
  resolveKeepLabels
} from "@nationaldesignstudio/rampart";

export const DEFAULT_KEEP_LABELS = ["CITY", "STATE", "ZIP_CODE"];

export async function buildDetector(options) {
  if (options.backendCommand) {
    return null;
  }

  if (options.heuristicsOnly) {
    return async () => [];
  }

  const { env: hfEnv, pipeline } = await import("@huggingface/transformers");
  hfEnv.allowLocalModels = false;
  hfEnv.allowRemoteModels = true;
  hfEnv.useBrowserCache = false;

  const rawClassifier = await pipeline("token-classification", options.model, {
    dtype: "q4",
    device: "cpu"
  });

  const classifier = (text, runtimeOptions) => rawClassifier(text, runtimeOptions);
  const tokenizer = rawClassifier?.tokenizer;
  if (typeof tokenizer?.encode === "function") {
    classifier.countTokens = (text) => tokenizer.encode(text, { add_special_tokens: false }).length;
  }
  if (typeof tokenizer?.tokenize === "function") {
    classifier.tokenize = (text) => tokenizer.tokenize(text);
  }

  return async (text) => detectNer(text, classifier);
}

export async function detectSpans(text, detector) {
  const heuristic = detectHeuristics(text);
  if (!detector) {
    return heuristic;
  }
  const mask = premask(text, heuristic);
  const maskedSpans = await detector(mask.masked);
  const contextual = [];
  for (const span of maskedSpans) {
    const projected = projectMaskedSpan(span, text, mask);
    if (projected !== null) {
      contextual.push(projected);
    }
  }
  return [...heuristic, ...contextual];
}

export function createSessionTable(options) {
  return new SessionEntityTable(options.aliases || {}, resolveKeepLabels(options.keepLabels));
}

export async function redactTextWithTable(text, table, detector, keepLabels) {
  const spans = await detectSpans(text, detector);
  const redacted = applyPolicy(spans, resolveKeepLabels(keepLabels));
  const result = table.scrub(text, spans);

  const mappings = [];
  const seen = new Set();
  for (const span of redacted) {
    const token = table.placeholderFor(span.label, span.text);
    if (seen.has(token)) {
      continue;
    }
    seen.add(token);
    mappings.push({
      token,
      label: span.label,
      value: span.text
    });
  }

  return {
    text: result.text,
    placeholders: result.placeholders,
    mappings
  };
}
