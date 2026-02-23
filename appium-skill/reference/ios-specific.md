# Appium — iOS-Specific Patterns

## XCUITest Driver Capabilities

```java
XCUITestOptions options = new XCUITestOptions();
options.setDeviceName("iPhone 16");
options.setPlatformVersion("18");
options.setApp("/path/to/app.ipa");
options.setAutomationName("XCUITest");
options.setBundleId("com.example.app");

// iOS-specific settings
options.setCapability("appium:wdaLaunchTimeout", 120000);
options.setCapability("appium:wdaConnectionTimeout", 240000);
options.setCapability("appium:showXcodeLog", true);
```

## iOS-Only Locators

```java
// Predicate string (fast, powerful)
driver.findElement(AppiumBy.iOSNsPredicateString(
    "type == 'XCUIElementTypeButton' AND label == 'Login'"
));

// Class chain (like XPath but faster on iOS)
driver.findElement(AppiumBy.iOSClassChain(
    "**/XCUIElementTypeCell[`label CONTAINS 'Item'`]"
));

// Accessibility ID (best — cross-platform)
driver.findElement(AppiumBy.accessibilityId("loginButton"));
```

## iOS Alerts

```java
// Handle system alerts (permissions, etc.)
options.setCapability("appium:autoAcceptAlerts", true);
// OR handle manually:
driver.switchTo().alert().accept();
```

## iOS Keyboard

```java
// Hide keyboard (iOS doesn't auto-hide)
driver.hideKeyboard();
// Or tap done button
driver.findElement(AppiumBy.accessibilityId("Done")).click();
```

## iOS-Specific Gestures

```java
// Pull-to-refresh
Map<String, Object> params = new HashMap<>();
params.put("direction", "down");
driver.executeScript("mobile: scroll", params);

// Swipe to delete in table
Map<String, Object> swipeParams = new HashMap<>();
swipeParams.put("direction", "left");
swipeParams.put("element", element.getId());
driver.executeScript("mobile: swipe", swipeParams);
```

## Face ID / Touch ID (Simulator)

```java
// Enroll biometrics
driver.executeScript("mobile: enrollBiometric", Map.of("isEnabled", true));

// Match (success)
driver.executeScript("mobile: sendBiometricMatch", Map.of("type", "faceId", "match", true));

// No match (failure)
driver.executeScript("mobile: sendBiometricMatch", Map.of("type", "faceId", "match", false));
```
