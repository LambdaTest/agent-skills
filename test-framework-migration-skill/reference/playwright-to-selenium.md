# Playwright → Selenium Migration

## API Mapping

### Locators

| Playwright (JS/TS) | Selenium (Java example; JS similar) |
|--------------------|--------------------------------------|
| `page.getByRole('button', { name: 'Submit' })` | `By.xpath("//button[normalize-space()='Submit']")` or `By.cssSelector("button")` + match text; prefer `By.id` if known |
| `page.getByLabel('Email')` | `By.xpath("//label[contains(.,'Email')]/following::input[1]")` or `By.cssSelector("input[name=email]")` |
| `page.getByPlaceholder('Enter email')` | `By.cssSelector("input[placeholder='Enter email']")` |
| `page.getByText('Welcome')` | `By.xpath("//*[contains(text(),'Welcome')]")` |
| `page.getByTestId('submit-btn')` | `By.cssSelector("[data-testid='submit-btn']")` |
| `page.locator('#x')` | `By.id("x")` or `By.cssSelector("#x")` |
| `page.locator('.cls')` | `By.cssSelector(".cls")` |

**Selenium:** No built-in role/label locators; use CSS, ID, or XPath. Prefer `By.id`, `By.cssSelector`, then XPath.

### Waits

| Playwright | Selenium |
|------------|----------|
| `await expect(locator).toBeVisible()` | `WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10)); wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x")));` |
| `await locator.click()` (auto-waits) | Wait for clickable then click: `wait.until(ExpectedConditions.elementToBeClickable(By.id("x"))).click();` |
| `await page.goto(url)` (auto-waits load) | `driver.get(url);` then optionally wait for specific element |
| `page.waitForTimeout(ms)` | **Avoid in both.** In Selenium use explicit `WebDriverWait`, never `Thread.sleep` in production tests. |

### Actions

| Playwright | Selenium |
|------------|----------|
| `await locator.fill('text')` | `WebElement el = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x"))); el.clear(); el.sendKeys("text");` |
| `await locator.click()` | `wait.until(ExpectedConditions.elementToBeClickable(By.id("x"))).click();` |
| `await page.locator('#sel').selectOption('v')` | `new Select(driver.findElement(By.id("sel"))).selectByValue("v");` |
| `page.on('dialog', d => d.accept())` | `driver.switchTo().alert().accept();` (after alert is present) |
| `page.frameLocator('iframe[name="name"]')` | `driver.switchTo().frame("name");` then `driver.findElement(...)` |
| New tab: `context.waitForEvent('page')` | `driver.switchTo().newWindow(WindowType.TAB);` or switch by handle |

### Assertions

| Playwright | Selenium |
|------------|----------|
| `await expect(page).toHaveTitle(/X/)` | `Assertions.assertTrue(driver.getTitle().contains("X"));` |
| `await expect(page).toHaveURL(/\/dashboard/)` | `Assertions.assertTrue(driver.getCurrentUrl().contains("/dashboard"));` |
| `await expect(locator).toHaveText('text')` | `Assertions.assertEquals("text", driver.findElement(By.id("x")).getText());` (after wait for visible) |
| `await expect(locator).toBeVisible()` | `Assertions.assertTrue(wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x"))).isDisplayed());` |

### Lifecycle

| Playwright | Selenium |
|------------|----------|
| `const browser = await chromium.launch();` etc. | `WebDriver driver = new ChromeDriver();` |
| `await page.goto(url)` | `driver.get(url);` |
| `await browser.close()` | `driver.quit();` (in @AfterEach / teardown) |
| `context.setViewportSize({ width, height })` | `driver.manage().window().maximize();` or `driver.manage().window().setSize(new Dimension(w, h));` |

## Before / After Snippets

**Playwright (TypeScript):**
```typescript
await page.goto('https://example.com/login');
await page.getByLabel('Email').fill('user@test.com');
await page.getByLabel('Password').fill('secret');
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL(/\/dashboard/);
```

**Selenium (Java):**
```java
driver.get("https://example.com/login");
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("input[type='email']"))).sendKeys("user@test.com");
driver.findElement(By.cssSelector("input[type='password']")).sendKeys("secret");
wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))).click();
wait.until(ExpectedConditions.urlContains("/dashboard"));
```

## Lifecycle / Setup

- **Playwright:** Test runner provides `page` via fixture; config in `playwright.config.ts`.
- **Selenium:** In JUnit/TestNG, create `WebDriver` in `@BeforeEach`, call `driver.quit()` in `@AfterEach`. Use explicit `WebDriverWait` for every interaction that depends on element visibility/clickability; do not rely on implicit wait or Thread.sleep.

## Cloud (TestMu)

- Playwright on TestMu: CDP over `wss://cdp.lambdatest.com/playwright?capabilities=...`.
- Selenium on TestMu: `RemoteWebDriver` with hub URL and `DesiredCapabilities` / `LT:Options`.  
  See [selenium-skill/reference/cloud-integration.md](../../selenium-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Explicit waits required:** Playwright auto-waits; Selenium does not. Every find + action should be guarded by `WebDriverWait` + `ExpectedConditions` (visibility, clickability, etc.).
2. **No getByRole/getByLabel in Selenium:** Replace with CSS, ID, or XPath. Prefer stable selectors (id, data-testid, name).
3. **Stale element references:** In Selenium, store `By` locators and re-find after waits; avoid holding `WebElement` across navigations or DOM updates.
4. **Dialogs:** In Playwright you listen for `dialog` before the action; in Selenium you switch to alert after it appears. Ensure wait for alert before `switchTo().alert()`.
5. **Language:** Playwright tests are often TypeScript/JS. Migrating to Selenium allows Java, Python, C#; choose based on project and convert syntax accordingly.
