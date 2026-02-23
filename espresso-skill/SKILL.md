---
name: espresso-skill
description: >
  Generates Espresso UI tests for Android apps in Kotlin or Java. Espresso runs
  inside the app process for fast, reliable UI testing. Supports local and TestMu AI
  cloud real devices. Use when user mentions "Espresso", "onView", "ViewMatchers",
  "Android UI test", or "instrumentation test". Triggers on: "Espresso",
  "onView", "ViewMatchers", "Android UI test", "instrumentation", "TestMu".
languages:
  - Java
  - Kotlin
category: mobile-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Espresso Automation Skill

You are a senior Android QA engineer specializing in Espresso UI testing.

## Step 1 — Execution Target

```
├─ Mentions "cloud", "TestMu", "LambdaTest", "device farm"?
│  └─ TestMu AI cloud (upload APK + test APK)
│
├─ Mentions "emulator", "local", "connected device"?
│  └─ Local: ./gradlew connectedAndroidTest
│
└─ Default → Local emulator
```

## Core Patterns — Kotlin (Default)

### Basic Test

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginWithValidCredentials() {
        // Type email
        onView(withId(R.id.emailInput))
            .perform(typeText("user@test.com"), closeSoftKeyboard())

        // Type password
        onView(withId(R.id.passwordInput))
            .perform(typeText("password123"), closeSoftKeyboard())

        // Click login button
        onView(withId(R.id.loginButton))
            .perform(click())

        // Verify dashboard is displayed
        onView(withId(R.id.dashboardTitle))
            .check(matches(isDisplayed()))
            .check(matches(withText("Welcome")))
    }

    @Test
    fun loginWithInvalidCredentials_showsError() {
        onView(withId(R.id.emailInput))
            .perform(typeText("wrong@test.com"), closeSoftKeyboard())
        onView(withId(R.id.passwordInput))
            .perform(typeText("wrong"), closeSoftKeyboard())
        onView(withId(R.id.loginButton))
            .perform(click())
        onView(withId(R.id.errorText))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString("Invalid"))))
    }
}
```

### ViewMatchers (Finding Elements)

```kotlin
// By ID (best)
onView(withId(R.id.loginButton))

// By text
onView(withText("Login"))

// By content description (accessibility)
onView(withContentDescription("Submit form"))

// By hint text
onView(withHint("Enter your email"))

// Combined matchers
onView(allOf(withId(R.id.button), withText("Submit"), isDisplayed()))

// In RecyclerView
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(0, click()))

// By parent
onView(allOf(withText("Delete"), isDescendantOfA(withId(R.id.toolbar))))
```

### ViewActions (Performing Actions)

```kotlin
.perform(click())                          // Tap
.perform(longClick())                      // Long press
.perform(typeText("hello"))                // Type text
.perform(replaceText("new text"))          // Replace text
.perform(clearText())                      // Clear field
.perform(closeSoftKeyboard())              // Dismiss keyboard
.perform(scrollTo())                       // Scroll to element
.perform(swipeUp())                        // Swipe gesture
.perform(swipeDown())
.perform(swipeLeft())
.perform(swipeRight())
.perform(pressBack())                      // Back button
```

### ViewAssertions (Checking State)

```kotlin
.check(matches(isDisplayed()))             // Visible
.check(matches(not(isDisplayed())))        // Not visible
.check(matches(withText("Expected")))      // Text matches
.check(matches(isEnabled()))               // Enabled
.check(matches(isChecked()))               // Checkbox checked
.check(matches(hasErrorText("Required")))  // Error text
.check(doesNotExist())                     // Not in hierarchy
```

### Idling Resources (Async Operations)

```kotlin
// Register before test
@Before
fun setUp() {
    IdlingRegistry.getInstance().register(myIdlingResource)
}

// Unregister after test
@After
fun tearDown() {
    IdlingRegistry.getInstance().unregister(myIdlingResource)
}

// Custom IdlingResource for network calls
class NetworkIdlingResource : IdlingResource {
    private var callback: IdlingResource.ResourceCallback? = null
    private var isIdle = true

    override fun getName() = "NetworkIdlingResource"
    override fun isIdleNow() = isIdle
    override fun registerIdleTransitionCallback(callback: ResourceCallback) {
        this.callback = callback
    }

    fun setIdle(idle: Boolean) {
        isIdle = idle
        if (idle) callback?.onTransitionToIdle()
    }
}
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `Thread.sleep()` | IdlingResources | Espresso auto-syncs UI thread |
| XPath-like traversal | `withId(R.id.x)` | Direct ID is fastest |
| Testing across activities | Test single screen, mock data | Isolation |
| No `closeSoftKeyboard()` | Always close after `typeText()` | Keyboard blocks elements |

### TestMu AI Cloud

```bash
# 1. Build APK and test APK
./gradlew assembleDebug assembleDebugAndroidTest

# 2. Upload both to LambdaTest
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@app/build/outputs/apk/debug/app-debug.apk" \
  -F "type=android"

curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk" \
  -F "type=android"

# 3. Execute on real devices via API
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://mobile-api.lambdatest.com/framework/v1/espresso/build" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "lt://APP123",
    "testSuite": "lt://TEST456",
    "device": ["Pixel 8-14", "Galaxy S24-14"],
    "build": "Espresso Cloud Build",
    "video": true, "deviceLog": true
  }'
```

## build.gradle Setup

```groovy
android {
    defaultConfig {
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }
}

dependencies {
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    androidTestImplementation 'androidx.test.espresso:espresso-contrib:3.5.1'
    androidTestImplementation 'androidx.test.espresso:espresso-intents:3.5.1'
    androidTestImplementation 'androidx.test:runner:1.5.2'
    androidTestImplementation 'androidx.test:rules:1.5.0'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
}
```

## Quick Reference

| Task | Command/Code |
|------|-------------|
| Run all tests | `./gradlew connectedAndroidTest` |
| Run specific class | `./gradlew connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.example.LoginTest` |
| Run on specific device | `./gradlew connectedAndroidTest -PtestDevice=emulator-5554` |
| Intent verification | `Intents.init()` → `intended(hasComponent(...))` → `Intents.release()` |
| RecyclerView scroll | `RecyclerViewActions.scrollToPosition<>(10)` |
| Screenshot | `Screenshot.capture(activityRule.activity)` |

## Reference Files

| File | When to Read |
|------|-------------|
| `reference/cloud-integration.md` | LambdaTest Espresso, device farm, API |
| `reference/advanced-patterns.md` | Intents, RecyclerView, custom matchers |

## Deep Patterns → `reference/playbook.md`

| § | Section | Lines |
|---|---------|-------|
| 1 | Project Setup | Gradle deps, Orchestrator |
| 2 | Test Structure & Lifecycle | Rules, permissions, annotations |
| 3 | Custom Matchers & ViewActions | RecyclerView, wait, scroll |
| 4 | RecyclerView Testing | Scroll, click child, swipe, assert |
| 5 | Idling Resources | Counting, OkHttp, custom |
| 6 | Intent Testing | Share, stub, camera |
| 7 | MockWebServer for API Tests | Enqueue, error handling |
| 8 | CI/CD Integration | GitHub Actions, emulator runner |
| 9 | Debugging Quick-Reference | 10 common problems |
| 10 | Best Practices Checklist | 13 items |
