# Detox — Advanced Implementation Playbook

## §1 Project Setup & Configuration

### .detoxrc.js — Production Config
```javascript
/** @type {Detox.DetoxConfig} */
module.exports = {
  testRunner: {
    args: {
      config: 'e2e/jest.config.js',
      maxWorkers: 1,
      _: ['e2e'],
    },
    jest: {
      setupTimeout: 120000,
      teardownTimeout: 30000,
    },
  },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/MyApp.app',
      build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build',
    },
    'ios.release': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Release-iphonesimulator/MyApp.app',
      build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Release -sdk iphonesimulator -derivedDataPath ios/build',
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
      reversePorts: [8081],
    },
    'android.release': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/release/app-release.apk',
      build: 'cd android && ./gradlew assembleRelease assembleAndroidTest -DtestBuildType=release',
    },
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_6_API_34' } },
    'attached.android': { type: 'android.attached', device: { adbName: '.*' } },
  },
  configurations: {
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'ios.sim.release': { device: 'simulator', app: 'ios.release' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' },
    'android.emu.release': { device: 'emulator', app: 'android.release' },
    'android.att.debug': { device: 'attached.android', app: 'android.debug' },
  },
  artifacts: {
    rootDir: './e2e/artifacts',
    plugins: {
      screenshot: { shouldTakeAutomaticSnapshots: true, keepOnlyFailedTestsArtifacts: true },
      video: { enabled: true },
      log: { enabled: true },
    },
  },
  behavior: {
    init: { exposeGlobals: true },
    cleanup: { shutdownDevice: false },
  },
};
```

### e2e/jest.config.js
```javascript
module.exports = {
  maxWorkers: 1,
  testTimeout: 120000,
  rootDir: '..',
  testMatch: ['<rootDir>/e2e/**/*.test.js'],
  verbose: true,
  reporters: [
    'default',
    ['jest-junit', { outputDirectory: './e2e/artifacts', outputName: 'junit.xml' }],
  ],
};
```

---

## §2 Page Object Pattern

### BasePage
```javascript
class BasePage {
  async waitForVisible(testID, timeout = 5000) {
    await waitFor(element(by.id(testID)))
      .toBeVisible()
      .withTimeout(timeout);
  }

  async tapById(testID) {
    await element(by.id(testID)).tap();
  }

  async typeById(testID, text) {
    await element(by.id(testID)).clearText();
    await element(by.id(testID)).typeText(text);
  }

  async takeScreenshot(name) {
    await device.takeScreenshot(name);
  }
}
```

### LoginPage
```javascript
class LoginPage extends BasePage {
  get emailInput() { return element(by.id('email_input')); }
  get passwordInput() { return element(by.id('password_input')); }
  get loginButton() { return element(by.id('login_button')); }
  get errorMessage() { return element(by.id('error_message')); }

  async enterEmail(email) {
    await this.emailInput.clearText();
    await this.emailInput.typeText(email);
  }

  async enterPassword(password) {
    await this.passwordInput.clearText();
    await this.passwordInput.typeText(password);
  }

  async tapLogin() {
    await this.loginButton.tap();
  }

  async login(email, password) {
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.tapLogin();
    return new DashboardPage();
  }

  async expectError(message) {
    await expect(this.errorMessage).toBeVisible();
    await expect(this.errorMessage).toHaveText(message);
  }
}

module.exports = { LoginPage };
```

### DashboardPage
```javascript
class DashboardPage extends BasePage {
  get welcomeText() { return element(by.id('welcome_text')); }
  get productList() { return element(by.id('product_list')); }
  get cartBadge() { return element(by.id('cart_badge')); }

  async verifyOnScreen() {
    await waitFor(this.welcomeText).toBeVisible().withTimeout(10000);
  }

  async selectProduct(index) {
    await element(by.id(`product_item_${index}`)).tap();
    return new ProductDetailPage();
  }
}

module.exports = { DashboardPage };
```

---

## §3 Test Patterns

### Complete Flow Test
```javascript
const { LoginPage } = require('./pages/LoginPage');
const { DashboardPage } = require('./pages/DashboardPage');

describe('Purchase Flow', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true, permissions: { notifications: 'YES' } });
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should complete login → browse → purchase', async () => {
    const loginPage = new LoginPage();
    const dashboard = await loginPage.login('user@test.com', 'password123');

    await dashboard.verifyOnScreen();
    await device.takeScreenshot('dashboard_loaded');

    const productPage = await dashboard.selectProduct(0);
    await productPage.addToCart();
    await expect(dashboard.cartBadge).toBeVisible();

    await productPage.goToCart();
    await element(by.id('checkout_button')).tap();
    await waitFor(element(by.text('Order Confirmed')))
      .toBeVisible()
      .withTimeout(15000);
  });

  it('should show error for invalid credentials', async () => {
    const loginPage = new LoginPage();
    await loginPage.enterEmail('wrong@test.com');
    await loginPage.enterPassword('wrong');
    await loginPage.tapLogin();
    await loginPage.expectError('Invalid credentials');
  });
});
```

---

## §4 Advanced Interactions

### Scroll & Search
```javascript
// Scroll until element is visible
await waitFor(element(by.text('Load More')))
  .toBeVisible()
  .whileElement(by.id('scroll_view'))
  .scroll(200, 'down');

// Scroll to edge
await element(by.id('scroll_view')).scrollTo('bottom');
await element(by.id('scroll_view')).scrollTo('top');

// FlatList — scroll by index
await element(by.id('product_list')).scrollTo('bottom');
```

### Gestures
```javascript
// Swipe
await element(by.id('card')).swipe('left', 'fast', 0.75);
await element(by.id('card')).swipe('right', 'slow', 0.5);

// Long press
await element(by.id('item')).longPress(2000);

// Multi-tap
await element(by.id('zoom_target')).multiTap(2); // double-tap

// Pinch (iOS only)
await element(by.id('map_view')).pinch(1.5); // zoom in
await element(by.id('map_view')).pinch(0.5); // zoom out
```

### Device Operations
```javascript
// Location
await device.setLocation(37.7749, -122.4194);

// Deep links
await device.openURL('myapp://products/123');

// Shake device
await device.shake();

// Background & foreground
await device.sendToHome();
await device.launchApp({ newInstance: false });

// Biometric (iOS simulator)
await device.matchFace(); // or device.unmatchFace()
await device.matchFinger(); // or device.unmatchFinger()

// Set orientation
await device.setOrientation('landscape');
await device.setOrientation('portrait');
```

### Synchronization Control
```javascript
// Disable for animations that never settle
await device.disableSynchronization();
await element(by.id('lottie_animation')).tap();
await device.enableSynchronization();

// Wait with timeout for async elements
await waitFor(element(by.id('loaded_content')))
  .toBeVisible()
  .withTimeout(15000);
```

---

## §5 Matchers & Assertions

```javascript
// Visibility
await expect(element(by.id('header'))).toBeVisible();
await expect(element(by.id('hidden'))).not.toBeVisible();
await expect(element(by.id('deleted'))).not.toExist();

// Text
await expect(element(by.id('title'))).toHaveText('Welcome');
await expect(element(by.id('label'))).toHaveLabel('Submit');

// Toggles
await expect(element(by.id('switch'))).toHaveToggleValue(true);

// Slider
await expect(element(by.id('slider'))).toHaveSliderPosition(0.5, 0.1);

// Multiple matching elements
await expect(element(by.text('Item')).atIndex(0)).toBeVisible();
await expect(element(by.text('Item')).atIndex(2)).toBeVisible();

// Compound matchers
await element(by.id('save').and(by.text('Save'))).tap();
await element(by.id('cell').withAncestor(by.id('list_section_1'))).tap();
await element(by.id('icon').withDescendant(by.text('Edit'))).tap();
```

---

## §6 Network & Mock Server Integration

```javascript
// In your React Native app, use launch arguments for mock mode:
// if (__DEV__ && process.argv.includes('--mock-api')) { useMockServer(); }

// Detox can launch with arguments:
await device.launchApp({
  newInstance: true,
  launchArgs: {
    mockServerPort: '3001',
    detoxEnableSync: 0, // if needed for certain animations
  },
});

// Set up mock server with beforeAll
const { MockServer } = require('./helpers/mockServer');

beforeAll(async () => {
  MockServer.start(3001);
  MockServer.stub('GET', '/api/products', {
    status: 200,
    body: [{ id: 1, name: 'Test Product', price: 9.99 }],
  });
});

afterAll(async () => {
  MockServer.stop();
});
```

---

## §7 CI/CD Integration

### GitHub Actions (iOS)
```yaml
name: Detox E2E
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  ios-e2e:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with: { node-version: 20 }

      - name: Install deps
        run: |
          npm ci
          cd ios && pod install

      - name: Boot Simulator
        run: |
          xcrun simctl boot "iPhone 15" || true
          xcrun simctl status_bar "iPhone 15" override --time "9:41"

      - name: Build for Detox
        run: npx detox build --configuration ios.sim.debug

      - name: Run E2E tests
        run: npx detox test --configuration ios.sim.debug --cleanup --headless

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: detox-artifacts
          path: e2e/artifacts/

  android-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci

      - name: Android E2E
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          profile: Pixel 6
          script: |
            npx detox build --configuration android.emu.debug
            npx detox test --configuration android.emu.debug --headless
```

---

## §8 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `element(by.id(...))` not found | `testID` prop not set | Add `testID="identifier"` to React Native component |
| 2 | `pumpAndSettle`-style timeout | Infinite animation (Lottie, ActivityIndicator) | Use `device.disableSynchronization()` around animated sections |
| 3 | `device.reloadReactNative()` crashes | Metro bundler not running | Start Metro: `npx react-native start` before running tests |
| 4 | Build fails for Detox | CocoaPods or Gradle cache stale | `cd ios && pod install --repo-update`; `cd android && ./gradlew clean` |
| 5 | Test passes locally, fails on CI | Timing differences | Increase `withTimeout()` values; use explicit `waitFor` |
| 6 | Keyboard covers input field | Auto-scroll not triggered | Append `\n` to `typeText()` to dismiss; or scroll manually |
| 7 | `clearText()` doesn't clear | Focus not on field | Call `tap()` before `clearText()` |
| 8 | Android emulator extremely slow | No hardware acceleration | Use `-gpu host` and `x86_64` image; enable KVM on CI |
| 9 | `scrollTo` scrolls past element | Scroll offset too large | Use `whileElement().scroll(100, 'down')` with smaller increments |
| 10 | Multiple elements match | Non-unique `testID` | Use unique IDs; or use `.atIndex(n)` or compound matchers |
| 11 | `launchApp` hangs | Previous app instance stuck | Use `{ newInstance: true, delete: true }` to force fresh start |
| 12 | Artifacts not generated | Missing artifacts config | Add `artifacts.plugins` in `.detoxrc.js` with screenshot/video enabled |

---

## §9 Best Practices Checklist

1. ✅ Use `testID` prop on all interactive/assertable React Native elements
2. ✅ Use `device.reloadReactNative()` in `beforeEach` for clean state
3. ✅ Use `waitFor().toBeVisible().withTimeout()` — never `sleep` or fixed delays
4. ✅ Disable synchronization only for animations, re-enable immediately
5. ✅ Use `--reuse` flag during development to skip app rebuild
6. ✅ Use page objects for readable, maintainable tests
7. ✅ Use `device.takeScreenshot()` at key points for debugging and CI evidence
8. ✅ Handle keyboard by appending `\n` to `typeText()` or dismissing explicitly
9. ✅ Use compound matchers for elements inside lists: `by.id().withAncestor()`
10. ✅ Configure artifact collection (screenshots, videos, logs) for CI
11. ✅ Run iOS tests on macOS runners; Android tests with hardware acceleration
12. ✅ Use launch arguments for mock mode: `launchArgs: { mockServerPort: '3001' }`
13. ✅ Test on both platforms — matcher behavior differs between iOS and Android
