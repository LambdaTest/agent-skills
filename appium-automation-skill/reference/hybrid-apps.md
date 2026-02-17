# Appium — Hybrid App Testing

## Context Switching

Hybrid apps have NATIVE_APP and WEBVIEW contexts.

```java
// List available contexts
Set<String> contexts = driver.getContextHandles();
// e.g., [NATIVE_APP, WEBVIEW_com.example.app]

// Switch to WebView
driver.context("WEBVIEW_com.example.app");
// Now use Selenium-style locators
driver.findElement(By.id("web-element")).click();

// Switch back to native
driver.context("NATIVE_APP");
driver.findElement(AppiumBy.accessibilityId("nativeButton")).click();
```

## Enable WebView Debugging

For Android, the app must enable WebView debugging:
```java
// In app code (Android):
WebView.setWebContentsDebuggingEnabled(true);
```

For Appium capability:
```java
options.setCapability("appium:chromeOptions", Map.of("w3c", true));
```

## Python Example

```python
# Switch to webview
contexts = driver.contexts
webview = [c for c in contexts if 'WEBVIEW' in c][0]
driver.switch_to.context(webview)

# Interact with web content
driver.find_element(By.CSS_SELECTOR, "#web-button").click()

# Switch back
driver.switch_to.context("NATIVE_APP")
```
