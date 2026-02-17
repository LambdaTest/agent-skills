---
name: unittest-testing-skill
description: >
  Generates Python unittest tests. Built-in testing framework with TestCase,
  setUp/tearDown, and assertion methods. Use when user mentions "unittest",
  "TestCase", "self.assertEqual", "Python unittest". Triggers on: "unittest",
  "TestCase", "self.assertEqual", "Python unittest" (not pytest).
languages:
  - Python
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Python unittest Skill

## Core Patterns

### Basic Test

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(10, 0)

    def test_multiple_assertions(self):
        self.assertEqual(self.calc.add(2, 2), 4)
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertAlmostEqual(self.calc.divide(10, 3), 3.333, places=3)

    def tearDown(self):
        pass  # cleanup

if __name__ == '__main__':
    unittest.main()
```

### Assertions

```python
self.assertEqual(a, b)
self.assertNotEqual(a, b)
self.assertTrue(condition)
self.assertFalse(condition)
self.assertIsNone(obj)
self.assertIsNotNone(obj)
self.assertIs(a, b)              # same object
self.assertIn(item, collection)
self.assertNotIn(item, collection)
self.assertIsInstance(obj, cls)
self.assertAlmostEqual(a, b, places=5)
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertRegex(str, r'\d+')
self.assertCountEqual(a, b)     # same elements, any order

# Exception
with self.assertRaises(ValueError) as ctx:
    raise ValueError("bad")
self.assertIn("bad", str(ctx.exception))

# Warning
with self.assertWarns(DeprecationWarning):
    deprecated_function()
```

### SubTest (Parameterized)

```python
def test_add_multiple(self):
    test_cases = [(2, 3, 5), (-1, 1, 0), (0, 0, 0)]
    for a, b, expected in test_cases:
        with self.subTest(a=a, b=b):
            self.assertEqual(self.calc.add(a, b), expected)
```

### Mocking

```python
from unittest.mock import patch, MagicMock, Mock

class TestUserService(unittest.TestCase):
    @patch('myapp.service.UserRepository')
    @patch('myapp.service.EmailService')
    def test_create_user(self, MockEmail, MockRepo):
        mock_repo = MockRepo.return_value
        mock_repo.save.return_value = User(1, 'Alice')

        service = UserService()
        result = service.create_user('alice@test.com', 'Alice')

        self.assertEqual(result.id, 1)
        mock_repo.save.assert_called_once()
        MockEmail.return_value.send_welcome.assert_called_with('alice@test.com')
```

### Lifecycle

```
setUpClass()    → Once before all tests (classmethod)
setUp()         → Before each test
test_method()   → Test
tearDown()      → After each test
tearDownClass() → Once after all tests (classmethod)
```

## Run: `python -m unittest` or `python -m unittest test_module.TestClass.test_method`
## Discover: `python -m unittest discover -s tests -p "test_*.py"`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
