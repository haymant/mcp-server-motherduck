---
name: "e2e-test"
description: "E2E testing conventions and scaffold using Playwright. Used by QA for automated acceptance tests and evidence collection."
context: "End-to-end testing (Playwright)"
argument-hint: "Run Playwright E2E tests and attach traces/screenshots to CI artifacts"
compatibility: "Playwright"
user-invocable: false
metadata:
  agent: QA
---

Summary
-------
This skill explains the repository's E2E conventions and provides a lightweight scaffold under `e2e/` for Playwright tests. It follows Playwright best practices: modularized POMs, fixtures, verifiers, and centralized test data with secure credential handling. Test evidence (screenshots, traces, videos) is kept in the `e2e/results/` folder and ignored by git via `e2e/.gitignore`.

Save canonical, machine-readable test evidence to the external test-results folder used by the harness: `e2e/results`. The runner `e2e/scripts/run-e2e-ss.js` writes timestamped Playwright output to `e2e/results/<timestamp>`, copies the `playwright-report` HTML bundle into `e2e/results/playwright-report-<timestamp>`, and writes `e2e/results/.last-run.json` for CI consumers.

Goals
-----
- Provide a consistent E2E layout: `e2e/tests`, `e2e/pom`, `e2e/fixtures`, `e2e/verifiers`, `e2e/helpers`.
- Store test data as JSON objects in `e2e/fixtures/*.json` and reference them from tests.
- Securely manage credentials using placeholders + `.env.local`.
- Keep evidence and artifacts out of git by using `e2e/.gitignore`.
- Give QA a small example test and helpers to expand for the feature testing plan.

Test Data & Credentials Management
----------------------------------
- Secrets are stored in **`.env.local`** (gitignored).
- All test data lives in committed **`e2e/fixtures/*.json`** files.
- Use placeholder syntax `$VARIABLE_NAME` for secrets.

**Example `.env.local`**
```bash
TEST_USER_EMAIL=test.user@example.com
TEST_USER_PASSWORD=SuperSecret123!
TEST_ADMIN_EMAIL=admin@example.com
```

**Example `e2e/fixtures/users.json`**
```json
{
  "regularUser": {
    "email": "$TEST_USER_EMAIL",
    "password": "$TEST_USER_PASSWORD",
    "name": "Test User"
  }
}
```

**Helper:** See `e2e/helpers/fixtureLoader.ts` for the canonical fixture-loading helper used by E2E tests (loads `e2e/fixtures/*`, substitutes `$VARNAME` from `.env.{VARIANT}`, and exposes `loadFixture()` / `getTestUser()`).

Auth E2E Testing (OAuth)
------------------------
Prefer **real OAuth** for critical auth paths. Use saved `storageState` for day-to-day tests.

**`e2e/tests/auth.setup.ts`**
```ts
import { test as setup } from '@playwright/test';
import { getTestUser } from '../helpers/fixtureLoader';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  const user = getTestUser('regularUser');

  await page.goto('/login');
  await page.getByRole('button', { name: /Sign in with IDP|Vercel|Google|GitHub/i }).click();

  await page.waitForURL(/vercel\.com|accounts\.google\.com|github\.com/, { timeout: 30_000 });

  // Provider login steps using real credentials from fixture
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  // ... continue with provider flow

  await page.waitForURL(/\/dashboard|\/home/, { timeout: 30_000 });
  await page.context().storageState({ path: authFile });
});
```

For an e2e test, login should be done once, and the session stored as `storageState` for reuse. This balances test reliability with the need to validate real auth flows periodically.

Configure in `playwright.config.ts` with `dependencies: ['setup']` and `storageState`.

Browser Selection
-----------------
- On Ubuntu 26.04 with Playwright 1.59.1, prefer the system Chrome binary instead of bundled Chromium.
- `e2e/playwright.config.ts` should apply the same browser configuration to both the auth `setup` project and the main test project so auth does not fall back to unsupported bundled Chromium.
- By default, local Linux runs should auto-detect common Chrome paths such as `/usr/bin/google-chrome`.
- If auto-detection is insufficient on a developer machine or CI host, set `PW_CHROME_EXECUTABLE` explicitly.

Usage
-----
- Preferred test command (from repo root):
```bash
PW_CHROME_EXECUTABLE=/usr/bin/google-chrome bunx playwright test e2e --config=e2e/playwright.config.ts
bun run e2e
PW_CHROME_EXECUTABLE=/usr/bin/google-chrome bun run e2e:ss
```

Notes
-----
- Always use dedicated test accounts for OAuth.
- Keep a few tests that run the full real OAuth flow; use saved storage state for others.
- Light mocking of OAuth is allowed only for non-critical high-volume tests.
- For Linux hosts where bundled Chromium is unavailable, validate the resolved browser path before blaming auth or Playwright setup.
- Follow Playwright best practices: idempotent tests, test fixtures, expressive POMs/verifiers.