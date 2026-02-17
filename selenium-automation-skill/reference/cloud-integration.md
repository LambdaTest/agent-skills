# Selenium — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Hub URL Format

```
https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
```

## DesiredCapabilities Structure

```java
DesiredCapabilities caps = new DesiredCapabilities();
caps.setCapability("browserName", "Chrome");      // Chrome, MicrosoftEdge, Firefox, Safari
caps.setCapability("browserVersion", "latest");    // or specific: "120.0"

HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("platform", "Windows 11");
ltOptions.put("build", "Selenium Build");
ltOptions.put("name", "Test Name");
ltOptions.put("user", System.getenv("LT_USERNAME"));
ltOptions.put("accessKey", System.getenv("LT_ACCESS_KEY"));
ltOptions.put("video", true);
ltOptions.put("network", true);
ltOptions.put("console", true);
ltOptions.put("visual", true);
ltOptions.put("resolution", "1920x1080");
ltOptions.put("tunnel", false);           // true for localhost
ltOptions.put("tunnelName", "my-tunnel"); // named tunnel
ltOptions.put("geoLocation", "US");       // geo-testing
caps.setCapability("LT:Options", ltOptions);

WebDriver driver = new RemoteWebDriver(new URL(hub), caps);
```

## Parallel Execution — TestNG

```xml
<!-- testng.xml -->
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Cross Browser" parallel="tests" thread-count="5">
  <test name="Chrome Windows">
    <parameter name="browser" value="Chrome"/>
    <parameter name="version" value="latest"/>
    <parameter name="platform" value="Windows 11"/>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
  <test name="Firefox Mac">
    <parameter name="browser" value="Firefox"/>
    <parameter name="version" value="latest"/>
    <parameter name="platform" value="macOS Sequoia"/>
    <classes><class name="tests.LoginTest"/></classes>
  </test>
</suite>
```

```java
// Base test with @Parameters
public class BaseTest {
    protected WebDriver driver;

    @Parameters({"browser", "version", "platform"})
    @BeforeMethod
    public void setUp(String browser, String version, String platform) throws Exception {
        String hub = "https://" + System.getenv("LT_USERNAME") + ":"
                   + System.getenv("LT_ACCESS_KEY") + "@hub.lambdatest.com/wd/hub";

        DesiredCapabilities caps = new DesiredCapabilities();
        caps.setCapability("browserName", browser);
        caps.setCapability("browserVersion", version);
        HashMap<String, Object> ltOptions = new HashMap<>();
        ltOptions.put("platform", platform);
        ltOptions.put("build", "Parallel Build");
        ltOptions.put("name", browser + " " + platform);
        ltOptions.put("video", true);
        caps.setCapability("LT:Options", ltOptions);

        driver = new RemoteWebDriver(new URL(hub), caps);
        driver.manage().window().maximize();
    }

    @AfterMethod
    public void tearDown(ITestResult result) {
        if (driver != null) {
            String status = result.isSuccess() ? "passed" : "failed";
            ((JavascriptExecutor) driver).executeScript("lambda-status=" + status);
            driver.quit();
        }
    }
}
```

## Parallel Execution — JUnit 5

```properties
# junit-platform.properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=concurrent
junit.jupiter.execution.parallel.config.fixed.parallelism=5
```

## Mobile Testing on Cloud

```java
// Android
DesiredCapabilities caps = new DesiredCapabilities();
caps.setCapability("browserName", "Chrome");
caps.setCapability("browserVersion", "latest");
HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("platformName", "android");
ltOptions.put("deviceName", "Pixel 7");
ltOptions.put("platformVersion", "13");
ltOptions.put("isRealMobile", true);
caps.setCapability("LT:Options", ltOptions);

// iOS — IMPORTANT: use Safari, not Chrome
DesiredCapabilities iosCaps = new DesiredCapabilities();
iosCaps.setCapability("browserName", "Safari");
iosCaps.setCapability("browserVersion", "latest");
HashMap<String, Object> iosOptions = new HashMap<>();
iosOptions.put("platformName", "ios");
iosOptions.put("deviceName", "iPhone 16");
iosOptions.put("platformVersion", "18");
iosOptions.put("isRealMobile", true);
iosCaps.setCapability("LT:Options", iosOptions);
```

## Test Status Reporting

```java
// Java
((JavascriptExecutor) driver).executeScript("lambda-status=" + (passed ? "passed" : "failed"));

// With remark
((JavascriptExecutor) driver).executeScript(
    "lambda-action: {\"action\": \"setTestStatus\", \"arguments\": {\"status\": \""
    + status + "\", \"remark\": \"" + remark + "\"}}"
);
```
