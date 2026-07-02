import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..", "..");
const outputPath = path.join(repoRoot, "research", "wayback-archive-feature-audit.xlsx");
const dataPath = path.join(__dirname, "audit_data.json");
const require = createRequire(import.meta.url);

async function loadArtifactTool() {
  const extraNodeModulesPath = process.env.OAI_NODE_MODULES;
  const resolveOptions = extraNodeModulesPath ? { paths: [extraNodeModulesPath] } : undefined;
  const modulePath = require.resolve("@oai/artifact-tool", resolveOptions);
  return import(pathToFileURL(modulePath).href);
}

const { Workbook, SpreadsheetFile } = await loadArtifactTool();

const raw = await fs.readFile(dataPath, "utf-8");
const data = JSON.parse(raw);
const { generatedAt, sourceSkill, objective, currentLoop, statusList, stories, issues } = data;

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const storiesSheet = workbook.worksheets.add("Stories");
const issuesSheet = workbook.worksheets.add("Issues");

const titleRange = summary.getRange("A1:F1");
titleRange.merge();
titleRange.values = [["Wayback Archive Skill Feature Audit"]];
titleRange.format.fill = { color: "#1F4E78" };
titleRange.format.font = { color: "#FFFFFF", bold: true, size: 16 };
titleRange.format.horizontalAlignment = "center";

summary.getRange("A3:B7").values = [
  ["Generated At", generatedAt],
  ["Canonical Workbook", outputPath],
  ["Source Skill", sourceSkill],
  ["Objective", objective],
  ["Current Loop", currentLoop],
];
summary.getRange("A3:A7").format.font = { bold: true };
summary.getRange("A3:B7").format.wrapText = true;

const storyLastRow = stories.length + 1;
const issueLastRow = issues.length + 1;

summary.getRange("A10:B16").values = [
  ["Status", "Count"],
  ["Pass", `=COUNTIF(Stories!I2:I${storyLastRow},"Pass")`],
  ["Pass - External Risk", `=COUNTIF(Stories!I2:I${storyLastRow},"Pass - External Risk")`],
  ["Unit Only", `=COUNTIF(Stories!I2:I${storyLastRow},"Unit Only")`],
  ["Untested", `=COUNTIF(Stories!I2:I${storyLastRow},"Untested")`],
  ["Fail", `=COUNTIF(Stories!I2:I${storyLastRow},"Fail")`],
  ["Fixed Pending Retest", `=COUNTIF(Stories!I2:I${storyLastRow},"Fixed Pending Retest")`]
];
summary.getRange("A10:B10").format.fill = { color: "#D9EAF7" };
summary.getRange("A10:B10").format.font = { bold: true };
summary.getRange("A10:B16").format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
summary.getRange("A10:B16").format.horizontalAlignment = "center";

summary.getRange("D10:E15").values = [
  ["Issue Status", "Count"],
  ["Open", `=COUNTIF(Issues!C2:C${issueLastRow},"Open")`],
  ["Resolved", `=COUNTIF(Issues!C2:C${issueLastRow},"Resolved")`],
  ["Manual Stories Verified", `=COUNTIF(Stories!I2:I${storyLastRow},"Pass")+COUNTIF(Stories!I2:I${storyLastRow},"Pass - External Risk")`],
  ["Stories Needing More Work", `=COUNTIF(Stories!I2:I${storyLastRow},"Untested")+COUNTIF(Stories!I2:I${storyLastRow},"Fail")+COUNTIF(Stories!I2:I${storyLastRow},"Fixed Pending Retest")`],
  ["Stories Covered by Tests Only", `=COUNTIF(Stories!I2:I${storyLastRow},"Unit Only")`]
];
summary.getRange("D10:E10").format.fill = { color: "#E2F0D9" };
summary.getRange("D10:E10").format.font = { bold: true };
summary.getRange("D10:E15").format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
summary.getRange("A3:E20").format.wrapText = true;
summary.freezePanes.freezeRows(1);
summary.showGridLines = false;

const storyHeaders = [[
  "Story ID",
  "Command",
  "Feature",
  "User Story",
  "Expected Behavior",
  "Code Evidence",
  "Unit / Test Evidence",
  "Latest Manual Evidence",
  "Status",
  "Notes / Risk"
]];
storiesSheet.getRange(`A1:J${storyLastRow}`).values = [storyHeaders[0], ...stories];
storiesSheet.getRange("A1:J1").format.fill = { color: "#1F4E78" };
storiesSheet.getRange("A1:J1").format.font = { color: "#FFFFFF", bold: true };
storiesSheet.getRange(`A1:J${storyLastRow}`).format.wrapText = true;
storiesSheet.getRange(`A1:J${storyLastRow}`).format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
storiesSheet.freezePanes.freezeRows(1);
storiesSheet.showGridLines = false;
storiesSheet.getRange(`I2:I${storyLastRow}`).dataValidation = {
  rule: { type: "list", values: statusList }
};

for (let row = 2; row <= storyLastRow; row += 1) {
  const statusCell = storiesSheet.getCell(row - 1, 8);
  const status = stories[row - 2][8];
  if (status === "Pass") {
    statusCell.format.fill = { color: "#E2F0D9" };
  } else if (status === "Pass - External Risk") {
    statusCell.format.fill = { color: "#FFF2CC" };
  } else if (status === "Unit Only") {
    statusCell.format.fill = { color: "#D9EAF7" };
  } else if (status === "Untested") {
    statusCell.format.fill = { color: "#F2F2F2" };
  } else if (status === "Fail") {
    statusCell.format.fill = { color: "#F4CCCC" };
  } else if (status === "Fixed Pending Retest") {
    statusCell.format.fill = { color: "#FCE5CD" };
  }
}

const issueHeaders = [[
  "Issue ID",
  "Category",
  "State",
  "Problem",
  "Affected Stories",
  "Current Mitigation / Fix",
  "Evidence"
]];
issuesSheet.getRange(`A1:G${issueLastRow}`).values = [issueHeaders[0], ...issues];
issuesSheet.getRange("A1:G1").format.fill = { color: "#7F6000" };
issuesSheet.getRange("A1:G1").format.font = { color: "#FFFFFF", bold: true };
issuesSheet.getRange(`A1:G${issueLastRow}`).format.wrapText = true;
issuesSheet.getRange(`A1:G${issueLastRow}`).format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
issuesSheet.freezePanes.freezeRows(1);
issuesSheet.showGridLines = false;

summary.getUsedRange().format.autofitColumns();
storiesSheet.getUsedRange().format.autofitColumns();
issuesSheet.getUsedRange().format.autofitColumns();

storiesSheet.getRange("D:J").format.columnWidth = 28;
storiesSheet.getRange("A:C").format.columnWidth = 16;
issuesSheet.getRange("D:G").format.columnWidth = 28;
summary.getRange("A:B").format.columnWidth = 28;
summary.getRange("D:E").format.columnWidth = 24;

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

console.log(JSON.stringify({ outputPath }, null, 2));
