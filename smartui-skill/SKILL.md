---
name: smartui-skill
description: >
  Generates SmartUI visual regression test configurations for screenshot
  comparison on TestMu AI cloud. Framework-agnostic — works with Playwright,
  Selenium, Cypress, Puppeteer. Use when user mentions "SmartUI", "visual
  regression", "screenshot comparison", "visual testing". Triggers on:
  "SmartUI", "visual regression", "screenshot comparison", "pixel diff",
  "visual testing LambdaTest".
languages:
  - JavaScript
  - TypeScript
  - Java
category: visual-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# SmartUI Visual Regression Skill

## Core Patterns

### Playwright + SmartUI SDK

```javascript
const { chromium } = require('playwright');
const { smartuiSnapshot } = require('@lambdatest/smartui-cli');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('https://example.com');
  await smartuiSnapshot(page, 'Homepage');

  await page.goto('https://example.com/login');
  await smartuiSnapshot(page, 'Login Page');

  await browser.close();
})();
```

### Selenium + SmartUI

```java
// Take SmartUI screenshot
((JavascriptExecutor) driver).executeScript(
    "smartui.takeScreenshot=Login Page"
);
```

### CLI Execution

```bash
# Install
npm install @lambdatest/smartui-cli --save-dev

# Configure
npx smartui config:create smartui.config.json

# Execute
npx smartui exec -- node test.js
# or with Playwright
npx smartui exec -- npx playwright test
```

### smartui.config.json

```json
{
  "web": {
    "browsers": ["chrome", "firefox", "safari"],
    "viewports": [[1920, 1080], [1366, 768], [375, 812]]
  },
  "waitForPageRender": 5000,
  "waitForTimeout": 1000
}
```

### SmartUI with Storybook

```bash
npx smartui storybook http://localhost:6006 --config smartui.config.json
```

### Approval Workflow

1. First run creates baseline screenshots
2. Subsequent runs compare against baseline
3. Differences highlighted in dashboard
4. Approve/reject changes in LambdaTest SmartUI dashboard
5. Approved screenshots become new baseline

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| No viewport config | Multiple viewports | Responsive issues |
| No wait for render | `waitForPageRender` | Incomplete screenshots |
| Screenshot everything | Key pages/components | Noise reduction |
| No approval process | Review diffs in dashboard | Catch regressions |

### Cloud Authentication

Set environment variables:

```bash
export PROJECT_TOKEN="your-smartui-project-token"   # From SmartUI dashboard
export LT_USERNAME="your-username"                   # For Selenium/Playwright cloud
export LT_ACCESS_KEY="your-access-key"               # For Selenium/Playwright cloud
```

**CLI approach** (uses `PROJECT_TOKEN`):
```bash
npx smartui exec -- npx playwright test
```

**Selenium Cloud approach** (uses `LT_USERNAME`/`LT_ACCESS_KEY`):
```java
// Capabilities include SmartUI options
HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("user", System.getenv("LT_USERNAME"));
ltOptions.put("accessKey", System.getenv("LT_ACCESS_KEY"));
ltOptions.put("build", "SmartUI Build");
ltOptions.put("smartUI.project", "My SmartUI Project");
ChromeOptions options = new ChromeOptions();
options.setCapability("LT:Options", ltOptions);
WebDriver driver = new RemoteWebDriver(
    new URL("https://hub.lambdatest.com/wd/hub"), options);
```

## Quick Reference

| Task | Command |
|------|---------|
| Install | `npm install @lambdatest/smartui-cli` |
| Init config | `npx smartui config:create smartui.config.json` |
| Run | `npx smartui exec -- <test command>` |
| Storybook | `npx smartui storybook <url>` |
| Dashboard | `https://smartui.lambdatest.com` |

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
