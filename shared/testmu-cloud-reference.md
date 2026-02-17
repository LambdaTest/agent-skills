# TestMu AI Cloud Reference

Shared reference for all framework skills. Every cloud-enabled skill points here.

## Table of Contents
- Authentication
- WebSocket Endpoint
- Desktop Browsers
- Desktop Platforms
- Mobile Devices — Android
- Mobile Devices — iOS
- LT:Options Capability Reference
- Test Status Reporting
- Tunnel for Localhost
- Geo-Location Testing
- Network & Video Capture

## Authentication

All cloud tests require two environment variables:

```bash
export LT_USERNAME="your_username"
export LT_ACCESS_KEY="your_access_key"
```

Get credentials from https://accounts.lambdatest.com/security

## WebSocket Endpoint

All frameworks connect via CDP WebSocket:

```
wss://cdp.lambdatest.com/playwright?capabilities={encoded_json}
```

For Selenium-based frameworks, use Hub URL:

```
https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
```

## Desktop Browsers

| Browser | Value | Notes |
|---------|-------|-------|
| Chrome | `Chrome` | Default, most stable |
| Edge | `MicrosoftEdge` | Chromium-based |
| Playwright Chromium | `pw-chromium` | Playwright-specific builds |
| Playwright Firefox | `pw-firefox` | Playwright-specific builds |
| Playwright WebKit | `pw-webkit` | Playwright-specific builds |
| Firefox | `Firefox` | Selenium only |
| Safari | `Safari` | Selenium only, macOS only |

## Desktop Platforms

| Platform | Value |
|----------|-------|
| Windows 11 | `Windows 11` |
| Windows 10 | `Windows 10` |
| macOS Sequoia | `macOS Sequoia` |
| macOS Sonoma | `macOS Sonoma` |
| macOS Ventura | `macOS Ventura` |
| macOS Monterey | `macOS Monterey` |
| macOS Big Sur | `macOS Big Sur` |
| macOS Catalina | `macOS Catalina` |

## Mobile Devices — Android

Use `platformName: 'android'` + `isRealMobile: true`.

| Device | `deviceName` value | Versions |
|--------|-------------------|----------|
| Pixel 8 | `Pixel 8` | 14 |
| Pixel 7 | `Pixel 7` | 13, 14 |
| Pixel 6 | `Pixel 6` | 12, 13 |
| Pixel 5 | `Pixel 5` | 12 |
| Galaxy S24 | `Galaxy S24` | 14 |
| Galaxy S23 | `Galaxy S23` | 13, 14 |
| Galaxy S22 | `Galaxy S22` | 12, 13 |
| OnePlus 11 | `OnePlus 11` | 13 |
| OnePlus 10 Pro | `OnePlus 10 Pro` | 12 |

100+ more devices available — see https://www.lambdatest.com/capabilities-generator

## Mobile Devices — iOS

Use `platformName: 'ios'` + `isRealMobile: true`.

**CRITICAL**: iOS always uses `webkit` browser, never `chromium`.

| Device | `deviceName` value | Versions |
|--------|-------------------|----------|
| iPhone 16 | `iPhone 16` | 18 |
| iPhone 16 Pro Max | `iPhone 16 Pro Max` | 18 |
| iPhone 15 | `iPhone 15` | 17, 18 |
| iPhone 15 Pro Max | `iPhone 15 Pro Max` | 17, 18 |
| iPhone 14 | `iPhone 14` | 16, 17 |
| iPad Pro 12.9 | `iPad Pro 12.9 (2022)` | 16, 17 |
| iPad Air | `iPad Air (2022)` | 16, 17 |

## LT:Options Capability Reference

| Capability | Type | Required | Description |
|-----------|------|----------|-------------|
| `platform` | string | Desktop: Yes | OS (`Windows 11`, `macOS Sequoia`) |
| `build` | string | Recommended | Groups tests in LT dashboard |
| `name` | string | Recommended | Individual test name |
| `user` | string | Yes | `process.env.LT_USERNAME` |
| `accessKey` | string | Yes | `process.env.LT_ACCESS_KEY` |
| `network` | boolean | No | Capture network logs (default: false) |
| `video` | boolean | No | Record test video (default: false) |
| `console` | boolean | No | Capture browser console (default: false) |
| `tunnel` | boolean | No | Enable Lambda Tunnel for localhost |
| `tunnelName` | string | No | Named tunnel identifier |
| `geoLocation` | string | No | Country code (`US`, `GB`, `IN`) |
| `resolution` | string | No | Screen resolution (`1920x1080`) |
| `playwrightClientVersion` | string | No | Lock Playwright version |
| `platformName` | string | Mobile: Yes | `android` or `ios` |
| `deviceName` | string | Mobile: Yes | Device name from catalog above |
| `platformVersion` | string | Mobile: Yes | OS version (`14`, `18`) |
| `isRealMobile` | boolean | Mobile: Yes | Must be `true` for real devices |
| `isPwMobileWebviewTest` | boolean | No | Enable WebView testing |

## Test Status Reporting

TestMu AI marks tests as "Completed" by default. You MUST explicitly report pass/fail.

**JavaScript/TypeScript (Playwright, Puppeteer, Cypress via CDP):**
```javascript
await page.evaluate((_) => {},
  `lambdatest_action: ${JSON.stringify({
    action: 'setTestStatus',
    arguments: { status: 'passed', remark: 'All assertions passed' },
  })}`
);
```

**Java (Selenium, Appium):**
```java
((JavascriptExecutor) driver).executeScript(
  "lambda-status=passed"
);
```

**Python (Selenium, Appium):**
```python
driver.execute_script("lambda-status=passed")
```

**Ruby (Selenium):**
```ruby
driver.execute_script("lambda-status=passed")
```

**C# (Selenium):**
```csharp
((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=passed");
```

## Tunnel for Localhost

To test apps running on `localhost` or internal networks:

1. Download tunnel binary: https://www.lambdatest.com/support/docs/testing-locally-hosted-pages/
2. Start tunnel:
```bash
./LT --user ${LT_USERNAME} --key ${LT_ACCESS_KEY} --tunnelName myTunnel
```
3. Add to capabilities:
```json
{
  "tunnel": true,
  "tunnelName": "myTunnel"
}
```

## Geo-Location Testing

Add `geoLocation` to LT:Options with ISO country code:

```json
{ "geoLocation": "US" }
```

Supported: US, GB, DE, FR, IN, JP, AU, BR, CA, SG, and 50+ more.

## Network & Video Capture

Always enable for cloud debugging:

```json
{
  "network": true,
  "video": true,
  "console": true
}
```

Access recordings in LT dashboard under Automation > Build > Test > Video/Network/Console tabs.
