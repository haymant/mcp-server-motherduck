---
name: code-verifier
description: Use when reconciling generated KB artifacts against actual code behavior, implementation details, routes, jobs, tests, and current repository structure.
---

# Code Verifier

Use this skill after KB reconstruction or after a major implementation wave.

## Goal

Confirm that the KB reflects the actual codebase closely enough to serve as the new source of truth.

## Checks

- feature artifact content matches entrypoints and code ownership
- design assumptions still match module boundaries and data flow
- implementation-plan steps are plausible given the real repository structure
- testing-plan coverage matches the real risk surface

## Output expectations

- confirmed findings
- mismatches
- uncertain areas needing human review
- recommended KB updates

Use this skill with `knowledge-base` and `impact-assessment` when modernization work is active.