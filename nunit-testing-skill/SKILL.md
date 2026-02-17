---
name: nunit-testing-skill
description: >
  Generates NUnit 3 tests in C#. Covers Assert.That constraint model,
  parameterized tests, setup/teardown, and Moq mocking. Use when user mentions
  "NUnit", "[TestFixture]", "[Test]", "Assert.That", "C# unit test". Triggers on:
  "NUnit", "[Test]", "Assert.That", "C# test", "NUnit3".
languages:
  - C#
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# NUnit 3 Testing Skill

## Core Patterns

### Basic Test

```csharp
using NUnit.Framework;

[TestFixture]
public class CalculatorTests
{
    private Calculator _calculator;

    [SetUp]
    public void SetUp() => _calculator = new Calculator();

    [Test]
    public void Add_TwoPositiveNumbers_ReturnsSum()
    {
        Assert.That(_calculator.Add(2, 3), Is.EqualTo(5));
    }

    [Test]
    public void Divide_ByZero_ThrowsException()
    {
        Assert.Throws<DivideByZeroException>(() => _calculator.Divide(10, 0));
    }

    [TearDown]
    public void TearDown() { /* cleanup */ }
}
```

### Constraint Model (Assert.That)

```csharp
Assert.That(actual, Is.EqualTo(expected));
Assert.That(actual, Is.Not.EqualTo(unexpected));
Assert.That(value, Is.GreaterThan(5));
Assert.That(value, Is.InRange(1, 10));
Assert.That(str, Does.Contain("hello"));
Assert.That(str, Does.StartWith("He").IgnoreCase);
Assert.That(collection, Has.Count.EqualTo(3));
Assert.That(collection, Has.Member("item"));
Assert.That(collection, Is.All.GreaterThan(0));
Assert.That(obj, Is.Null);
Assert.That(obj, Is.Not.Null);
Assert.That(obj, Is.InstanceOf<MyClass>());
Assert.That(actual, Is.EqualTo(3.14).Within(0.01));
Assert.That(() => Method(), Throws.TypeOf<ArgumentException>()
    .With.Message.Contains("invalid"));
```

### Parameterized Tests

```csharp
[TestCase(2, 3, 5)]
[TestCase(-1, 1, 0)]
[TestCase(0, 0, 0)]
public void Add_ReturnsCorrectSum(int a, int b, int expected)
{
    Assert.That(_calculator.Add(a, b), Is.EqualTo(expected));
}

[TestCaseSource(nameof(DivisionCases))]
public void Divide_ReturnsCorrectQuotient(int a, int b, double expected)
{
    Assert.That(_calculator.Divide(a, b), Is.EqualTo(expected).Within(0.01));
}

private static IEnumerable<TestCaseData> DivisionCases()
{
    yield return new TestCaseData(10, 2, 5.0).SetName("10/2=5");
    yield return new TestCaseData(7, 3, 2.33).SetName("7/3=2.33");
}
```

### Mocking with Moq

```csharp
using Moq;

[TestFixture]
public class UserServiceTests
{
    private Mock<IUserRepository> _mockRepo;
    private Mock<IEmailService> _mockEmail;
    private UserService _service;

    [SetUp]
    public void SetUp()
    {
        _mockRepo = new Mock<IUserRepository>();
        _mockEmail = new Mock<IEmailService>();
        _service = new UserService(_mockRepo.Object, _mockEmail.Object);
    }

    [Test]
    public void CreateUser_SavesAndSendsEmail()
    {
        _mockRepo.Setup(r => r.Save(It.IsAny<User>())).Returns(new User { Id = 1 });

        var result = _service.CreateUser("alice@test.com", "Alice");

        Assert.That(result.Id, Is.EqualTo(1));
        _mockRepo.Verify(r => r.Save(It.IsAny<User>()), Times.Once);
        _mockEmail.Verify(e => e.SendWelcome("alice@test.com"), Times.Once);
    }
}
```

### Lifecycle

```
[OneTimeSetUp]    → Before all tests in fixture
[SetUp]           → Before each test
[Test]            → Test method
[TearDown]        → After each test
[OneTimeTearDown] → After all tests in fixture
```

### Categories and Attributes

```csharp
[Test, Category("Smoke")]
public void QuickTest() { }

[Test, Ignore("Bug #123")]
public void SkippedTest() { }

[Test, Timeout(5000)]
public void TimeLimitedTest() { }

[Test, Retry(3)]
public void FlakyTest() { }
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `Assert.AreEqual(a, b)` (classic) | `Assert.That(a, Is.EqualTo(b))` | Constraint model is richer |
| No `[SetUp]` | Proper lifecycle | Resource management |
| Testing private methods | Test public API | Encapsulation |
| No categories | `[Category("Smoke")]` | Run subsets |

## Setup: `dotnet add package NUnit NUnit3TestAdapter Microsoft.NET.Test.Sdk`
## Run: `dotnet test` or `dotnet test --filter TestCategory=Smoke`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
