# Flaky test fixes playbook

Companion to `SKILL.md`. The procedure lives in `SKILL.md`; this page holds repeat commands per framework, the debugging table and a CI job for quarantined tests.

For TestMu AI cloud capabilities, see [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Repeat commands

| Framework | Command |
|-----------|---------|
| Playwright | `npx playwright test path/to/spec.ts --repeat-each=30 --workers=4` |
| Cypress | `npx cypress run --spec path/to/spec.cy.ts` in a shell loop, or `Cypress._.times(30, ...)` around the test |
| Jest | `for i in $(seq 1 30); do npx jest path/to/test || echo "FAIL $i"; done` |
| pytest | `pytest path/to/test.py --count=30` (pytest-repeat) |
| JUnit 5 | `@RepeatedTest(30)` on a copy of the test |
| TestNG | `@Test(invocationCount = 30)` |
| WebdriverIO | `npx wdio run wdio.conf.ts --spec path/to/spec.ts --repeat 30` |

Shuffle the order to expose shared state: `pytest -p randomly` (pytest-randomly) or `jest --randomize`.

## Debugging table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Fails more on slow runners, passes under a debugger | the test acts before the app is ready | wait for the element state, URL or response the step depends on |
| 2 | Click does nothing right after page load | handler not attached yet (hydration) | wait for the app's readiness signal, then click |
| 3 | Passes alone, fails in the suite | state left behind by another test | fresh context and unique data per test; reset server state |
| 4 | Fails in a different place when order changes | order dependence | each test sets up what it needs; run shuffled to prove it |
| 5 | Fails only with several workers | shared record, account or port | namespace by worker index; one account per worker |
| 6 | Fails around midnight or month end | real clock in the test | freeze time; pin timezone and locale |
| 7 | Fails after a slow third-party call | live external dependency | mock it at the network layer |
| 8 | Element found, then stale or detached | re-render between find and act | find again after the action; do not hold references |
| 9 | Click lands on the wrong thing | animation or layout shift in progress | disable animations in tests, or wait for the transition to end |
| 10 | Fails on one browser or viewport | environment-specific rendering | pin viewport and browser version; run the same image in CI and locally |
| 11 | Fails at roughly the backend error rate | a real intermittent product bug | reproduce outside the test with Kane CLI; fix the app |
| 12 | Fails only on the first run after deploy | cold cache or cold start | warm up in global setup, or wait on the health endpoint |

## Quarantine job

A quarantined test still runs. It stops blocking merges and keeps producing evidence.

```yaml
name: quarantine
on:
  schedule: [{ cron: "0 */6 * * *" }]
jobs:
  flaky:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --grep @quarantine --repeat-each=10 --reporter=json > quarantine.json
      - uses: actions/upload-artifact@v4
        with: { name: quarantine-results, path: quarantine.json }
```

Every quarantined test needs a linked issue with the measured failure rate, the evidence and an owner.
