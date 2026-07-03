---
name: kb-update
description: Guidance and automation pattern for agents to propose and apply small KB updates when repository evidence diverges from KB artifacts.
---

# KB Update Skill

This skill describes a deterministic, auditable pattern agents should use when they detect that live repository evidence (code, tests, CI output) diverges from KB documentation.

When to use

- BA or Architect agents discover mismatches between KB artifacts and repository/state evidence.
- Automated scans or validators detect stale or incorrect KB frontmatter/related-artifact references.

Procedure

1. Capture evidence: include file paths, snippets, test output, and a short rationale.
2. Draft patch: create the minimal KB artifact change (frontmatter + short explanatory text). Include `last_updated` and a `change_log` entry.
3. Validate: run `python3 scripts/validate_kb.py kb/features/<feature-slug>` and resolve errors.
4. Publish: apply the patch directly for non-policy edits, or open a PR and set `status: review-required` for policy/security-sensitive changes.
5. Trace: append validator output and evidence to the feature's `testing-report.md` or a `change_log` entry for auditability.

Human-in-the-loop

- For changes that impact security, sandboxing, or runtime execution policies, require Architect sign-off before moving `status` to `stable`.

Tooling

- Agents should run the KB validator after drafting patches and include its output with any PR or direct update.
- Prefer small, incremental changes; avoid large rewrites without explicit human review.
