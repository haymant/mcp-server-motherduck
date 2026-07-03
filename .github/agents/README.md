# Agent Folder Guide

This folder contains the role agents used by the SDLC starter. The flat `.agent.md` files here are the discovery surface for VS Code Copilot.

## What This Folder Is For

- Humans use it to understand which agent owns which phase.
- Agents can use it as a compact index of role boundaries and handoff expectations.
- Orchestrator should route work across these roles instead of collapsing all phases into one response.

## Agent Index

- `Guide.agent.md`: helps business users and developers find the right docs, learning path, and next agent.
- `Orchestrator.agent.md`: coordinates phases, checks gates, routes work, and blocks phase-skipping.
- `BA.agent.md`: defines business value, scope, constraints, and acceptance criteria.
- `Architect.agent.md`: owns technical design, interfaces, sequencing, and risk analysis.
- `Developer.agent.md`: implements approved work and updates tests.
- `QA.agent.md`: produces test planning, evidence, defects, and residual risk statements.
- `DevOps.agent.md`: handles deployment, migration, runtime configuration, rollback, and release readiness.

## Entry Guidance By User Type

- Business users should start with `Guide.agent.md` for a plain-language system walkthrough or with Orchestrator when the request spans discovery, requirements, and delivery state.
- Developers should start with `Guide.agent.md` for workspace orientation, then move to Orchestrator or the phase-specific role agent once the task is scoped.
- Everyone should treat `kb/` as canonical and the subrepo README for the code surface they are editing as the local operating guide.

## Human Coordination Rules

Use Orchestrator first when the next role is unclear.

Route by phase:

1. BA for requirements.
2. Architect for design.
3. Developer for implementation.
4. QA for proof.
5. DevOps for release or migration.

Do not claim a phase is complete until the KB has been updated in `kb/features/<feature-slug>/`.

## Related Surfaces

- `.github/copilot-instructions.md` contains the standing SDLC rules.
- `.github/instructions/` contains scoped editing guidance.
- `.github/skills/` contains reusable methods used inside the phases.
- `.github/prompts/` contains stage and legacy workflow entry points.
- `../../kb/TEAM-HANDBOOK.md` is the human onboarding guide.
