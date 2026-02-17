# JUnit 5 — Advanced Implementation Playbook

## §1 — Project Setup & Configuration

```xml
<!-- pom.xml -->
<dependencies>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.25.3</version>
    <scope>test</scope>
  </dependency>
</dependencies>
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-surefire-plugin</artifactId>
      <version>3.2.5</version>
    </plugin>
  </plugins>
</build>
```

```properties
# src/test/resources/junit-platform.properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=same_thread
junit.jupiter.execution.parallel.mode.classes.default=concurrent
junit.jupiter.execution.parallel.config.fixed.parallelism=4
junit.jupiter.testinstance.lifecycle.default=per_class
```

## §2 — Test Lifecycle & Structure

```java
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("User Service Tests")
class UserServiceTest {
    private UserService service;
    private UserRepository mockRepo;

    @BeforeAll
    static void initAll() {
        // Run once — DB connection, heavy resources
    }

    @BeforeEach
    void setUp() {
        mockRepo = Mockito.mock(UserRepository.class);
        service = new UserService(mockRepo);
    }

    @Test
    @DisplayName("Creates user with valid data")
    @Tag("smoke")
    void testCreateUser() {
        User user = new User("Alice", "alice@test.com");
        when(mockRepo.save(any(User.class))).thenReturn(user);
        User result = service.create("Alice", "alice@test.com");
        assertAll(
            () -> assertEquals("Alice", result.getName()),
            () -> assertEquals("alice@test.com", result.getEmail()),
            () -> verify(mockRepo).save(any(User.class))
        );
    }

    @AfterEach
    void tearDown() {
        Mockito.reset(mockRepo);
    }

    @AfterAll
    static void tearDownAll() {
        // Cleanup heavy resources
    }
}
```

## §3 — Parameterized Tests

```java
// CSV Source
@ParameterizedTest(name = "validate({0}) = {1}")
@CsvSource({
    "user@test.com, true",
    "invalid, false",
    "'', false",
    "user@.com, false",
})
void testEmailValidation(String email, boolean expected) {
    assertEquals(expected, EmailValidator.isValid(email));
}

// CSV File Source
@ParameterizedTest
@CsvFileSource(resources = "/testdata/login-scenarios.csv", numLinesToSkip = 1)
void testLoginScenarios(String email, String password, String expectedResult) {
    LoginResult result = authService.login(email, password);
    assertEquals(expectedResult, result.getStatus());
}

// Method Source — complex objects
@ParameterizedTest
@MethodSource("provideUsers")
void testUserCreation(String name, String email, boolean shouldSucceed) {
    if (shouldSucceed) {
        assertDoesNotThrow(() -> service.create(name, email));
    } else {
        assertThrows(ValidationException.class, () -> service.create(name, email));
    }
}

static Stream<Arguments> provideUsers() {
    return Stream.of(
        Arguments.of("Alice", "alice@test.com", true),
        Arguments.of("", "bob@test.com", false),
        Arguments.of("Charlie", "", false)
    );
}

// Enum Source
@ParameterizedTest
@EnumSource(value = UserRole.class, names = {"ADMIN", "EDITOR"})
void testWritePermissions(UserRole role) {
    assertTrue(PermissionService.canWrite(role));
}

// Value Source
@ParameterizedTest
@ValueSource(strings = {"admin", "editor", "viewer"})
void testRoleExists(String role) {
    assertNotNull(RoleService.findByName(role));
}
```

## §4 — Mockito Integration

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock private OrderRepository orderRepo;
    @Mock private PaymentGateway paymentGateway;
    @Mock private EmailService emailService;
    @InjectMocks private OrderService orderService;

    @Test
    void testPlaceOrder() {
        Order order = new Order("item-1", 29.99);
        when(paymentGateway.charge(anyDouble())).thenReturn(true);
        when(orderRepo.save(any(Order.class))).thenReturn(order);

        Order result = orderService.placeOrder(order);

        assertNotNull(result);
        verify(paymentGateway).charge(29.99);
        verify(orderRepo).save(order);
        verify(emailService).sendConfirmation(eq(order), anyString());
    }

    @Test
    void testPlaceOrder_paymentFails() {
        when(paymentGateway.charge(anyDouble())).thenReturn(false);
        assertThrows(PaymentException.class, () ->
            orderService.placeOrder(new Order("item-1", 29.99))
        );
        verify(orderRepo, never()).save(any());
    }

    // Argument captor
    @Captor private ArgumentCaptor<Order> orderCaptor;

    @Test
    void testOrderCapture() {
        when(paymentGateway.charge(anyDouble())).thenReturn(true);
        orderService.placeOrder(new Order("item-1", 29.99));
        verify(orderRepo).save(orderCaptor.capture());
        assertEquals("item-1", orderCaptor.getValue().getItemId());
    }

    // Verify call order
    @Test
    void testCallOrder() {
        when(paymentGateway.charge(anyDouble())).thenReturn(true);
        orderService.placeOrder(new Order("item-1", 29.99));
        InOrder inOrder = inOrder(paymentGateway, orderRepo, emailService);
        inOrder.verify(paymentGateway).charge(anyDouble());
        inOrder.verify(orderRepo).save(any());
        inOrder.verify(emailService).sendConfirmation(any(), anyString());
    }
}
```

## §5 — Nested & Dynamic Tests

```java
@DisplayName("Calculator")
class CalculatorTest {
    Calculator calc = new Calculator();

    @Nested
    @DisplayName("Addition")
    class AdditionTests {
        @Test void positiveNumbers() { assertEquals(5, calc.add(2, 3)); }
        @Test void negativeNumbers() { assertEquals(-5, calc.add(-2, -3)); }
        @Test void zero() { assertEquals(3, calc.add(3, 0)); }
    }

    @Nested
    @DisplayName("Division")
    class DivisionTests {
        @Test void normalDivision() { assertEquals(2, calc.divide(6, 3)); }
        @Test void divisionByZero() {
            assertThrows(ArithmeticException.class, () -> calc.divide(6, 0));
        }
    }

    // Dynamic tests generated at runtime
    @TestFactory
    Stream<DynamicTest> testSquareRoots() {
        return Stream.of(
            new int[]{4, 2}, new int[]{9, 3}, new int[]{16, 4}, new int[]{25, 5}
        ).map(pair -> DynamicTest.dynamicTest(
            "sqrt(" + pair[0] + ") = " + pair[1],
            () -> assertEquals(pair[1], (int) Math.sqrt(pair[0]))
        ));
    }
}
```

## §6 — AssertJ Fluent Assertions

```java
import static org.assertj.core.api.Assertions.*;

@Test
void testWithAssertJ() {
    User user = userService.findById(1);

    assertThat(user)
        .isNotNull()
        .extracting(User::getName, User::getEmail)
        .containsExactly("Alice", "alice@test.com");

    assertThat(user.getRoles())
        .hasSize(2)
        .contains("ADMIN")
        .doesNotContain("VIEWER");

    assertThat(user.getCreatedAt())
        .isAfter(LocalDate.of(2024, 1, 1))
        .isBefore(LocalDate.now());

    // Exception assertion
    assertThatThrownBy(() -> userService.findById(999))
        .isInstanceOf(NotFoundException.class)
        .hasMessageContaining("not found");

    // Collection assertions
    List<User> users = userService.findAll();
    assertThat(users)
        .hasSizeGreaterThan(0)
        .extracting(User::getName)
        .contains("Alice", "Bob")
        .doesNotContain("Unknown");
}
```

## §7 — Conditional Execution & Assumptions

```java
@Test
@EnabledOnOs(OS.LINUX)
void testLinuxOnly() { /* ... */ }

@Test
@DisabledIfEnvironmentVariable(named = "CI", matches = "true")
void testLocalOnly() { /* ... */ }

@Test
@EnabledIf("isDevEnvironment")
void testDevOnly() { /* ... */ }

static boolean isDevEnvironment() {
    return "dev".equals(System.getProperty("env"));
}

@Test
void testWithAssumption() {
    assumeTrue(System.getenv("API_KEY") != null, "API key required");
    // Test only runs if API key is set
}
```

## §8 — Custom Extensions

```java
// Timing extension — log test duration
public class TimingExtension implements BeforeTestExecutionCallback, AfterTestExecutionCallback {
    @Override
    public void beforeTestExecution(ExtensionContext ctx) {
        ctx.getStore(Namespace.GLOBAL).put("start", System.currentTimeMillis());
    }

    @Override
    public void afterTestExecution(ExtensionContext ctx) {
        long start = ctx.getStore(Namespace.GLOBAL).get("start", Long.class);
        long duration = System.currentTimeMillis() - start;
        System.out.printf("⏱ %s: %dms%n", ctx.getDisplayName(), duration);
    }
}
// Usage: @ExtendWith(TimingExtension.class)

// Retry extension — retry flaky tests
public class RetryExtension implements TestExecutionExceptionHandler {
    @Override
    public void handleTestExecutionException(ExtensionContext ctx, Throwable t) throws Throwable {
        int maxRetries = 2;
        int retries = ctx.getStore(Namespace.GLOBAL).getOrDefault("retry", Integer.class, 0);
        if (retries < maxRetries) {
            ctx.getStore(Namespace.GLOBAL).put("retry", retries + 1);
        } else {
            throw t;
        }
    }
}
```

## §9 — CI/CD Integration

```yaml
name: JUnit Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Cache Maven
        uses: actions/cache@v4
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
      - name: Run tests
        run: mvn test -Dparallel=true
      - name: Publish test results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: JUnit Results
          path: target/surefire-reports/TEST-*.xml
          reporter: java-junit
```

## §10 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Test not discovered | Wrong naming or missing `@Test` | Name `*Test.java`, add `@Test` annotation |
| `@BeforeAll` must be static | Instance lifecycle is `per_method` | Use `@TestInstance(Lifecycle.PER_CLASS)` or make static |
| Mock returns null | Missing `when().thenReturn()` | Add stubbing or use `@Mock` with `lenient()` |
| Parameterized fails | Wrong arg count or types | Ensure source matches parameter list |
| Parallel tests flaky | Shared mutable state | Use `@Isolated` or separate state per test |
| Extension not applied | Missing `@ExtendWith` | Add annotation or register in `META-INF/services` |
| assertAll shows one error | Expected — runs all, reports first | Use `assertAll` to see all failures at once |
| Slow test suite | No parallelism | Enable in `junit-platform.properties` |

## §11 — Best Practices Checklist

- ✅ Use `@DisplayName` for readable test names
- ✅ Use `assertAll()` to check multiple conditions together
- ✅ Use `@ParameterizedTest` over copy-pasting test methods
- ✅ Use `@ExtendWith(MockitoExtension.class)` for Mockito
- ✅ Use `@Nested` for logical grouping of related tests
- ✅ Use `@Tag` for categorizing tests (smoke, integration, etc.)
- ✅ Use AssertJ for fluent, readable assertions
- ✅ Use `ArgumentCaptor` for verifying complex arguments
- ✅ Use `@TestFactory` for dynamic test generation
- ✅ Enable parallel execution in CI for speed
- ✅ One logical assertion per test (use `assertAll` for compound checks)
- ✅ Structure: `src/test/java/` mirroring `src/main/java/`
