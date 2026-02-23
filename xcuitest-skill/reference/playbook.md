# XCUITest — Advanced Implementation Playbook

## §1 Project Setup & Configuration

### Test Target Setup (Xcode)
```
1. File → New → Target → UI Testing Bundle
2. Set target membership for test files
3. Set Host Application to your app target
```

### Base Test Class
```swift
import XCTest

class BaseUITest: XCTestCase {
    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = [
            "--uitesting",
            "--reset-state",
            "--disable-animations",
        ]
        app.launchEnvironment = [
            "BASE_URL": ProcessInfo.processInfo.environment["TEST_BASE_URL"] ?? "http://localhost:3001",
            "MOCK_API": "true",
        ]
        app.launch()
    }

    override func tearDownWithError() throws {
        let screenshot = XCUIScreen.main.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = "\(name)_final"
        attachment.lifetime = .deleteOnSuccess
        add(attachment)
        app.terminate()
    }

    // MARK: - Helpers
    func takeNamedScreenshot(_ name: String) {
        let screenshot = XCUIScreen.main.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func waitForElement(_ element: XCUIElement, timeout: TimeInterval = 10) {
        XCTAssertTrue(element.waitForExistence(timeout: timeout),
                      "\(element) not found within \(timeout)s")
    }
}
```

---

## §2 Page Object Pattern

### Screen Protocol
```swift
protocol Screen {
    var app: XCUIApplication { get }
    func verifyOnScreen() -> Self
}

extension Screen {
    @discardableResult
    func verifyOnScreen() -> Self { return self }
}
```

### LoginScreen
```swift
class LoginScreen: Screen {
    let app: XCUIApplication

    init(app: XCUIApplication) { self.app = app }

    // MARK: - Elements
    var emailField: XCUIElement { app.textFields["email_field"] }
    var passwordField: XCUIElement { app.secureTextFields["password_field"] }
    var loginButton: XCUIElement { app.buttons["login_button"] }
    var errorLabel: XCUIElement { app.staticTexts["error_message"] }
    var forgotPasswordLink: XCUIElement { app.buttons["forgot_password"] }

    // MARK: - Actions
    @discardableResult
    func verifyOnScreen() -> Self {
        XCTAssertTrue(emailField.waitForExistence(timeout: 10))
        return self
    }

    @discardableResult
    func enterEmail(_ email: String) -> Self {
        emailField.tap()
        emailField.clearAndType(email)
        return self
    }

    @discardableResult
    func enterPassword(_ password: String) -> Self {
        passwordField.tap()
        passwordField.clearAndType(password)
        return self
    }

    @discardableResult
    func tapLogin() -> DashboardScreen {
        loginButton.tap()
        return DashboardScreen(app: app)
    }

    func login(email: String, password: String) -> DashboardScreen {
        return enterEmail(email)
            .enterPassword(password)
            .tapLogin()
    }

    func loginExpectingError(email: String, password: String) -> Self {
        enterEmail(email)
            .enterPassword(password)
        loginButton.tap()
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 5))
        return self
    }
}
```

### DashboardScreen
```swift
class DashboardScreen: Screen {
    let app: XCUIApplication

    init(app: XCUIApplication) { self.app = app }

    var welcomeLabel: XCUIElement { app.staticTexts["welcome_label"] }
    var settingsButton: XCUIElement { app.buttons["settings_button"] }
    var productList: XCUIElement { app.collectionViews["product_list"] }
    var logoutButton: XCUIElement { app.buttons["logout_button"] }

    @discardableResult
    func verifyOnScreen() -> Self {
        XCTAssertTrue(welcomeLabel.waitForExistence(timeout: 10))
        return self
    }

    func tapSettings() -> SettingsScreen {
        settingsButton.tap()
        return SettingsScreen(app: app)
    }

    func logout() -> LoginScreen {
        logoutButton.tap()
        return LoginScreen(app: app)
    }
}
```

---

## §3 XCUIElement Extensions

```swift
extension XCUIElement {
    func clearAndType(_ text: String) {
        tap()
        if let currentValue = value as? String, !currentValue.isEmpty {
            let deleteString = String(repeating: XCUIKeyboardKey.delete.rawValue,
                                      count: currentValue.count)
            typeText(deleteString)
        }
        typeText(text)
    }

    func waitAndTap(timeout: TimeInterval = 10) {
        XCTAssertTrue(waitForExistence(timeout: timeout),
                      "\(self) not found in \(timeout)s")
        tap()
    }

    func waitForValue(_ expected: String, timeout: TimeInterval = 10) {
        let predicate = NSPredicate(format: "value == %@", expected)
        let expectation = XCTNSPredicateExpectation(predicate: predicate,
                                                     object: self)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        XCTAssertEqual(result, .completed,
                       "Element value did not become '\(expected)' within \(timeout)s")
    }

    var isVisible: Bool {
        exists && isHittable
    }
}
```

### Scroll Helpers
```swift
func scrollToElement(_ element: XCUIElement,
                     in scrollView: XCUIElement,
                     direction: Direction = .down,
                     maxSwipes: Int = 10) {
    var count = 0
    while !element.isHittable && count < maxSwipes {
        switch direction {
        case .down:  scrollView.swipeUp()
        case .up:    scrollView.swipeDown()
        case .left:  scrollView.swipeRight()
        case .right: scrollView.swipeLeft()
        }
        count += 1
    }
    XCTAssertTrue(element.isHittable, "Could not scroll to \(element)")
}

enum Direction { case up, down, left, right }
```

---

## §4 System Alerts & Permissions

```swift
class BaseUITest: XCTestCase {
    override func setUpWithError() throws {
        // Handle system permission dialogs
        addUIInterruptionMonitor(withDescription: "Permission Dialog") { alert in
            let allowButtons = ["Allow", "Allow While Using App", "OK", "Allow Full Access"]
            for buttonLabel in allowButtons {
                let button = alert.buttons[buttonLabel]
                if button.exists {
                    button.tap()
                    return true
                }
            }
            return false
        }
    }
}

// Trigger interruption monitor (requires an interaction after alert appears)
func handlePermissionAlert() {
    app.tap() // triggers the interruption monitor
}
```

### Springboard Interaction (Reset Permissions)
```swift
func resetAppPermissions() {
    let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
    let settingsApp = XCUIApplication(bundleIdentifier: "com.apple.Preferences")

    settingsApp.launch()
    settingsApp.tables.staticTexts["General"].tap()
    settingsApp.tables.staticTexts["Transfer or Reset iPhone"].tap()
    settingsApp.tables.staticTexts["Reset"].tap()
    settingsApp.tables.staticTexts["Reset Location & Privacy"].tap()
}
```

---

## §5 Advanced Test Patterns

### XCTContext for Test Organization
```swift
func testCheckoutFlow() throws {
    XCTContext.runActivity(named: "Login") { _ in
        LoginScreen(app: app)
            .login(email: "user@test.com", password: "password")
            .verifyOnScreen()
    }

    XCTContext.runActivity(named: "Add product to cart") { _ in
        let dashboard = DashboardScreen(app: app)
        dashboard.productList.cells.firstMatch.tap()
        app.buttons["add_to_cart"].waitAndTap()
        takeNamedScreenshot("product_added")
    }

    XCTContext.runActivity(named: "Complete checkout") { _ in
        app.buttons["cart_icon"].tap()
        app.buttons["checkout_button"].waitAndTap()
        waitForElement(app.staticTexts["Order Confirmed"])
        takeNamedScreenshot("order_confirmed")
    }
}
```

### Data-Driven Tests
```swift
func testEmailValidation() throws {
    let testCases: [(email: String, valid: Bool)] = [
        ("user@test.com", true),
        ("invalid", false),
        ("", false),
        ("user@.com", false),
        ("a@b.co", true),
    ]

    let login = LoginScreen(app: app)
    for testCase in testCases {
        XCTContext.runActivity(named: "Email: '\(testCase.email)' → valid: \(testCase.valid)") { _ in
            login.enterEmail(testCase.email)
                .enterPassword("password")
            login.loginButton.tap()

            if testCase.valid {
                XCTAssertFalse(login.errorLabel.exists)
            } else {
                XCTAssertTrue(login.errorLabel.waitForExistence(timeout: 3))
            }
            // Reset for next iteration
            if login.emailField.waitForExistence(timeout: 2) {
                login.emailField.clearAndType("")
            }
        }
    }
}
```

### Handling Keyboard
```swift
func dismissKeyboard() {
    if app.keyboards.count > 0 {
        app.toolbars.buttons["Done"].tap()
    }
}

// Alternative: tap outside
func dismissKeyboardByTapping() {
    app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.1)).tap()
}
```

---

## §6 Network & Performance Testing

### Launch Performance Test
```swift
func testLaunchPerformance() throws {
    if #available(macOS 10.15, iOS 13.0, tvOS 13.0, watchOS 7.0, *) {
        measure(metrics: [XCTApplicationLaunchMetric()]) {
            XCUIApplication().launch()
        }
    }
}
```

### Scroll Performance
```swift
func testScrollPerformance() throws {
    if #available(iOS 14.0, *) {
        let options = XCTMeasureOptions()
        options.invocationCount = 5
        measure(metrics: [XCTOSSignpostMetric.scrollDecelerationMetric],
                options: options) {
            app.collectionViews.firstMatch.swipeUp(velocity: .fast)
        }
    }
}
```

### Monitoring Network Activity
```swift
// Use launch argument to enable network logging in app
app.launchArguments.append("--log-network")

// Assert network calls via UI state
func waitForDataLoaded(timeout: TimeInterval = 15) {
    let loaded = app.staticTexts["data_loaded_indicator"]
    let error = app.staticTexts["error_indicator"]

    let predicate = NSPredicate(format: "exists == true")
    let loadedExpectation = XCTNSPredicateExpectation(predicate: predicate, object: loaded)
    let errorExpectation = XCTNSPredicateExpectation(predicate: predicate, object: error)

    let result = XCTWaiter.wait(for: [loadedExpectation, errorExpectation],
                                 timeout: timeout)
    XCTAssertNotEqual(result, .timedOut, "Data did not load within \(timeout)s")
    XCTAssertFalse(error.exists, "Error indicator appeared")
}
```

---

## §7 LambdaTest Integration

```swift
// Use LambdaTest's real device cloud for XCUITest
// Upload via API:
// curl -u "user:key" \
//   -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
//   -F "appFile=@/path/to/App.ipa" \
//   -F "name=MyApp"

// Configure in .xcodeproj or via xcodebuild:
// xcodebuild test \
//   -project MyApp.xcodeproj \
//   -scheme MyAppUITests \
//   -destination 'platform=iOS,id=<device_udid>'
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: XCUITest CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  ui-test:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app

      - name: Boot Simulator
        run: |
          xcrun simctl boot "iPhone 15"
          xcrun simctl status_bar "iPhone 15" override \
            --time "9:41" --batteryState charged --batteryLevel 100

      - name: Build and Test
        run: |
          xcodebuild test \
            -project MyApp.xcodeproj \
            -scheme MyAppUITests \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.2' \
            -resultBundlePath TestResults.xcresult \
            -enableCodeCoverage YES

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults.xcresult
```

### Fastlane Integration
```ruby
# Fastfile
lane :ui_tests do
  scan(
    project: "MyApp.xcodeproj",
    scheme: "MyAppUITests",
    devices: ["iPhone 15"],
    clean: true,
    code_coverage: true,
    output_directory: "./test_results",
    result_bundle: true,
    fail_build: true
  )
end
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Element not found | Wrong accessibility identifier | Use Accessibility Inspector; verify `accessibilityIdentifier` is set in code |
| 2 | `waitForExistence` times out | Element behind keyboard or off-screen | Dismiss keyboard first; scroll to element before waiting |
| 3 | System alert blocks test | Permission dialog not handled | Add `addUIInterruptionMonitor`; call `app.tap()` to trigger it |
| 4 | `typeText` types wrong characters | Keyboard language mismatch | Set `app.launchArguments += ["-AppleLanguages", "(en)"]` |
| 5 | Flaky tap — element not hittable | Element exists but covered by another view | Use `isHittable` check; scroll or dismiss overlapping elements |
| 6 | `clearAndType` leaves residual text | Secure text field masks character count | Use `tap()` then `press(forDuration: 1.0)` → "Select All" → delete |
| 7 | Screenshots blank in CI | Simulator not fully booted | Add `xcrun simctl boot` + wait before running tests |
| 8 | Animations cause timing issues | Real animations run in test | Set `--disable-animations` launch arg; set `UIView.setAnimationsEnabled(false)` |
| 9 | `app.launch()` slow in setUp | Full app startup each test | Use `app.activate()` for warm start when state reset isn't needed |
| 10 | Interruption monitor doesn't fire | No user interaction after alert | Call `app.tap()` or interact with any element to trigger the handler |
| 11 | Cannot access child of cell | Complex cell hierarchy | Use `.cells.element(boundBy: index).descendants(matching: .button)` |
| 12 | Test passes locally, fails on CI | Different simulator state | Reset simulator: `xcrun simctl erase all` before test run |

---

## §10 Best Practices Checklist

1. ✅ Use accessibility identifiers on every interactive element — never rely on text
2. ✅ Use `waitForExistence(timeout:)` — never use `sleep()` or `Thread.sleep()`
3. ✅ Use `continueAfterFailure = false` for fail-fast behavior
4. ✅ Implement Page Object pattern with fluent `@discardableResult` chaining
5. ✅ Use `XCTContext.runActivity(named:)` to organize test steps in reports
6. ✅ Attach screenshots on failure via `XCTAttachment` in `tearDown`
7. ✅ Use launch arguments/environment for test configuration (mock API, reset state)
8. ✅ Handle system alerts with `addUIInterruptionMonitor` + `app.tap()` trigger
9. ✅ Use `measure(metrics:)` for performance baselines (launch, scroll)
10. ✅ Run on CI with deterministic simulator state: erase + boot + status bar override
11. ✅ Use Fastlane `scan` for structured test execution and reporting
12. ✅ Minimize test coupling — each test should start from a known state
13. ✅ Use `XCTAssertTrue/False` with descriptive messages for clear failure output
