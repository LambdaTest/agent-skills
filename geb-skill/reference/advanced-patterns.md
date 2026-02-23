# Geb — Advanced Patterns & Playbook

## Page Objects with Modules

```groovy
class LoginPage extends Page {
    static url = "/login"
    static at = { title == "Login" }

    static content = {
        emailField { $("#email") }
        passwordField { $("#password") }
        submitBtn { $("button", type: "submit") }
        errorMsg(required: false) { $(".error-message") }
    }

    void loginAs(String email, String password) {
        emailField.value(email)
        passwordField.value(password)
        submitBtn.click()
    }
}

class NavigationModule extends Module {
    static content = {
        links { $("nav a") }
        activeLink { $("nav a.active") }
    }
    void navigateTo(String label) { links.find { it.text() == label }.click() }
}

class DashboardPage extends Page {
    static at = { $("h1").text() == "Dashboard" }
    static content = {
        nav { module NavigationModule, $("nav") }
        cards { $(".card").moduleList(CardModule) }
    }
}
```

## Spock Integration

```groovy
class LoginSpec extends GebSpec {
    def "admin can login"() {
        when:
        to LoginPage
        loginAs("admin@test.com", "password")

        then:
        at DashboardPage
        nav.activeLink.text() == "Dashboard"
    }

    @Unroll
    def "login fails for #scenario"() {
        when:
        to LoginPage
        loginAs(email, password)

        then:
        errorMsg.displayed
        errorMsg.text() == expectedError

        where:
        scenario        | email            | password | expectedError
        "wrong password"| "admin@test.com" | "wrong"  | "Invalid credentials"
        "empty email"   | ""               | "pass"   | "Email required"
    }
}
```

## Configuration

```groovy
// GebConfig.groovy
import org.openqa.selenium.chrome.ChromeOptions

environments {
    chrome {
        driver = { new ChromeDriver(new ChromeOptions().addArguments("--headless")) }
    }
    firefox {
        driver = { new FirefoxDriver() }
    }
}

waiting { timeout = 10; retryInterval = 0.5 }
atCheckWaiting = true
baseUrl = System.getenv("APP_URL") ?: "http://localhost:3000"
reportsDir = "build/geb-reports"
```

## Anti-Patterns

- ❌ `Thread.sleep()` — use Geb's `waitFor {}` or content `wait: true`
- ❌ Direct `$()` in test body — use page object content definitions
- ❌ Missing `at` checker — page verification becomes implicit
- ❌ Hardcoded URLs — use `static url` and `to PageClass` navigation
