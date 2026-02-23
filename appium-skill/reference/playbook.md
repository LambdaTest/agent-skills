# Appium — Advanced Implementation Playbook

## §1 — Project Setup & Capabilities

```java
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>io.appium</groupId>
        <artifactId>java-client</artifactId>
        <version>9.1.0</version>
    </dependency>
    <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>4.18.1</version>
    </dependency>
    <dependency>
        <groupId>org.testng</groupId>
        <artifactId>testng</artifactId>
        <version>7.9.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>io.qameta.allure</groupId>
        <artifactId>allure-testng</artifactId>
        <version>2.25.0</version>
    </dependency>
</dependencies>
```

### Android Capabilities

```java
UiAutomator2Options androidOptions() {
    return new UiAutomator2Options()
        .setDeviceName(System.getProperty("device.name", "Pixel_6"))
        .setPlatformVersion(System.getProperty("platform.version", "14"))
        .setApp(System.getProperty("app.path", "src/test/resources/app-debug.apk"))
        .setAutomationName("UiAutomator2")
        .setAutoGrantPermissions(true)
        .setNoReset(Boolean.parseBoolean(System.getProperty("no.reset", "false")))
        .setNewCommandTimeout(Duration.ofSeconds(300))
        .setAdbExecTimeout(Duration.ofSeconds(60))
        .setUiautomator2ServerInstallTimeout(Duration.ofSeconds(120))
        .setAmplitude(new HashMap<>() {{ put("appWaitActivity", "*"); }});
}
```

### iOS Capabilities

```java
XCUITestOptions iosOptions() {
    return new XCUITestOptions()
        .setDeviceName(System.getProperty("device.name", "iPhone 15"))
        .setPlatformVersion(System.getProperty("platform.version", "17.2"))
        .setApp(System.getProperty("app.path", "src/test/resources/MyApp.app"))
        .setAutomationName("XCUITest")
        .setWdaLaunchTimeout(Duration.ofSeconds(120))
        .setWdaConnectionTimeout(Duration.ofSeconds(120))
        .setAutoAcceptAlerts(true)
        .setShowXcodeLog(true);
}
```

## §2 — BaseTest with Thread-Safe Driver

```java
public class BaseTest {
    protected static final ThreadLocal<AppiumDriver> driverThread = new ThreadLocal<>();
    protected AppiumDriver driver;

    @Parameters({"platform", "deviceName", "platformVersion"})
    @BeforeMethod(alwaysRun = true)
    public void setUp(@Optional("android") String platform,
                      @Optional("Pixel_6") String deviceName,
                      @Optional("14") String platformVersion) throws Exception {
        String appiumUrl = System.getProperty("appium.url", "http://127.0.0.1:4723");

        BaseOptions<?> options;
        if ("ios".equalsIgnoreCase(platform)) {
            options = iosOptions()
                .setDeviceName(deviceName)
                .setPlatformVersion(platformVersion);
        } else {
            options = androidOptions()
                .setDeviceName(deviceName)
                .setPlatformVersion(platformVersion);
        }

        AppiumDriver d = new AppiumDriver(new URL(appiumUrl), options);
        d.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driverThread.set(d);
        driver = d;
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult result) {
        AppiumDriver d = driverThread.get();
        if (d != null) {
            if (result.getStatus() == ITestResult.FAILURE) {
                captureScreenshot(result.getName());
            }
            d.quit();
            driverThread.remove();
        }
    }

    public AppiumDriver getDriver() { return driverThread.get(); }

    private void captureScreenshot(String testName) {
        try {
            byte[] screenshot = driverThread.get().getScreenshotAs(OutputType.BYTES);
            Allure.addAttachment(testName + "-failure", "image/png",
                new ByteArrayInputStream(screenshot), "png");
        } catch (Exception e) { /* log */ }
    }

    protected boolean isAndroid() {
        return driver.getCapabilities().getPlatformName()
            .toString().equalsIgnoreCase("android");
    }
}
```

## §3 — Cross-Platform Page Objects

```java
public class LoginScreen {
    private final AppiumDriver driver;
    private final WebDriverWait wait;

    @AndroidFindBy(accessibility = "email_input")
    @iOSXCUITFindBy(accessibility = "email_input")
    private WebElement emailField;

    @AndroidFindBy(accessibility = "password_input")
    @iOSXCUITFindBy(accessibility = "password_input")
    private WebElement passwordField;

    @AndroidFindBy(accessibility = "login_button")
    @iOSXCUITFindBy(accessibility = "login_button")
    private WebElement loginBtn;

    @AndroidFindBy(id = "com.app:id/error_text")
    @iOSXCUITFindBy(iOSNsPredicate = "type == 'XCUIElementTypeStaticText' AND name CONTAINS 'error'")
    private WebElement errorMsg;

    public LoginScreen(AppiumDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        PageFactory.initElements(new AppiumFieldDecorator(driver, Duration.ofSeconds(15)), this);
    }

    public HomeScreen login(String email, String password) {
        emailField.clear(); emailField.sendKeys(email);
        passwordField.clear(); passwordField.sendKeys(password);
        hideKeyboard();
        loginBtn.click();
        return new HomeScreen(driver);
    }

    public String getError() {
        wait.until(ExpectedConditions.visibilityOf(errorMsg));
        return errorMsg.getText();
    }

    public boolean isDisplayed() {
        try { return emailField.isDisplayed(); }
        catch (Exception e) { return false; }
    }

    private void hideKeyboard() {
        try { driver.hideKeyboard(); } catch (Exception e) { /* not shown */ }
    }
}
```

## §4 — Advanced Gestures (W3C Actions)

```java
public class GestureHelper {
    private final AppiumDriver driver;

    public GestureHelper(AppiumDriver driver) { this.driver = driver; }

    // Swipe direction
    public void swipe(Direction direction, double percent) {
        Dimension size = driver.manage().window().getSize();
        int startX, startY, endX, endY;
        switch (direction) {
            case LEFT:
                startX = (int)(size.width * 0.8); endX = (int)(size.width * 0.2);
                startY = endY = size.height / 2; break;
            case RIGHT:
                startX = (int)(size.width * 0.2); endX = (int)(size.width * 0.8);
                startY = endY = size.height / 2; break;
            case UP:
                startY = (int)(size.height * 0.8); endY = (int)(size.height * 0.2);
                startX = endX = size.width / 2; break;
            case DOWN:
                startY = (int)(size.height * 0.2); endY = (int)(size.height * 0.8);
                startX = endX = size.width / 2; break;
            default: throw new IllegalArgumentException("Invalid direction");
        }
        performSwipe(startX, startY, endX, endY, 600);
    }

    private void performSwipe(int startX, int startY, int endX, int endY, int durationMs) {
        PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger");
        Sequence swipe = new Sequence(finger, 0)
            .addAction(finger.createPointerMove(Duration.ZERO,
                PointerInput.Origin.viewport(), startX, startY))
            .addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
            .addAction(finger.createPointerMove(Duration.ofMillis(durationMs),
                PointerInput.Origin.viewport(), endX, endY))
            .addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));
        driver.perform(Collections.singletonList(swipe));
    }

    // Long press
    public void longPress(WebElement element, int durationMs) {
        Point center = element.getLocation();
        Dimension elemSize = element.getSize();
        int x = center.x + elemSize.width / 2;
        int y = center.y + elemSize.height / 2;

        PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger");
        Sequence longPress = new Sequence(finger, 0)
            .addAction(finger.createPointerMove(Duration.ZERO,
                PointerInput.Origin.viewport(), x, y))
            .addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
            .addAction(new Pause(finger, Duration.ofMillis(durationMs)))
            .addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));
        driver.perform(Collections.singletonList(longPress));
    }

    // Pinch zoom
    public void pinchZoom(int centerX, int centerY, int distance) {
        PointerInput f1 = new PointerInput(PointerInput.Kind.TOUCH, "finger1");
        PointerInput f2 = new PointerInput(PointerInput.Kind.TOUCH, "finger2");

        Sequence s1 = new Sequence(f1, 0)
            .addAction(f1.createPointerMove(Duration.ZERO, PointerInput.Origin.viewport(), centerX, centerY))
            .addAction(f1.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
            .addAction(f1.createPointerMove(Duration.ofMillis(600),
                PointerInput.Origin.viewport(), centerX, centerY - distance))
            .addAction(f1.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

        Sequence s2 = new Sequence(f2, 0)
            .addAction(f2.createPointerMove(Duration.ZERO, PointerInput.Origin.viewport(), centerX, centerY))
            .addAction(f2.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
            .addAction(f2.createPointerMove(Duration.ofMillis(600),
                PointerInput.Origin.viewport(), centerX, centerY + distance))
            .addAction(f2.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));

        driver.perform(Arrays.asList(s1, s2));
    }

    // Scroll to element — Android
    public WebElement scrollToText(String text) {
        return driver.findElement(AppiumBy.androidUIAutomator(
            "new UiScrollable(new UiSelector().scrollable(true))" +
            ".scrollIntoView(new UiSelector().text(\"" + text + "\"))"));
    }

    // Scroll to element — iOS
    public void scrollToElementIOS(String label) {
        driver.executeScript("mobile: scroll", Map.of(
            "direction", "down",
            "predicateString", "label == '" + label + "'"
        ));
    }

    enum Direction { UP, DOWN, LEFT, RIGHT }
}
```

## §5 — WebView & Hybrid App Testing

```java
// Switch between NATIVE and WEBVIEW contexts
@Test
public void testHybridApp() {
    // Start in native context
    loginScreen.login("user@test.com", "pass123");

    // Wait for WebView
    new WebDriverWait(driver, Duration.ofSeconds(20)).until(d -> {
        Set<String> contexts = ((SupportsContextSwitching) d).getContextHandles();
        return contexts.stream().anyMatch(c -> c.contains("WEBVIEW"));
    });

    // Switch to WebView
    Set<String> contexts = ((SupportsContextSwitching) driver).getContextHandles();
    String webViewContext = contexts.stream()
        .filter(c -> c.contains("WEBVIEW"))
        .findFirst().orElseThrow();
    ((SupportsContextSwitching) driver).context(webViewContext);

    // Now use web selectors
    driver.findElement(By.cssSelector("[data-testid='web-content']")).click();

    // Switch back to native
    ((SupportsContextSwitching) driver).context("NATIVE_APP");
    assertTrue(driver.findElement(AppiumBy.accessibilityId("home_tab")).isDisplayed());
}
```

## §6 — Device Interactions

```java
// Push/pull files
driver.pushFile("/sdcard/Download/test.txt", new File("testdata/test.txt"));
byte[] fileData = driver.pullFile("/sdcard/Download/result.txt");

// App lifecycle
driver.terminateApp("com.myapp");
driver.activateApp("com.myapp");
boolean isRunning = driver.isAppInstalled("com.myapp");
driver.installApp("/path/to/app.apk");
driver.removeApp("com.myapp");

// Notifications (Android)
driver.openNotifications();
driver.findElement(AppiumBy.xpath("//android.widget.TextView[@text='New message']")).click();

// Clipboard
driver.setClipboardText("test data");
String clipboardText = driver.getClipboardText();

// Device orientation
driver.rotate(ScreenOrientation.LANDSCAPE);
driver.rotate(ScreenOrientation.PORTRAIT);

// Geolocation
driver.setLocation(new Location(37.7749, -122.4194, 10));  // San Francisco

// Network conditions (Android)
driver.toggleWifi();
driver.toggleAirplaneMode();
driver.toggleData();

// Deep linking
driver.get("myapp://screen/settings");
```

## §7 — Parallel Device Execution

```xml
<!-- testng.xml — multi-device parallel -->
<suite name="Mobile Suite" parallel="tests" thread-count="4">
    <listeners>
        <listener class-name="listeners.AllureListener"/>
        <listener class-name="listeners.RetryListener"/>
    </listeners>

    <test name="Android Pixel 6">
        <parameter name="platform" value="android"/>
        <parameter name="deviceName" value="Pixel_6"/>
        <parameter name="platformVersion" value="14"/>
        <parameter name="appiumPort" value="4723"/>
        <classes><class name="tests.LoginTest"/></classes>
    </test>

    <test name="Android Samsung S23">
        <parameter name="platform" value="android"/>
        <parameter name="deviceName" value="Samsung_S23"/>
        <parameter name="platformVersion" value="14"/>
        <parameter name="appiumPort" value="4724"/>
        <classes><class name="tests.LoginTest"/></classes>
    </test>

    <test name="iOS iPhone 15">
        <parameter name="platform" value="ios"/>
        <parameter name="deviceName" value="iPhone 15"/>
        <parameter name="platformVersion" value="17.2"/>
        <parameter name="appiumPort" value="4725"/>
        <classes><class name="tests.LoginTest"/></classes>
    </test>
</suite>
```

## §8 — LambdaTest Real Device Cloud

```java
public AppiumDriver createLambdaTestDriver(String platform, String device) throws Exception {
    String username = System.getenv("LT_USERNAME");
    String accessKey = System.getenv("LT_ACCESS_KEY");
    String url = "https://" + username + ":" + accessKey + "@mobile-hub.lambdatest.com/wd/hub";

    HashMap<String, Object> ltOptions = new HashMap<>();
    ltOptions.put("build", "Build " + System.getenv("BUILD_NUMBER"));
    ltOptions.put("name", "Appium Tests");
    ltOptions.put("isRealMobile", true);
    ltOptions.put("video", true);
    ltOptions.put("network", true);
    ltOptions.put("console", true);
    ltOptions.put("visual", true);

    if ("android".equalsIgnoreCase(platform)) {
        UiAutomator2Options options = new UiAutomator2Options()
            .setDeviceName(device)
            .setPlatformVersion("14")
            .setApp("lt://APP_ID")
            .setCapability("LT:Options", ltOptions);
        return new AppiumDriver(new URL(url), options);
    } else {
        XCUITestOptions options = new XCUITestOptions()
            .setDeviceName(device)
            .setPlatformVersion("17")
            .setApp("lt://APP_ID")
            .setCapability("LT:Options", ltOptions);
        return new AppiumDriver(new URL(url), options);
    }
}
```

## §9 — CI/CD Integration

```yaml
# GitHub Actions
name: Appium Tests
on: [push, pull_request]
jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Start emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          target: google_apis
          arch: x86_64
          script: |
            npm install -g appium
            appium driver install uiautomator2
            appium &
            sleep 10
            mvn test -DsuiteXmlFile=testng-android.xml -Dplatform=android
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: appium-results
          path: |
            target/surefire-reports/
            allure-results/
            screenshots/

  cloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: mvn test -DsuiteXmlFile=testng-cloud.xml
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
```

## §10 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Element not found | Wrong locator strategy | Use Appium Inspector; prefer `accessibilityId` |
| Session creation fails | Incompatible capabilities | Verify device name, platform version, app path |
| App not installed | Invalid APK/IPA path | Use absolute path, verify file exists |
| iOS WDA build fails | Xcode/provisioning issue | Clean DerivedData, increase `wdaLaunchTimeout` |
| Android permission dialog | Runtime permission blocking | Set `autoGrantPermissions: true` |
| Slow element finding | XPath locator | Switch to `accessibilityId` or `id` (10x faster) |
| Keyboard covers element | Soft keyboard blocking | Call `driver.hideKeyboard()` before tap |
| Touch action fails | Wrong coordinates | Use element center: `element.getRect()` |
| WebView not found | Context not switched | List contexts first, wait for WEBVIEW context |
| App crash mid-test | App state corrupted | Use `noReset: false` for clean state between tests |
| Flaky on real devices | Timing/animation issues | Increase waits, disable animations in developer options |
| Parallel port conflicts | Same Appium port | Use different `systemPort` per device |

## §11 — Best Practices Checklist

- ✅ Use `accessibilityId` locator for cross-platform (fastest, most stable)
- ✅ Use `@AndroidFindBy` / `@iOSXCUITFindBy` for platform-specific elements
- ✅ Use `ThreadLocal<AppiumDriver>` for parallel-safe execution
- ✅ Use W3C Actions API for gestures (not deprecated TouchAction)
- ✅ Use `GestureHelper` utility class for reusable swipe/scroll/zoom
- ✅ Set `autoGrantPermissions: true` (Android) and `autoAcceptAlerts: true` (iOS)
- ✅ Use `noReset: true` for speed, `fullReset: true` for clean state
- ✅ Call `hideKeyboard()` after text input before next interaction
- ✅ Use Appium Inspector for locator discovery and validation
- ✅ Capture screenshots + page source on failure via listener
- ✅ Run on real device cloud (LambdaTest) for production confidence
- ✅ Use WebView context switching for hybrid app testing
- ✅ Structure: `screens/`, `tests/`, `utils/`, `testdata/`, `listeners/`
