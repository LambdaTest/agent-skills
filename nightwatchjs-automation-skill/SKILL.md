---
name: nightwatchjs-automation-skill
description: >
  Generates NightwatchJS E2E tests in JavaScript. Integrated test runner with
  Selenium WebDriver, built-in assertions, and page objects. Use when user
  mentions "Nightwatch", "NightwatchJS", "nightwatch.conf.js". Triggers on:
  "Nightwatch", "NightwatchJS", "nightwatch test".
languages:
  - JavaScript
  - TypeScript
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# NightwatchJS Automation Skill

## Step 1 — Execution Target

```
├─ "cloud", "TestMu", "LambdaTest" → Cloud: nightwatch.conf.js with LT env
├─ "local" → Local: ChromeDriver/GeckoDriver
└─ Default → Local, mention cloud option
```

## Core Patterns

### Basic Test

```javascript
module.exports = {
  'Login with valid credentials': function(browser) {
    browser
      .url('http://localhost:3000/login')
      .waitForElementVisible('#email', 5000)
      .setValue('#email', 'user@test.com')
      .setValue('#password', 'password123')
      .click('button[type="submit"]')
      .waitForElementVisible('.dashboard', 10000)
      .assert.containsText('.welcome', 'Welcome')
      .assert.urlContains('/dashboard')
      .end();
  },

  'Login with invalid credentials shows error': function(browser) {
    browser
      .url('http://localhost:3000/login')
      .waitForElementVisible('#email', 5000)
      .setValue('#email', 'wrong@test.com')
      .setValue('#password', 'wrong')
      .click('button[type="submit"]')
      .waitForElementVisible('.error-message', 5000)
      .assert.containsText('.error-message', 'Invalid credentials')
      .end();
  }
};
```

### Page Objects

```javascript
// pages/loginPage.js
module.exports = {
  url: '/login',
  elements: {
    emailInput: '#email',
    passwordInput: '#password',
    loginButton: 'button[type="submit"]',
    errorMessage: '.error-message',
  },
  commands: [{
    login(email, password) {
      return this
        .setValue('@emailInput', email)
        .setValue('@passwordInput', password)
        .click('@loginButton');
    }
  }]
};

// tests/loginTest.js
module.exports = {
  'Login test': function(browser) {
    const login = browser.page.loginPage();
    login.navigate()
      .login('user@test.com', 'password123');
    browser.assert.urlContains('/dashboard');
  }
};
```

### Assertions

```javascript
browser.assert.visible(selector);
browser.assert.not.visible(selector);
browser.assert.containsText(selector, 'text');
browser.assert.urlContains('/path');
browser.assert.titleContains('Page Title');
browser.assert.elementPresent(selector);
browser.assert.cssClassPresent(selector, 'active');
browser.assert.value('#input', 'expected');
browser.assert.attributeEquals(selector, 'href', '/link');
browser.assert.elementsCount('li', 5);
```

### TestMu AI Cloud Config

For full capabilities and shared reference, see [reference/cloud-integration.md](reference/cloud-integration.md).

```javascript
// nightwatch.conf.js
module.exports = {
  test_settings: {
    default: {
      launch_url: 'http://localhost:3000',
      desiredCapabilities: { browserName: 'chrome' }
    },
    lambdatest: {
      selenium: {
        host: 'hub.lambdatest.com',
        port: 80
      },
      desiredCapabilities: {
        browserName: 'chrome',
        browserVersion: 'latest',
        'LT:Options': {
          platform: 'Windows 11',
          build: 'Nightwatch Build',
          name: 'Login Tests',
          user: process.env.LT_USERNAME,
          accessKey: process.env.LT_ACCESS_KEY,
          video: true, console: true, network: true
        }
      }
    }
  },
  page_objects_path: ['pages/'],
};
```

## Setup: `npm install nightwatch --save-dev`
## Run: `npx nightwatch` or `npx nightwatch --env lambdatest`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
