# NUnit — Advanced Patterns & Playbook

## Parameterized Tests

```csharp
[TestFixture]
public class ValidatorTests
{
    [TestCase("alice@test.com", true)]
    [TestCase("invalid", false)]
    [TestCase("", false)]
    public void EmailValidation(string email, bool expected)
    {
        Assert.That(Validator.IsValidEmail(email), Is.EqualTo(expected));
    }

    [TestCaseSource(nameof(DivisionCases))]
    public void Divide(int a, int b, int expected)
    {
        Assert.That(Calculator.Divide(a, b), Is.EqualTo(expected));
    }

    static object[] DivisionCases = {
        new object[] { 10, 2, 5 },
        new object[] { 100, 4, 25 },
        new object[] { 0, 5, 0 }
    };

    // Combinatorial
    [Test, Combinatorial]
    public void CrossBrowser(
        [Values("Chrome", "Firefox")] string browser,
        [Values("Windows", "macOS")] string os)
    {
        var driver = CreateDriver(browser, os);
        Assert.That(driver, Is.Not.Null);
    }
}
```

## Custom Constraints

```csharp
public class BeValidJsonConstraint : Constraint
{
    public override ConstraintResult ApplyTo<TActual>(TActual actual)
    {
        try { JsonDocument.Parse(actual as string); return new ConstraintResult(this, actual, true); }
        catch { return new ConstraintResult(this, actual, false); }
    }
    public override string Description => "valid JSON string";
}

public static class Is2 { public static BeValidJsonConstraint ValidJson() => new(); }

[Test]
public void ApiReturnsJson()
{
    var response = client.Get("/api/users");
    Assert.That(response.Content, Is2.ValidJson());
}
```

## Async Testing with Moq

```csharp
[TestFixture]
public class UserServiceTests
{
    private Mock<IUserRepository> _mockRepo;
    private Mock<IEmailService> _mockEmail;
    private UserService _service;

    [SetUp]
    public void Setup()
    {
        _mockRepo = new Mock<IUserRepository>();
        _mockEmail = new Mock<IEmailService>();
        _service = new UserService(_mockRepo.Object, _mockEmail.Object);
    }

    [Test]
    public async Task CreateUser_SendsWelcomeEmail()
    {
        _mockRepo.Setup(r => r.AddAsync(It.IsAny<User>()))
            .ReturnsAsync(new User { Id = 1, Name = "Alice" });
        _mockEmail.Setup(e => e.SendAsync(It.IsAny<string>(), It.IsAny<string>()))
            .Returns(Task.CompletedTask);

        var user = await _service.CreateAsync("Alice", "alice@test.com");

        Assert.That(user.Id, Is.EqualTo(1));
        _mockEmail.Verify(e => e.SendAsync("alice@test.com",
            It.Is<string>(s => s.Contains("Welcome"))), Times.Once);
    }

    [Test]
    public void CreateUser_ThrowsOnDuplicate()
    {
        _mockRepo.Setup(r => r.AddAsync(It.IsAny<User>()))
            .ThrowsAsync(new DuplicateException());

        Assert.ThrowsAsync<DuplicateException>(
            () => _service.CreateAsync("Alice", "dup@test.com"));
    }
}
```

## Lifecycle & Parallelism

```csharp
[TestFixture, Parallelizable(ParallelScope.Children)]
[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]
public class ParallelTests
{
    [OneTimeSetUp] public void FixtureSetup() { /* once per fixture */ }
    [OneTimeTearDown] public void FixtureTeardown() { /* once per fixture */ }
    [SetUp] public void TestSetup() { /* before each test */ }
    [TearDown] public void TestTeardown() { /* after each test */ }
}
```

## Anti-Patterns

- ❌ `Assert.AreEqual(expected, actual)` — use constraint model: `Assert.That(actual, Is.EqualTo(expected))`
- ❌ `Thread.Sleep` in async tests — use `await` with proper timeouts
- ❌ `[Ignore]` without reason — `[Ignore("JIRA-1234: pending fix")]`
- ❌ Setup methods doing too much — extract to builder/factory patterns
