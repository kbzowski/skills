---
name: fix-playwright
description: >
  Run and fix all Playwright E2E test failures and flaky tests, then verify stability with 3 consecutive green runs.
  Use when the user asks to: fix e2e tests, fix failing tests, fix flaky tests, stabilize the test suite,
  or debug Playwright test failures.
---

# Fix Playwright Tests

Run all E2E tests, fix every failure and flaky test, confirm stability with 3 consecutive green runs.

## When to Use

- All or some Playwright tests are failing
- Tests pass sometimes but fail intermittently (flaky)
- Test suite needs stabilization after code changes

## When NOT to Use

- Writing new tests from scratch — this skill fixes existing failures
- Unit or integration test failures — this is Playwright-specific
- Performance or visual regression testing

## Before Starting

- Read the project's test helpers, fixtures, and setup files to understand existing patterns.
- Check `package.json` scripts for the E2E test command (e.g., `test:e2e`, `e2e`). If none found, fall back to `npx playwright test`.
- Do NOT commit unless the user explicitly asks.

## Phase 1: Diagnostic Run

Run the project's E2E test command:

```
<e2e-command from package.json>
```

- All pass → skip to Phase 3.
- Failures → Phase 2.

## Phase 2: Fix Loop

For each failing test — read error, stack trace, test code, and application code. Classify and fix:

- **App bug** → fix source code, not the test.
- **Test bug** → fix selector, missing await, race condition, etc.
- **Flaky** → find root cause (timing, shared state, animation, network) and fix.
- **Setup issue** → fix test setup/fixtures.

### Rules

- NEVER `test.skip` or delete tests.
- NEVER remove or weaken assertions.
- Use web-first assertions: `expect(locator).toBeVisible()`, `expect.poll()`, `toPass()` — NOT `waitForTimeout()` or arbitrary sleeps.
- Use stable locators: `getByRole()`, `getByTestId()`, `getByLabel()` — NOT fragile CSS selectors.
- Ensure test isolation: generate unique data per test run, clean up after tests. Follow AAA pattern (Arrange/Act/Assert).
- Follow the project's existing fixture and helper patterns for consistency.

Re-run after fixes. Still failing → repeat Phase 2. All pass → Phase 3.

Max 10 fix-loop iterations. If tests still fail after 10 → report remaining failures to the user with diagnosis and ask how to proceed.

## Phase 3: Stability Verification (3x pass)

Run the E2E test command 3 times consecutively with `--retries 0` to disable Playwright's built-in retries (which can mask flakiness):

- Any failure → flaky test. Return to Phase 2, then restart verification from scratch (3 runs from beginning).
- Max 5 verification cycles. Still flaky after 5 → report to user with details.

## Phase 4: Report

Use this exact format:

```
## Results
All tests pass (3/3 runs).

## Fixed Issues
| Test | Problem | Fix |
|------|---------|-----|
| `file.spec.ts` > test name | what was wrong | what changed |

## Changed Files
- `path/to/file.ts` — brief change description
```
