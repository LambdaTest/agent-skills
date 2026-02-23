# Appium — JavaScript/WebdriverIO Patterns

## Setup

```bash
npm init wdio@latest  # Select Appium service
npm install @wdio/appium-service --save-dev
```

## Config (wdio.conf.js)

```javascript
exports.config = {
    runner: 'local',
    port: 4723,
    path: '/',
    services: ['appium'],
    capabilities: [{
        platformName: 'Android',
        'appium:deviceName': 'emulator-5554',
        'appium:app': '/path/to/app.apk',
        'appium:automationName': 'UiAutomator2',
    }],
    framework: 'mocha',
    mochaOpts: { timeout: 60000 },
};
```

## Test

```javascript
describe('Login', () => {
    it('should login successfully', async () => {
        const email = await $('~emailInput');  // ~ = accessibilityId
        await email.setValue('user@test.com');
        await $('~passwordInput').setValue('password123');
        await $('~loginButton').click();
        await expect($('~dashboard')).toBeDisplayed();
    });
});
```

## Cloud Config

```javascript
capabilities: [{
    platformName: 'Android',
    'appium:deviceName': 'Pixel 7',
    'appium:platformVersion': '13',
    'appium:app': 'lt://APP1234567890',
    'appium:automationName': 'UiAutomator2',
    'LT:Options': {
        w3c: true, build: 'WDIO Appium Build',
        isRealMobile: true, video: true,
    }
}],
hostname: 'mobile-hub.lambdatest.com',
port: 80,
user: process.env.LT_USERNAME,
key: process.env.LT_ACCESS_KEY,
```
