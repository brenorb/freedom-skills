#!/usr/bin/env node

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

const payload = JSON.parse(input || "{}");
const texts = Array.isArray(payload.texts) ? payload.texts : [];
const prefixParts = [];
if (payload.heuristicsOnly) {
  prefixParts.push("[HEURISTICS]");
}
if (payload.model && payload.model !== "nationaldesignstudio/rampart") {
  prefixParts.push(`[MODEL:${payload.model}]`);
}
const prefix = prefixParts.join("");
const tokenMatchers = [
  {
    label: "EMAIL",
    pattern: /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
  },
  {
    label: "SSN",
    pattern: /\b\d{3}-\d{2}-\d{4}\b/g
  },
  {
    label: "PHONE",
    pattern: /\b(?:\d{3}[-. ]?){2}\d{4}\b/g
  }
];

const results = texts.map((text) => {
  const mappings = [];
  let replaced = String(text);
  for (const matcher of tokenMatchers) {
    replaced = replaced.replace(matcher.pattern, (value) => {
      const token = `[${matcher.label}_${1}]`;
      mappings.push({
        token,
        label: matcher.label,
        value
      });
      return token;
    });
  }
  return {
    text: `${prefix}${replaced}`,
    mappings
  };
});

process.stdout.write(
  JSON.stringify({
    texts: results.map((result) => result.text),
    mappings: results.map((result) => result.mappings)
  })
);
