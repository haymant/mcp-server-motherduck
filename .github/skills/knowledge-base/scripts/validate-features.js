#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function readFile(file) {
  try {
    return fs.readFileSync(file, "utf8");
  } catch (e) {
    return null;
  }
}

function parseFrontmatter(content) {
  if (!content) return {};
  const m = content.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return {};
  const body = m[1];
  const lines = body.split(/\r?\n/);
  const out = {};
  for (const line of lines) {
    const parts = line.split(":");
    if (parts.length < 2) continue;
    const key = parts[0].trim();
    const val = parts.slice(1).join(":").trim().replace(/^"|"$/g, "");
    out[key] = val;
  }
  return out;
}

function isDirectory(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch (e) {
    return false;
  }
}

function main() {
  const repoRoot = path.join(__dirname, "..", "..", "..", "..");
  const featuresDir = path.join(repoRoot, "kb", "features");
  const featureIndex = path.join(featuresDir, "feature-index.md");

  const errors = [];
  const warnings = [];

  if (!isDirectory(featuresDir)) {
    console.error("kb/features directory not found");
    process.exit(2);
  }

  const entries = fs.readdirSync(featuresDir).filter((e) => {
    const p = path.join(featuresDir, e);
    const req = path.join(p, "requirements.md");
    return isDirectory(p) && fs.existsSync(req);
  });

  const seenIds = new Set();

  for (const dir of entries) {
    const reqPath = path.join(featuresDir, dir, "requirements.md");
    const rel = path.relative(repoRoot, reqPath);
    const content = readFile(reqPath);
    if (!content) {
      errors.push(`Missing requirements.md in ${dir} (${rel})`);
      continue;
    }

    const fm = parseFrontmatter(content);
    const needed = [
      "feature_id",
      "artifact",
      "owner_agent",
      "status",
      "last_updated",
    ];
    for (const k of needed) {
      if (!fm[k]) {
        errors.push(`${dir}/requirements.md missing frontmatter key: ${k}`);
      }
    }

    if (fm.feature_id) {
      // If the declared feature_id doesn't match the folder name, attempt to auto-fix it
      if (fm.feature_id !== dir) {
        if (seenIds.has(dir)) {
          errors.push(
            `Cannot rename feature_id of ${dir} to ${dir}: target id already used by another feature`,
          );
        } else {
          // Attempt to rewrite the frontmatter to set feature_id to the folder name
          const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
          if (fmMatch) {
            const fmBlock = fmMatch[1];
            let newFmBlock;
            if (/^\s*feature_id:/m.test(fmBlock)) {
              newFmBlock = fmBlock.replace(/(^feature_id:\s*).*/m, `$1${dir}`);
            } else {
              newFmBlock = `feature_id: ${dir}\n` + fmBlock;
            }
            const newContent = content.replace(
              fmMatch[0],
              `---\n${newFmBlock}\n---`,
            );
            try {
              fs.writeFileSync(reqPath, newContent, "utf8");
              console.log(`Updated feature_id in ${reqPath} to ${dir}`);
              fm.feature_id = dir;
            } catch (e) {
              errors.push(
                `Failed to write updated frontmatter for ${dir}: ${e.message}`,
              );
            }
          } else {
            errors.push(`Malformed frontmatter in ${dir}/requirements.md`);
          }
        }
      }

      if (seenIds.has(fm.feature_id)) {
        errors.push(`Duplicate feature_id ${fm.feature_id} in ${dir}`);
      }
      seenIds.add(fm.feature_id);
    }
  }

  // Check feature-index references (best-effort): ensure folder names or feature_ids appear
  const indexText = readFile(featureIndex) || "";
  for (const dir of entries) {
    const reqPath = path.join(featuresDir, dir, "requirements.md");
    const content = readFile(reqPath) || "";
    const fm = parseFrontmatter(content);
    const featureId = fm.feature_id || "";
    if (
      indexText.indexOf(dir) === -1 &&
      featureId &&
      indexText.indexOf(featureId) === -1
    ) {
      warnings.push(
        `Feature '${dir}' not referenced in feature-index.md (folder name or feature_id not found)`,
      );
    }
  }

  if (errors.length) {
    console.error("\nKB validation errors:");
    for (const e of errors) console.error("- " + e);
    process.exit(1);
  }

  if (warnings.length) {
    console.warn("\nKB validation warnings:");
    for (const w of warnings) console.warn("- " + w);
  }

  console.log("\nKB validation: OK");
}

main();
