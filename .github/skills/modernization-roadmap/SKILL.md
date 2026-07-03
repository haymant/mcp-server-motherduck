---
name: modernization-roadmap
description: Use when planning a phased modernization of a legacy hybrid Next.js and Python system including reconstruction, stabilization, refactor sequencing, strangler migration, and risk-managed delivery.
---

# Modernization Roadmap

Use this skill when the team wants a delivery-safe path from a legacy system to a cleaner target architecture.

## Goals

- preserve behavior while improving structure
- avoid rewriting without a reconstructed KB
- sequence work into small, reviewable increments

## Phases

1. reconstruct the KB from legacy code
2. stabilize the current behavior with tests and observability
3. isolate boundaries between Next.js and Python surfaces
4. refactor or replace one slice at a time
5. prove parity before removing old paths

## Output expectations

- current-state summary
- target-state summary
- migration slices
- risks and rollback notes
- recommended first increment