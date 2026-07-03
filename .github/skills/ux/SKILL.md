---
name: "ux"
description: "Guidelines for UI developers and architects to keep frontend components, pages, and UX patterns consistent across Open Agents."
context: "Frontend / UI development (apps/web)"
argument-hint: "Reference when building settings pages and components"
compatibility: "Next.js"
user-invocable: false
metadata:
	agent: Developer
---

Purpose
-------
This `SKILL.md` documents the frontend stack conventions, component patterns, accessibility and testing guidance, and integration points developers should follow when adding UI features (for example, `/settings/providers`). It aims to keep UI behavior consistent and predictable for users.

Tech stack summary
------------------
- Framework: Next.js (app directory) under `apps/web`.
- Styling: global stylesheet at `apps/web/app/globals.css`; Tailwind utilities are used in parts of the app — prefer existing component utility classes when available.
- Data fetching: server routes and client hooks; use `useSWR` for client-side caching where existing patterns use it (see `apps/web/hooks/use-model-options.ts`).
- Components: colocate reusable components under `apps/web/components` and feature-specific UI under `apps/web/app/...`.

Component & hook conventions
---------------------------
- Small components: keep components focused (single responsibility). Extract logic to hooks in `apps/web/hooks` when state or data fetching is required.
- Naming: files and folders use kebab-case; React components and types use PascalCase.
- Data contracts: server routes should return small, typed payloads. Client hooks should map responses to UI-friendly shapes (see `useModelOptions`).
- Reuse existing building blocks: use settings shell and existing list/table components for new settings pages to maintain consistent UX.

Forms & Validation
------------------
- Use Zod for server-side validation when accepting structured input. Mirror validation client-side for UX but treat server as the source of truth.
- For sensitive fields (API keys), use masked inputs and never render the raw secret after save. Provide a rotate/edit flow instead of showing the key.

UX patterns
-----------
- Settings pages: follow the existing settings layout with sidebar navigation and per-user scope. Add a `Providers` sidebar entry at `apps/web/app/settings/providers/page.tsx`.
- Empty / loading states: always provide clear empty states with a call-to-action. For a fresh deployment with no providers, instruct the user to add a provider first.
- Collapsible provider groups: the chat model dropdown must collapse provider groups by default. Use an accessible disclosure pattern and preserve keyboard navigation and focus.
- Explanatory copy: include concise copy indicating that model lists are sourced via the AI SDK and naming the provider connection used for the group.

Accessibility
-------------
- Use semantic HTML and ARIA where needed (disclosure, listbox, dialogs). Verify with `axe` in CI or local dev.
- Ensure all interactive controls are keyboard accessible and have visible focus states.

Testing & E2E
-------------
- Unit tests: test pure functions, option builders, and small components with React Testing Library.
- Integration tests: test pages and data flows with the app test harness; exercise `GET/POST/DELETE/PATCH /api/settings/providers` routes in integration tests.
- E2E: use Playwright for the automated test cases described in `kb/features/ai-provider-management/testing-plan.md`.

Files & locations
-----------------
- New settings page: `apps/web/app/settings/providers/page.tsx`
- API routes: `apps/web/app/api/settings/providers/route.ts` and `apps/web/app/api/settings/providers/[id]/route.ts`
- Hooks: `apps/web/hooks/use-providers.ts` (new) and reuse `use-model-options.ts` integration.
- Components: `apps/web/components/providers/*` for provider list, form, discovery-status, and confirm-delete dialog.

Design-to-implementation checklist
---------------------------------
When implementing a UI feature, include the following in your feature PR:

1. Design doc or link to `kb/features/<feature>/design.md`.
2. `implementation-plan.md` listing schema changes, expected migration name, and backfill plan (if any).
3. Unit tests for new hooks and option builders.
4. Integration tests for new API routes and pages.
5. Playwright E2E tests for the acceptance criteria.

References
----------
- Existing model options hook: `apps/web/hooks/use-model-options.ts`
- Settings shell usage: `apps/web/app/settings/*`
- DB/migration conventions: `.github/skills/drizzle/SKILL.md`
