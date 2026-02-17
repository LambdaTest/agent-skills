# Detox (React Native) — Advanced Patterns & Playbook

## Screen Object Pattern

```javascript
class LoginScreen {
  get emailInput() { return element(by.id('email-input')); }
  get passwordInput() { return element(by.id('password-input')); }
  get submitBtn() { return element(by.id('login-button')); }
  get errorText() { return element(by.id('error-message')); }

  async login(email, password) {
    await this.emailInput.replaceText(email);
    await this.passwordInput.replaceText(password);
    await this.submitBtn.tap();
  }

  async expectError(message) {
    await expect(this.errorText).toBeVisible();
    await expect(this.errorText).toHaveText(message);
  }
}

class HomeScreen {
  get welcomeText() { return element(by.id('welcome-text')); }
  get productList() { return element(by.id('product-list')); }

  async scrollToProduct(name) {
    await waitFor(element(by.text(name)))
      .toBeVisible()
      .whileElement(by.id('product-list'))
      .scroll(200, 'down');
  }
}
```

## Advanced Interactions

```javascript
describe('Gestures', () => {
  it('supports swipe to delete', async () => {
    await element(by.id('item-1')).swipe('left', 'fast', 0.75);
    await element(by.id('delete-confirm')).tap();
    await expect(element(by.id('item-1'))).not.toExist();
  });

  it('supports pull to refresh', async () => {
    await element(by.id('list')).swipe('down', 'slow', 0.5, 0.5, 0.1);
    await waitFor(element(by.id('refreshed-indicator'))).toBeVisible().withTimeout(5000);
  });

  it('supports long press', async () => {
    await element(by.id('item-1')).longPress();
    await expect(element(by.id('context-menu'))).toBeVisible();
  });
});
```

## Device Capabilities

```javascript
describe('System interactions', () => {
  it('handles permissions', async () => {
    await device.launchApp({ permissions: { notifications: 'YES', camera: 'YES' } });
  });

  it('handles deep links', async () => {
    await device.openURL({ url: 'myapp://product/123' });
    await expect(element(by.id('product-detail'))).toBeVisible();
  });

  it('handles background/foreground', async () => {
    await device.sendToHome();
    await device.launchApp({ newInstance: false });
    await expect(element(by.id('home-screen'))).toBeVisible();
  });

  it('handles orientation', async () => {
    await device.setOrientation('landscape');
    await expect(element(by.id('landscape-layout'))).toBeVisible();
  });
});
```

## Configuration

```javascript
// .detoxrc.js
module.exports = {
  testRunner: { args: { $0: 'jest', config: 'e2e/jest.config.js' }, jest: { setupTimeout: 120000 } },
  apps: {
    'ios.debug': { type: 'ios.app', binaryPath: 'ios/build/Debug/MyApp.app', build: 'xcodebuild ...' },
    'android.debug': { type: 'android.apk', binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk' }
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_6_API_34' } }
  },
  configurations: {
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' }
  }
};
```

## Anti-Patterns

- ❌ `await new Promise(r => setTimeout(r, 3000))` — use `waitFor().toBeVisible().withTimeout()`
- ❌ Matching by text for dynamic content — use `testID` props and `by.id()`
- ❌ Missing `device.reloadReactNative()` between unrelated test suites
- ❌ Not using `replaceText` — `typeText` appends, which causes issues with pre-filled fields
