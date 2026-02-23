---
name: mstest-skill
description: >
  Generates MSTest tests in C#. Microsoft's built-in testing framework for .NET.
  Use when user mentions "MSTest", "[TestMethod]", "[TestClass]",
  "Assert.AreEqual". Triggers on: "MSTest", "[TestMethod]", "[TestClass]",
  "Microsoft test framework".
languages:
  - C#
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# MSTest Testing Skill

## Core Patterns

### Basic Test

```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;

[TestClass]
public class CalculatorTests
{
    private Calculator _calc;

    [TestInitialize]
    public void SetUp() => _calc = new Calculator();

    [TestMethod]
    public void Add_TwoNumbers_ReturnsSum()
    {
        Assert.AreEqual(5, _calc.Add(2, 3));
    }

    [TestMethod]
    [ExpectedException(typeof(DivideByZeroException))]
    public void Divide_ByZero_Throws()
    {
        _calc.Divide(10, 0);
    }
}
```

### Data-Driven Tests

```csharp
[DataTestMethod]
[DataRow(2, 3, 5)]
[DataRow(-1, 1, 0)]
[DataRow(0, 0, 0)]
public void Add_Parameterized(int a, int b, int expected)
{
    Assert.AreEqual(expected, _calc.Add(a, b));
}

[DataTestMethod]
[DynamicData(nameof(GetTestData), DynamicDataSourceType.Method)]
public void Add_DynamicData(int a, int b, int expected)
{
    Assert.AreEqual(expected, _calc.Add(a, b));
}

private static IEnumerable<object[]> GetTestData()
{
    yield return new object[] { 1, 2, 3 };
    yield return new object[] { 10, -5, 5 };
}
```

### Assertions

```csharp
Assert.AreEqual(expected, actual);
Assert.AreNotEqual(unexpected, actual);
Assert.IsTrue(condition);
Assert.IsFalse(condition);
Assert.IsNull(obj);
Assert.IsNotNull(obj);
Assert.IsInstanceOfType(obj, typeof(MyClass));
Assert.ThrowsException<ArgumentException>(() => Method());
CollectionAssert.Contains(list, item);
CollectionAssert.AreEquivalent(expected, actual);
StringAssert.Contains(str, "substring");
StringAssert.StartsWith(str, "prefix");
StringAssert.Matches(str, new Regex(@"\d+"));
```

### Lifecycle

```
[AssemblyInitialize]  → Once per assembly (static)
[ClassInitialize]     → Once per class (static)
[TestInitialize]      → Before each test
[TestMethod]          → Test
[TestCleanup]         → After each test
[ClassCleanup]        → Once after class (static)
[AssemblyCleanup]     → Once after assembly (static)
```

### Categories

```csharp
[TestMethod, TestCategory("Smoke")]
public void QuickTest() { }

[TestMethod, Ignore("Bug #456")]
public void SkippedTest() { }

[TestMethod, Timeout(5000)]
public void TimedTest() { }
```

## Setup: `dotnet add package MSTest.TestFramework MSTest.TestAdapter Microsoft.NET.Test.Sdk`
## Run: `dotnet test` or `dotnet test --filter "TestCategory=Smoke"`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | .csproj deps, .runsettings with parallel + coverage config |
| §2 Test Patterns | TestMethod, DataTestMethod, DynamicData, exception testing |
| §3 FluentAssertions | AssertionScope, async exceptions, collection assertions |
| §4 Class & Assembly Initialize | Testcontainers, shared expensive setup, global config |
| §5 WebApplicationFactory | API integration tests with in-memory DB |
| §6 Bogus Test Data | Faker patterns for realistic data generation |
| §7 TestContext & Logging | Diagnostic output, categories, timeouts |
| §8 CI/CD Integration | GitHub Actions with coverage reporting and thresholds |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item production checklist |
