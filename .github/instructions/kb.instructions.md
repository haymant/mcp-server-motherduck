---
description: Load when editing knowledge-base artifacts so frontmatter, phase state, and artifact linkage remain coherent.
applyTo: '(^|.*/)kb/.+\.md$'
---

KB rules:

- keep one feature folder per feature
- update existing feature artifacts in place for additive work
- preserve frontmatter consistency across requirements, design, implementation-plan, testing-plan, and testing-report
- keep acceptance criteria explicit and testable
- keep evidence in `testing-report.md`, not only in chat

Before closing a feature, verify:

- artifact set exists
- statuses are coherent
- related artifact links still make sense
- evidence maps to acceptance criteria
