---
name: kb-bootstrapper
description: Use when creating or filling requirements design implementation-plan testing-plan and testing-report artifacts from legacy code analysis or sparse project knowledge.
---

# KB Bootstrapper

Use this skill after legacy scanning or when a feature folder exists only partially.

## Goal

Create a coherent feature artifact set that the SDLC agents can use as the new source of truth.

## Workflow

1. Create any missing feature artifacts from the templates.
2. Populate frontmatter with legacy-oriented initial values.
3. Put uncertain findings into open questions rather than presenting them as settled facts.
4. Add a change log entry noting that the artifact was bootstrapped from existing code.
5. Hand the feature to BA or Architect for review depending on artifact maturity.

## Frontmatter convention for legacy bootstrap

- `version: 1.0-legacy`
- `status: draft`
- add a change log entry such as `Bootstrapped from legacy code on 2026-03-29`

## Validation

After bootstrapping, run:

```bash
python3 scripts/validate_kb.py kb/features/<feature-slug>
```