# JUnit 5 — Advanced Patterns & Playbook

## Parameterized Tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

@ParameterizedTest(name = "{0} is valid email: {1}")
@CsvSource({"alice@test.com, true", "invalid, false", "@bad.com, false"})
void testEmailValidation(String email, boolean expected) {
    assertEquals(expected, validator.isValidEmail(email));
}

@ParameterizedTest
@MethodSource("userProvider")
void testUserCreation(String name, int age, String role) {
    User user = new User(name, age, role);
    assertAll(
        () -> assertEquals(name, user.getName()),
        () -> assertEquals(age, user.getAge()),
        () -> assertEquals(role, user.getRole())
    );
}

static Stream<Arguments> userProvider() {
    return Stream.of(
        Arguments.of("Alice", 30, "ADMIN"),
        Arguments.of("Bob", 25, "USER")
    );
}

// Custom argument provider
@ParameterizedTest
@ArgumentsSource(RandomUsersProvider.class)
void testWithRandomData(User user) { assertNotNull(user.getId()); }

static class RandomUsersProvider implements ArgumentsProvider {
    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext ctx) {
        return Stream.generate(() -> Arguments.of(User.random())).limit(10);
    }
}
```

## Extension Model

```java
// Retry extension
public class RetryExtension implements TestExecutionExceptionHandler {
    @Override
    public void handleTestExecutionException(ExtensionContext ctx, Throwable t) throws Throwable {
        int maxRetries = ctx.getTestMethod()
            .map(m -> m.getAnnotation(Retry.class))
            .map(Retry::value).orElse(0);
        for (int i = 0; i < maxRetries; i++) {
            try {
                ctx.getTestMethod().get().invoke(ctx.getTestInstance().get());
                return;
            } catch (Throwable retry) { /* continue */ }
        }
        throw t;
    }
}

// Database extension with transaction rollback
public class DatabaseExtension implements BeforeEachCallback, AfterEachCallback {
    @Override
    public void beforeEach(ExtensionContext ctx) {
        getStore(ctx).put("tx", DataSource.beginTransaction());
    }
    @Override
    public void afterEach(ExtensionContext ctx) {
        getStore(ctx).get("tx", Transaction.class).rollback();
    }
    private ExtensionContext.Store getStore(ExtensionContext ctx) {
        return ctx.getStore(ExtensionContext.Namespace.create(getClass(), ctx.getRequiredTestMethod()));
    }
}

// Usage
@ExtendWith({DatabaseExtension.class, RetryExtension.class})
class UserServiceTest { /* ... */ }
```

## Nested & Dynamic Tests

```java
@Nested
@DisplayName("When user is authenticated")
class AuthenticatedUser {
    @BeforeEach
    void login() { session = authService.login("admin", "pass"); }

    @Test
    void canAccessDashboard() { assertTrue(session.canAccess("/dashboard")); }

    @Nested
    @DisplayName("with admin role")
    class AdminRole {
        @Test
        void canDeleteUsers() { assertTrue(session.canDelete("/users/1")); }
    }
}

// Dynamic tests generated at runtime
@TestFactory
Stream<DynamicTest> dynamicTestsFromFiles() {
    return Files.list(Path.of("test-data/"))
        .filter(p -> p.toString().endsWith(".json"))
        .map(path -> DynamicTest.dynamicTest(
            "Test: " + path.getFileName(),
            () -> { TestCase tc = loadTestCase(path); assertEquals(tc.expected, process(tc.input)); }
        ));
}
```

## Mockito Integration

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock UserRepository userRepo;
    @Mock PaymentGateway gateway;
    @Spy NotificationService notifier;
    @InjectMocks OrderService orderService;
    @Captor ArgumentCaptor<Payment> paymentCaptor;

    @Test
    void processOrder() {
        when(userRepo.findById(1L)).thenReturn(Optional.of(new User(1L, "Alice")));
        when(gateway.charge(any())).thenReturn(PaymentResult.success("txn-123"));

        orderService.process(new Order(1L, BigDecimal.TEN));

        verify(gateway).charge(paymentCaptor.capture());
        assertEquals(BigDecimal.TEN, paymentCaptor.getValue().getAmount());
        verify(notifier).send(argThat(msg -> msg.contains("txn-123")));
    }

    @Test
    void handlesPaymentFailure() {
        when(userRepo.findById(anyLong())).thenReturn(Optional.of(new User()));
        when(gateway.charge(any())).thenReturn(PaymentResult.failure("declined"));

        assertThrows(PaymentException.class, () -> orderService.process(new Order(1L, BigDecimal.TEN)));
        verify(notifier, never()).send(anyString());
    }
}
```

## Configuration

```xml
<!-- pom.xml — production-grade -->
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.11.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <version>5.12.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
<build><plugins>
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
            <parallel>methods</parallel>
            <threadCount>4</threadCount>
            <includes><include>**/*Test.java</include></includes>
        </configuration>
    </plugin>
</plugins></build>
```

## Anti-Patterns

- ❌ `@Test void test1()` — use descriptive names: `shouldThrowWhenInputNull`
- ❌ Multiple assertions without `assertAll` — first failure hides subsequent issues
- ❌ `@BeforeAll` non-static in non-`@TestInstance(PER_CLASS)` — causes runtime error
- ❌ Mocking value objects — mock interfaces and services, not POJOs
- ❌ `assertEquals(true, result)` → use `assertTrue(result)`
