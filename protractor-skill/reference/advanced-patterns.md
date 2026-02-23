# Protractor — Advanced Patterns & Playbook

## Page Objects (TypeScript)

```typescript
export class LoginPage {
  private emailInput = element(by.css('#email'));
  private passwordInput = element(by.css('#password'));
  private submitBtn = element(by.buttonText('Sign In'));
  private errorMsg = element(by.css('.error'));

  async navigateTo(): Promise<void> {
    await browser.get('/login');
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.sendKeys(email);
    await this.passwordInput.sendKeys(password);
    await this.submitBtn.click();
    await browser.wait(ExpectedConditions.urlContains('/dashboard'), 10000);
  }

  async getError(): Promise<string> {
    await browser.wait(ExpectedConditions.visibilityOf(this.errorMsg), 5000);
    return this.errorMsg.getText();
  }
}
```

## Angular-Specific Patterns

```typescript
// Wait for Angular
await browser.waitForAngular();

// By binding (AngularJS)
element(by.binding('user.name'));

// By model (AngularJS)
element(by.model('searchQuery')).sendKeys('test');

// Repeater
element.all(by.repeater('item in items')).then(items => {
  expect(items.length).toBeGreaterThan(0);
});

// Non-Angular pages
browser.waitForAngularEnabled(false);
await browser.get('https://non-angular-site.com');
```

## Configuration

```javascript
// conf.js
exports.config = {
  framework: 'jasmine',
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: ['specs/**/*.spec.ts'],
  capabilities: { browserName: 'chrome', chromeOptions: { args: ['--headless'] } },
  jasmineNodeOpts: { defaultTimeoutInterval: 30000 },
  onPrepare: async () => {
    await browser.manage().window().setSize(1920, 1080);
    require('ts-node').register({ project: 'tsconfig.json' });
    const { SpecReporter } = require('jasmine-spec-reporter');
    jasmine.getEnv().addReporter(new SpecReporter({ spec: { displayStacktrace: 'raw' } }));
  }
};
```

## Anti-Patterns

- ❌ `browser.sleep(5000)` — use `browser.wait(EC.visibilityOf(el), timeout)`
- ❌ Mixing async/await with `.then()` chains
- ❌ Not disabling `waitForAngular` on non-Angular pages
- ❌ Note: Protractor is deprecated — consider migrating to Playwright or Cypress
