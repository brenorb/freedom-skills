#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { createRequire } = require("module");

const FILEPIZZA_URL = "https://file.pizza/";
const runtimeRequire = createRequire(path.join(process.cwd(), "package.json"));
const { chromium } = runtimeRequire("playwright");

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function writeJson(filePath, payload) {
  fs.writeFileSync(filePath, JSON.stringify(payload, null, 2));
}

async function extractLinks(page) {
  return page.evaluate(() => {
    const values = Array.from(document.querySelectorAll("input, textarea"))
      .map((node) => node.value || "")
      .filter(Boolean);
    return values.filter((value) => /^https:\/\/file\.pizza\/download\//.test(value));
  });
}

async function waitForLinks(page) {
  const started = Date.now();
  while (Date.now() - started < 300000) {
    const links = await extractLinks(page);
    if (links.length >= 2) {
      return links;
    }
    await sleep(1000);
  }
  throw new Error("Timed out waiting for FilePizza links");
}

async function main() {
  const filePath = process.argv[2];
  const statePath = process.argv[3];
  const uploadId = process.argv[4];

  if (!filePath || !statePath || !uploadId) {
    throw new Error("Usage: node filepizza_seed.js <file-path> <state-path> <upload-id>");
  }

  const resolvedFilePath = path.resolve(filePath);
  const browser = await chromium.launch({ headless: true });
  let closed = false;

  const closeBrowser = async () => {
    if (closed) {
      return;
    }
    closed = true;
    await browser.close().catch(() => {});
  };

  process.on("SIGINT", async () => {
    await closeBrowser();
    process.exit(0);
  });
  process.on("SIGTERM", async () => {
    await closeBrowser();
    process.exit(0);
  });

  const page = await browser.newPage();
  await page.goto(FILEPIZZA_URL, { waitUntil: "domcontentloaded" });
  await page.setInputFiles('input[type="file"]', resolvedFilePath);
  if (typeof page.locator === "function") {
    await page.locator("#start-button").click();
  } else {
    await page.getByRole("button", { name: "Start" }).click();
  }

  const links = await waitForLinks(page);
  const longUrl = links.find((value) => value.split("/").length > 5) || links[0];
  const shortUrl = links.find((value) => value !== longUrl) || links[0];

  writeJson(statePath, {
    ok: true,
    upload_id: uploadId,
    file: resolvedFilePath,
    pid: process.pid,
    long_url: longUrl,
    short_url: shortUrl,
    status: "seeding",
    started_at: new Date().toISOString(),
  });

  setInterval(() => {}, 60000);
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
