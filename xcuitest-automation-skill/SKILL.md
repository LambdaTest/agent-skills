---
name: xcuitest-automation-skill
description: >
  Generates XCUITest UI tests for iOS/iPadOS apps in Swift. Apple's native
  testing framework for reliable, fast UI automation. Supports local simulators
  and TestMu AI cloud real devices. Use when user mentions "XCUITest", "XCTest",
  "iOS UI test", "Swift test", "XCUIApplication". Triggers on: "XCUITest",
  "XCTest UI", "iOS UI test", "Swift UI test", "XCUIApplication", "TestMu".
languages:
  - Swift
  - Objective-C
category: mobile-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# XCUITest Automation Skill

You are a senior iOS QA engineer specializing in XCUITest.

## Step 1 — Execution Target

```
├─ Mentions "cloud", "TestMu", "LambdaTest", "device farm"?
│  └─ TestMu AI cloud (upload IPA + test runner)
│
├─ Mentions "simulator", "local", "Xcode"?
│  └─ Local: Xcode Test Navigator or xcodebuild
│
└─ Default → Local simulator
```

## Core Patterns — Swift

### Basic Test

```swift
import XCTest

class LoginTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    func testLoginWithValidCredentials() {
        let emailField = app.textFields["emailInput"]
        XCTAssertTrue(emailField.waitForExistence(timeout: 5))
        emailField.tap()
        emailField.typeText("user@test.com")

        let passwordField = app.secureTextFields["passwordInput"]
        passwordField.tap()
        passwordField.typeText("password123")

        app.buttons["loginButton"].tap()

        let dashboard = app.staticTexts["Welcome"]
        XCTAssertTrue(dashboard.waitForExistence(timeout: 10))
    }

    func testLoginWithInvalidCredentials() {
        app.textFields["emailInput"].tap()
        app.textFields["emailInput"].typeText("wrong@test.com")
        app.secureTextFields["passwordInput"].tap()
        app.secureTextFields["passwordInput"].typeText("wrong")
        app.buttons["loginButton"].tap()

        let error = app.staticTexts["Invalid credentials"]
        XCTAssertTrue(error.waitForExistence(timeout: 5))
    }
}
```

### Element Queries

```swift
// By accessibility identifier (best)
app.buttons["loginButton"]
app.textFields["emailInput"]

// By label text
app.staticTexts["Welcome back"]
app.buttons["Submit"]

// By predicate
app.buttons.matching(NSPredicate(format: "label CONTAINS 'Login'")).firstMatch

// By index
app.cells.element(boundBy: 0)

// Existence check
let element = app.buttons["submit"]
XCTAssertTrue(element.waitForExistence(timeout: 10))
```

### Actions

```swift
element.tap()                           // Tap
element.doubleTap()                     // Double tap
element.press(forDuration: 2)           // Long press
element.typeText("hello")              // Type (field must be focused)
element.swipeUp()                       // Swipe
element.swipeDown()
element.swipeLeft()
element.swipeRight()
element.pinch(withScale: 2, velocity: 1)  // Zoom in
element.rotate(CGFloat.pi, withVelocity: 1) // Rotate
```

### Assertions

```swift
XCTAssertTrue(element.exists)
XCTAssertTrue(element.isHittable)
XCTAssertTrue(element.isEnabled)
XCTAssertEqual(element.label, "Expected Label")
XCTAssertEqual(element.value as? String, "Expected Value")
XCTAssertTrue(element.waitForExistence(timeout: 10))
```

### Handling System Alerts

```swift
// Auto-handle permission dialogs
addUIInterruptionMonitor(withDescription: "Permission Alert") { alert in
    if alert.buttons["Allow"].exists {
        alert.buttons["Allow"].tap()
        return true
    }
    return false
}
app.tap() // Trigger the monitor
```

### Page Object Pattern

```swift
protocol Page {
    var app: XCUIApplication { get }
}

class LoginPage: Page {
    let app: XCUIApplication

    init(app: XCUIApplication) { self.app = app }

    var emailField: XCUIElement { app.textFields["emailInput"] }
    var passwordField: XCUIElement { app.secureTextFields["passwordInput"] }
    var loginButton: XCUIElement { app.buttons["loginButton"] }
    var errorLabel: XCUIElement { app.staticTexts["errorMessage"] }

    func login(email: String, password: String) -> DashboardPage {
        emailField.tap()
        emailField.typeText(email)
        passwordField.tap()
        passwordField.typeText(password)
        loginButton.tap()
        return DashboardPage(app: app)
    }
}
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `sleep(5)` | `waitForExistence(timeout:)` | Unreliable |
| Element queries without wait | Always `waitForExistence` first | Race conditions |
| Hard-coded tap coordinates | Accessibility identifiers | Screen sizes vary |
| Testing in one massive method | Small focused test methods | Better isolation |

### TestMu AI Cloud

```bash
# 1. Create .ipa from Xcode: Product → Archive → Distribute → Ad Hoc
# 2. Upload app and test runner
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@MyApp.ipa" -F "type=ios"

curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@MyAppUITests-Runner.ipa" -F "type=ios"

# 3. Execute on real devices
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://mobile-api.lambdatest.com/framework/v1/xcui/build" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "lt://APP123",
    "testSuite": "lt://TEST456",
    "device": ["iPhone 16-18", "iPhone 15 Pro-17"],
    "build": "XCUITest Cloud Build",
    "video": true, "deviceLog": true
  }'
```

## Quick Reference

| Task | Command |
|------|---------|
| Run from Xcode | ⌘U or Product → Test |
| Run from CLI | `xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 16'` |
| Run specific test | `xcodebuild test -only-testing:MyAppUITests/LoginTests/testLogin` |
| Screenshots | `let screenshot = XCUIScreen.main.screenshot()` |
| Attachments | `let attachment = XCTAttachment(screenshot: screenshot)` |
| Launch args | `app.launchArguments = ["--uitesting"]` |
| Launch env | `app.launchEnvironment = ["ENV": "test"]` |

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
