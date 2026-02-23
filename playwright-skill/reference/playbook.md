# Playwright — Advanced Implementation Playbook

## §1 — Production Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'results.json' }],
    ['junit', { outputFile: 'results.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] }, dependencies: ['setup'] },
    { name: 'webkit', use: { ...devices['Desktop Safari'] }, dependencies: ['setup'] },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] }, dependencies: ['setup'] },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] }, dependencies: ['setup'] },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

## §2 — Auth Fixture Reuse

```typescript
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

```typescript
// tests/fixtures/auth.fixture.ts
import { test as base, Page } from '@playwright/test';

type Fixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

export const test = base.extend<Fixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'playwright/.auth/user.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
  adminPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'playwright/.auth/admin.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
});

export { expect } from '@playwright/test';
```

## §3 — Page Object Model

```typescript
// tests/pages/base.page.ts
import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  protected async navigate(path: string) {
    await this.page.goto(path);
    await this.page.waitForLoadState('domcontentloaded');
  }

  protected getByTestId(id: string): Locator {
    return this.page.getByTestId(id);
  }

  async waitForToast(text: string) {
    await expect(this.page.getByRole('alert')).toContainText(text);
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }
}

// tests/pages/login.page.ts
import { BasePage } from './base.page';
import { DashboardPage } from './dashboard.page';

export class LoginPage extends BasePage {
  private emailInput = this.page.getByLabel('Email');
  private passwordInput = this.page.getByLabel('Password');
  private submitButton = this.page.getByRole('button', { name: 'Sign In' });
  private errorMessage = this.page.getByRole('alert');

  async open() {
    await this.navigate('/login');
    return this;
  }

  async loginAs(email: string, password: string): Promise<DashboardPage> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await this.page.waitForURL('/dashboard');
    return new DashboardPage(this.page);
  }

  async loginExpectingError(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    return this;
  }

  async getErrorText(): Promise<string> {
    return await this.errorMessage.textContent() || '';
  }
}

// Usage in test:
test('login with valid credentials', async ({ page }) => {
  const loginPage = await new LoginPage(page).open();
  const dashboard = await loginPage.loginAs('user@test.com', 'password');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Dashboard');
});
```

## §4 — Advanced Network Interception

```typescript
// Mock API response
test('handles API failure gracefully', async ({ page }) => {
  await page.route('**/api/products', route =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    })
  );
  await page.goto('/products');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});

// Modify live response
test('injects test data into real response', async ({ page }) => {
  await page.route('**/api/products', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.push({ id: 999, name: 'Test Product', price: 0.01 });
    await route.fulfill({ response, json });
  });
  await page.goto('/products');
  await expect(page.getByText('Test Product')).toBeVisible();
});

// Wait for specific API response
test('waits for data load', async ({ page }) => {
  const responsePromise = page.waitForResponse(
    resp => resp.url().includes('/api/dashboard') && resp.status() === 200
  );
  await page.goto('/dashboard');
  const response = await responsePromise;
  const data = await response.json();
  expect(data.items.length).toBeGreaterThan(0);
});

// Block resources for speed
test('fast page load without images', async ({ page }) => {
  await page.route('**/*.{png,jpg,jpeg,gif,svg}', route => route.abort());
  await page.goto('/heavy-page');
});

// HAR recording & replay
test('replay from HAR file', async ({ page }) => {
  await page.routeFromHAR('tests/fixtures/api.har', { notFound: 'fallback' });
  await page.goto('/products');
});
```

## §5 — Visual Regression Testing

```typescript
test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixelRatio: 0.01,
    animations: 'disabled',
    mask: [page.locator('.timestamp'), page.locator('.ad-banner')],
  });
});

test('component visual test', async ({ page }) => {
  await page.goto('/components');
  const card = page.locator('.product-card').first();
  await expect(card).toHaveScreenshot('product-card.png', { threshold: 0.2 });
});

// Update baselines: npx playwright test --update-snapshots
```

## §6 — File Upload & Download

```typescript
// File upload
test('upload profile photo', async ({ page }) => {
  await page.goto('/settings/profile');
  const fileChooserPromise = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Upload Photo' }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles('tests/fixtures/avatar.png');
  await expect(page.getByAltText('Profile Photo')).toBeVisible();
});

// Multiple files
test('upload multiple documents', async ({ page }) => {
  await page.setInputFiles('input[type="file"]', [
    'tests/fixtures/doc1.pdf',
    'tests/fixtures/doc2.pdf',
  ]);
});

// File download
test('download report', async ({ page }) => {
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download Report' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('report.pdf');
  await download.saveAs(`downloads/${download.suggestedFilename()}`);
});
```

## §7 — Multi-Tab, Popup & Dialog Handling

```typescript
// Handle new tab/popup
test('external link opens new tab', async ({ page, context }) => {
  const pagePromise = context.waitForEvent('page');
  await page.getByRole('link', { name: 'External Link' }).click();
  const newPage = await pagePromise;
  await newPage.waitForLoadState();
  expect(newPage.url()).toContain('external-site.com');
  await newPage.close();
});

// Handle dialog (alert/confirm/prompt)
test('confirm delete action', async ({ page }) => {
  page.on('dialog', dialog => {
    expect(dialog.message()).toContain('Are you sure?');
    dialog.accept();
  });
  await page.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText('Deleted successfully')).toBeVisible();
});

// Handle prompt dialog
test('rename item via prompt', async ({ page }) => {
  page.on('dialog', dialog => dialog.accept('New Name'));
  await page.getByRole('button', { name: 'Rename' }).click();
});
```

## §8 — Geolocation, Permissions & Device Emulation

```typescript
test('location-based search', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: 40.7128, longitude: -74.0060 },
    permissions: ['geolocation'],
  });
  const page = await context.newPage();
  await page.goto('/stores/nearby');
  await expect(page.getByText('New York')).toBeVisible();
  await context.close();
});

// Timezone & locale
test('displays correct timezone', async ({ browser }) => {
  const context = await browser.newContext({
    timezoneId: 'Asia/Tokyo',
    locale: 'ja-JP',
  });
  const page = await context.newPage();
  await page.goto('/settings');
  await expect(page.getByText('日本時間')).toBeVisible();
  await context.close();
});

// Color scheme
test('dark mode renders correctly', async ({ browser }) => {
  const context = await browser.newContext({ colorScheme: 'dark' });
  const page = await context.newPage();
  await page.goto('/');
  await expect(page.locator('body')).toHaveCSS('background-color', 'rgb(0, 0, 0)');
  await context.close();
});
```

## §9 — Custom Test Fixtures

```typescript
import { test as base, APIRequestContext } from '@playwright/test';

// Database seeding fixture
type MyFixtures = {
  seedDB: void;
  apiContext: APIRequestContext;
};

export const test = base.extend<MyFixtures>({
  seedDB: [async ({}, use) => {
    await fetch('http://localhost:3001/api/test/seed', { method: 'POST' });
    await use();
    await fetch('http://localhost:3001/api/test/cleanup', { method: 'POST' });
  }, { auto: true }],

  apiContext: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: 'http://localhost:3000/api',
      extraHTTPHeaders: { Authorization: 'Bearer test-token' },
    });
    await use(ctx);
    await ctx.dispose();
  },
});
```

## §10 — API Testing with Playwright

```typescript
import { test, expect } from '@playwright/test';

test.describe('API Tests', () => {
  test('GET /api/users returns users', async ({ request }) => {
    const response = await request.get('/api/users');
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveLength(expect.any(Number));
    expect(body[0]).toHaveProperty('name');
  });

  test('POST /api/users creates user', async ({ request }) => {
    const response = await request.post('/api/users', {
      data: { name: 'Test User', email: 'test@example.com' },
    });
    expect(response.status()).toBe(201);
    const user = await response.json();
    expect(user.name).toBe('Test User');
  });

  test('end-to-end: API + UI', async ({ page, request }) => {
    // Create via API
    const response = await request.post('/api/products', {
      data: { name: 'Playwright Widget', price: 29.99 },
    });
    const product = await response.json();

    // Verify in UI
    await page.goto(`/products/${product.id}`);
    await expect(page.getByRole('heading')).toHaveText('Playwright Widget');
  });
});
```

## §11 — Accessibility Testing Integration

```typescript
import AxeBuilder from '@axe-core/playwright';

test('page passes accessibility audit', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .exclude('.third-party-widget')
    .analyze();
  expect(results.violations).toEqual([]);
});

test('form has proper ARIA labels', async ({ page }) => {
  await page.goto('/contact');
  const results = await new AxeBuilder({ page })
    .include('#contact-form')
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## §12 — Parallel & Sharding

```bash
# Run with sharding (CI matrix)
npx playwright test --shard=1/4
npx playwright test --shard=2/4

# Merge shard reports
npx playwright merge-reports ./all-blob-reports --reporter html
```

```yaml
# GitHub Actions with sharding
jobs:
  test:
    strategy:
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}
      - uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ strategy.job-index }}
          path: blob-report/
  merge-reports:
    needs: test
    steps:
      - uses: actions/download-artifact@v4
        with: { pattern: blob-report-*, merge-multiple: true, path: all-blob-reports }
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
```

## §13 — CI/CD Integration

```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          CI: true
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

## §14 — Debugging Toolkit

```bash
# Debug mode — step through tests
npx playwright test --debug

# UI mode — interactive test explorer
npx playwright test --ui

# Trace viewer
npx playwright test --trace on
npx playwright show-trace test-results/trace.zip

# Codegen — record tests from browser
npx playwright codegen https://example.com

# Show report
npx playwright show-report

# Run specific test
npx playwright test login.spec.ts --project=chromium
```

## §15 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| `TimeoutError: locator.click` | Element not found or not clickable | Check locator accuracy, use `--debug` to inspect |
| `strict mode violation` | Locator matches multiple elements | Add `first()`, `nth()`, or make locator more specific |
| `Target closed` | Page/context closed during operation | Await navigation properly, check `waitForURL` |
| `net::ERR_CONNECTION_REFUSED` | webServer not started | Check `webServer` config, verify `reuseExistingServer` |
| Test passes locally, fails CI | Timing/rendering differences | Use `waitForLoadState`, add `retries: 2` for CI |
| Flaky test | Race condition | Use web-first assertions (`expect(locator)`), avoid raw `page.$` |
| Screenshot mismatch | Font/rendering differences | Use `maxDiffPixelRatio`, `mask` dynamic elements |
| `download` event not firing | Missing browser-level trigger | Use `waitForEvent('download')` before click |
| `filechooser` never resolves | Input hidden or overlayed | Use `setInputFiles('input[type=file]', ...)` directly |
| Slow parallel tests | Workers exceed CPU cores | Set `workers` to CPU count, use sharding for CI |

## §16 — Best Practices Checklist

- ✅ Use `getByRole`, `getByLabel`, `getByText` over CSS/XPath selectors
- ✅ Use web-first assertions (`expect(locator)`) — they auto-retry
- ✅ Use `storageState` to skip login in non-auth tests
- ✅ Mock external APIs with `page.route()` for reliability
- ✅ Enable trace on first retry: `trace: 'on-first-retry'`
- ✅ Keep tests independent — no shared state between test files
- ✅ Use `baseURL` in config, never hardcode URLs
- ✅ Set `fullyParallel: true` for maximum speed
- ✅ Use fixtures for shared setup/teardown, not `beforeAll`
- ✅ Use Page Object Model for 3+ page interactions
- ✅ Run `npx playwright codegen` to bootstrap tests quickly
- ✅ Use sharding in CI for faster feedback
- ✅ Set `forbidOnly: !!process.env.CI` to prevent `.only` in CI
- ✅ Use `test.slow()` for known-slow tests instead of increasing global timeout
- ✅ Structure: `pages/`, `specs/`, `fixtures/`, `utils/`
- ✅ Use `@axe-core/playwright` for accessibility testing in pipeline
- ✅ Store auth state in `playwright/.auth/` with `.gitignore`
