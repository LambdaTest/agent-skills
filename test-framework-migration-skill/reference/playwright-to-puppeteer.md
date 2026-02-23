# Playwright → Puppeteer Migration

## API Mapping

### Locators

| Playwright | Puppeteer |
|------------|-----------|
| `page.locator('#x')` | `await page.$('#x')` (returns ElementHandle; use immediately for action or store for one-off use) |
| `page.getByRole('button', { name: 'Submit' })` | No direct equivalent; use `page.$('button')` or CSS/XPath that matches text (e.g. `page.$('xpath///button[contains(.,"Submit")]')`) |
| `page.getByLabel('Email')` | `page.$('input[type=email]')` or `page.$('[aria-label="Email"]')` or form-associated selector |
| `page.getByTestId('btn')` | `page.$('[data-testid="btn"]')` |
| `page.locator('.item').all()` | `await page.$$('.item')` |

**Puppeteer:** No role/label locators; use CSS, XPath, or data attributes. Prefer stable selectors (id, data-testid).

### Waits

| Playwright | Puppeteer |
|------------|-----------|
| Auto-wait on `locator.click()` | No auto-wait; use `await page.waitForSelector('#btn', { visible: true }); await page.click('#btn');` |
| `await expect(locator).toBeVisible()` | `await page.waitForSelector(selector, { visible: true, timeout: 10000 });` |
| `await page.goto(url)` (waits for load) | `await page.goto(url, { waitUntil: 'networkidle0' });` or `domcontentloaded` |
| No waitForTimeout | `await new Promise(r => setTimeout(r, ms))` only for debugging; prefer waitForSelector/waitForFunction |

### Actions

| Playwright | Puppeteer |
|------------|-----------|
| `await locator.fill('text')` | `await page.$('#x')` then `(await page.$('#x')).type('text')` or `page.evaluate((sel, t) => { document.querySelector(sel).value = t; }, '#x', 'text');` |
| `await locator.click()` | `await page.click('#selector')` (after waitForSelector if needed) |
| `await page.locator('#sel').selectOption('v')` | `await page.select('#sel', 'v');` |
| `page.on('dialog', d => d.accept())` | Same in Puppeteer |
| `page.frameLocator('iframe')` | `const frame = page.frames().find(f => f.name() === 'x');` then `frame.$()`, `frame.click()`, etc. |
| New tab | `context.waitForEvent('page')` in Playwright | `const [newPage] = await Promise.all([new Promise(r => page.once('popup', r)), page.click('a[target=_blank]')]);` |

### Assertions

| Playwright | Puppeteer |
|------------|-----------|
| `await expect(page).toHaveTitle(/X/)` | `const title = await page.title(); expect(title).toMatch(/X/);` (Jest/Mocha) |
| `await expect(page).toHaveURL(/\/dashboard/)` | `expect(page.url()).toMatch(/\/dashboard/);` |
| `await expect(locator).toHaveText('x')` | `const text = await (await page.$('#el')).evaluate(el => el.textContent); expect(text).toContain('x');` |

### Lifecycle

| Playwright | Puppeteer |
|------------|-----------|
| Test fixture `{ page }` or `chromium.launch()` + `newContext()` + `newPage()` | `puppeteer.launch()` then `browser.newPage()` |
| `await page.goto(url)` | `await page.goto(url, { waitUntil: 'networkidle0' })` |
| `await browser.close()` | `await browser.close()` |
| `context.setViewportSize(...)` | `await page.setViewport({ width, height })` |

## Before / After Snippets

**Playwright (TypeScript):**
```typescript
await page.goto('https://example.com/login');
await page.getByLabel('Email').fill('user@test.com');
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL(/\/dashboard/);
```

**Puppeteer (JavaScript):**
```javascript
await page.goto('https://example.com/login', { waitUntil: 'networkidle0' });
await page.type('input[type="email"]', 'user@test.com');
await page.waitForSelector('button[type="submit"]', { visible: true });
await page.click('button[type="submit"]');
await page.waitForNavigation({ waitUntil: 'networkidle0' });
expect(page.url()).toMatch(/\/dashboard/);
```

## Lifecycle / Setup

- **Playwright:** Often uses @playwright/test with config and fixtures.
- **Puppeteer:** Typically manual launch/newPage/close; use Mocha/Jest or similar for structure. No built-in multi-browser config like Playwright projects.

## Cloud (TestMu)

- Playwright: CDP to LambdaTest (see playwright-skill/reference/cloud-integration.md).
- Puppeteer: WebSocket connect to LambdaTest (see puppeteer-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Add explicit waits:** Playwright auto-waits; Puppeteer does not. After migration, add `waitForSelector` or `waitForNavigation` before clicks/navigation-dependent asserts.
2. **getByRole/getByLabel:** Replace with CSS/XPath or data-testid; document the semantic meaning so selectors stay maintainable.
3. **fill vs type:** Playwright `fill()` clears and sets value; in Puppeteer use `element.type()` or `evaluate` to set value. For keyboard simulation use `page.keyboard.type()`.
4. **Chrome-only:** Playwright can run Firefox/WebKit; moving to Puppeteer limits you to Chrome/Chromium.
5. **Stale handles:** In Puppeteer, ElementHandles can go stale after navigation or DOM update; re-query with `page.$()` when in doubt.
