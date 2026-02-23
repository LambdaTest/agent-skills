# Selenium — JavaScript/Node.js Patterns

## Setup

```bash
npm install selenium-webdriver mocha chai
```

## Basic Test (Mocha)

```javascript
const { Builder, By, until } = require('selenium-webdriver');
const { expect } = require('chai');

describe('Login', function() {
    let driver;
    this.timeout(30000);

    before(async () => {
        driver = await new Builder().forBrowser('chrome').build();
    });

    it('should login successfully', async () => {
        await driver.get('https://example.com/login');
        await driver.wait(until.elementLocated(By.id('username')), 10000);
        await driver.findElement(By.id('username')).sendKeys('user@test.com');
        await driver.findElement(By.id('password')).sendKeys('password123');
        await driver.findElement(By.css("button[type='submit']")).click();
        await driver.wait(until.urlContains('/dashboard'), 10000);
        const title = await driver.getTitle();
        expect(title).to.include('Dashboard');
    });

    after(async () => {
        if (driver) await driver.quit();
    });
});
```

## TestMu AI Cloud (Node.js)

```javascript
const { Builder } = require('selenium-webdriver');

const capabilities = {
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
        platform: 'Windows 11',
        build: 'Node Build',
        name: 'Node Test',
        user: process.env.LT_USERNAME,
        accessKey: process.env.LT_ACCESS_KEY,
        video: true,
        network: true,
    }
};

const driver = await new Builder()
    .usingServer(`https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`)
    .withCapabilities(capabilities)
    .build();
```
