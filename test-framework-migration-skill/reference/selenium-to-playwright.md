# Selenium → Playwright Migration

## API Mapping

### Locators

| Selenium (Java/JS) | Playwright (JS/TS) |
|--------------------|--------------------|
| `By.id("x")` | `page.locator('#x')` or `page.getByRole(..., { name: ... })` when semantic |
| `By.cssSelector(".cls")` | `page.locator('.cls')` |
| `By.xpath("//button")` | `page.locator('xpath=//button')` or prefer `page.getByRole('button', { name: '...' })` |
| `By.name("q")` | `page.getByRole('textbox', { name: '...' })` or `page.locator('[name=q]')` |
| `driver.findElement(By.id("x"))` | `page.locator('#x')` (returns Locator, not ElementHandle for most flows) |

**Playwright preference:** Use `getByRole`, `getByLabel`, `getByPlaceholder`, `getByText`, `getByTestId` before falling back to `locator(selector)`.

### Waits

| Selenium | Playwright |
|----------|------------|
| `WebDriverWait` + `ExpectedConditions.elementToBeClickable(By.id("x"))` | `await page.locator('#x').click()` (auto-waits) or `await expect(page.locator('#x')).toBeVisible()` |
| `wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x")))` | `await expect(page.locator('#x')).toBeVisible()` |
| `Thread.sleep(3000)` | **Avoid.** Use `await expect(locator).toBeVisible()` or `await locator.waitFor()` |
| Implicit wait | Not used; Playwright auto-waits on actions and assertions |

### Actions

| Selenium | Playwright |
|----------|------------|
| `element.sendKeys("text")` | `await locator.fill('text')` or `await locator.pressSequentially('text')` |
| `element.click()` | `await locator.click()` |
| `element.clear()` | `await locator.clear()` or `await locator.fill('')` |
| `new Select(driver.findElement(By.id("sel"))).selectByValue("v")` | `await page.locator('#sel').selectOption('v')` |
| `driver.switchTo().alert().accept()` | `page.on('dialog', d => d.accept())` or handle before action |
| `driver.switchTo().frame("name")` | `await page.frameLocator('iframe[name="name"]')` then use that for locators |
| `driver.switchTo().newWindow(WindowType.TAB)` | `const [newPage] = await Promise.all([context.waitForEvent('page'), page.click('a[target=_blank]')])` |

### Assertions

| Selenium | Playwright |
|----------|------------|
| `Assertions.assertTrue(driver.getTitle().contains("X"))` | `await expect(page).toHaveTitle(/X/)` |
| `Assertions.assertTrue(driver.getCurrentUrl().contains("/dashboard"))` | `await expect(page).toHaveURL(/\/dashboard/)` |
| `Assertions.assertEquals("text", element.getText())` | `await expect(locator).toHaveText('text')` |
| `element.isDisplayed()` | `await expect(locator).toBeVisible()` |

### Lifecycle

| Selenium | Playwright |
|----------|------------|
| `WebDriver driver = new ChromeDriver();` | `const browser = await chromium.launch(); const context = await browser.newContext(); const page = await context.newPage();` |
| `driver.get("https://...")` | `await page.goto('https://...')` |
| `driver.quit()` | `await browser.close()` or rely on test runner teardown |
| `driver.manage().window().maximize()` | `await context.setViewportSize({ width: 1920, height: 1080 })` |

## Before / After Snippets

**Selenium (Java):**
```java
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
driver.get("https://example.com/login");
wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("user@test.com");
driver.findElement(By.id("password")).sendKeys("secret");
driver.findElement(By.cssSelector("button[type='submit']")).click();
wait.until(ExpectedConditions.urlContains("/dashboard"));
Assertions.assertTrue(driver.getTitle().contains("Dashboard"));
```

**Playwright (TypeScript):**
```typescript
await page.goto('https://example.com/login');
await page.locator('#username').fill('user@test.com');
await page.locator('#password').fill('secret');
await page.locator('button[type="submit"]').click();
await expect(page).toHaveURL(/\/dashboard/);
await expect(page).toHaveTitle(/Dashboard/);
```

## Lifecycle / Setup

- **Selenium:** One `WebDriver` per test; `@BeforeEach` create driver, `@AfterEach` driver.quit(). With Grid, use `RemoteWebDriver` + `DesiredCapabilities`.
- **Playwright:** Use `test.beforeEach` to get `page` from fixture (or create `browser` → `context` → `page`). Use `playwright.config.ts` and `defineConfig`; `page` and `context` are typically provided by the test runner. No explicit "quit" in test if using built-in fixtures.

## Cloud (TestMu)

- Selenium on TestMu: `RemoteWebDriver` + hub URL + `LT:Options` in capabilities.
- Playwright on TestMu: CDP connection to `wss://cdp.lambdatest.com/playwright?capabilities=...` with `LT:Options`.  
  See [playwright-automation-skill/reference/cloud-integration.md](../../playwright-automation-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **No Thread.sleep:** Playwright uses auto-wait. Use `expect(locator).toBeVisible()` or action that implies wait; never `page.waitForTimeout(ms)` unless debugging.
2. **Language shift:** Selenium Java/Python/C# → Playwright usually means rewriting in TypeScript/JavaScript. Playwright does have Java/Python/C# bindings if you want to keep language.
3. **Locator vs ElementHandle:** Prefer keeping `Locator` and reusing it; Playwright re-resolves on each action. Avoid storing stale element references.
4. **Alerts/dialogs:** In Selenium you switch to alert after it appears. In Playwright, set `page.on('dialog', ...)` before the action that triggers the dialog.
5. **Multiple windows:** Playwright uses `context.waitForEvent('page')` or `page.context().pages()`; there is no direct `switchTo().window(handle)`.
