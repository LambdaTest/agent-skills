---
name: detox-automation-skill
description: >
  Generates Detox E2E tests for React Native apps in JavaScript. Gray-box testing
  framework with automatic synchronization. Supports local simulators/emulators
  and TestMu AI cloud. Use when user mentions "Detox", "React Native test",
  "element(by.id())", "device.launchApp". Triggers on: "Detox", "React Native E2E",
  "React Native test", "element(by.id)", "device.launchApp".
languages:
  - JavaScript
  - TypeScript
category: mobile-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Detox Automation Skill

You are a senior React Native QA engineer specializing in Detox.

## Core Patterns

### Basic Test

```javascript
describe('Login', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should login with valid credentials', async () => {
    await element(by.id('emailInput')).typeText('user@test.com');
    await element(by.id('passwordInput')).typeText('password123');
    await element(by.id('loginButton')).tap();
    await expect(element(by.id('dashboardTitle'))).toBeVisible();
    await expect(element(by.text('Welcome'))).toBeVisible();
  });

  it('should show error for invalid credentials', async () => {
    await element(by.id('emailInput')).typeText('wrong@test.com');
    await element(by.id('passwordInput')).typeText('wrong');
    await element(by.id('loginButton')).tap();
    await expect(element(by.id('errorMessage'))).toBeVisible();
  });
});
```

### Matchers (Finding Elements)

```javascript
element(by.id('uniqueId'))                    // testID prop (best)
element(by.text('Login'))                      // Text content
element(by.label('Submit'))                    // Accessibility label
element(by.type('RCTTextInput'))              // Native type
element(by.traits(['button']))                 // iOS traits

// Combined
element(by.id('list').withDescendant(by.text('Item 1')))
element(by.id('item').withAncestor(by.id('list')))

// At index (multiple matches)
element(by.text('Delete')).atIndex(0)
```

### Actions

```javascript
await element(by.id('btn')).tap();
await element(by.id('btn')).longPress();
await element(by.id('btn')).multiTap(3);
await element(by.id('input')).typeText('hello');
await element(by.id('input')).replaceText('new text');
await element(by.id('input')).clearText();
await element(by.id('scrollView')).scroll(200, 'down');
await element(by.id('scrollView')).scrollTo('bottom');
await element(by.id('item')).swipe('left', 'fast');
await element(by.id('input')).tapReturnKey();
```

### Expectations

```javascript
await expect(element(by.id('title'))).toBeVisible();
await expect(element(by.id('title'))).not.toBeVisible();
await expect(element(by.id('title'))).toExist();
await expect(element(by.id('title'))).toHaveText('Welcome');
await expect(element(by.id('toggle'))).toHaveToggleValue(true);
await expect(element(by.id('input'))).toHaveValue('hello');
```

### Device Control

```javascript
await device.launchApp({ newInstance: true });
await device.reloadReactNative();
await device.sendToHome();
await device.terminateApp();
await device.installApp();
await device.shake();                       // Shake gesture
await device.setLocation(37.7749, -122.4194); // GPS
await device.setURLBlacklist(['.*cdn.example.*']); // Block URLs
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `waitFor().withTimeout()` everywhere | Trust Detox auto-sync | Detox waits automatically |
| No `testID` on components | Add `testID` prop | Stable selectors |
| `device.launchApp()` in every test | `device.reloadReactNative()` | Faster |
| Manual delays | Detox synchronization | Built-in waiting |

### .detoxrc.js Configuration

```javascript
module.exports = {
  testRunner: { args: { config: 'e2e/jest.config.js' } },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/MyApp.app',
      build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build',
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
      reversePorts: [8081],
    },
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 16' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_7_API_34' } },
  },
  configurations: {
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' },
  },
};
```

## Cloud Execution on TestMu AI

Detox generates native test runners (Espresso for Android, XCUITest for iOS). Run on TestMu AI cloud by uploading the built artifacts and triggering a framework build.

### Android (Espresso) Cloud Run

```bash
# 1. Build the app and test APKs
detox build --configuration android.emu.debug

# 2. Upload app APK
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@android/app/build/outputs/apk/debug/app-debug.apk" \
  -F "name=DetoxApp"
# Response: {"app_url": "lt://APP_ID", ...}

# 3. Upload test APK
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk" \
  -F "name=DetoxTestSuite"
# Response: {"app_url": "lt://TEST_SUITE_ID", ...}

# 4. Trigger Espresso build
curl -X POST "https://mobile-api.lambdatest.com/framework/v1/espresso/build" \
  -H "Authorization: Basic <BASE64_AUTH>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "lt://APP_ID",
    "testSuite": "lt://TEST_SUITE_ID",
    "device": ["Galaxy S21 5G-12", "Pixel 6-12"],
    "build": "Detox-Android",
    "deviceLog": true,
    "video": true
  }'
```

### iOS (XCUITest) Cloud Run

```bash
# 1. Build the iOS app and test runner
detox build --configuration ios.sim.release

# 2. Create .ipa from the build artifacts, then upload
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@MyApp.ipa" -F "name=DetoxApp"

# 3. Upload test runner .ipa
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@MyAppTests-Runner.ipa" -F "name=DetoxTestSuite"

# 4. Trigger XCUITest build
curl -X POST "https://mobile-api.lambdatest.com/framework/v1/xcui/build" \
  -H "Authorization: Basic <BASE64_AUTH>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "lt://APP_ID",
    "testSuite": "lt://TEST_SUITE_ID",
    "device": ["iPhone 14-16", "iPhone 13-15"],
    "build": "Detox-iOS",
    "devicelog": true,
    "video": true
  }'
```

## Quick Reference

| Task | Command |
|------|---------|
| Build iOS | `detox build --configuration ios.sim.debug` |
| Test iOS | `detox test --configuration ios.sim.debug` |
| Build Android | `detox build --configuration android.emu.debug` |
| Test Android | `detox test --configuration android.emu.debug` |
| Specific test | `detox test --configuration ios.sim.debug e2e/login.test.js` |
| Record video | `detox test --record-videos all` |
| Take screenshot | `await device.takeScreenshot('login-page')` |

## Setup

```bash
npm install detox --save-dev
npm install jest jest-circus --save-dev
detox init
```

## React Native Component Setup

```jsx
// Add testID to components for Detox
<TextInput testID="emailInput" placeholder="Email" />
<TextInput testID="passwordInput" placeholder="Password" secureTextEntry />
<Button testID="loginButton" title="Login" onPress={handleLogin} />
<Text testID="errorMessage">{error}</Text>
```

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
