/**
 * lambdatest-setup.ts — TestMu AI cloud fixture for Playwright Test Runner.
 *
 * How it works:
 *   - Projects with "@lambdatest" in the name connect to TestMu AI cloud.
 *   - Projects without "@lambdatest" run locally (default Playwright behavior).
 *   - Project name format: browserName:version:platform@lambdatest
 *   - Test status is auto-reported to TestMu AI dashboard.
 *
 * Usage in tests:
 *   import { test, expect } from '../lambdatest-setup';
 *
 * Run:
 *   npx playwright test --project=chromium                              # local
 *   npx playwright test --project="chrome:latest:Windows 11@lambdatest" # cloud
 */

import { test as base } from '@playwright/test';
import { chromium } from 'playwright';
import { execSync } from 'child_process';

const pwVersion = execSync('npx playwright --version').toString().trim().split(' ')[1];

export const test = base.extend<{}>({
  page: async ({}, use, testInfo) => {
    const projectName = testInfo.project.name;

    if (projectName.includes('@lambdatest')) {
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
      await ltPage.evaluate(
        (_: any) => {},
        `lambdatest_action: ${JSON.stringify({
          action: 'setTestStatus',
          arguments: { status, remark },
        })}`
      );

      await ltPage.close();
      await context.close();
      await browser.close();
    } else {
      // Local execution — default Playwright behavior
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
