# Mobile Testing — Real Devices on TestMu AI

## Table of Contents
- Android Testing
- iOS Testing
- Critical Differences
- Timeout Requirements
- Mobile Gestures

## Android Testing

Use `_android.connect()` — not `chromium.connect()`.

```typescript
import { _android } from 'playwright';

const capabilities = {
  browserName: 'Chrome',
  browserVersion: 'latest',
  'LT:Options': {
    platformName: 'android',
    deviceName: 'Pixel 7',
    platformVersion: '13',
    isRealMobile: true,
    build: 'Android Build',
    name: 'Android Test',
    user: process.env.LT_USERNAME,
    accessKey: process.env.LT_ACCESS_KEY,
    network: true,
    video: true,
  },
};

(async () => {
  const device = await _android.connect(
    `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(
      JSON.stringify(capabilities)
    )}`
  );
  const context = await device.launchBrowser();
  const page = await context.newPage();
  // CRITICAL: Real devices are slower — extend timeout
  context.setDefaultTimeout(120_000);

  try {
    await page.goto('https://example.com');
    // ... test logic ...

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'passed', remark: 'OK' },
      })}`
    );
  } catch (e) {
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'failed', remark: String(e) },
      })}`
    );
  } finally {
    await context.close();
    await device.close();
  }
})();
```

### Android Shell Commands

```typescript
// Force-stop Chrome before testing
await device.shell('am force-stop com.android.chrome');
// Check device info
const model = await device.shell('getprop ro.product.model');
```

## iOS Testing

**CRITICAL**: iOS uses `webkit.connect()` — NEVER `chromium.connect()`.

```typescript
import { webkit } from 'playwright';

const capabilities = {
  browserName: 'pw-webkit',
  browserVersion: 'latest',
  'LT:Options': {
    platformName: 'ios',
    deviceName: 'iPhone 16',
    platformVersion: '18',
    isRealMobile: true,
    build: 'iOS Build',
    name: 'iOS Test',
    user: process.env.LT_USERNAME,
    accessKey: process.env.LT_ACCESS_KEY,
    network: true,
    video: true,
  },
};

(async () => {
  const browser = await webkit.connect(
    `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(
      JSON.stringify(capabilities)
    )}`
  );
  const context = await browser.newContext();
  const page = await context.newPage();
  context.setDefaultTimeout(120_000);

  try {
    await page.goto('https://example.com');
    // ... test logic ...

    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'passed', remark: 'OK' },
      })}`
    );
  } catch (e) {
    await page.evaluate((_) => {},
      `lambdatest_action: ${JSON.stringify({
        action: 'setTestStatus',
        arguments: { status: 'failed', remark: String(e) },
      })}`
    );
  } finally {
    await context.close();
    await browser.close();
  }
})();
```

## Critical Differences

| | Android | iOS |
|---|---|---|
| Import | `_android` from `playwright` | `webkit` from `playwright` |
| Connect method | `_android.connect(wsEndpoint)` | `webkit.connect(wsEndpoint)` |
| browserName capability | `Chrome` | `pw-webkit` |
| platformName | `android` | `ios` |
| Shell commands | `device.shell(cmd)` available | Not available |
| Browser launch | `device.launchBrowser()` then `context.newPage()` | `browser.newContext()` then `context.newPage()` |

## Timeout Requirements

Real devices are slower than desktop VMs. Always set extended timeouts:

```typescript
// 120 seconds for real devices (default 30s will cause flaky failures)
context.setDefaultTimeout(120_000);
```

**Why 120s**: Device provisioning, app install, network latency over real cellular/WiFi.

## Mobile Gestures

For touch interactions, use Playwright's built-in methods:

```typescript
// Tap (equivalent to click on mobile)
await page.getByRole('button').tap();

// Swipe (via touch events)
await page.touchscreen.tap(200, 300);

// Scroll to element
await page.getByText('Footer').scrollIntoViewIfNeeded();
```

For full device catalogs, see [../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
