# Test Framework Migration — Unified Playbook

## §1 — Migration Decision Framework

Use this table to decide whether to migrate between frameworks. Evaluate against your project's constraints before committing.

### Selenium to Playwright

| Migrate when | Stay when |
|-------------|-----------|
| Tests are flaky due to manual wait management | Large Java/Python/C# codebase with extensive Selenium Grid investment |
| Need built-in API mocking, tracing, or auto-wait | Team has deep Selenium expertise and stable suite |
| Want single JS/TS codebase with modern tooling | Regulatory or enterprise tooling requires Selenium |
| Need multi-browser (Chromium, Firefox, WebKit) without Grid | Already using RemoteWebDriver + cloud grid at scale |

### Selenium to Puppeteer

| Migrate when | Stay when |
|-------------|-----------|
| Chrome-only automation (scraping, PDF generation) | Need multi-browser support |
| Want lightweight Node.js library without test runner | Tests are in Java/Python/C# |
| Existing codebase is already Node.js | Need built-in assertions, tracing, or test runner |

### Selenium to Cypress

| Migrate when | Stay when |
|-------------|-----------|
| Team prefers Cypress DX and component testing | Need multi-tab or multi-window support |
| Want built-in retry-ability and time-travel debugging | Tests are in Java/Python/C# (Cypress is JS/TS only) |
| Primarily testing a single web application | Need cross-browser beyond Chrome/Firefox/Edge |

### Playwright to Selenium

| Migrate when | Stay when |
|-------------|-----------|
| Enterprise requires Selenium Grid or specific Selenium tooling | Playwright suite is stable and team is proficient |
| Need Ruby or PHP bindings not available in Playwright | Already using Playwright's tracing, auto-wait, and API mocking |
| Integrating with existing Java/C# test infrastructure | No strong reason to leave modern tooling |

### Puppeteer to Playwright

| Migrate when | Stay when |
|-------------|-----------|
| Need Firefox or WebKit support | Chrome-only scraping that works fine |
| Want built-in test runner, assertions, and tracing | Simple scripts with no test framework needs |
| Need auto-wait instead of manual `waitForSelector` | Minimal codebase not worth the effort |

### Cypress to Playwright

| Migrate when | Stay when |
|-------------|-----------|
| Need multiple tabs/windows, which Cypress does not support | Team is productive with Cypress DX |
| Need non-Chromium browsers (WebKit) | Cypress component testing is core to workflow |
| Want async/await control flow instead of chain-based | Invested in Cypress Cloud dashboard |

### Playwright to Cypress

| Migrate when | Stay when |
|-------------|-----------|
| Team prefers Cypress DX and time-travel debugging | Need multi-tab support |
| Want Cypress component testing features | Need WebKit testing |
| Existing Cypress Cloud investment | Already leveraging Playwright's tracing and API mocking |

For detailed API mappings for any pair, see the pair-specific reference files listed in [overview.md](overview.md).

## §2 — Language Matrix

| Framework | Java | Python | JavaScript | TypeScript | C# | Ruby | PHP |
|-----------|:----:|:------:|:----------:|:----------:|:---:|:----:|:---:|
| **Selenium** | Yes | Yes | Yes | -- | Yes | Yes | Yes |
| **Playwright** | Yes | Yes | Yes | Yes | Yes | -- | -- |
| **Puppeteer** | -- | -- | Yes | Yes | -- | -- | -- |
| **Cypress** | -- | -- | Yes | Yes | -- | -- | -- |

**Key implications for migration:**

- **Selenium (Java/Python/C#) to Playwright:** Most common path is to rewrite in TypeScript/JavaScript. Playwright also has Java, Python, and C# bindings if you prefer to keep the language.
- **Playwright/Puppeteer/Cypress to Selenium:** Target language can be any Selenium supports; choose based on team expertise.
- **Puppeteer/Cypress:** JS/TS only. Migration to or from these frameworks implies JS/TS.

## §3 — Migration Workflow (10-Step Process)

### Step 1: Audit existing test suite

```bash
# Count test files and lines
find tests/ -name "*.java" -o -name "*.py" -o -name "*.js" -o -name "*.ts" | wc -l
# Identify page objects
find . -path "*/pages/*" -o -path "*/pageobjects/*" | head -20
# Check for cloud/grid usage
grep -r "RemoteWebDriver\|cdp.lambdatest\|GRID_URL\|HUB_URL" --include="*.java" --include="*.js" --include="*.ts" --include="*.py" .
```

Document:
- Total test count and lines of code
- Number of page objects
- Frameworks and runners in use (JUnit, TestNG, pytest, Mocha, Jest)
- CI/CD pipeline configuration
- Cloud/grid dependencies (Selenium Grid, LambdaTest, BrowserStack)
- Custom utilities (retry logic, screenshot helpers, data providers)

### Step 2: Choose target language

Refer to the Language Matrix in [section 2](#2--language-matrix). If the source is Java Selenium and the target is Playwright, decide JS/TS vs Playwright Java bindings. For most Playwright migrations, TypeScript is recommended.

### Step 3: Set up target framework project

```bash
# Example: Playwright TypeScript
npm init -y
npm install -D @playwright/test
npx playwright install

# Example: Selenium Java (Maven)
mvn archetype:generate -DgroupId=com.tests -DartifactId=selenium-tests
# Add selenium-java, webdrivermanager to pom.xml

# Example: Cypress
npm init -y
npm install -D cypress
npx cypress open
```

Create the project structure for the target framework before migrating any tests.

### Step 4: Migrate infrastructure (config, base classes, utilities)

Migrate in this order:
1. Configuration files (base URL, timeouts, browser settings)
2. Base page class / shared utilities
3. Test fixtures and setup/teardown hooks
4. Custom wait helpers and retry logic
5. Reporting integration

### Step 5: Convert page objects

For each page object, convert locators, actions, and internal methods using the pair-specific API mapping tables in the reference files. See [overview.md](overview.md) for the list of all pair-specific references.

**Example — Selenium Java → Playwright TypeScript page object:**

```java
// BEFORE: Selenium Java
public class LoginPage {
    private By emailField = By.id("email");
    private By submitBtn = By.cssSelector("button[type='submit']");
    public LoginPage(WebDriver driver) { this.driver = driver; }
    public void login(String email, String pass) {
        wait.until(ExpectedConditions.visibilityOfElementLocated(emailField)).sendKeys(email);
        driver.findElement(submitBtn).click();
    }
}
```

```typescript
// AFTER: Playwright TypeScript
export class LoginPage {
    readonly emailField = this.page.getByLabel('Email');
    readonly submitBtn = this.page.getByRole('button', { name: 'Sign in' });
    constructor(private page: Page) {}
    async login(email: string, pass: string) {
        await this.emailField.fill(email);
        await this.submitBtn.click(); // auto-waits for visible + enabled
    }
}
```

**Locator conversion priority (Playwright target):**
1. Use `getByRole`, `getByLabel`, `getByText`, `getByTestId` where possible
2. Fall back to `page.locator(css)` for complex selectors
3. Avoid `xpath=` unless there is no CSS equivalent

### Step 6: Migrate tests in batches

Migrate tests in batches of 5-10, grouped by feature or page. After each batch:
- Run the batch locally
- Fix any conversion issues
- Commit the batch

Do NOT attempt to migrate all tests at once.

### Step 7: Run locally and fix issues

```bash
# Playwright
npx playwright test --headed

# Selenium (Maven)
mvn test -Dbrowser=chrome

# Cypress
npx cypress run

# Puppeteer (with Jest)
npx jest --runInBand
```

Use the debugging table in [section 6](#6--debugging-quick-reference) for common issues.

### Step 8: Update CI/CD pipeline

See the CI/CD Migration Checklist in [section 7](#7--cicd-migration-checklist).

### Step 9: Cloud migration

If running tests on a cloud grid (LambdaTest / TestMu):
- Update connection strings and capabilities for the target framework
- See pair-specific reference files for cloud (TestMu) sections
- See [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md) for cross-framework cloud configuration

### Step 10: Decommission old framework

1. Confirm all migrated tests pass in CI for at least 2 consecutive runs
2. Remove old framework dependencies from package.json / pom.xml / requirements.txt
3. Delete old test files, page objects, and utilities
4. Update documentation and README
5. Archive the old CI pipeline configuration

## §4 — Common Migration Patterns

For full API mapping tables, always consult the pair-specific reference file. Below are the most frequently needed cross-framework conversions.

### Locator Conversion

| Concept | Selenium | Playwright | Puppeteer | Cypress |
|---------|----------|------------|-----------|---------|
| By ID | `By.id("x")` | `page.locator('#x')` | `page.$('#x')` | `cy.get('#x')` |
| By CSS | `By.cssSelector(".c")` | `page.locator('.c')` | `page.$('.c')` | `cy.get('.c')` |
| By text | `By.xpath("//*[contains(text(),'T')]")` | `page.getByText('T')` | XPath or evaluate | `cy.contains('T')` |
| By role | No built-in | `page.getByRole('button', {name: 'X'})` | No built-in | No built-in |
| By test ID | `By.cssSelector("[data-testid='x']")` | `page.getByTestId('x')` | `page.$('[data-testid="x"]')` | `cy.get('[data-testid="x"]')` |

### Wait Strategy Conversion

| Concept | Selenium | Playwright | Puppeteer | Cypress |
|---------|----------|------------|-----------|---------|
| Wait for visible | `WebDriverWait` + `visibilityOfElementLocated` | Auto-wait on actions; `expect(loc).toBeVisible()` | `page.waitForSelector(sel, {visible:true})` | `cy.get(sel).should('be.visible')` |
| Wait for clickable | `elementToBeClickable` | Auto-wait on `.click()` | `waitForSelector` + `.click()` | `cy.get(sel).click()` (retries) |
| Wait for URL | `urlContains` | `expect(page).toHaveURL(...)` | Check `page.url()` in loop or `waitForNavigation` | `cy.url().should('include', ...)` |
| Hard sleep | `Thread.sleep(ms)` -- avoid | `page.waitForTimeout(ms)` -- avoid | `page.waitForTimeout(ms)` -- avoid | `cy.wait(ms)` -- avoid |

### Assertion Conversion

| Concept | Selenium | Playwright | Puppeteer | Cypress |
|---------|----------|------------|-----------|---------|
| Title contains | `assertTrue(getTitle().contains("X"))` | `expect(page).toHaveTitle(/X/)` | `expect(await page.title()).toContain('X')` | `cy.title().should('include', 'X')` |
| URL contains | `assertTrue(getCurrentUrl().contains("/d"))` | `expect(page).toHaveURL(/\/d/)` | `expect(page.url()).toContain('/d')` | `cy.url().should('include', '/d')` |
| Text equals | `assertEquals("t", el.getText())` | `expect(loc).toHaveText('t')` | `expect(await el.evaluate(e=>e.textContent)).toBe('t')` | `cy.get(s).should('have.text','t')` |
| Element visible | `assertTrue(el.isDisplayed())` | `expect(loc).toBeVisible()` | `expect(await el.isIntersectingViewport()).toBe(true)` | `cy.get(s).should('be.visible')` |

### Lifecycle Conversion

| Concept | Selenium | Playwright | Puppeteer | Cypress |
|---------|----------|------------|-----------|---------|
| Launch browser | `new ChromeDriver()` | `chromium.launch()` or test fixture | `puppeteer.launch()` | Managed by runner |
| Navigate | `driver.get(url)` | `page.goto(url)` | `page.goto(url)` | `cy.visit(url)` |
| Close | `driver.quit()` | `browser.close()` or fixture teardown | `browser.close()` | Managed by runner |
| Viewport | `window().maximize()` | `setViewportSize({w,h})` | `page.setViewport({w,h})` | `cy.viewport(w,h)` |

## §5 — Advanced Pattern Conversions

### Alert / Dialog Handling

| Framework | Pattern |
|-----------|---------|
| Selenium | `wait.until(alertIsPresent()); driver.switchTo().alert().accept();` |
| Playwright | `page.on('dialog', d => d.accept());` -- register before triggering action |
| Puppeteer | `page.on('dialog', d => d.accept());` -- same pattern as Playwright |
| Cypress | `cy.on('window:alert', () => true);` for alerts; `cy.on('window:confirm', () => true);` for confirms -- stub before action |

### iframe Handling

| Framework | Pattern |
|-----------|---------|
| Selenium | `driver.switchTo().frame("name"); ... driver.switchTo().defaultContent();` |
| Playwright | `page.frameLocator('iframe[name="name"]').locator('button').click();` |
| Puppeteer | `const frame = page.frames().find(f => f.name() === 'name'); await frame.click('button');` |
| Cypress | `cy.get('iframe').its('0.contentDocument.body').then(cy.wrap).find('button').click();` |

### Multiple Tabs / Windows

| Framework | Pattern |
|-----------|---------|
| Selenium | `driver.switchTo().newWindow(WindowType.TAB);` or iterate `getWindowHandles()` |
| Playwright | `const [newPage] = await Promise.all([context.waitForEvent('page'), page.click('a')]);` |
| Puppeteer | `const [newPage] = await Promise.all([browser.waitForTarget(t => t.opener()), page.click('a')]);` then `await newPage.page()` |
| Cypress | Not supported natively; workaround by removing `target=_blank` or using `cy.origin()` |

### Network Mocking / Interception

| Framework | Pattern |
|-----------|---------|
| Selenium | No built-in; use DevTools protocol or application-level mocks |
| Playwright | `await page.route('**/api/*', route => route.fulfill({body: '...'}));` |
| Puppeteer | `await page.setRequestInterception(true); page.on('request', req => {...});` |
| Cypress | `cy.intercept('GET', '/api/*', {body: ...}).as('alias');` |

### File Upload

| Framework | Pattern |
|-----------|---------|
| Selenium | `driver.findElement(By.id("upload")).sendKeys("/path/to/file");` |
| Playwright | `await page.locator('#upload').setInputFiles('/path/to/file');` |
| Puppeteer | `const input = await page.$('#upload'); await input.uploadFile('/path/to/file');` |
| Cypress | `cy.get('#upload').selectFile('path/to/file');` |

### Attribute Reading

| Framework | Pattern |
|-----------|---------|
| Selenium | `element.getAttribute("href")` |
| Playwright | `await locator.getAttribute('href')` or `expect(loc).toHaveAttribute('href', /pattern/)` |
| Puppeteer | `await element.evaluate(el => el.getAttribute('href'))` |
| Cypress | `cy.get(sel).should('have.attr', 'href', '/expected')` or `cy.get(sel).invoke('attr', 'href')` |

### JavaScript Execution

| Framework | Pattern |
|-----------|---------|
| Selenium | `((JavascriptExecutor) driver).executeScript("return arguments[0].scrollHeight", element);` |
| Playwright | `await locator.evaluate(el => el.scrollHeight)` or `await page.evaluate(() => document.title)` |
| Puppeteer | `await element.evaluate(el => el.scrollHeight)` or `await page.evaluate(() => document.title)` |
| Cypress | `cy.get(sel).then($el => $el[0].scrollHeight)` or `cy.window().then(win => win.document.title)` |

## §6 — Debugging Quick-Reference

| # | Problem | Likely Cause | Fix |
|---|---------|-------------|-----|
| 1 | Tests pass locally, fail in CI | Display, timing, or viewport differences | Run headless locally; set explicit viewport (e.g. `--window-size=1920,1080`); increase timeouts; check for missing fonts/deps in CI image |
| 2 | Element not found | Element not yet in DOM, wrong locator, or inside iframe | Use explicit wait or auto-wait assertion; verify locator in browser DevTools; check if element is inside an iframe or shadow DOM |
| 3 | Stale element reference | DOM re-rendered after element was located | Re-locate element after each navigation or DOM change; in Selenium use `By` locators with `WebDriverWait`; in Playwright use `Locator` (auto-resolves) |
| 4 | Timeout waiting for element | Element never appears, wrong page, or selector mismatch | Verify URL is correct; check for redirects; validate selector; increase timeout; add debug screenshot before wait |
| 5 | Alert/dialog not handled | Alert appeared before handler registered, or handler registered too late | Selenium: wait for `alertIsPresent()` before `switchTo().alert()`; Playwright/Puppeteer: register `page.on('dialog')` before the action that triggers it; Cypress: use `cy.on('window:confirm')` before action |
| 6 | Multiple tab/window issues | Wrong browsing context after opening new tab | Selenium: iterate `getWindowHandles()` and `switchTo().window(handle)`; Playwright: use `context.waitForEvent('page')`; Cypress: remove `target=_blank` or restructure test |
| 7 | File upload fails | Input element hidden or not a file input | Selenium: `sendKeys()` only works on `<input type="file">`; Playwright: use `setInputFiles()`; ensure the element is the actual file input, not a styled wrapper |
| 8 | iframe elements not found | Test is in the wrong browsing context | Selenium: `switchTo().frame()` before interacting, `switchTo().defaultContent()` after; Playwright: use `frameLocator()`; Puppeteer: get frame from `page.frames()` |
| 9 | Network mock not intercepting | Route pattern does not match actual request URL | Log actual request URLs; verify glob/regex pattern; ensure mock is registered before navigation; check request method (GET vs POST) |
| 10 | Parallel execution failures | Shared state between tests (cookies, DB, global variables) | Isolate browser contexts per test; use unique test data; avoid shared mutable state; in Selenium use `ThreadLocal<WebDriver>` |
| 11 | Screenshots blank or wrong size | Headless viewport not set, or screenshot taken after browser closed | Set explicit viewport size; take screenshot before teardown; verify browser is still open when screenshot is captured |
| 12 | Cloud grid connection fails | Wrong hub URL, expired credentials, or capability mismatch | Verify hub URL and credentials; check `LT:Options` / capabilities format; ensure browser version is available on grid; see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md) |
| 13 | async/await errors (Playwright/Puppeteer) | Missing `await` on async call, or using `await` with Cypress `cy` commands | Playwright/Puppeteer: ensure every action and assertion is `await`ed; Cypress: never use `async/await` with `cy` commands |
| 14 | Compile/type errors after migration | Incorrect API usage for target framework, leftover source framework calls | Review the pair-specific API mapping table; search for leftover imports (`import org.openqa.selenium`, `require('puppeteer')`, etc.); run TypeScript compiler or linter |
| 15 | Select/dropdown not working | Different API between frameworks for `<select>` elements | Selenium: `new Select(el).selectByValue()`; Playwright: `locator.selectOption()`; Puppeteer: `page.select()`; Cypress: `cy.get(sel).select()` |
| 16 | Hover/drag-and-drop not working | Actions API differs between frameworks | Selenium: `new Actions(driver).moveToElement(el).perform()`; Playwright: `locator.hover()` or `page.dragAndDrop()`; Puppeteer: `page.hover()` or mouse API; Cypress: `cy.get(el).trigger('mouseover')` or plugins |

## §7 — CI/CD Migration Checklist

Follow these steps when migrating CI/CD pipelines to a new test framework:

| # | Step | Details |
|---|------|---------|
| 1 | Install target framework in CI | Add install steps (e.g. `npm ci && npx playwright install --with-deps` for Playwright; add Maven dependencies for Selenium) |
| 2 | Update environment variables | Migrate `SELENIUM_REMOTE_URL`, `GRID_URL` to target equivalents; update `LT_USERNAME` / `LT_ACCESS_KEY` references if connection method changes |
| 3 | Update test run command | Replace `mvn test` with `npx playwright test`, or `npx cypress run`, etc. |
| 4 | Configure headless mode | Selenium: `--headless=new --no-sandbox --disable-dev-shm-usage`; Playwright: headless by default; Cypress: `npx cypress run` is headless; Puppeteer: `launch({headless: true})` |
| 5 | Set up artifact collection | Upload test results, screenshots, videos, and traces as CI artifacts; adjust paths for target framework output directories |
| 6 | Configure parallel execution | Selenium: TestNG parallel or JUnit parallel; Playwright: `--workers=N` or `fullyParallel: true` in config; Cypress: `cypress-parallel` or Cypress Cloud; Puppeteer: Jest `--workers` |
| 7 | Update reporting | Replace Allure/Surefire with target framework's reporter (Playwright HTML reporter, Cypress Dashboard, etc.); ensure JUnit XML output for CI integration |
| 8 | Run both old and new suites in parallel during transition | Keep old pipeline active until new suite achieves equivalent coverage; compare results before decommissioning old suite |

## §8 — Best Practices

1. **Migrate incrementally** -- convert tests in small batches (5-10 at a time), not the entire suite at once
2. **Run old and new suites in parallel** during migration to catch regressions
3. **Convert page objects first** before migrating individual tests
4. **Use the target framework's idiomatic patterns** -- do not transliterate source framework patterns (e.g. do not add explicit waits in Playwright where auto-wait suffices)
5. **Prefer semantic locators** when migrating to Playwright (`getByRole`, `getByLabel`, `getByTestId`) instead of literal CSS/XPath translation
6. **Remove all hard sleeps** (`Thread.sleep`, `page.waitForTimeout`, `cy.wait(ms)`) and replace with proper wait strategies
7. **Update assertions to target framework style** -- use Playwright `expect()`, Cypress `.should()`, or Selenium `WebDriverWait` + JUnit/TestNG assertions
8. **Verify cloud/grid configuration** for the target framework before migrating CI (see pair-specific cloud sections)
9. **Keep test data and fixtures framework-agnostic** where possible (JSON, CSV, environment variables)
10. **Set explicit viewport sizes** in both local and CI environments to avoid layout-dependent flakiness
11. **Take screenshots on failure** in the target framework from day one
12. **Consider TypeScript** when migrating to Playwright (strongly recommended for fixture typing), Puppeteer, or Cypress for better IDE support; JavaScript is fine for Puppeteer/Cypress if the team prefers it
13. **Document the migration** -- track which tests have been migrated, which are pending, and any known issues
14. **Do not mix frameworks in the same test file** -- complete migration per file before moving to the next
15. **Test the CI pipeline early** -- do not wait until all tests are migrated to verify CI works with the new framework

## §9 — Cross-References

| Need | Reference |
|------|-----------|
| Pair-specific API mappings (Selenium to Playwright, etc.) | [overview.md](overview.md) lists all 10 pair files |
| Full Playwright patterns, POM, fixtures | `playwright-skill/SKILL.md` and `playwright-skill/reference/` |
| Full Selenium patterns, POM, Grid | `selenium-skill/SKILL.md` and `selenium-skill/reference/` |
| Full Puppeteer patterns | `puppeteer-skill/SKILL.md` and `puppeteer-skill/reference/` |
| Full Cypress patterns, component testing | `cypress-skill/SKILL.md` and `cypress-skill/reference/` |
| TestMu / LambdaTest cloud configuration (all frameworks) | [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md) |
| Playwright cloud integration | [playwright-skill/reference/cloud-integration.md](../../playwright-skill/reference/cloud-integration.md) |
| Selenium cloud integration | [selenium-skill/reference/cloud-integration.md](../../selenium-skill/reference/cloud-integration.md) |
| Cypress cloud integration | [cypress-skill/reference/cloud-integration.md](../../cypress-skill/reference/cloud-integration.md) |
| Puppeteer cloud integration | [puppeteer-skill/reference/cloud-integration.md](../../puppeteer-skill/reference/cloud-integration.md) |
