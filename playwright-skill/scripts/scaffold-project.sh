#!/bin/bash
# scaffold-project.sh — Generate a Playwright project structure
# Usage: bash scaffold-project.sh [project-name] [--cloud]
#
# Exit codes:
#   0 = success
#   1 = npm not found
#   2 = directory already exists

set -e

PROJECT_NAME="${1:-playwright-tests}"
CLOUD_ENABLED=false

if [[ "$2" == "--cloud" ]] || [[ "$1" == "--cloud" ]]; then
    CLOUD_ENABLED=true
    if [[ "$1" == "--cloud" ]]; then
        PROJECT_NAME="playwright-tests"
    fi
fi

echo "🎭 Scaffolding Playwright project: $PROJECT_NAME"
echo "   Cloud integration: $CLOUD_ENABLED"

# Check prerequisites
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Install Node.js from https://nodejs.org"
    exit 1
fi

if [ -d "$PROJECT_NAME" ]; then
    echo "❌ Directory '$PROJECT_NAME' already exists."
    echo "   Choose a different name or delete the existing directory."
    exit 2
fi

# Create structure
mkdir -p "$PROJECT_NAME"/{tests,pages,fixtures,utils}
cd "$PROJECT_NAME"

echo "📦 Initializing npm project..."
npm init -y > /dev/null 2>&1
npm install -D @playwright/test typescript > /dev/null 2>&1

echo "🌐 Installing browsers..."
npx playwright install --with-deps chromium > /dev/null 2>&1

# tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "."
  },
  "include": ["tests/**/*.ts", "pages/**/*.ts", "fixtures/**/*.ts"]
}
EOF

# playwright.config.ts
cat > playwright.config.ts << 'EOF'
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
EOF

# Base page
cat > pages/base.page.ts << 'EOF'
import { Page } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string) {
    await this.page.goto(path);
  }
}
EOF

# Example page object
cat > pages/home.page.ts << 'EOF'
import { Page, Locator } from '@playwright/test';
import { BasePage } from './base.page';

export class HomePage extends BasePage {
  readonly heading: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { level: 1 });
  }

  async goto() {
    await this.navigate('/');
  }
}
EOF

# Fixtures
cat > fixtures/pages.fixture.ts << 'EOF'
import { test as base } from '@playwright/test';
import { HomePage } from '../pages/home.page';

type Pages = {
  homePage: HomePage;
};

export const test = base.extend<Pages>({
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
});

export { expect } from '@playwright/test';
EOF

# Example test
cat > tests/home.spec.ts << 'EOF'
import { test, expect } from '../fixtures/pages.fixture';

test.describe('Home Page', () => {
  test('should display heading', async ({ homePage }) => {
    await homePage.goto();
    await expect(homePage.heading).toBeVisible();
  });
});
EOF

# Cloud setup (if enabled)
if [ "$CLOUD_ENABLED" = true ]; then
    echo "☁️  Adding TestMu AI cloud integration..."

    cat > lambdatest-setup.ts << 'CLOUDEOF'
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
          network: true, video: true, console: true,
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

      const status = testInfo.status === 'passed' ? 'passed' : 'failed';
      await ltPage.evaluate((_: any) => {},
        `lambdatest_action: ${JSON.stringify({
          action: 'setTestStatus',
          arguments: { status, remark: testInfo.error?.message || 'OK' },
        })}`
      );
      await ltPage.close();
      await context.close();
      await browser.close();
    } else {
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
CLOUDEOF

    echo ""
    echo "   Add cloud projects to playwright.config.ts projects array:"
    echo "   { name: 'chrome:latest:Windows 11@lambdatest', use: { viewport: { width: 1920, height: 1080 } } },"
fi

# .gitignore
cat > .gitignore << 'EOF'
node_modules/
test-results/
playwright-report/
dist/
*.env
EOF

echo ""
echo "✅ Project scaffolded successfully!"
echo ""
echo "   cd $PROJECT_NAME"
echo "   npx playwright test              # Run tests"
echo "   npx playwright test --ui         # Interactive mode"
echo "   npx playwright test --debug      # Debug mode"
if [ "$CLOUD_ENABLED" = true ]; then
    echo ""
    echo "   ☁️  Cloud setup:"
    echo "   export LT_USERNAME=your_username"
    echo "   export LT_ACCESS_KEY=your_access_key"
    echo "   npx playwright test --project='chrome:latest:Windows 11@lambdatest'"
fi
