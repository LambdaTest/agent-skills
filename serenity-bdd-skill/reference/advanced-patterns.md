# Serenity BDD — Advanced Patterns & Playbook

## Screenplay Pattern

```java
import net.serenitybdd.screenplay.*;
import net.serenitybdd.screenplay.actions.*;
import net.serenitybdd.screenplay.questions.*;

public class Login implements Task {
    private final String username, password;
    public Login(String username, String password) {
        this.username = username; this.password = password;
    }

    @Override
    @Step("{0} logs in as #username")
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
            Navigate.to("/login"),
            Enter.theValue(username).into("#username"),
            Enter.theValue(password).into("#password"),
            Click.on("#submit")
        );
    }

    public static Login withCredentials(String user, String pass) {
        return new Login(user, pass);
    }
}

// Question
public class CurrentUser implements Question<String> {
    @Override
    public String answeredBy(Actor actor) {
        return Text.of("#user-display").answeredBy(actor);
    }
    public static Question<String> name() { return new CurrentUser(); }
}

// Test
@Test
void adminCanLogin() {
    Actor admin = Actor.named("Admin");
    admin.attemptsTo(Login.withCredentials("admin", "pass"));
    admin.should(seeThat(CurrentUser.name(), equalTo("Admin")));
}
```

## REST API Testing

```java
@Steps SerenityRest restSteps;

@Test
void createUser() {
    given().contentType(JSON).body(new User("Alice", "alice@test.com"))
        .when().post("/api/users")
        .then().statusCode(201)
        .body("name", equalTo("Alice"));

    // Chained API verification
    String id = lastResponse().jsonPath().getString("id");
    given().when().get("/api/users/" + id)
        .then().statusCode(200)
        .body("name", equalTo("Alice"));
}
```

## Living Documentation

```java
// Feature narrative in Cucumber
@Narrative(text = {"As a customer", "I want to manage my cart",
    "So that I can purchase items"})
@WithTags({@WithTag("cart"), @WithTag("smoke")})
public class CartTest extends SerenityStory {
    @Test @Title("Add item to cart and verify total")
    void addToCart() { /* ... */ }
}
```

## Anti-Patterns

- ❌ Direct WebDriver calls — use Screenplay Tasks and Actions
- ❌ Assertions in Task classes — use Questions for verification
- ❌ Skipping `@Step` annotations — breaks living documentation reports
- ❌ Fat step definitions — delegate to reusable Task objects
