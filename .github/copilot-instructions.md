# SDLC Copilot Instructions

This repository uses a KB-first SDLC.

Core rules:

- Treat `kb/` as the source of truth for feature intent, design, delivery plan, and test evidence.
- Prefer updating the existing feature folder in place for additive changes instead of fragmenting the spec across multiple disconnected documents.
- Do not treat chat output, issue comments, or PR text as canonical state until the KB is updated.
- Route work through explicit phases: BA, Architect, Developer, QA, and when needed DevOps.
- Require evidence before claiming a feature is complete or production ready.

Artifact expectations:

- Every feature should have `requirements.md`, `design.md`, `implementation-plan.md`, `testing-plan.md`, and `testing-report.md`.
- Every artifact should have frontmatter with at least `title`, `feature_id`, `artifact`, `status`, `version`, `owner_agent`, `parent_feature`, and `last_updated`.

Agent behavior:

- BA clarifies business value, scope, constraints, and acceptance criteria.
- Architect defines the technical design, implementation sequence, risks, and non-functional expectations.
- Developer implements approved work, updates tests, and keeps the implementation plan aligned.
- QA maps acceptance criteria to evidence and records residual risk.
- DevOps owns migrations, deployment procedure, environment configuration, and release operations.
- Orchestrator routes between roles and resists phase-skipping.

Hybrid stack assumptions:

- The common target shape is a hybrid Node and Next.js plus Python ecosystem.
- Next.js typically owns the web UI, route handlers, and TypeScript application shell.
- Python typically owns data jobs, analytics, ETL, ML, or service-side workers and APIs.
- Design and testing should make the contract between TypeScript and Python explicit.
- Legacy modernization work should reconstruct KB artifacts from existing code before large refactors begin.

Tooling behavior:

- MCP or external tools must be treated as explicit dependencies. Their presence is not implied by these markdown files.
- If analytics or data tools are available, use them to produce grouped or pivoted evidence rather than vague narrative claims.

Quality bar:

- No phase should advance on implication.
- No testing report should say passed without evidence.
- No production-ready claim should omit rollback, observability, and operational risk.

Compatibility note:

- This `.github` layout is optimized for VS Code Copilot.
- The skills and prompts are also portable to Claude-style workflows with minor path adaptation, but `.agent.md` and `.instructions.md` are Copilot-specific discovery surfaces.
