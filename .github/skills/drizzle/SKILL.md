---
name: "drizzle"
description: "Guidance and conventions for using Drizzle ORM and Drizzle Kit migrations in this repository."
context: "Database schema and migrations (apps/web)"
argument-hint: "Run migration generation after changing apps/web/lib/db/schema.ts"
compatibility: "Drizzle ORM, Drizzle Kit"
user-invocable: false
metadata:
  agent: Developer
---

Summary
-------
This document captures the conventions this repo uses for relational schema design, migrations, and testing with Drizzle (Drizzle ORM + Drizzle Kit). It is intended as the canonical reference for future `design.md`/`implementation-plan.md` work that touches the database layer.

Where the schema lives
----------------------
- Primary schema file: `apps/web/lib/db/schema.ts`.
  - Exported `pgTable(...)` declarations model the Postgres schema and are the single source of truth for migrations.

Migration workflow (required)
----------------------------
- After any change to `apps/web/lib/db/schema.ts`, generate a SQL migration using Drizzle Kit from the `apps/web` package root:

```bash
bun run --cwd apps/web db:generate "describe-your-change"
```

- This command creates a new `.sql` migration file (Drizzle Kit output). Commit the generated `.sql` file alongside your `schema.ts` change. Do NOT use `db:push` — always generate and commit explicit SQL migrations.
- Migrations are applied automatically in CI and during the app build process (see `apps/web/lib/db/migrate.ts`). Local dev can rely on `bun run web` or the repository's documented build path to run migrations, or you can run the migrate helper directly if necessary.

Applying & rolling back
-----------------------
- Apply migrations: the CI/build step runs migrations automatically. For local troubleshooting you can run the migration helper used by the app; consult `apps/web/package.json` scripts for convenience aliases (e.g., `bun run --cwd apps/web <script>`).
- Rollback strategy: prefer creating an explicit reversal migration (an SQL file that undoes the schema change) and commit it as the next migration. Avoid manual `db:push` or destructive direct DB edits in ephemeral environments.

Secrets and encryption
----------------------
- Token/secret handling: do not store plaintext secrets in non-encrypted columns.
- For provider API keys and other sensitive material, follow app conventions: encrypt before persisting (use app secret like `BETTER_AUTH_SECRET` where appropriate) and never return raw token values in API responses or logs.

Repository conventions and code patterns
-------------------------------------
- Keep schema changes minimal and focused: one logical change per migration (e.g., "add provider table", "add discovery snapshot column").
- Prefer table-based storage for features that require indexing, joins, or secrets (e.g., provider configs) rather than bloating a JSON `user_preferences` blob.
- Use typed Drizzle helpers rather than raw SQL where the ORM offers a clear type-safety benefit; prefer raw SQL only when needed for complex migrations or performance-critical operations.

Testing strategy
----------------
- Unit tests:
  - Test migration helper utilities (normalization, validation) in isolation.
  - Test DB-adjacent helpers using an in-memory or test DB with an isolated schema per test run.
- Integration tests:
  - Route and API tests that exercise provider CRUD should run against the test database with migrations applied prior to the test run.
  - Use deterministic provider IDs and deterministic fixtures for tests that assert persisted IDs and selection behavior.
- E2E (Playwright) tests:
  - Seed the test DB with fixture provider rows using the same migration-applied schema.
  - Use test-mode encryption keys or mocks for secret handling so tests can assert persistence shape without accessing real secrets.

CI and quality gates
--------------------
- After modifying `schema.ts`, CI must verify a migration was generated and committed. Implement a CI check (or use the existing `bun run ci`) that runs `db:generate` and fails if there are uncommitted migrations expected by the schema.
- Tests that touch the DB must run after migrations are applied in CI.

Operational notes
-----------------
- Neon / preview DB branching: when running preview deployments, rely on Neon branch isolation if configured in the project (the repo uses Neon branching in Vercel previews by default). This ensures preview deploys get isolated DB state.
- Migrations are part of the deploy path and must be reviewed in PRs. Always include the generated SQL in the PR so reviewers can verify schema intent.

References
----------
- Primary schema: `apps/web/lib/db/schema.ts`
- Migration generation: `bun run --cwd apps/web db:generate "<name>"`
- Migration application helper: `apps/web/lib/db/migrate.ts`
- Project DB guidance: `AGENTS.md` and `docs/*` (search for `Schema lives in apps/web/lib/db/schema.ts`).

Troubleshooting
---------------
- If migrations fail in CI or locally, inspect the generated SQL in the migration file and confirm the `POSTGRES_URL` used by the runner points to an isolated test DB.
- If you see schema drift between environments, ensure the correct migrations are present and applied; do not manually patch production schema without a migration review and an explicit migration file.

What to do next
----------------
- When planning features that require DB changes (design → implement), add a short migration checklist to the feature `implementation-plan.md` that includes:
  - the `schema.ts` diff summary
  - the expected generated migration name
  - data migration considerations (backfill plan, windowed rollout)
  - rollback plan (reverse migration)
