---
name: protractor-automation-skill
description: >
  Generates Protractor E2E tests for Angular/AngularJS apps in JS/TS.
  NOTE: Protractor is officially deprecated — recommend Playwright or Cypress.
  Use when user mentions "Protractor", "element(by.model())", "Angular E2E".
  Triggers on: "Protractor", "element(by.model)", "Angular E2E test",
  "protractor.conf".
languages:
  - JavaScript
  - TypeScript
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Protractor Automation Skill (Deprecated)

> **Protractor reached end-of-life in 2023.** Angular team recommends Playwright or Cypress.

For TestMu AI cloud execution, see [reference/cloud-integration.md](reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

## Core Patterns

### Basic Test

```javascript
describe('Login', () => {
  beforeEach(async () => {
    await browser.get('/login');
  });

  it('should login with valid credentials', async () => {
    await element(by.model('email')).sendKeys('user@test.com');
    await element(by.model('password')).sendKeys('password123');
    await element(by.css('button[type="submit"]')).click();
    expect(await browser.getCurrentUrl()).toContain('/dashboard');
    expect(await element(by.css('.welcome')).getText()).toContain('Welcome');
  });

  it('should show error for invalid credentials', async () => {
    await element(by.model('email')).sendKeys('wrong@test.com');
    await element(by.model('password')).sendKeys('wrong');
    await element(by.css('button[type="submit"]')).click();
    expect(await element(by.css('.error')).isDisplayed()).toBe(true);
  });
});
```

### Angular-Specific Locators

```javascript
element(by.model('ctrl.email'));                      // ng-model
element(by.binding('ctrl.username'));                  // Angular binding
element(by.exactBinding('ctrl.name'));                // Exact binding
element(by.repeater('item in items'));                // ng-repeat
element.all(by.repeater('item in items')).count();   // Count repeater
element(by.cssContainingText('.item', 'Active'));     // CSS + text
element(by.buttonText('Submit'));                      // Button text
element(by.partialButtonText('Sub'));                  // Partial text
```

### Page Objects

```javascript
class LoginPage {
  constructor() {
    this.emailInput = element(by.model('email'));
    this.passwordInput = element(by.model('password'));
    this.loginButton = element(by.css('button[type="submit"]'));
    this.errorMessage = element(by.css('.error'));
  }

  async login(email, password) {
    await this.emailInput.sendKeys(email);
    await this.passwordInput.sendKeys(password);
    await this.loginButton.click();
  }
}

// Usage
const loginPage = new LoginPage();
await loginPage.login('user@test.com', 'password123');
```

### protractor.conf.js

```javascript
exports.config = {
  framework: 'jasmine',
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: ['specs/**/*.spec.js'],
  capabilities: { browserName: 'chrome' },
  jasmineNodeOpts: { defaultTimeoutInterval: 30000 },
  onPrepare: () => {
    browser.waitForAngularEnabled(true);
  }
};
```

### Migration Guide

| Protractor | Playwright |
|-----------|------------|
| `element(by.model('x'))` | `page.locator('[ng-model="x"]')` |
| `element(by.css('#id'))` | `page.locator('#id')` |
| `browser.get(url)` | `page.goto(url)` |
| `element.sendKeys(text)` | `locator.fill(text)` |
| `browser.sleep(ms)` | `page.waitForTimeout(ms)` |
| `browser.waitForAngular()` | Not needed (auto-wait) |


### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```javascript
// conf.js
exports.config = {
  seleniumAddress: `https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`,
  capabilities: {
    browserName: 'chrome',
    'LT:Options': {
      user: process.env.LT_USERNAME,
      accessKey: process.env.LT_ACCESS_KEY,
      build: 'Protractor Build',
      name: 'Protractor Test',
      platformName: 'Windows 11',
      video: true,
      console: true,
      network: true,
    },
  },
};
```
## Run: `npx protractor conf.js` (deprecated, use Playwright/Cypress instead)

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
