# SmartUI Visual Regression — Advanced Playbook

## §1 — Project Setup

### CLI Installation & Configuration
```bash
# Install SmartUI CLI
npm install -g @lambdatest/smartui-cli

# Project setup
mkdir smartui-project && cd smartui-project
npm init -y
npm install @lambdatest/smartui-cli playwright @playwright/test --save-dev

# Install browsers
npx playwright install chromium
```

### Project Structure
```
smartui-project/
├── .smartui.json              # SmartUI configuration
├── urls.json                  # Static URL list for crawl mode
├── playwright.config.ts       # Playwright test config
├── tests/
│   ├── visual-homepage.spec.ts
│   ├── visual-login.spec.ts
│   └── visual-components.spec.ts
├── baselines/                 # Reference screenshots
└── reports/                   # Local comparison reports
```

### .smartui.json Configuration
```json
{
  "web": {
    "browsers": [
      "chrome",
      "firefox",
      "safari",
      "edge"
    ],
    "viewports": [
      [1920, 1080],
      [1366, 768],
      [1280, 1024],
      [375, 812],
      [768, 1024]
    ]
  },
  "waitForPageRender": 2000,
  "waitForTimeout": 5000,
  "enableJavaScript": true,
  "allowedHostnames": ["example.com", "cdn.example.com"]
}
```

### Environment Setup
```bash
# Set LambdaTest credentials
export LT_USERNAME="your-username"
export LT_ACCESS_KEY="your-access-key"
export PROJECT_TOKEN="your-smartui-project-token"
```

---

## §2 — Static URL Testing

### urls.json — Crawl Mode
```json
[
  {
    "name": "Homepage",
    "url": "https://example.com/",
    "waitForTimeout": 3000
  },
  {
    "name": "Login Page",
    "url": "https://example.com/login",
    "waitForTimeout": 2000
  },
  {
    "name": "Pricing Page",
    "url": "https://example.com/pricing",
    "waitForTimeout": 2000
  },
  {
    "name": "About Page",
    "url": "https://example.com/about",
    "waitForTimeout": 2000
  },
  {
    "name": "Contact Page",
    "url": "https://example.com/contact",
    "waitForTimeout": 2000
  }
]
```

### Running Static Crawl
```bash
# Execute SmartUI crawl
npx smartui --config .smartui.json capture urls.json

# With custom build name
npx smartui --config .smartui.json capture urls.json --buildName "Release-v2.1"

# With baseline branch
npx smartui --config .smartui.json capture urls.json --buildName "PR-123" --baseline
```

---

## §3 — Playwright Integration

### Playwright Config for SmartUI
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: 'https://example.com',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'mobile-chrome',
      use: {
        browserName: 'chromium',
        viewport: { width: 375, height: 812 },
        isMobile: true,
      },
    },
  ],
});
```

### Basic Visual Tests
```typescript
// tests/visual-homepage.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Homepage Visual Tests', () => {

  test('homepage full page screenshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // SmartUI screenshot via LambdaTest action
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: {
          fullPage: true,
          screenshotName: 'homepage-full',
        },
      })}`
    );
  });

  test('homepage hero section', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.hero-section', { state: 'visible' });

    // Element-level screenshot
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: {
          screenshotName: 'homepage-hero',
          element: '.hero-section',
        },
      })}`
    );
  });

  test('homepage with dynamic content masked', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Hide dynamic elements before screenshot
    await page.evaluate(() => {
      // Hide ads, timestamps, and dynamic counters
      document.querySelectorAll('.ad-banner, .timestamp, .live-counter')
        .forEach(el => (el as HTMLElement).style.visibility = 'hidden');
    });

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: {
          fullPage: true,
          screenshotName: 'homepage-stable',
          ignoreDOM: {
            id: ['ad-container', 'live-chat-widget'],
            class: ['dynamic-timestamp', 'visitor-count'],
          },
        },
      })}`
    );
  });
});
```

### Interactive State Testing
```typescript
// tests/visual-login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login Page Visual States', () => {

  test('login page default state', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: { screenshotName: 'login-default', fullPage: true },
      })}`
    );
  });

  test('login page with validation errors', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"]');
    await page.waitForSelector('.error-message', { state: 'visible' });

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: { screenshotName: 'login-validation-errors', fullPage: true },
      })}`
    );
  });

  test('login page with filled form', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'password123');

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: { screenshotName: 'login-filled', fullPage: true },
      })}`
    );
  });

  test('login page focus states', async ({ page }) => {
    await page.goto('/login');
    await page.focus('[data-testid="email"]');

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: { screenshotName: 'login-focus-state', fullPage: true },
      })}`
    );
  });
});
```

---

## §4 — Component-Level Testing

### Design System Components
```typescript
// tests/visual-components.spec.ts
import { test } from '@playwright/test';

const COMPONENTS = [
  { name: 'button-primary', url: '/storybook/button--primary' },
  { name: 'button-secondary', url: '/storybook/button--secondary' },
  { name: 'button-disabled', url: '/storybook/button--disabled' },
  { name: 'card-default', url: '/storybook/card--default' },
  { name: 'modal-open', url: '/storybook/modal--open' },
  { name: 'form-input', url: '/storybook/input--default' },
  { name: 'dropdown-open', url: '/storybook/dropdown--open' },
  { name: 'alert-success', url: '/storybook/alert--success' },
  { name: 'alert-error', url: '/storybook/alert--error' },
  { name: 'table-default', url: '/storybook/table--default' },
];

test.describe('Design System Visual Tests', () => {
  for (const component of COMPONENTS) {
    test(`visual: ${component.name}`, async ({ page }) => {
      await page.goto(component.url);
      await page.waitForLoadState('networkidle');

      await page.evaluate((_) => {},
        `lambdatest_action: ${JSON.stringify({
          action: 'smartui.takeScreenshot',
          arguments: {
            screenshotName: `component-${component.name}`,
            fullPage: false,
          },
        })}`
      );
    });
  }
});
```

### Responsive Testing
```typescript
// tests/visual-responsive.spec.ts
import { test, devices } from '@playwright/test';

const VIEWPORTS = [
  { name: 'desktop-hd', width: 1920, height: 1080 },
  { name: 'desktop', width: 1366, height: 768 },
  { name: 'tablet-landscape', width: 1024, height: 768 },
  { name: 'tablet-portrait', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 812 },
  { name: 'mobile-small', width: 320, height: 568 },
];

const PAGES = ['/', '/pricing', '/about', '/contact'];

test.describe('Responsive Visual Tests', () => {
  for (const viewport of VIEWPORTS) {
    for (const pagePath of PAGES) {
      test(`${pagePath} at ${viewport.name}`, async ({ browser }) => {
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
        });
        const page = await context.newPage();
        await page.goto(pagePath);
        await page.waitForLoadState('networkidle');

        const slug = pagePath === '/' ? 'home' : pagePath.replace('/', '');
        await page.evaluate((_) => {},
          `lambdatest_action: ${JSON.stringify({
            action: 'smartui.takeScreenshot',
            arguments: {
              screenshotName: `${slug}-${viewport.name}`,
              fullPage: true,
            },
          })}`
        );

        await context.close();
      });
    }
  }
});
```

---

## §5 — Advanced Configuration

### Ignore Regions & DOM Manipulation
```typescript
// Helper function for consistent screenshot setup
async function takeSmartUIScreenshot(
  page: any,
  name: string,
  options: {
    fullPage?: boolean;
    element?: string;
    ignoreSelectors?: string[];
    hideSelectors?: string[];
    removeSelectors?: string[];
    waitMs?: number;
  } = {}
) {
  // Wait for stability
  if (options.waitMs) {
    await page.waitForTimeout(options.waitMs);
  }

  // Hide dynamic elements
  if (options.hideSelectors?.length) {
    await page.evaluate((selectors: string[]) => {
      selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el =>
          (el as HTMLElement).style.visibility = 'hidden'
        );
      });
    }, options.hideSelectors);
  }

  // Remove elements from DOM
  if (options.removeSelectors?.length) {
    await page.evaluate((selectors: string[]) => {
      selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => el.remove());
      });
    }, options.removeSelectors);
  }

  const args: any = {
    screenshotName: name,
    fullPage: options.fullPage ?? true,
  };

  if (options.element) {
    args.element = options.element;
  }

  if (options.ignoreSelectors?.length) {
    args.ignoreDOM = { class: options.ignoreSelectors };
  }

  await page.evaluate((_: any) => {},
    `lambdatest_action: ${JSON.stringify({
      action: 'smartui.takeScreenshot',
      arguments: args,
    })}`
  );
}

// Usage
test('dashboard with stable content', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  await takeSmartUIScreenshot(page, 'dashboard-stable', {
    fullPage: true,
    hideSelectors: ['.timestamp', '.live-data', '.user-avatar'],
    removeSelectors: ['.cookie-banner', '.chat-widget'],
    ignoreSelectors: ['notification-badge', 'graph-canvas'],
    waitMs: 2000,
  });
});
```

### Custom Comparison Thresholds
```json
{
  "web": {
    "browsers": ["chrome"],
    "viewports": [[1920, 1080]]
  },
  "comparison": {
    "threshold": 0.05,
    "largeImageThreshold": 1200,
    "ignoreAntialiasing": true,
    "ignoreColors": false,
    "transparency": 0.3,
    "boundingBoxes": [
      { "left": 0, "top": 0, "right": 200, "bottom": 80 }
    ],
    "ignoredBoxes": [
      { "left": 800, "top": 400, "right": 1100, "bottom": 600 }
    ]
  }
}
```

---

## §6 — Selenium Integration

### Selenium Java with SmartUI
```java
public class SmartUISeleniumTest {
    private RemoteWebDriver driver;

    @BeforeEach
    void setup() {
        String username = System.getenv("LT_USERNAME");
        String accessKey = System.getenv("LT_ACCESS_KEY");

        ChromeOptions options = new ChromeOptions();
        options.setPlatformName("Windows 11");
        options.setBrowserVersion("latest");

        Map<String, Object> ltOptions = new HashMap<>();
        ltOptions.put("build", "smartui-selenium");
        ltOptions.put("name", "Visual Test");
        ltOptions.put("smartUI.project", "My Project");
        ltOptions.put("smartUI.build", "build-" + System.getenv("BUILD_ID"));

        options.setCapability("LT:Options", ltOptions);

        driver = new RemoteWebDriver(
            new URL("https://" + username + ":" + accessKey + "@hub.lambdatest.com/wd/hub"),
            options
        );
    }

    @Test
    void homepageVisual() {
        driver.get("https://example.com");
        // Wait for content
        new WebDriverWait(driver, Duration.ofSeconds(10))
            .until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("h1")));

        // Take SmartUI screenshot
        driver.executeScript("smartui.takeScreenshot=homepage-full");
    }

    @Test
    void loginPageVisual() {
        driver.get("https://example.com/login");
        new WebDriverWait(driver, Duration.ofSeconds(10))
            .until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='email']")));

        driver.executeScript("smartui.takeScreenshot=login-default");

        // Fill form and capture another state
        driver.findElement(By.cssSelector("[data-testid='email']")).sendKeys("user@test.com");
        driver.executeScript("smartui.takeScreenshot=login-filled");
    }

    @AfterEach
    void teardown() {
        if (driver != null) driver.quit();
    }
}
```

### Cypress Integration
```javascript
// cypress/e2e/visual.cy.js
describe('Visual Regression Tests', () => {
  it('homepage visual check', () => {
    cy.visit('/');
    cy.get('h1').should('be.visible');

    // SmartUI screenshot
    cy.window().then((win) => {
      win.eval(`lambdatest_action: ${JSON.stringify({
        action: 'smartui.takeScreenshot',
        arguments: { screenshotName: 'homepage', fullPage: true },
      })}`);
    });
  });
});
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: SmartUI Visual Tests
on:
  pull_request:
    branches: [main]

jobs:
  visual-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci && npx playwright install chromium

      - name: Run SmartUI tests
        run: |
          npx smartui --config .smartui.json \
            exec -- npx playwright test tests/visual-*.spec.ts
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
          PROJECT_TOKEN: ${{ secrets.SMARTUI_PROJECT_TOKEN }}
          BUILD_NAME: "PR-${{ github.event.pull_request.number }}"

      - name: Static URL crawl
        run: |
          npx smartui --config .smartui.json capture urls.json \
            --buildName "crawl-PR-${{ github.event.pull_request.number }}"
        env:
          PROJECT_TOKEN: ${{ secrets.SMARTUI_PROJECT_TOKEN }}

      - name: Post results to PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## SmartUI Visual Test Results\nCheck the [SmartUI Dashboard](https://smartui.lambdatest.com/) for visual comparison results.'
            });
```

### Pre-Release Visual Gate
```yaml
# Run before deployment
visual-gate:
  runs-on: ubuntu-latest
  needs: [build]
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: 20, cache: npm }
    - run: npm ci && npx playwright install chromium

    - name: Run visual tests against staging
      run: |
        npx smartui --config .smartui.json \
          exec -- npx playwright test tests/visual-*.spec.ts
      env:
        BASE_URL: "https://staging.example.com"
        PROJECT_TOKEN: ${{ secrets.SMARTUI_PROJECT_TOKEN }}
        LT_USERNAME: ${{ secrets.LT_USERNAME }}
        LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Screenshots show blank page | Page not fully loaded before capture | Add `waitForLoadState('networkidle')` and `waitForTimeout(2000)` before screenshot |
| 2 | False positives on every run | Dynamic content (timestamps, ads, counters) | Use `ignoreDOM`, `hideSelectors`, or mask dynamic elements before capture |
| 3 | Comparison threshold too sensitive | Default threshold catches anti-aliasing | Set `"threshold": 0.1` or `"ignoreAntialiasing": true` in config |
| 4 | Missing baselines | First run has no reference to compare | First run creates baselines; approve them in SmartUI dashboard |
| 5 | Font rendering differences | Cross-browser font smoothing varies | Test same browser; or increase threshold for text-heavy areas |
| 6 | `PROJECT_TOKEN` invalid | Token expired or wrong project | Regenerate token in SmartUI dashboard settings |
| 7 | Screenshots not captured in CI | Missing `npx smartui exec --` wrapper | Wrap test command with `npx smartui --config .smartui.json exec --` |
| 8 | Viewport mismatch between runs | Different `viewports` in config | Pin viewport config in `.smartui.json`; match in Playwright config |
| 9 | Elements shifted between comparisons | Lazy-loaded images change layout | Use `waitForLoadState('networkidle')` and explicit element waits |
| 10 | Cookie/GDPR banner in screenshots | Banner appears inconsistently | Remove or dismiss banners before screenshot; add to `removeSelectors` |
| 11 | Build not appearing in dashboard | Credentials not set in env | Verify `LT_USERNAME`, `LT_ACCESS_KEY`, `PROJECT_TOKEN` are exported |
| 12 | Screenshots identical but marked diff | Sub-pixel rendering or scrollbar | Set explicit viewport, hide scrollbars via CSS, use `ignoreAntialiasing` |

---

## §9 — Best Practices Checklist

1. **Wait for network idle** — always `waitForLoadState('networkidle')` before screenshots
2. **Mask dynamic content** — hide timestamps, ads, avatars, live data before capture
3. **Test all breakpoints** — include desktop, tablet, and mobile viewports in config
4. **Name screenshots descriptively** — `login-validation-error` not `screenshot-1`
5. **Run on every PR** — catch visual regressions before merge
6. **Use element-level screenshots** — isolate component testing from full-page noise
7. **Set appropriate thresholds** — 0.05-0.1 for strict; 0.2+ for pages with animation
8. **Approve baselines deliberately** — review first-run baselines in SmartUI dashboard
9. **Helper functions for consistency** — centralize screenshot logic with `takeSmartUIScreenshot()`
10. **Cross-browser visual testing** — test Chrome, Firefox, Safari, Edge in config
11. **Component library testing** — screenshot each design system component individually
12. **CI as visual gate** — block deployments on unapproved visual changes
13. **Remove interfering overlays** — dismiss cookie banners, chat widgets, tooltips
14. **Version your config** — commit `.smartui.json` to source control for reproducibility
