---
name: production-readiness
description: Use when deciding whether a feature is ready for release, rollout, migration, rollback, operational support, observability, environment changes, or hybrid Next.js and Python deployment readiness.
---

# Production Readiness

Use this skill as the final SDLC gate before release or handoff.

Check:

- reliability and timeout behavior
- security and secret handling
- observability and actionable logs
- performance or scale assumptions
- deployment procedure and rollback plan
- migration or backfill notes
- runtime assumptions for both Node and Python surfaces
- environment consistency between web, API, worker, ETL, and scheduled job processes

## Deterministic check

Run:

```bash
node scripts/release_gate.mjs kb/features/<feature-slug>
```

Use the output to identify missing approvals, absent evidence, or incomplete readiness notes.
