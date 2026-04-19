# Test Framework Migration Skill — Add Missing Playbook

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the missing `reference/playbook.md` to `test-framework-migration-skill` — the only validation warning in the repo.

**Architecture:** The playbook consolidates migration guidance into a single reference doc following the same structure as other skills (e.g., `selenium-skill/reference/playbook.md`). It covers project setup, decision framework, migration workflow, debugging table (10+ entries), and best practices checklist (14+ items). Content synthesizes what already exists in the 10 pair-specific reference files + `overview.md` into a unified playbook.

**Tech Stack:** Markdown

---

### Task 1: Create `reference/playbook.md` with complete content

**Files:**
- Create: `test-framework-migration-skill/reference/playbook.md`

- [ ] **Step 1: Create the playbook file**

Write the file at `test-framework-migration-skill/reference/playbook.md` with the following complete content:

```markdown
# Test Framework Migration — Complete Playbook

## §1 — Migration Decision Framework

### When to Migrate

| From → To | Migrate when... | Stay when... |
|-----------|-----------------|-------------|
| Selenium → Playwright | Flaky waits, need API mocking, want trace debugging, single JS/TS codebase | Existing Grid infrastructure, multi-language teams (Java/C#/Ruby), deep enterprise tooling |
| Selenium → Puppeteer | Chrome-only use case, scraping/PDF generation, lighter weight needed | Need cross-browser, need test-level assertions, need non-Chrome |
| Playwright → Selenium | Need Java/Python/C#/Ruby, existing Selenium Grid, enterprise compliance | Already stable in Playwright, no multi-language requirement |
| Puppeteer → Playwright | Need Firefox/WebKit, stronger assertions, trace/video, multi-browser CI | Chrome-only is fine, minimal test assertions needed |
| Cypress → Playwright | Need multi-tab, non-Chromium browsers, standard Node.js CI, parallel without paid cloud | Team prefers Cypress DX, component testing in Cypress, Cypress Dashboard investment |
| Playwright → Cypress | Team Cypress preference, Cypress component testing needed, existing Cypress cloud | Need multi-tab, non-Chromium, or API mocking at network level |
| Selenium → Cypress | Want dev-friendly DX, built-in retry-ability, time-travel debugging | Need multi-language, multi-tab, or existing Grid |
| Cypress → Selenium | Need Java/Python/C#/Ruby, Selenium Grid, enterprise tooling | JS/TS codebase, no Grid requirement |

### Language Matrix

| Framework | Java | Python | JS | TS | C# | Ruby | PHP |
|-----------|------|--------|-----|-----|-----|------|-----|
| Selenium | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Playwright | Yes | Yes | Yes | Yes | Yes | — | — |
| Puppeteer | — | — | Yes | Yes | — | — | — |
| Cypress | — | — | Yes | Yes | — | — | — |

**Key implication:** Migrating from Selenium (Java/C#) to Playwright/Puppeteer/Cypress usually means rewriting to JS/TS. Mention this to the user upfront.

## §2 — Migration Workflow

### Step-by-Step Process

1. **Audit existing tests** — Count tests, identify patterns (POM, utilities, custom waits), list external dependencies (Grid, reporters, CI).
2. **Choose target language** — Use the language matrix above. Default: keep same language if supported, otherwise JS/TS.
3. **Set up target project** — Install target framework, configure test runner, set up project structure. See the target framework's skill for setup details.
4. **Migrate infrastructure first** — Convert setup/teardown, driver/browser initialization, config files. This is the foundation.
5. **Convert page objects / utilities** — Translate reusable abstractions before tests. Tests depend on these.
6. **Migrate tests in batches** — Start with the simplest tests, build confidence, then tackle complex ones. Use the pair-specific reference files for API mappings.
7. **Run migrated tests locally** — Verify each batch passes before moving on.
8. **Update CI/CD** — Swap runner commands, update reporters, adjust parallel config.
9. **Cloud migration** — If using TestMu AI / LambdaTest, update capabilities and connection. See target framework's `reference/cloud-integration.md`.
10. **Decommission old framework** — Remove old dependencies, delete old tests only after new tests are stable.

### Pair-Specific Reference Files

For detailed API mappings (locators, waits, actions, assertions, lifecycle), always read the pair-specific file:

| Migration | Reference |
|-----------|-----------|
| Selenium → Playwright | [selenium-to-playwright.md](selenium-to-playwright.md) |
| Playwright → Selenium | [playwright-to-selenium.md](playwright-to-selenium.md) |
| Selenium → Puppeteer | [selenium-to-puppeteer.md](selenium-to-puppeteer.md) |
| Puppeteer → Selenium | [puppeteer-to-selenium.md](puppeteer-to-selenium.md) |
| Puppeteer → Playwright | [puppeteer-to-playwright.md](puppeteer-to-playwright.md) |
| Playwright → Puppeteer | [playwright-to-puppeteer.md](playwright-to-puppeteer.md) |
| Cypress → Playwright | [cypress-to-playwright.md](cypress-to-playwright.md) |
| Playwright → Cypress | [playwright-to-cypress.md](playwright-to-cypress.md) |
| Selenium → Cypress | [selenium-to-cypress.md](selenium-to-cypress.md) |
| Cypress → Selenium | [cypress-to-selenium.md](cypress-to-selenium.md) |

## §3 — Common Migration Patterns

### Locator Strategy Conversion

| Source Pattern | Playwright | Puppeteer | Cypress | Selenium |
|---------------|------------|-----------|---------|----------|
| By ID | `page.locator('#id')` | `page.$('#id')` | `cy.get('#id')` | `By.id('id')` |
| By CSS | `page.locator('.cls')` | `page.$('.cls')` | `cy.get('.cls')` | `By.cssSelector('.cls')` |
| By XPath | `page.locator('xpath=//btn')` | `page.$x('//btn')` | N/A (use CSS) | `By.xpath('//btn')` |
| By Text | `page.getByText('Submit')` | N/A (use XPath) | `cy.contains('Submit')` | `By.xpath("//*[text()='Submit']")` |
| By Role | `page.getByRole('button', {name: 'Submit'})` | N/A | N/A | N/A |
| By Test ID | `page.getByTestId('submit-btn')` | `page.$('[data-testid="submit-btn"]')` | `cy.get('[data-testid="submit-btn"]')` | `By.cssSelector('[data-testid="submit-btn"]')` |

### Wait Strategy Conversion

| Source Pattern | Playwright | Puppeteer | Cypress | Selenium |
|---------------|------------|-----------|---------|----------|
| Wait for element visible | Auto-wait on actions | `page.waitForSelector('#el', {visible: true})` | Built-in retry | `WebDriverWait` + `visibilityOfElementLocated` |
| Wait for navigation | `page.waitForURL()` | `page.waitForNavigation()` | `cy.url().should('include', '/path')` | `WebDriverWait` + `urlContains` |
| Wait for network idle | `page.waitForLoadState('networkidle')` | `page.waitForNavigation({waitUntil: 'networkidle0'})` | `cy.intercept()` + alias | Custom wait on network |
| Explicit sleep | **Avoid** — use assertions | `await new Promise(r => setTimeout(r, ms))` | `cy.wait(ms)` (avoid) | `Thread.sleep(ms)` (avoid) |

### Assertion Style Conversion

| Source Pattern | Playwright | Puppeteer | Cypress | Selenium |
|---------------|------------|-----------|---------|----------|
| Element visible | `expect(loc).toBeVisible()` | Manual check + Jest/Mocha | `cy.get('#el').should('be.visible')` | `assertTrue(el.isDisplayed())` |
| Text content | `expect(loc).toHaveText('x')` | `expect(await el.textContent()).toBe('x')` | `cy.get('#el').should('have.text', 'x')` | `assertEquals('x', el.getText())` |
| URL | `expect(page).toHaveURL(/path/)` | `expect(page.url()).toContain('/path')` | `cy.url().should('include', '/path')` | `assertTrue(driver.getCurrentUrl().contains('/path'))` |
| Title | `expect(page).toHaveTitle(/title/)` | `expect(await page.title()).toBe('title')` | `cy.title().should('eq', 'title')` | `assertEquals('title', driver.getTitle())` |

## §4 — Debugging Common Migration Issues

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests pass locally, fail in CI | Timing differences, missing browser deps | Use `--headed` locally to reproduce; add `npx playwright install-deps` or equivalent to CI |
| 2 | Element not found after migration | Locator strategy mismatch | Check selector syntax changed between frameworks (e.g., Selenium `By.id("x")` vs Playwright `#x`) |
| 3 | Stale element / detached from DOM | Old framework used element references; new framework re-queries | In Playwright: use Locators (auto-retry). In Cypress: chain from `cy.get()`. In Selenium: re-find element. |
| 4 | Timeout on click/fill | Old test had explicit waits that papered over slow loads | Playwright: check auto-wait is sufficient, increase `actionTimeout`. Cypress: increase `defaultCommandTimeout`. |
| 5 | Alert/dialog handling broken | Different dialog handling model | Playwright: register `page.on('dialog')` BEFORE the action. Cypress: `cy.on('window:confirm')`. Selenium: `driver.switchTo().alert()`. |
| 6 | Multi-tab/window tests fail | Cypress doesn't support multi-tab; Playwright/Puppeteer use different APIs | Playwright: `context.waitForEvent('page')`. Puppeteer: `browser.on('targetcreated')`. Cypress: stub `window.open`. |
| 7 | File upload doesn't work | API difference for file input | Playwright: `locator.setInputFiles()`. Cypress: `cy.selectFile()`. Puppeteer: `elementHandle.uploadFile()`. Selenium: `sendKeys(path)`. |
| 8 | iframe content not accessible | Different iframe traversal model | Playwright: `page.frameLocator()`. Cypress: `cy.iframe()` plugin. Puppeteer: `page.frames()`. Selenium: `driver.switchTo().frame()`. |
| 9 | Network mocking doesn't translate | Different interception APIs | Playwright: `page.route()`. Cypress: `cy.intercept()`. Puppeteer: `page.setRequestInterception(true)`. Selenium: use proxy or external tool. |
| 10 | Parallel execution config broken | Runner-specific parallel model | Playwright: `workers` in config. Cypress: `--parallel` (needs Dashboard). Selenium: TestNG `parallel` or Grid. Puppeteer: manual process spawning. |
| 11 | Screenshots/videos not captured | Different capture config | Playwright: `screenshot: 'only-on-failure'` in config. Cypress: built-in on failure. Puppeteer: manual `page.screenshot()`. |
| 12 | Cloud (TestMu AI) connection fails | Capability format changed between frameworks | Check target framework's `reference/cloud-integration.md` for correct capability format and connection URL. |
| 13 | Async/await errors in Cypress | Cypress uses chaining, not async/await | Remove all `async/await` from `cy.*` commands. Use `.then()` for values. Never `return` a `cy.*` call. |
| 14 | Java/Python tests won't compile after migration | Target framework has different API shape | Check the pair-specific reference file for exact API mappings in that language. |

## §5 — CI/CD Migration Checklist

| Step | Action |
|------|--------|
| 1 | Update runner install step (e.g., `npm install` → `npx playwright install`) |
| 2 | Update test run command (e.g., `npx cypress run` → `npx playwright test`) |
| 3 | Update reporter config (JUnit XML, HTML, JSON paths may change) |
| 4 | Update artifact paths for screenshots, videos, traces |
| 5 | Update parallel execution config (workers, sharding, matrix) |
| 6 | Update environment variables (cloud credentials, base URL) |
| 7 | Update branch protection rules if test command name changed |
| 8 | Remove old framework dependencies from `package.json` / `pom.xml` / `requirements.txt` |

## §6 — Best Practices Checklist

1. **Migrate incrementally** — Don't rewrite all tests at once. Run old and new in parallel until confident.
2. **Start with smoke tests** — Migrate critical path tests first to validate the approach.
3. **Keep the same test structure** — Mirror test file organization (1:1 mapping from old to new).
4. **Preserve test IDs/names** — Keep test names consistent for reporting continuity.
5. **Use semantic locators** — During migration, upgrade `By.id` / CSS selectors to `getByRole` / `getByLabel` where possible (Playwright).
6. **Remove explicit sleeps** — Migration is the best time to eliminate `Thread.sleep` / `waitForTimeout` / `cy.wait(ms)`.
7. **Update page objects together** — Migrate PO + its tests as a unit, not separately.
8. **Test cloud connectivity early** — Don't wait until the end to test TestMu AI / LambdaTest integration.
9. **Keep old tests running** — Don't delete old tests until new ones have been stable for at least one release cycle.
10. **Document mapping decisions** — Record non-obvious conversions (e.g., "We chose `getByRole` over `locator` for all form fields").
11. **Run both suites in CI** — During transition, run old and new suites in parallel in CI.
12. **Handle flaky tests during migration** — If a test was flaky before, fix it during migration rather than porting the flakiness.
13. **Version-lock new framework** — Pin the exact version of the new framework to avoid surprises.
14. **Validate coverage parity** — After migration, verify the new suite covers the same scenarios as the old one.
15. **Update team documentation** — Update README, onboarding docs, and runbooks to reflect the new framework.

## §7 — Cross-References

| Need | Resource |
|------|----------|
| Full Playwright patterns, POM, cloud | `playwright-skill` |
| Full Selenium patterns, POM, cloud | `selenium-skill` |
| Full Puppeteer patterns, cloud | `puppeteer-skill` |
| Full Cypress patterns, cloud | `cypress-skill` |
| TestMu AI capabilities (all frameworks) | `shared/testmu-cloud-reference.md` |
| Framework comparison & language matrix | [overview.md](overview.md) |
```

- [ ] **Step 2: Run validation to verify the warning is resolved**

Run: `cd /Users/mia/myspace/opensource-work/agent-skills && python3 scripts/validate_skills.py`
Expected: `Skills found: 46`, `Errors: 0`, `Warnings: 0`, `All skills pass validation!`

- [ ] **Step 3: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add test-framework-migration-skill/reference/playbook.md
git commit -m "feat(migration-skill): add missing reference/playbook.md

Adds the complete playbook with migration decision framework, workflow,
common patterns (locators, waits, assertions), debugging table (14 entries),
CI/CD migration checklist, and best practices (15 items).

Resolves the only validation warning in the repository."
```

---

### Task 2: Update `skills_index.json` to include playbook reference

**Files:**
- Modify: `skills_index.json` (the `test-framework-migration-skill` entry)

- [ ] **Step 1: Add playbook.md to the reference list in skills_index.json**

Find the `test-framework-migration-skill` entry in `skills_index.json`. Its current `"reference": []` is empty. Replace it with the full list of reference files that exist on disk:

```json
"reference": [
  "test-framework-migration-skill/reference/cypress-to-playwright.md",
  "test-framework-migration-skill/reference/cypress-to-selenium.md",
  "test-framework-migration-skill/reference/overview.md",
  "test-framework-migration-skill/reference/playbook.md",
  "test-framework-migration-skill/reference/playwright-to-cypress.md",
  "test-framework-migration-skill/reference/playwright-to-puppeteer.md",
  "test-framework-migration-skill/reference/playwright-to-selenium.md",
  "test-framework-migration-skill/reference/puppeteer-to-playwright.md",
  "test-framework-migration-skill/reference/puppeteer-to-selenium.md",
  "test-framework-migration-skill/reference/selenium-to-cypress.md",
  "test-framework-migration-skill/reference/selenium-to-playwright.md",
  "test-framework-migration-skill/reference/selenium-to-puppeteer.md"
]
```

- [ ] **Step 2: Run validation again**

Run: `cd /Users/mia/myspace/opensource-work/agent-skills && python3 scripts/validate_skills.py`
Expected: `Skills found: 46`, `Errors: 0`, `Warnings: 0`

- [ ] **Step 3: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add skills_index.json
git commit -m "fix(index): add all reference files for test-framework-migration-skill

The skills_index.json entry had an empty reference array despite 12
reference files existing on disk. Lists all files including the new
playbook.md."
```
