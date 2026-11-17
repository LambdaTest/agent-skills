# Playwright patterns playbook

Companion to `SKILL.md`. The rules live in `SKILL.md`; this page holds the debugging table and the CI setup.

For TestMu AI cloud capabilities and devices, see [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md). To scaffold a project or connect to the cloud grid, use `playwright-skill`.

## Debugging table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `strict mode violation: locator resolved to 2 elements` | the locator is ambiguous | scope it to a parent locator or add `filter({ hasText })`; do not add `.first()` |
| 2 | `Timeout 30000ms exceeded` waiting for a locator | wrong locator, element inside an iframe, or the app never rendered it | open the trace, check the DOM snapshot at the failing step; use `frameLocator()` for iframes |
| 3 | `Element is not attached to the DOM` | a stored `ElementHandle` went stale after a re-render | use `Locator` objects, which re-resolve on every action |
| 4 | `<div> intercepts pointer events` | an overlay, toast or sticky header covers the target | wait for the overlay to be hidden, or close it; do not use `force: true` |
| 5 | Passes locally, fails in CI | slower runner, different viewport or base URL | pin `viewport` and `baseURL`, turn on `trace: 'on-first-retry'`, compare traces |
| 6 | Passes alone, fails in the full suite | state shared between tests | fresh context per test, unique data per test, no shared `page` |
| 7 | Fails only with several workers | two tests edit the same record | namespace data with `testInfo.workerIndex`, or one account per worker |
| 8 | `page.goto` times out | the page never fires `load` because of long polling or a stuck resource | `goto(url, { waitUntil: 'domcontentloaded' })`, then assert on the element that proves readiness |
| 9 | Redirected to login mid-suite | the saved `storageState` expired | regenerate it in the setup project on every run; do not commit it |
| 10 | Route mock has no effect | `page.route()` was registered after `page.goto()` | register routes before navigation |
| 11 | `toHaveText` fails on spacing or dynamic values | exact match against unstable text | use a regular expression or `toContainText` for the stable part |
| 12 | Screenshot assertions flicker | animations, caret blink, web fonts loading | `animations: 'disabled'`, mask dynamic regions, wait for `document.fonts.ready` |

## Reading a trace

1. `npx playwright show-trace trace.zip`
2. Go to the failing action and look at the before and after snapshots.
3. Check the network tab for a failed or slow request just before it.
4. Check the console tab for an application error.

## CI: GitHub Actions

```yaml
name: e2e
on: [pull_request]
jobs:
  playwright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
      - name: Verify the main flow with Kane CLI
        run: |
          npm install -g @testmuai/kane-cli
          kane-cli login --username "${{ secrets.LT_USERNAME }}" --access-key "${{ secrets.LT_ACCESS_KEY }}"
          kane-cli run "Go to ${{ vars.PREVIEW_URL }} and assert the home page heading is visible" --agent --headless --timeout 120
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: playwright-report, path: playwright-report/ }
```
