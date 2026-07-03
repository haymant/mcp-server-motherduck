---
description: Load when working in this starter pack to enforce the KB-first SDLC, role routing, and artifact discipline.
applyTo: "(^|.*/)\.github/.*|(^|.*/)kb/.*|(^|.*/)scripts/.*"
---

This starter pack is built for a KB-first SDLC in VS Code Copilot.

Always assume:

- the KB is the canonical source of feature state
- agents are specialized by role
- requirements, design, implementation, testing, and release should be represented by explicit artifacts
- modernization of legacy code should first reconstruct the KB before major refactors proceed

Stack default:

- Next.js and TypeScript for web and route surfaces
- Python for ETL, workers, analytics, and service-side jobs
- explicit contracts between the two layers

Route work in this order unless a later phase is already validated:

- BA
- Architect
- Developer
- QA
- DevOps when operational work is involved

Phase transitions should be based on artifact quality, not momentum or convenience.
