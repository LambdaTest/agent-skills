# Appium — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## App Upload

```bash
# Android APK
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  --location --request POST 'https://manual-api.lambdatest.com/app/upload/realDevice' \
  --form 'name="MyApp"' \
  --form 'appFile=@"/path/to/app.apk"'

# iOS IPA
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  --location --request POST 'https://manual-api.lambdatest.com/app/upload/realDevice' \
  --form 'name="MyApp"' \
  --form 'appFile=@"/path/to/app.ipa"'

# Response: { "app_url": "lt://APP1234567890", "name": "MyApp", ... }
```

## Android Capabilities

```java
UiAutomator2Options options = new UiAutomator2Options();
options.setPlatformName("android");
options.setDeviceName("Pixel 8");
options.setPlatformVersion("14");
options.setApp("lt://APP1234567890");
options.setAutomationName("UiAutomator2");

HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("w3c", true);
ltOptions.put("build", "Android Build");
ltOptions.put("name", "Login Test");
ltOptions.put("isRealMobile", true);
ltOptions.put("video", true);
ltOptions.put("network", true);
ltOptions.put("devicelog", true);
options.setCapability("LT:Options", ltOptions);

String hub = "https://" + LT_USERNAME + ":" + LT_ACCESS_KEY
           + "@mobile-hub.lambdatest.com/wd/hub";
AndroidDriver driver = new AndroidDriver(new URL(hub), options);
```

## iOS Capabilities

```java
XCUITestOptions options = new XCUITestOptions();
options.setPlatformName("ios");
options.setDeviceName("iPhone 16");
options.setPlatformVersion("18");
options.setApp("lt://APP1234567890");
options.setAutomationName("XCUITest");

HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("w3c", true);
ltOptions.put("build", "iOS Build");
ltOptions.put("name", "Login Test");
ltOptions.put("isRealMobile", true);
ltOptions.put("video", true);
options.setCapability("LT:Options", ltOptions);

String hub = "https://" + LT_USERNAME + ":" + LT_ACCESS_KEY
           + "@mobile-hub.lambdatest.com/wd/hub";
IOSDriver driver = new IOSDriver(new URL(hub), options);
```

## Available Real Devices

**Android:** Pixel 8/7/6/5, Samsung Galaxy S24/S23/S22/S21, OnePlus 11/10 Pro, Xiaomi 13
**iOS:** iPhone 16/15/14/13 Pro Max, iPad Pro (M2), iPad Air

## Parallel Execution

Use TestNG with different device capabilities per test:

```xml
<suite name="Mobile Parallel" parallel="tests" thread-count="5">
  <test name="Pixel 8">
    <parameter name="device" value="Pixel 8"/>
    <parameter name="platform" value="android"/>
    <parameter name="version" value="14"/>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
  <test name="iPhone 16">
    <parameter name="device" value="iPhone 16"/>
    <parameter name="platform" value="ios"/>
    <parameter name="version" value="18"/>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
</suite>
```

## Test Status Reporting

```java
// Java
((JavascriptExecutor) driver).executeScript("lambda-status=" + status);

// Python
driver.execute_script("lambda-status=" + status)

// JavaScript
await driver.execute("lambda-status=" + status);
```
