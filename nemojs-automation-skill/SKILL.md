---
name: nemojs-automation-skill
description: >
  Generates Nemo.js automation tests in JavaScript. PayPal's Selenium-based
  test framework for Node.js. Use when user mentions "Nemo.js", "nemo
  automation". Triggers on: "Nemo.js", "nemo automation", "nemo test",
  "PayPal test framework".
languages:
  - JavaScript
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Nemo.js Automation Skill

> PayPal's Selenium-based test automation framework for Node.js.

For TestMu AI cloud execution, see [reference/cloud-integration.md](reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

## Core Patterns

### Basic Test (Mocha)

```javascript
const Nemo = require('nemo');
const { expect } = require('chai');

describe('Login Flow', function() {
  this.timeout(30000);
  let nemo;

  before(async () => {
    nemo = await Nemo();
  });

  after(async () => {
    await nemo.driver.quit();
  });

  it('should login with valid credentials', async () => {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    const email = await nemo.view._find('#email');
    await email.sendKeys('user@test.com');
    const password = await nemo.view._find('#password');
    await password.sendKeys('password123');
    await nemo.view._find('button[type="submit"]').click();

    await nemo.view._waitVisible('.dashboard', 10000);
    const url = await nemo.driver.getCurrentUrl();
    expect(url).to.include('/dashboard');
  });

  it('should show error for invalid credentials', async () => {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    await nemo.view._find('#email').sendKeys('wrong@test.com');
    await nemo.view._find('#password').sendKeys('wrong');
    await nemo.view._find('button[type="submit"]').click();

    await nemo.view._waitVisible('.error', 5000);
    const error = await nemo.view._find('.error');
    const text = await error.getText();
    expect(text).to.include('Invalid');
  });
});
```

### View Locators

```javascript
await nemo.view._find('#css-id');                    // CSS
await nemo.view._find('.class-name');                // CSS class
await nemo.view._find('[data-testid="login"]');     // Data attribute
await nemo.view._find('xpath://button[@type]');     // XPath prefix
await nemo.view._waitVisible(locator, timeout);     // Wait + find
await nemo.view._finds('.items');                    // Find multiple
```

### Configuration (nemo.config.json)

```json
{
  "driver": {
    "browser": "chrome",
    "server": "http://localhost:4444/wd/hub"
  },
  "data": {
    "baseUrl": "http://localhost:3000"
  },
  "view": ["locator"],
  "plugins": {
    "view": { "module": "nemo-view" }
  }
}
```

### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```json
{
  "driver": {
    "browser": "chrome",
    "server": "https://hub.lambdatest.com/wd/hub",
    "serverCaps": {
      "username": "${LT_USERNAME}",
      "accessKey": "${LT_ACCESS_KEY}"
    },
    "capabilities": {
      "LT:Options": {
        "user": "${LT_USERNAME}",
        "accessKey": "${LT_ACCESS_KEY}",
        "build": "Nemo Build",
        "name": "Nemo Test",
        "platformName": "Windows 11",
        "video": true,
        "console": true,
        "network": true
      }
    }
  }
}
```

## Setup: `npm install nemo nemo-view --save-dev`
## Run: `npx mocha test/*.js --timeout 30000`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
