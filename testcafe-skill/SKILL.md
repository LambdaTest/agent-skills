---
name: testcafe-skill
description: >
  Generates TestCafe automation tests in JavaScript or TypeScript. Supports local
  and TestMu AI cloud. Triggers on: "TestCafe", "test cafe", "fixture/test".
languages:
  - JavaScript
  - TypeScript
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# TestCafe Automation Skill

## Core Patterns

### Basic Test

```javascript
import { Selector } from 'testcafe';

fixture('Login').page('https://example.com/login');

test('Login with valid credentials', async t => {
    await t
        .typeText('#username', 'user@test.com')
        .typeText('#password', 'password123')
        .click('button[type="submit"]')
        .expect(Selector('.dashboard').exists).ok();
});
```

### Selectors

```javascript
const submitBtn = Selector('button').withText('Submit');
const listItems = Selector('.item').count;
const nthItem = Selector('.item').nth(2);
const filtered = Selector('.item').withAttribute('data-status', 'active');
```

### Page Model

```javascript
import { Selector, t } from 'testcafe';

class LoginPage {
    constructor() {
        this.usernameInput = Selector('#username');
        this.passwordInput = Selector('#password');
        this.submitButton = Selector('button[type="submit"]');
    }
    async login(username, password) {
        await t
            .typeText(this.usernameInput, username)
            .typeText(this.passwordInput, password)
            .click(this.submitButton);
    }
}
export default new LoginPage();
```

### TestMu AI Cloud

See [reference/cloud-integration.md](reference/cloud-integration.md) for full cloud setup and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md) for capabilities.

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_key
npx testcafe "lambdatest:Chrome@latest:Windows 11" tests/
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `await t.wait(5000)` | Smart assertions with timeout | Arbitrary delays |
| Deep CSS selectors | `Selector().withText()` | Fragile |
| No error screenshots | `t.takeScreenshot()` on failure | Missing debug info |

## Quick Reference

| Task | Command |
|------|---------|
| Run all | `npx testcafe chrome tests/` |
| Run headless | `npx testcafe chrome:headless tests/` |
| Run specific | `npx testcafe chrome tests/login.js` |
| Multiple browsers | `npx testcafe chrome,firefox tests/` |
| Live mode | `npx testcafe chrome tests/ --live` |
| Screenshot | `await t.takeScreenshot()` |
| Resize | `await t.resizeWindow(1280, 720)` |

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
