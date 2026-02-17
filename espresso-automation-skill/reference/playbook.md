# Espresso — Advanced Implementation Playbook

## §1 — Project Setup

```gradle
// build.gradle (app)
android {
    defaultConfig {
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        testInstrumentationRunnerArguments clearPackageData: "true"
    }
    testOptions {
        animationsDisabled = true
        execution "ANDROIDX_TEST_ORCHESTRATOR"
    }
}

dependencies {
    androidTestImplementation "androidx.test.espresso:espresso-core:3.5.1"
    androidTestImplementation "androidx.test.espresso:espresso-contrib:3.5.1"
    androidTestImplementation "androidx.test.espresso:espresso-intents:3.5.1"
    androidTestImplementation "androidx.test.espresso:espresso-idling-resource:3.5.1"
    androidTestImplementation "androidx.test.ext:junit:1.1.5"
    androidTestImplementation "androidx.test:runner:1.5.2"
    androidTestImplementation "androidx.test:rules:1.5.0"
    androidTestUtil "androidx.test:orchestrator:1.4.2"
    androidTestImplementation "com.jakewharton.espresso:okhttp3-idling-resource:1.0.0"
    androidTestImplementation "org.mockito:mockito-android:5.10.0"
    androidTestImplementation "io.mockk:mockk-android:1.13.10"
    androidTestImplementation "com.squareup.okhttp3:mockwebserver:4.12.0"
}
```

## §2 — Test Structure & Lifecycle

```kotlin
@RunWith(AndroidJUnit4::class)
@LargeTest
class LoginTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @get:Rule
    val grantPermissionRule = GrantPermissionRule.grant(
        android.Manifest.permission.CAMERA,
        android.Manifest.permission.ACCESS_FINE_LOCATION
    )

    @Before
    fun setup() {
        IdlingRegistry.getInstance().register(EspressoIdlingResource.countingIdlingResource)
    }

    @After
    fun teardown() {
        IdlingRegistry.getInstance().unregister(EspressoIdlingResource.countingIdlingResource)
    }

    @Test
    fun successfulLogin() {
        onView(withId(R.id.emailInput))
            .perform(typeText("user@test.com"), closeSoftKeyboard())
        onView(withId(R.id.passwordInput))
            .perform(typeText("password123"), closeSoftKeyboard())
        onView(withId(R.id.loginBtn)).perform(click())
        onView(withId(R.id.welcomeText))
            .check(matches(withText(containsString("Welcome"))))
    }

    @Test
    fun showsErrorOnInvalidEmail() {
        onView(withId(R.id.emailInput))
            .perform(typeText("invalid"), closeSoftKeyboard())
        onView(withId(R.id.loginBtn)).perform(click())
        onView(withId(R.id.emailError))
            .check(matches(withText("Invalid email format")))
    }

    @Test
    fun emptyFieldsShowValidation() {
        onView(withId(R.id.loginBtn)).perform(click())
        onView(withId(R.id.emailError))
            .check(matches(isDisplayed()))
        onView(withId(R.id.passwordError))
            .check(matches(isDisplayed()))
    }
}
```

## §3 — Custom Matchers & ViewActions

```kotlin
// Custom matcher: RecyclerView item count
fun hasItemCount(count: Int): Matcher<View> =
    object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(desc: Description) { desc.appendText("has $count items") }
        override fun matchesSafely(rv: RecyclerView) = rv.adapter?.itemCount == count
    }

// Custom matcher: EditText error text
fun hasErrorText(expected: String): Matcher<View> =
    object : BoundedMatcher<View, EditText>(EditText::class.java) {
        override fun describeTo(desc: Description) { desc.appendText("has error: $expected") }
        override fun matchesSafely(item: EditText) = item.error?.toString() == expected
    }

// Custom matcher: view at specific position in RecyclerView
fun atPosition(position: Int, matcher: Matcher<View>): Matcher<View> =
    object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(desc: Description) {
            desc.appendText("has item at position $position matching: ")
            matcher.describeTo(desc)
        }
        override fun matchesSafely(rv: RecyclerView): Boolean {
            val vh = rv.findViewHolderForAdapterPosition(position) ?: return false
            return matcher.matches(vh.itemView)
        }
    }

// Wait for view (idling-safe alternative)
fun waitForView(viewMatcher: Matcher<View>, timeout: Long = 5000): ViewInteraction {
    val end = System.currentTimeMillis() + timeout
    while (System.currentTimeMillis() < end) {
        try {
            return onView(viewMatcher).check(matches(isDisplayed()))
        } catch (e: Exception) { Thread.sleep(100) }
    }
    throw AssertionError("View not found within ${timeout}ms")
}

// Custom scroll action for NestedScrollView
fun nestedScrollTo(): ViewAction = object : ViewAction {
    override fun getConstraints() = allOf(isDescendantOfA(isAssignableFrom(NestedScrollView::class.java)))
    override fun getDescription() = "nested scroll to"
    override fun perform(uiController: UiController, view: View) {
        view.requestRectangleOnScreen(Rect(0, 0, view.width, view.height), true)
        uiController.loopMainThreadUntilIdle()
    }
}
```

## §4 — RecyclerView Testing

```kotlin
// Scroll and click
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.scrollToPosition<ViewHolder>(15))
    .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(15, click()))

// Click on specific view inside item
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(3,
        clickOnViewChild(R.id.deleteBtn)))

fun clickOnViewChild(viewId: Int): ViewAction = object : ViewAction {
    override fun getConstraints() = null
    override fun getDescription() = "Click on child view"
    override fun perform(uiController: UiController, view: View) {
        view.findViewById<View>(viewId).performClick()
    }
}

// Assert item content
onView(withId(R.id.recyclerView))
    .check(matches(atPosition(0,
        hasDescendant(withText("First Item")))))

// Assert total count
onView(withId(R.id.recyclerView)).check(matches(hasItemCount(10)))

// Swipe to dismiss
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(2,
        swipeLeft()))
```

## §5 — Idling Resources

```kotlin
// CountingIdlingResource (most common)
object EspressoIdlingResource {
    private const val RESOURCE = "GLOBAL"
    @JvmField val countingIdlingResource = CountingIdlingResource(RESOURCE)

    fun increment() = countingIdlingResource.increment()
    fun decrement() {
        if (!countingIdlingResource.isIdleNow) countingIdlingResource.decrement()
    }
}

// Usage in production code
class UserRepository(private val api: UserApi) {
    suspend fun getUsers(): List<User> {
        EspressoIdlingResource.increment()
        try {
            return api.getUsers()
        } finally {
            EspressoIdlingResource.decrement()
        }
    }
}

// OkHttp IdlingResource
val client = OkHttpClient.Builder().build()
val idlingResource = OkHttp3IdlingResource.create("OkHttp", client)

@Before fun register() { IdlingRegistry.getInstance().register(idlingResource) }
@After fun unregister() { IdlingRegistry.getInstance().unregister(idlingResource) }

// Custom IdlingResource for animations
class ViewAnimationIdlingResource(private val view: View) : IdlingResource {
    private var callback: IdlingResource.ResourceCallback? = null
    override fun getName() = "ViewAnimation:${view.id}"
    override fun isIdleNow(): Boolean {
        val idle = !view.isAnimating()
        if (idle) callback?.onTransitionToIdle()
        return idle
    }
    override fun registerIdleTransitionCallback(cb: IdlingResource.ResourceCallback) { callback = cb }
}
```

## §6 — Intent Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class IntentTest {
    @get:Rule val intentsRule = IntentsTestRule(MainActivity::class.java)

    @Test
    fun opensShareIntent() {
        onView(withId(R.id.shareBtn)).perform(click())

        intended(allOf(
            hasAction(Intent.ACTION_SEND),
            hasType("text/plain"),
            hasExtra(Intent.EXTRA_TEXT, containsString("Check this out"))
        ))
    }

    @Test
    fun stubsExternalActivity() {
        // Stub external intent response
        intending(hasAction(Intent.ACTION_VIEW))
            .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, null))

        onView(withId(R.id.externalLink)).perform(click())

        intended(hasData(Uri.parse("https://example.com")))
    }

    @Test
    fun stubsCameraIntent() {
        val resultData = Intent().apply {
            putExtra("data", createTestBitmap())
        }
        intending(hasAction(MediaStore.ACTION_IMAGE_CAPTURE))
            .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, resultData))

        onView(withId(R.id.cameraBtn)).perform(click())
        onView(withId(R.id.previewImage)).check(matches(isDisplayed()))
    }
}
```

## §7 — MockWebServer for API Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class ApiIntegrationTest {
    private lateinit var mockServer: MockWebServer

    @Before
    fun setup() {
        mockServer = MockWebServer()
        mockServer.start(8080)
        // Configure app to use mock server URL
    }

    @After
    fun teardown() { mockServer.shutdown() }

    @Test
    fun displaysUsersFromApi() {
        mockServer.enqueue(MockResponse()
            .setBody("""[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]""")
            .addHeader("Content-Type", "application/json"))

        val scenario = ActivityScenario.launch(UserListActivity::class.java)

        onView(withId(R.id.recyclerView))
            .check(matches(hasItemCount(2)))
        onView(withId(R.id.recyclerView))
            .check(matches(atPosition(0, hasDescendant(withText("Alice")))))
    }

    @Test
    fun handlesServerError() {
        mockServer.enqueue(MockResponse().setResponseCode(500))

        val scenario = ActivityScenario.launch(UserListActivity::class.java)

        onView(withId(R.id.errorView)).check(matches(isDisplayed()))
        onView(withId(R.id.retryBtn)).check(matches(isDisplayed()))
    }
}
```

## §8 — CI/CD Integration

```yaml
# GitHub Actions
name: Espresso Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Run Espresso tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          target: google_apis
          arch: x86_64
          disable-animations: true
          script: ./gradlew connectedAndroidTest
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: espresso-results
          path: app/build/reports/androidTests/
```

## §9 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| `NoMatchingViewException` | View not in hierarchy | Check `onView(isRoot()).perform(closeSoftKeyboard())`, scroll to view |
| `AmbiguousViewMatcherException` | Multiple matching views | Add more matchers: `allOf(withId(...), isDisplayed())` |
| `PerformException` on click | View not clickable/visible | Use `scrollTo()` or `nestedScrollTo()` before click |
| Test hangs | No IdlingResource for async | Register `CountingIdlingResource` or `OkHttp3IdlingResource` |
| Animations cause flakiness | System animations enabled | Set `animationsDisabled = true` in `testOptions` |
| `NoActivityResumedError` | Activity finished or crashed | Check `ActivityScenarioRule` setup, verify activity launches |
| RecyclerView not found | Not scrolled into view | Use `RecyclerViewActions.scrollToPosition()` first |
| Intent not captured | `Intents.init()` not called | Use `IntentsTestRule` or call `Intents.init()` in `@Before` |
| Keyboard overlaps view | Soft keyboard blocking | Call `closeSoftKeyboard()` after `typeText()` |
| Flaky on CI | Timing issues | Use Orchestrator, disable animations, increase timeout |

## §10 — Best Practices Checklist

- ✅ Use `IdlingResource` instead of `Thread.sleep()` — always
- ✅ Use `withId()` over `withText()` for selector stability
- ✅ Always call `closeSoftKeyboard()` after `typeText()`
- ✅ Use `ActivityScenarioRule` for lifecycle management
- ✅ Set `animationsDisabled = true` in Gradle test options
- ✅ Use Orchestrator for isolated test execution
- ✅ Use `MockWebServer` for API response testing
- ✅ Use `@LargeTest` / `@MediumTest` / `@SmallTest` annotations
- ✅ Use custom matchers for RecyclerView assertions
- ✅ Release `Intents` in `@After` to prevent leaks
- ✅ Use `GrantPermissionRule` for runtime permissions
- ✅ Register/unregister IdlingResources in `@Before`/`@After`
- ✅ Structure: `androidTest/tests/`, `androidTest/robots/`, `androidTest/utils/`
