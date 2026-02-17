# Espresso — Advanced Patterns

## Intent Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class IntentTest {
    @get:Rule
    val intentsRule = IntentsTestRule(MainActivity::class.java)

    @Test
    fun clickShare_launchesChooser() {
        onView(withId(R.id.shareButton)).perform(click())
        intended(hasAction(Intent.ACTION_CHOOSER))
    }

    @Test
    fun clickLink_opensExternalBrowser() {
        intending(hasAction(Intent.ACTION_VIEW))
            .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, null))
        onView(withId(R.id.externalLink)).perform(click())
        intended(allOf(hasAction(Intent.ACTION_VIEW), hasData("https://example.com")))
    }
}
```

## RecyclerView Testing

```kotlin
// Click item at position
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<ViewHolder>(3, click()))

// Scroll to item with text
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.scrollTo<ViewHolder>(
        hasDescendant(withText("Item 42"))
    ))

// Check item at position
onView(withId(R.id.recyclerView))
    .check(matches(atPosition(0, hasDescendant(withText("First Item")))))
```

## Custom ViewMatcher

```kotlin
fun withItemCount(expectedCount: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("RecyclerView with item count: $expectedCount")
        }
        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == expectedCount
        }
    }
}

// Usage
onView(withId(R.id.recyclerView)).check(matches(withItemCount(10)))
```
