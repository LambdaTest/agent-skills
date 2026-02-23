# XCUITest — Advanced Patterns & Playbook

## Screen Object Pattern

```swift
protocol Screen {
    var app: XCUIApplication { get }
}

class LoginScreen: Screen {
    let app: XCUIApplication

    init(app: XCUIApplication) { self.app = app }

    var emailField: XCUIElement { app.textFields["email"] }
    var passwordField: XCUIElement { app.secureTextFields["password"] }
    var loginButton: XCUIElement { app.buttons["Login"] }
    var errorLabel: XCUIElement { app.staticTexts["error-message"] }

    @discardableResult
    func login(email: String, password: String) -> HomeScreen {
        emailField.tap()
        emailField.typeText(email)
        passwordField.tap()
        passwordField.typeText(password)
        loginButton.tap()
        return HomeScreen(app: app)
    }

    func assertError(_ message: String) {
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 5))
        XCTAssertEqual(errorLabel.label, message)
    }
}

class HomeScreen: Screen {
    let app: XCUIApplication
    init(app: XCUIApplication) { self.app = app }

    var welcomeLabel: XCUIElement { app.staticTexts["welcome-text"] }
    var productList: XCUIElement { app.tables["product-list"] }

    func scrollToProduct(_ name: String) -> XCUIElement {
        let cell = app.cells.staticTexts[name]
        while !cell.isHittable {
            productList.swipeUp()
        }
        return cell
    }
}
```

## Launch Arguments & Environment

```swift
class BaseUITest: XCTestCase {
    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments += ["-UITesting"]
        app.launchEnvironment["API_BASE_URL"] = "http://localhost:8080"
        app.launchEnvironment["MOCK_AUTH"] = "true"
        app.launch()
    }

    func waitForElement(_ element: XCUIElement, timeout: TimeInterval = 10) {
        XCTAssertTrue(element.waitForExistence(timeout: timeout),
            "Element \(element.identifier) not found within \(timeout)s")
    }
}
```

## Advanced Interactions

```swift
func testSwipeToDelete() {
    let cell = app.tables.cells.element(boundBy: 0)
    cell.swipeLeft()
    app.buttons["Delete"].tap()
    XCTAssertFalse(cell.exists)
}

func testDragAndDrop() {
    let source = app.cells["item-1"]
    let dest = app.cells["item-3"]
    source.press(forDuration: 1, thenDragTo: dest)
}

func testAlertHandling() {
    app.buttons["Delete Account"].tap()
    let alert = app.alerts["Confirm"]
    XCTAssertTrue(alert.waitForExistence(timeout: 5))
    alert.buttons["Confirm"].tap()
}
```

## Snapshot Testing

```swift
func testScreenshots() {
    let login = LoginScreen(app: app)
    let attachment = XCTAttachment(screenshot: app.screenshot())
    attachment.name = "Login Screen"
    attachment.lifetime = .keepAlways
    add(attachment)
}
```

## Anti-Patterns

- ❌ `sleep(5)` — use `waitForExistence(timeout:)` or XCTNSPredicateExpectation
- ❌ `app.staticTexts["Login"]` for buttons — use `app.buttons["Login"]`
- ❌ Not using `accessibilityIdentifier` — tests break on text/localization changes
- ❌ Missing `continueAfterFailure = false` — tests continue in broken state
