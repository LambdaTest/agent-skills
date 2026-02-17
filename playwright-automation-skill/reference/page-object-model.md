# Page Object Model — Playwright

## Table of Contents
- When to Use POM
- Base Page Class
- Concrete Page Objects
- Custom Fixtures
- Full Test Example
- Multi-Page Flows

## When to Use POM

| Situation | Use POM? |
|---|---|
| One-off script, <3 tests | No — inline selectors |
| Test suite with shared pages | Yes |
| Team project | Yes |
| User has existing POM structure | Match theirs |

## Base Page Class

```typescript
// pages/base.page.ts
import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string) {
    await this.page.goto(path);
  }

  async getTitle(): Promise<string> {
    return this.page.title();
  }

  // Common components
  get header() {
    return this.page.getByRole('banner');
  }

  get footer() {
    return this.page.getByRole('contentinfo');
  }

  get mainNav() {
    return this.page.getByRole('navigation', { name: 'Main' });
  }
}
```

## Concrete Page Objects

```typescript
// pages/login.page.ts
import { Page, Locator } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password' });
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async goto() {
    await this.navigate('/login');
  }
}
```

```typescript
// pages/dashboard.page.ts
import { Page, Locator } from '@playwright/test';
import { BasePage } from './base.page';

export class DashboardPage extends BasePage {
  readonly welcomeHeading: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.welcomeHeading = page.getByRole('heading', { name: /Welcome/ });
    this.userMenu = page.getByRole('button', { name: 'User menu' });
    this.logoutButton = page.getByRole('menuitem', { name: 'Logout' });
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }

  async goto() {
    await this.navigate('/dashboard');
  }
}
```

## Custom Fixtures

Inject page objects via Playwright fixtures for automatic setup:

```typescript
// fixtures/pages.fixture.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { DashboardPage } from '../pages/dashboard.page';

type Pages = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<Pages>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect } from '@playwright/test';
```

## Full Test Example

```typescript
// tests/auth.spec.ts
import { test, expect } from '../fixtures/pages.fixture';

test.describe('Authentication', () => {
  test('successful login redirects to dashboard', async ({ loginPage, dashboardPage }) => {
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await expect(dashboardPage.welcomeHeading).toBeVisible();
  });

  test('invalid credentials show error', async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.login('bad@example.com', 'wrong');
    await expect(loginPage.errorMessage).toHaveText('Invalid credentials');
  });

  test('logout returns to login', async ({ loginPage, dashboardPage, page }) => {
    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await dashboardPage.logout();
    await expect(page).toHaveURL('/login');
  });
});
```

## Multi-Page Flows

For flows spanning multiple pages, chain page objects:

```typescript
test('complete purchase flow', async ({ page }) => {
  const catalog = new CatalogPage(page);
  const cart = new CartPage(page);
  const checkout = new CheckoutPage(page);
  const confirmation = new ConfirmationPage(page);

  await test.step('Browse and add to cart', async () => {
    await catalog.goto();
    await catalog.addProduct('Blue T-Shirt');
  });

  await test.step('Review cart', async () => {
    await cart.goto();
    await expect(cart.itemCount).toHaveText('1');
  });

  await test.step('Complete checkout', async () => {
    await checkout.goto();
    await checkout.fillShipping({ name: 'John', address: '123 Main St' });
    await checkout.fillPayment({ card: '4111111111111111' });
    await checkout.submit();
  });

  await test.step('Verify confirmation', async () => {
    await expect(confirmation.orderNumber).toBeVisible();
  });
});
```
