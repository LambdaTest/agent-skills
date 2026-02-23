# Puppeteer → Playwright Migration

## API Mapping

### Locators

| Puppeteer | Playwright |
|-----------|------------|
| `await page.$('#x')` | `page.locator('#x')` (Locator; use with await on actions) |
| `await page.$$('.item')` | `page.locator('.item')` then use `.all()` or iterate; or `page.locator('.item').count()` |
| `page.$('xpath///button')` | `page.locator('xpath=//button')` |
| ElementHandle from `page.$()` | Prefer keeping Locator: `page.locator('#x')`; Playwright re-resolves on each action |

**Playwright preference:** Use `page.getByRole()`, `getByLabel()`, `getByPlaceholder()`, `getByText()`, `getByTestId()` where possible instead of raw selectors.

### Waits

| Puppeteer | Playwright |
|-----------|------------|
| `await page.waitForSelector('.sel', { visible: true })` | Not needed; `await page.locator('.sel').click()` auto-waits. Or `await expect(page.locator('.sel')).toBeVisible()` |
| `await page.waitForNavigation({ waitUntil: 'networkidle0' })` | Usually unnecessary; actions wait for load. For explicit: `await page.waitForURL(/\/dashboard/)` or wait for element |
| `await page.waitForFunction(...)` | `await page.locator(...).evaluate(...)` or `await expect(locator).toHaveText(...)` |
| `page.waitForTimeout(ms)` | **Avoid.** Use `expect(locator).toBeVisible()` or action that implies wait |

### Actions

| Puppeteer | Playwright |
|-----------|------------|
| `await page.type('#x', 'text')` | `await page.locator('#x').fill('text')` or `await page.locator('#x').pressSequentially('text')` |
| `await page.click('#btn')` | `await page.locator('#btn').click()` |
| `await page.select('#sel', 'value')` | `await page.locator('#sel').selectOption('value')` |
| `page.on('dialog', d => d.accept())` | Same: `page.on('dialog', d => d.accept());` |
| Frame: `page.frames()` / `frame.$()` | `const frame = page.frameLocator('iframe[name="x"]'); frame.locator('button').click();` |
| `await page.setViewport({ width, height })` | `await page.setViewportSize({ width, height })` or set in context |

### Assertions

| Puppeteer | Playwright |
|-----------|------------|
| `const title = await page.title(); expect(title).toContain('X')` | `await expect(page).toHaveTitle(/X/)` |
| `expect(page.url()).toContain('/dashboard')` | `await expect(page).toHaveURL(/\/dashboard/)` |
| `await (await page.$('#x')).evaluate(el => el.textContent)` | `await expect(page.locator('#x')).toHaveText('...')` or `await page.locator('#x').textContent()` |

### Lifecycle

| Puppeteer | Playwright |
|-----------|------------|
| `const browser = await puppeteer.launch(); const page = await browser.newPage();` | Use test fixture: `test('...', async ({ page }) => { ... })` or `const browser = await chromium.launch(); const context = await browser.newContext(); const page = await context.newPage();` |
| `await page.goto(url)` | `await page.goto(url)` (same) |
| `await browser.close()` | `await browser.close()` or test runner teardown |
| `page.setViewport(...)` | `context.setViewportSize(...)` or in config |

## Before / After Snippets

**Puppeteer (JavaScript):**
```javascript
await page.goto('https://example.com/login', { waitUntil: 'networkidle0' });
await page.type('#username', 'user@test.com');
await page.type('#password', 'secret');
await page.click('button[type="submit"]');
await page.waitForNavigation({ waitUntil: 'networkidle0' });
```

**Playwright (TypeScript):**
```typescript
await page.goto('https://example.com/login');
await page.locator('#username').fill('user@test.com');
await page.locator('#password').fill('secret');
await page.locator('button[type="submit"]').click();
await expect(page).toHaveURL(/\/dashboard/);
```

## Lifecycle / Setup

- **Puppeteer:** Manual launch, newPage(), close. Often no test runner or Mocha/Jest.
- **Playwright:** Use `@playwright/test` and `defineConfig`; `page` and `context` provided by fixture. Optional `playwright.config.ts` with projects for multiple browsers (Chromium, Firefox, WebKit).

## Cloud (TestMu)

- Puppeteer: connect via LambdaTest WebSocket.
- Playwright: CDP to `wss://cdp.lambdatest.com/playwright?capabilities=...`. See [playwright-skill/reference/cloud-integration.md](../../playwright-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Auto-wait:** Playwright auto-waits on actions and assertions; remove explicit `waitForSelector`/`waitForNavigation` where they only wait for visibility/navigation.
2. **fill vs type:** Playwright's `fill()` clears and types; use `pressSequentially()` for key-by-key simulation if needed.
3. **Locator vs handle:** Don't store ElementHandle-like references; keep Locators and reuse them (Playwright re-resolves).
4. **Multi-browser:** Playwright supports Chromium, Firefox, WebKit out of the box; Puppeteer is Chrome/Chromium. After migration you can add Firefox/WebKit projects.
5. **Test runner:** Playwright has built-in test runner with fixtures, config, and reporting; consider moving to `npx playwright test` and `playwright.config.ts`.
