import { defineConfig, devices } from '@playwright/test';

/**
 * Hybrid Playwright config — local + TestMu AI cloud projects.
 *
 * Local:  npx playwright test --project=chromium
 * Cloud:  npx playwright test --project="chrome:latest:Windows 11@lambdatest"
 * All:    npx playwright test
 *
 * Cloud projects require:
 *   export LT_USERNAME=your_username
 *   export LT_ACCESS_KEY=your_access_key
 *
 * Cloud project naming: browserName:version:platform@lambdatest
 * Parsed by lambdatest-setup.ts fixture.
 */
export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    // ── Local browsers ──────────────────────────────────
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },

    // ── TestMu AI Cloud ─────────────────────────────────
    // Format: browserName:version:platform@lambdatest
    // Requires lambdatest-setup.ts fixture
    {
      name: 'chrome:latest:Windows 11@lambdatest',
      use: { viewport: { width: 1920, height: 1080 } },
    },
    {
      name: 'MicrosoftEdge:latest:Windows 10@lambdatest',
      use: { viewport: { width: 1920, height: 1080 } },
    },
    {
      name: 'pw-webkit:latest:macOS Sonoma@lambdatest',
      use: { viewport: { width: 1920, height: 1080 } },
    },
    {
      name: 'pw-firefox:latest:macOS Ventura@lambdatest',
      use: { viewport: { width: 1920, height: 1080 } },
    },
  ],

  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
