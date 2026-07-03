---
description: Load when editing or reviewing custom Copilot agent definitions for this SDLC starter.
applyTo: '(^|.*/)\.github/agents/.*\.agent\.md$'
---

Agent files in this project should follow VS Code Copilot discovery expectations:

- use flat `.agent.md` files directly under `.github/agents/`
- keep `name`, `description`, and `argument-hint` in frontmatter
- make descriptions discovery-friendly by including trigger phrases such as requirements, design, coding, testing, release, migration, or orchestration

Role rules:

- BA owns requirements quality.
- Architect owns design quality.
- Developer owns implementation and test updates.
- QA owns proof and residual risk.
- DevOps owns deployment, migration, and release operations.
- Orchestrator owns routing and gate discipline.
