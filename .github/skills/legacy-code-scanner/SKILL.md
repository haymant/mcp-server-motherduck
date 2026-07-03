---
name: legacy-code-scanner
description: Use when reverse engineering a legacy codebase into KB artifacts by scanning Node Next.js Python routes jobs modules comments constants entrypoints and current system behavior.
---

# Legacy Code Scanner

Use this skill at the start of modernization when the code exists but the KB does not.

## Goal

Infer candidate features, responsibilities, and current system behavior from a legacy codebase without pretending uncertain behavior is proven.

## Workflow

1. Build a surface inventory of the target directory.
2. Identify entrypoints, routes, jobs, and user-visible workflows.
3. Separate Next.js and Python concerns.
4. Extract candidate requirements, constraints, and data flows.
5. Produce draft KB artifact suggestions, starting with `requirements.md`.

## Deterministic helpers

Run one or both of these before drafting findings:

```bash
python3 scripts/legacy_inventory.py <target-dir>
node scripts/hybrid_surface_map.mjs <target-dir>
```

## Output expectations

- inferred feature name
- likely owner surfaces
- candidate user workflows
- observed integrations
- open questions that require human confirmation

## Safety rule

Do not modify legacy source code as part of scanning. This skill is for discovery and KB reconstruction.