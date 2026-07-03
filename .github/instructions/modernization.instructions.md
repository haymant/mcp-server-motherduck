---
description: Load when reverse engineering legacy code, reconstructing KB artifacts, or planning phased modernization in a hybrid Next.js and Python system.
applyTo: '(^|.*/)kb/.+\.md$|(^|.*/)(\.github|scripts)/.+|(^|.*/)(app|pages|src|services|workers|jobs|etl|api)/.*'
---

Modernization rules:

- reconstruct the KB before major rewrites
- distinguish current-state facts from target-state proposals
- do not infer product intent from implementation detail without marking it as provisional
- preserve delivery safety by planning migration in slices
- make Next.js to Python boundaries explicit in design and testing

When handling legacy code:

- identify entrypoints, routes, jobs, and integrations first
- write draft requirements as draft requirements, not approved truth
- put uncertainty into open questions and risk notes
- keep the modernization roadmap separate from the current-state design summary