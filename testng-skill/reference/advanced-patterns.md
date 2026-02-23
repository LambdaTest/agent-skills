# TestNG — Advanced Patterns & Playbook

## Data Providers

```java
@DataProvider(name = "loginData", parallel = true)
public Object[][] loginData() {
    return new Object[][] {
        {"admin", "pass123", true},
        {"user", "wrong", false},
        {"", "", false}
    };
}

@Test(dataProvider = "loginData")
public void testLogin(String user, String pass, boolean expected) {
    assertEquals(authService.login(user, pass), expected);
}

// External data provider from Excel/CSV
@DataProvider(name = "excelData")
public Iterator<Object[]> excelData() throws Exception {
    return ExcelReader.read("test-data/users.xlsx").stream()
        .map(row -> new Object[]{row.get("name"), row.get("email")})
        .iterator();
}

// Factory pattern for dynamic test instances
@Factory(dataProvider = "browserData")
public BrowserTest(String browser, String version) {
    this.browser = browser; this.version = version;
}
@DataProvider
public static Object[][] browserData() {
    return new Object[][] {{"chrome","latest"},{"firefox","latest"}};
}
```

## Groups & Dependencies

```java
@Test(groups = {"smoke", "regression"})
public void testHomepage() { /* ... */ }

@Test(groups = "regression", dependsOnGroups = "smoke")
public void testCheckout() { /* ... */ }

@Test(dependsOnMethods = "testLogin", alwaysRun = true)
public void testLogout() { /* ... */ }

// Soft assertions — collect all failures
@Test
public void testUserProfile() {
    SoftAssert soft = new SoftAssert();
    User user = getUser(1);
    soft.assertEquals(user.getName(), "Alice");
    soft.assertEquals(user.getAge(), 30);
    soft.assertNotNull(user.getEmail());
    soft.assertAll(); // Report all failures at once
}
```

## Listeners

```java
public class RetryAnalyzer implements IRetryAnalyzer {
    private int count = 0;
    private static final int MAX_RETRY = 2;
    @Override
    public boolean retry(ITestResult result) {
        return count++ < MAX_RETRY;
    }
}

public class TestListener implements ITestListener {
    @Override
    public void onTestStart(ITestResult result) {
        System.out.println("Starting: " + result.getName());
    }
    @Override
    public void onTestFailure(ITestResult result) {
        // Capture screenshot, log details
        Screenshot.capture(result.getName());
    }
}

// Apply globally
@Listeners({TestListener.class})
public class BaseTest { /* ... */ }
```

## Suite Configuration

```xml
<!-- testng.xml -->
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Regression" parallel="methods" thread-count="4" verbose="1">
    <listeners>
        <listener class-name="com.test.TestListener"/>
    </listeners>
    <test name="Smoke">
        <groups><run><include name="smoke"/></run></groups>
        <classes><class name="com.test.SmokeTests"/></classes>
    </test>
    <test name="Full">
        <packages><package name="com.test.regression"/></packages>
    </test>
</suite>
```

## Anti-Patterns

- ❌ `@Test(priority = N)` for ordering — use `dependsOnMethods` or groups
- ❌ `Thread.sleep()` in tests — use explicit waits or polling
- ❌ `@Test(enabled = false)` committed — use groups to exclude instead
- ❌ Hardcoded test data in methods — use DataProviders
- ❌ Missing `SoftAssert.assertAll()` — silently passes with failures
