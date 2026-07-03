---
name: knowledge-base
description: Use when working with the project knowledge base, feature folders, requirements.md, design.md, implementation-plan.md, testing-plan.md, testing-report.md, or KB frontmatter validation.
---

# Knowledge Base

Use this skill whenever the task depends on the state of a feature or when a result should be written back to the KB.

## Responsibilities

- locate the correct feature folder
- check that required artifacts exist
- verify frontmatter fields and status coherence
- update the KB when the task changes canonical project state

## Required artifact set

- `requirements.md`
- `design.md`
- `implementation-plan.md`
- `testing-plan.md`
- `testing-report.md`

## Deterministic check

When validating KB structure, run:

```bash
node .github/skills/knowledge-base/scripts/validate-and-generate.js
```

Use the script output to identify missing artifacts, missing frontmatter keys, broken related artifact references, and the split between documented features and incomplete placeholder entries.

## KB Update Procedure (automation guidance)

When an agent discovers that repository evidence (code, tests, CI output) differs from the canonical KB, follow this deterministic update procedure:

1. Capture evidence: record file paths, snippets, and a short rationale for the change.
2. Draft patch: create or modify the minimal KB artifact (requirements/design/implementation) with updated frontmatter (`last_updated`, `change_log`) and a short explanatory note.
3. Validate: run `python3 scripts/validate_kb.py kb/features/<feature-slug>` and resolve validator issues until the patch passes.
4. Publish: if change is non-policy and validator-passing, apply the patch to the KB; if the change affects security/sandboxing/policy, mark `status: review-required` and create a PR for Architect review.
5. Record trace: append the evidence and validator output to the feature's `testing-report.md` or `change_log` so the decision trail is auditable.

Agents using this skill should prefer small, well-formed KB updates that keep documentation truthful. For policy-sensitive changes, require explicit Architect sign-off before promotion to `status: stable`.

## Consistency rule & local validator

- Every feature folder under `kb/features/` should contain a `requirements.md` with frontmatter keys: `feature_id`, `artifact`, `owner_agent`, `status`, and `last_updated`.
- Run the included validator from this skill folder before publishing KB changes:


```bash
# Preferred (single-step): run the validator and automatically generate cleanup tasks if validation fails
node .github/skills/knowledge-base/scripts/validate-and-generate.js

# Or run the validator directly (manual flow):
node .github/skills/knowledge-base/scripts/validate-features.js
```

If the validator detects missing artifacts or malformed frontmatter, the wrapper `validate-and-generate.js` will invoke the cleanup generator and write `.github/skills/knowledge-base/cleanup-tasks.md` with four explicit outputs:

- documented feature folders that currently count as the implemented or documented side of the KB inventory
- incomplete feature folders that should stay separate until reconstructed
- raw validator errors and warnings
- BA, Architect, and Developer next actions for cleanup

The validator performs a best-effort check that each folder has the required `requirements.md` frontmatter and flags features not mentioned in `kb/features/feature-index.md`.
