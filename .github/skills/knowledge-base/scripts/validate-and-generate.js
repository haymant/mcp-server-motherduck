#!/usr/bin/env node
const path = require("path");
const { spawnSync } = require("child_process");

const repoRoot = path.join(__dirname, "..", "..", "..", "..");

console.log("Running KB validator...");
const validator = path.join(__dirname, "validate-features.js");
const res = spawnSync("node", [validator], {
  cwd: repoRoot,
  encoding: "utf8",
});
process.stdout.write(res.stdout || "");
process.stderr.write(res.stderr || "");

if (res.status === 0) {
  console.log("Validator passed. No cleanup required.");
  process.exit(0);
}

console.log("Validator failed. Running cleanup task generator...");
const generator = path.join(__dirname, "generate-cleanup-tasks.js");
const gen = spawnSync("node", [generator], {
  cwd: repoRoot,
  encoding: "utf8",
});
process.stdout.write(gen.stdout || "");
process.stderr.write(gen.stderr || "");

console.log(
  "Wrote cleanup tasks to .github/skills/knowledge-base/cleanup-tasks.md",
);
process.exit(res.status || 1);
