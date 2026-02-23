# Geb — Advanced Playbook

## §1 — Project Setup

### build.gradle
```groovy
plugins {
    id 'groovy'
    id 'idea'
}

repositories {
    mavenCentral()
}

dependencies {
    // Geb
    testImplementation 'org.gebish:geb-spock:7.0'
    testImplementation 'org.gebish:geb-core:7.0'

    // Spock
    testImplementation 'org.spockframework:spock-core:2.4-M1-groovy-4.0'
    testImplementation platform('org.apache.groovy:groovy-bom:4.0.15')
    testImplementation 'org.apache.groovy:groovy'

    // Selenium
    testImplementation 'org.seleniumhq.selenium:selenium-java:4.18.1'
    testImplementation 'io.github.bonigarcia:webdrivermanager:5.7.0'

    // Reporting
    testImplementation 'org.gebish:geb-reports:7.0'
}

test {
    useJUnitPlatform()
    systemProperty 'geb.env', System.getProperty('geb.env', 'chrome')
    systemProperty 'geb.build.reportsDir', 'build/geb-reports'
}
```

### GebConfig.groovy
```groovy
import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.remote.RemoteWebDriver

waiting {
    timeout = 10
    retryInterval = 0.5
    includeCauseInMessage = true
    presets {
        slow  { timeout = 30; retryInterval = 1 }
        quick { timeout = 3;  retryInterval = 0.25 }
    }
}

atCheckWaiting = true

environments {
    chrome {
        driver = {
            ChromeOptions options = new ChromeOptions()
            options.addArguments('--disable-search-engine-choice-screen')
            new ChromeDriver(options)
        }
    }

    chromeHeadless {
        driver = {
            ChromeOptions options = new ChromeOptions()
            options.addArguments('--headless=new', '--no-sandbox', '--disable-gpu')
            new ChromeDriver(options)
        }
    }

    firefox {
        driver = { new FirefoxDriver() }
    }

    lambdatest {
        driver = {
            String username = System.getenv('LT_USERNAME')
            String accessKey = System.getenv('LT_ACCESS_KEY')

            ChromeOptions options = new ChromeOptions()
            options.setPlatformName('Windows 11')
            options.setBrowserVersion('latest')

            Map ltOptions = [
                project : 'Geb Tests',
                build   : "geb-${System.getenv('BUILD_NUMBER') ?: 'local'}",
                name    : 'Geb Spec',
                console : true,
                network : true,
                visual  : true,
                w3c     : true
            ]
            options.setCapability('LT:Options', ltOptions)

            new RemoteWebDriver(
                new URL("https://${username}:${accessKey}@hub.lambdatest.com/wd/hub"),
                options
            )
        }
    }
}

baseUrl = System.getProperty('geb.baseUrl', 'http://localhost:3000')
reportsDir = new File('build/geb-reports')
```

### Project Structure
```
project/
├── src/test/groovy/
│   ├── specs/
│   │   ├── LoginSpec.groovy
│   │   ├── CheckoutSpec.groovy
│   │   └── ApiSpec.groovy
│   ├── pages/
│   │   ├── LoginPage.groovy
│   │   ├── DashboardPage.groovy
│   │   └── modules/
│   │       ├── NavModule.groovy
│   │       └── AlertModule.groovy
│   └── utils/
│       └── TestDataHelper.groovy
├── src/test/resources/
│   ├── GebConfig.groovy
│   └── testdata/
│       └── users.json
├── build.gradle
└── settings.gradle
```

---

## §2 — Page Objects

### Basic Page Object
```groovy
import geb.Page

class LoginPage extends Page {
    static url = '/login'
    static at = { title.contains('Login') && emailInput.displayed }

    static content = {
        emailInput    { $('input[data-testid="email"]') }
        passwordInput { $('input[data-testid="password"]') }
        submitBtn     { $('button[data-testid="login-submit"]') }
        errorMsg      { $('[role="alert"]', required: false) }
        rememberMe    { $('input[name="remember"]') }
        forgotLink    { $('a', text: 'Forgot password?') }
    }

    void login(String email, String password) {
        emailInput.value(email)
        passwordInput.value(password)
        submitBtn.click()
    }

    boolean hasError() {
        errorMsg.displayed
    }

    String getError() {
        errorMsg.text()
    }
}

class DashboardPage extends Page {
    static url = '/dashboard'
    static at = { heading.displayed }

    static content = {
        heading     { $('h1[data-testid="welcome"]') }
        nav         { module NavModule }
        statsCards  { $('[data-testid="stat-card"]') }
        recentItems { $('[data-testid="recent-item"]') }
        userMenu    { $('[data-testid="user-menu"]') }
        logoutBtn   { $('[data-testid="logout"]') }
    }

    String getWelcomeText() {
        heading.text()
    }

    int getStatCount() {
        statsCards.size()
    }

    void logout() {
        userMenu.click()
        logoutBtn.click()
    }
}
```

### Modules (Reusable Components)
```groovy
import geb.Module

class NavModule extends Module {
    static content = {
        links      { $('nav a') }
        activeLink { $('nav a.active') }
        dropdown   { $('[data-testid="nav-dropdown"]', required: false) }
    }

    void navigateTo(String linkText) {
        links.find { it.text() == linkText }.click()
    }

    boolean isActive(String linkText) {
        activeLink.text() == linkText
    }
}

class AlertModule extends Module {
    static content = {
        container { $('[role="alert"]') }
        message   { container.$('.alert-message') }
        closeBtn  { container.$('.alert-close') }
    }

    String getText() {
        message.text()
    }

    void dismiss() {
        closeBtn.click()
        waitFor { !container.displayed }
    }
}

class DataTableModule extends Module {
    static content = {
        headers { $('thead th') }
        rows    { $('tbody tr') }
        cells   { rows.$('td') }
        sortBtn { $('th button.sort') }
    }

    int getRowCount() {
        rows.size()
    }

    List<String> getColumnValues(int colIndex) {
        rows.collect { it.$('td', colIndex).text() }
    }

    void sortBy(String columnName) {
        sortBtn.find { it.closest('th').text().contains(columnName) }.click()
    }
}
```

### Page with Parameterized URL
```groovy
class ProductPage extends Page {
    static url = '/products'

    static at = { productTitle.displayed }

    static content = {
        productTitle  { $('h1.product-name') }
        price         { $('[data-testid="price"]') }
        addToCartBtn  { $('button', text: 'Add to Cart') }
        quantity      { $('input[name="quantity"]') }
        reviews       { $('[data-testid="review"]') }
        avgRating     { $('[data-testid="avg-rating"]') }
    }

    void setQuantity(int qty) {
        quantity.value(qty)
    }

    void addToCart() {
        addToCartBtn.click()
    }

    BigDecimal getPrice() {
        new BigDecimal(price.text().replaceAll('[^0-9.]', ''))
    }
}
```

---

## §3 — Spec Tests (Spock Integration)

### Basic Spec
```groovy
import geb.spock.GebReportingSpec
import spock.lang.Narrative
import spock.lang.Stepwise

@Narrative('User authentication scenarios')
class LoginSpec extends GebReportingSpec {

    def 'successful login redirects to dashboard'() {
        when: 'user navigates to login page'
        to LoginPage

        and: 'enters valid credentials'
        login('user@test.com', 'password123')

        then: 'redirected to dashboard'
        at DashboardPage

        and: 'welcome message is displayed'
        welcomeText.contains('Welcome')
    }

    def 'invalid credentials show error message'() {
        when:
        to LoginPage
        login('user@test.com', 'wrongpassword')

        then:
        at LoginPage
        hasError()
        getError() == 'Invalid email or password'
    }

    def 'empty form shows validation errors'() {
        when:
        to LoginPage
        submitBtn.click()

        then:
        at LoginPage
        $('.field-error').size() >= 2
    }
}
```

### Data-Driven Testing
```groovy
import spock.lang.Unroll

class SearchSpec extends GebReportingSpec {

    @Unroll
    def 'search for "#query" returns at least #minResults results'() {
        when:
        to SearchPage
        searchInput.value(query)
        searchBtn.click()

        then:
        waitFor { resultList.displayed }
        resultItems.size() >= minResults

        where:
        query        | minResults
        'laptop'     | 5
        'wireless'   | 3
        'xyznonexist'| 0
    }

    @Unroll
    def 'filter by category #category shows correct products'() {
        when:
        to ProductListPage
        categoryFilter.value(category)
        applyFilters()

        then:
        waitFor { productCards.displayed }
        productCards.every { it.$('.category-badge').text() == category }

        where:
        category << ['Electronics', 'Books', 'Clothing']
    }
}
```

### Stepwise Spec (Ordered Scenarios)
```groovy
@Stepwise
class CheckoutFlowSpec extends GebReportingSpec {

    def 'user logs in'() {
        when:
        to LoginPage
        login('buyer@test.com', 'pass123')

        then:
        at DashboardPage
    }

    def 'user adds product to cart'() {
        when:
        to ProductPage
        setQuantity(2)
        addToCart()

        then:
        waitFor { $('[data-testid="cart-badge"]').text() == '2' }
    }

    def 'user completes checkout'() {
        when:
        to CartPage
        checkoutBtn.click()

        then:
        at CheckoutPage

        when:
        fillShippingAddress()
        selectPaymentMethod('credit_card')
        confirmOrder()

        then:
        at OrderConfirmationPage
        orderNumber.displayed
    }
}
```

---

## §4 — Waiting & Async Content

### Waiting Strategies
```groovy
class AsyncSpec extends GebReportingSpec {

    def 'lazy-loaded content appears'() {
        when:
        to DashboardPage

        then: 'wait with default timeout (10s)'
        waitFor { recentItems.displayed }
        recentItems.size() > 0
    }

    def 'slow API response handled with preset'() {
        when:
        to ReportsPage
        generateBtn.click()

        then: 'use slow waiting preset (30s)'
        waitFor('slow') { reportTable.displayed }
        reportTable.rows.size() > 0
    }

    def 'quick check for toast notification'() {
        when:
        to SettingsPage
        saveBtn.click()

        then: 'use quick preset (3s)'
        waitFor('quick') { toastMessage.displayed }
        toastMessage.text().contains('Saved')
    }

    def 'element disappears after action'() {
        when:
        to ModalPage
        openModalBtn.click()
        waitFor { modal.displayed }
        modal.closeBtn.click()

        then:
        waitFor { !modal.displayed }
    }

    def 'retry content assertion'() {
        when:
        to LiveFeedPage

        then: 'content updates dynamically'
        waitFor {
            feedItems.size() >= 5 && feedItems[0].text().contains('new')
        }
    }
}
```

### JavaScript Interaction
```groovy
class JsInteractionSpec extends GebReportingSpec {

    def 'execute JavaScript on page'() {
        when:
        to DashboardPage

        then:
        js.exec('return document.title') == 'Dashboard'

        when: 'scroll to element'
        js.exec('arguments[0].scrollIntoView(true)', footer.firstElement())

        then:
        footer.displayed
    }

    def 'interact with browser alert'() {
        when:
        to SettingsPage
        deleteAccountBtn.click()

        then:
        withAlert { it == 'Are you sure?' }
    }

    def 'handle confirm dialog'() {
        when:
        to SettingsPage
        deleteAccountBtn.click()

        then:
        withConfirm(true) { it.contains('Are you sure') }
    }
}
```

---

## §5 — Advanced Patterns

### File Upload & Download
```groovy
class FileSpec extends GebReportingSpec {

    def 'upload a file'() {
        when:
        to UploadPage
        fileInput.value(new File('src/test/resources/testdata/sample.pdf').absolutePath)
        uploadBtn.click()

        then:
        waitFor { successMsg.displayed }
        successMsg.text().contains('sample.pdf')
    }

    def 'download report'() {
        given:
        def downloadDir = new File('build/downloads')
        downloadDir.mkdirs()

        when:
        to ReportsPage
        exportBtn.click()

        then:
        waitFor(30) {
            downloadDir.listFiles()?.any { it.name.endsWith('.csv') }
        }
    }
}
```

### Multiple Windows & Frames
```groovy
class WindowSpec extends GebReportingSpec {

    def 'handle new window'() {
        when:
        to DashboardPage
        externalLink.click()

        then:
        withWindow({ title.contains('External') }) {
            $('h1').text() == 'External Page'
        }
    }

    def 'interact with iframe'() {
        when:
        to EditorPage

        then:
        withFrame('editor-frame') {
            $('body').text().contains('Edit here')
        }
    }
}
```

### Custom Navigator Extensions
```groovy
// In GebConfig.groovy or separate file
import geb.navigator.Navigator

Navigator.metaClass.selectOption = { String text ->
    delegate.find('option', text: text).click()
}

Navigator.metaClass.hasClass = { String className ->
    delegate.classes().contains(className)
}

// Usage in specs
class CustomSpec extends GebReportingSpec {
    def 'use custom extensions'() {
        when:
        to FormPage
        roleSelect.selectOption('Admin')

        then:
        roleSelect.hasClass('selected')
    }
}
```

---

## §6 — API Testing with Geb

### REST API Specs
```groovy
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

class ApiSpec extends GebReportingSpec {

    def jsonSlurper = new JsonSlurper()
    def baseApiUrl = System.getProperty('geb.baseUrl', 'http://localhost:3000')

    def 'create and retrieve user via API'() {
        given:
        def payload = JsonOutput.toJson([
            name: 'Test User',
            email: "test_${System.currentTimeMillis()}@example.com"
        ])

        when: 'create user'
        def conn = new URL("${baseApiUrl}/api/users").openConnection()
        conn.requestMethod = 'POST'
        conn.setRequestProperty('Content-Type', 'application/json')
        conn.doOutput = true
        conn.outputStream.write(payload.bytes)

        then:
        conn.responseCode == 201
        def created = jsonSlurper.parseText(conn.inputStream.text)
        created.id != null

        when: 'retrieve user'
        def getConn = new URL("${baseApiUrl}/api/users/${created.id}").openConnection()

        then:
        getConn.responseCode == 200
        def user = jsonSlurper.parseText(getConn.inputStream.text)
        user.name == 'Test User'
    }
}
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: Geb Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  geb-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Set up Chrome
        uses: browser-actions/setup-chrome@latest
        with:
          chrome-version: stable

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}

      - name: Run Geb tests
        run: ./gradlew test -Dgeb.env=chromeHeadless -Dgeb.baseUrl=http://localhost:3000
        env:
          DISPLAY: ':99'

      - name: Upload Geb reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: geb-reports
          path: build/geb-reports/

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/reports/tests/
```

### CLI Commands
```bash
# Run all tests
./gradlew test

# Run with specific environment
./gradlew test -Dgeb.env=chromeHeadless

# Run specific spec class
./gradlew test --tests "specs.LoginSpec"

# Run specific test method
./gradlew test --tests "specs.LoginSpec.successful login redirects to dashboard"

# Run with custom base URL
./gradlew test -Dgeb.baseUrl=https://staging.example.com

# Run with LambdaTest
./gradlew test -Dgeb.env=lambdatest
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `geb.error.RequiredPageContentNotPresent` | Content block element not found on page | Check CSS selector; add `required: false` for optional content; verify `at` check passes first |
| 2 | `at` check fails unexpectedly | Page not fully loaded when `at` runs | Enable `atCheckWaiting = true` in GebConfig; add explicit `waitFor` in `at` closure |
| 3 | `StaleElementReferenceException` | DOM changed after navigator was resolved | Re-query the element; use `waitFor` with fresh selector; avoid storing navigators in variables |
| 4 | `waiting` timeout exceeded | Default 10s too short for slow operations | Use waiting presets: `waitFor('slow') { ... }`; increase global timeout in GebConfig |
| 5 | `$()` returns empty navigator silently | Selector doesn't match; no error by default | Use `required: true` in content blocks; check selector in browser DevTools first |
| 6 | Tests pass alone, fail together | Shared browser state between specs | Use `GebReportingSpec` (not `GebSpec`); clear cookies in `cleanup()`; avoid `@Stepwise` unless needed |
| 7 | Module content not accessible | Module not properly attached to page content | Ensure module is declared with `{ module ModuleName }` in content block; check module base element |
| 8 | `ChromeDriver version mismatch` | Chrome browser updated, driver outdated | Use WebDriverManager: `WebDriverManager.chromedriver().setup()` in driver factory |
| 9 | Screenshots not generated on failure | Not using `GebReportingSpec` | Extend `GebReportingSpec` instead of `GebSpec`; verify `reportsDir` is set in GebConfig |
| 10 | JavaScript interaction fails | Element not in viewport or page not ready | Scroll element into view with `js.exec`; add `waitFor` before JS operations |
| 11 | Content closure evaluated too early | Eager evaluation instead of lazy | Content blocks are lazy by default; don't call `.text()` at declaration time |
| 12 | `geb.env` not applied | System property not passed through Gradle | Add `systemProperty 'geb.env', System.getProperty('geb.env', 'chrome')` in `build.gradle` test block |

---

## §9 — Best Practices Checklist

1. Use `at` checks on every page — validates correct page before interacting
2. Use `GebReportingSpec` for automatic screenshots on failure
3. Use modules for reusable UI components — navigation, alerts, tables
4. Configure `atCheckWaiting = true` to handle async page transitions
5. Define waiting presets (`slow`, `quick`) for different timeout needs
6. Use `required: false` for optional content that may not always be present
7. Prefer Geb's built-in `waitFor` over explicit `Thread.sleep()`
8. Keep page objects focused — one class per logical page/view
9. Use `@Unroll` with `where` blocks for data-driven testing
10. Configure multiple environments in GebConfig (local, headless, cloud)
11. Use `@Stepwise` sparingly — only for true sequential flows
12. Avoid storing navigator references in variables — re-query for freshness
13. Set `reportsDir` for organized failure artifacts in CI
14. Use content DSL features: `wait`, `cache`, `required` for resilient selectors
