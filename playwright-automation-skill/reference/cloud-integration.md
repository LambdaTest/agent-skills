# Cloud Integration — TestMu AI

## Table of Contents
- Choosing a Pattern
- Pattern 1: Direct Connect (Standalone Scripts)
- Pattern 2: Test Runner Fixture (Existing Suites)
- Pattern 3: Playwright SDK (Zero Code Changes)
- Parallel Cloud Execution
- Hybrid Config (Local + Cloud)

## Choosing a Pattern

| Situation | Pattern | Why |
|---|---|---|
| Quick one-off script, no test runner | **Pattern 1: Direct Connect** | Simplest, no setup |
| Existing test suite, want fine control | **Pattern 2: Fixture** | Default — recommended |
| Existing suite, zero code changes | **Pattern 3: SDK** | Install + YAML only |
| Not sure | **Pattern 2: Fixture** | Most flexible |

## Pattern 1: Direct Connect

For standalone scripts without `@playwright/test` runner.

```typescript
import { chromium } from 'playwright';

const capabilities = {
  browserName: 'Chrome',
  browserVersion: 'latest',
  'LT:Options': {
    platform: 'Windows 11',
    build: 'Standalone Build',
    name: 'My Test',
    user: process.env.LT_USERNAME,
    accessKey: process.env.LT_ACCESS_KEY,
    network: true,
    video: true,
    console: true,
  },
};

(async () => {
  const browser = await chromium.connect({
    wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(
      JSON.stringify(capabilities)
    )}`,
  });
  const page = await browser.newPage();

  try {
    await page.goto('https://example.com');
    const title = await page.title();
    if (title !== 'Example Domain') throw new Error(`Expected 'Example Domain', got '${title}'`);

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'passed', remark: 'Title verified' },
      })}`
    );
  } catch (error) {
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'failed', remark: String(error) },
      })}`
    );
    throw error;
  } finally {
    await browser.close();
  }
})();
```

## Pattern 2: Test Runner Fixture (Recommended)

Creates a custom fixture that intercepts the `page` object. When a project name contains `@lambdatest`, it connects to cloud. Otherwise, runs locally.

**Step 1** — Create `lambdatest-setup.ts`:

```typescript
import { test as base } from '@playwright/test';
import { chromium } from 'playwright';
import { execSync } from 'child_process';

const pwVersion = execSync('npx playwright --version').toString().trim().split(' ')[1];

export const test = base.extend<{}>({
  page: async ({}, use, testInfo) => {
    const projectName = testInfo.project.name;

    if (projectName.includes('@lambdatest')) {
      // Parse "browserName:version:platform@lambdatest"
      const parts = projectName.split('@lambdatest')[0].split(':');
      const capabilities = {
        browserName: parts[0] || 'Chrome',
        browserVersion: parts[1] || 'latest',
        'LT:Options': {
          platform: parts[2] || 'Windows 11',
          build: `PW Build - ${new Date().toISOString().split('T')[0]}`,
          name: testInfo.title,
          user: process.env.LT_USERNAME,
          accessKey: process.env.LT_ACCESS_KEY,
          network: true,
          video: true,
          console: true,
          playwrightClientVersion: pwVersion,
        },
      };

      const browser = await chromium.connect({
        wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(
          JSON.stringify(capabilities)
        )}`,
      });
      const context = await browser.newContext(testInfo.project.use);
      const ltPage = await context.newPage();

      await use(ltPage);

      // Auto-report test status
      const status = testInfo.status === 'passed' ? 'passed' : 'failed';
      const remark = testInfo.error?.message || 'OK';
      await ltPage.evaluate((_) => {},
        `lambdatest_action: ${JSON.stringify({
          action: 'setTestStatus',
          arguments: { status, remark },
        })}`
      );

      await ltPage.close();
      await context.close();
      await browser.close();
    } else {
      // Local execution — use default Playwright page
      const browser = await chromium.launch();
      const context = await browser.newContext();
      const page = await context.newPage();
      await use(page);
      await context.close();
      await browser.close();
    }
  },
});

export { expect } from '@playwright/test';
```

**Step 2** — Add cloud projects to `playwright.config.ts`:

```typescript
projects: [
  // Local
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },

  // Cloud — format: browserName:version:platform@lambdatest
  { name: 'chrome:latest:Windows 11@lambdatest', use: { viewport: { width: 1920, height: 1080 } } },
  { name: 'MicrosoftEdge:latest:macOS Sonoma@lambdatest', use: { viewport: { width: 1920, height: 1080 } } },
  { name: 'pw-webkit:latest:macOS Ventura@lambdatest', use: { viewport: { width: 1920, height: 1080 } } },
],
```

**Step 3** — Import from fixture in tests:

```typescript
// tests/example.spec.ts
import { test, expect } from '../lambdatest-setup';

test('homepage loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading')).toBeVisible();
});
```

**Run:**

```bash
npx playwright test --project=chromium                                  # local
npx playwright test --project="chrome:latest:Windows 11@lambdatest"    # cloud
npx playwright test                                                      # all
```

## Pattern 3: Playwright SDK (Zero Code Changes)

No test code changes required. Cloud config via YAML only.

```bash
npm install -D playwright-node-sdk
```

Create `lambdatest.yml`:

```yaml
user: ${LT_USERNAME}
key: ${LT_ACCESS_KEY}
buildName: "SDK Build"
network: true
video: true
console: true
resolution: "1920x1080"

playwrightConfigOptions:
  testDir: "tests"

platforms:
  - platform: "Windows 11"
    browserName: "chrome"
    browserVersion: "latest"
  - platform: "macOS Sequoia"
    browserName: "pw-webkit"
    browserVersion: "latest"
  - platform: "Windows 10"
    browserName: "pw-firefox"
    browserVersion: "latest"
```

Run:

```bash
npx playwright-node-sdk playwright test
```

## Parallel Cloud Execution

Run across multiple browser/OS combos simultaneously using Pattern 1:

```typescript
import { chromium } from 'playwright';

const browsers = [
  { browserName: 'Chrome', platform: 'Windows 11' },
  { browserName: 'MicrosoftEdge', platform: 'macOS Sonoma' },
  { browserName: 'pw-webkit', platform: 'macOS Ventura' },
];

const runTest = async (config: { browserName: string; platform: string }) => {
  const caps = {
    browserName: config.browserName,
    browserVersion: 'latest',
    'LT:Options': {
      platform: config.platform,
      build: 'Parallel Build',
      name: `Test on ${config.browserName} - ${config.platform}`,
      user: process.env.LT_USERNAME,
      accessKey: process.env.LT_ACCESS_KEY,
      network: true,
      video: true,
    },
  };

  const browser = await chromium.connect({
    wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(
      JSON.stringify(caps)
    )}`,
  });
  const page = await browser.newPage();

  try {
    await page.goto('https://example.com');
    // ... your test logic ...
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'passed', remark: 'OK' },
      })}`
    );
  } catch (e) {
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'failed', remark: String(e) },
      })}`
    );
  } finally {
    await browser.close();
  }
};

// Run all in parallel
Promise.all(browsers.map(runTest));
```

## Hybrid Config (Local + Cloud)

Full `playwright.config.ts` template in [../templates/playwright.config.ts](../templates/playwright.config.ts).

Key design: same tests, different projects. Cloud projects detected by `@lambdatest` suffix.

```bash
# Local only
npx playwright test --project=chromium --project=firefox

# Cloud only
npx playwright test --grep @smoke --project="chrome:latest:Windows 11@lambdatest"

# Everything
npx playwright test
```
