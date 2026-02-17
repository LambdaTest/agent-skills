# Python unittest — Advanced Playbook

## §1 — Project Setup

### Project Structure
```
project/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── email_service.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_user_service.py
│   │   ├── test_email_service.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── fixtures/
│       ├── users.json
│       └── responses/
│           └── api_response.json
└── .coveragerc
```

### pyproject.toml
```toml
[project]
name = "myapp"
version = "1.0.0"
requires-python = ">=3.10"

[project.optional-dependencies]
test = [
    "coverage>=7.4",
    "responses>=0.25",
    "freezegun>=1.4",
    "parameterized>=0.9",
]

[tool.coverage.run]
source = ["src/myapp"]
omit = ["tests/*", "*/migrations/*"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
]
```

### .coveragerc
```ini
[run]
source = src/myapp
branch = true

[report]
fail_under = 80
show_missing = true
```

---

## §2 — Core Test Patterns

### Basic Test Structure
```python
import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from myapp.services.user_service import UserService
from myapp.models.user import User


class TestUserService(unittest.TestCase):
    """Test suite for UserService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repo = Mock()
        self.mock_email = Mock()
        self.service = UserService(repo=self.mock_repo, email_service=self.mock_email)

    def tearDown(self):
        """Clean up after tests."""
        self.mock_repo.reset_mock()
        self.mock_email.reset_mock()

    # --- Creation Tests ---

    def test_create_user_returns_user_with_id(self):
        self.mock_repo.save.return_value = User(id=1, name="Alice", email="alice@test.com")

        user = self.service.create("Alice", "alice@test.com")

        self.assertIsNotNone(user.id)
        self.assertEqual("Alice", user.name)
        self.assertEqual("alice@test.com", user.email)
        self.mock_repo.save.assert_called_once()

    def test_create_user_sends_welcome_email(self):
        self.mock_repo.save.return_value = User(id=1, name="Alice", email="alice@test.com")

        self.service.create("Alice", "alice@test.com")

        self.mock_email.send_welcome.assert_called_once_with("alice@test.com", "Alice")

    def test_create_user_with_invalid_email_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.create("Alice", "bad-email")
        self.assertIn("invalid email", str(ctx.exception).lower())

    def test_create_user_with_duplicate_email_raises(self):
        self.mock_repo.find_by_email.return_value = User(id=1, name="Existing", email="alice@test.com")

        with self.assertRaises(ValueError) as ctx:
            self.service.create("Alice", "alice@test.com")
        self.assertIn("already exists", str(ctx.exception).lower())

    # --- Retrieval Tests ---

    def test_find_returns_user_when_exists(self):
        expected = User(id=1, name="Alice", email="alice@test.com")
        self.mock_repo.find.return_value = expected

        result = self.service.find(1)

        self.assertEqual(expected, result)
        self.mock_repo.find.assert_called_once_with(1)

    def test_find_returns_none_for_missing_user(self):
        self.mock_repo.find.return_value = None
        self.assertIsNone(self.service.find(999))

    # --- Collection Assertions ---

    def test_list_returns_all_users(self):
        users = [User(id=i, name=f"User{i}", email=f"u{i}@test.com") for i in range(3)]
        self.mock_repo.find_all.return_value = users

        result = self.service.list()

        self.assertEqual(3, len(result))
        self.assertIsInstance(result, list)

    def test_search_filters_by_name(self):
        users = [
            User(id=1, name="Alice Smith", email="alice@test.com"),
            User(id=2, name="Bob Jones", email="bob@test.com"),
        ]
        self.mock_repo.find_all.return_value = users

        result = self.service.search("Alice")

        self.assertTrue(all("Alice" in u.name for u in result))

    # --- Numeric Assertions ---

    def test_balance_calculation(self):
        self.assertAlmostEqual(10.05, self.service.calculate_balance(10.0, 0.05), places=2)

    def test_discount_within_range(self):
        discount = self.service.calculate_discount(100.0, "VIP")
        self.assertGreaterEqual(discount, 0)
        self.assertLessEqual(discount, 100)
```

---

## §3 — Mocking & Patching

### Patch Decorator & Context Manager
```python
class TestExternalIntegration(unittest.TestCase):

    @patch("myapp.services.user_service.requests.get")
    def test_fetch_external_user(self, mock_get):
        """Patch at the location where it's used, not where it's defined."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"name": "Alice", "id": 42}

        result = self.service.fetch_external(42)

        self.assertEqual("Alice", result["name"])
        mock_get.assert_called_once_with("https://api.example.com/users/42", timeout=10)

    @patch("myapp.services.user_service.requests.get")
    def test_fetch_external_handles_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout("Connection timed out")

        with self.assertRaises(ServiceUnavailableError):
            self.service.fetch_external(42)

    @patch("myapp.services.user_service.requests.get")
    def test_fetch_external_retries_on_failure(self, mock_get):
        mock_get.side_effect = [
            requests.ConnectionError("failed"),
            requests.ConnectionError("failed"),
            Mock(status_code=200, json=Mock(return_value={"name": "Alice"})),
        ]

        result = self.service.fetch_external(42)

        self.assertEqual("Alice", result["name"])
        self.assertEqual(3, mock_get.call_count)

    def test_context_manager_patching(self):
        with patch("myapp.services.email_service.smtplib.SMTP") as mock_smtp:
            instance = mock_smtp.return_value.__enter__.return_value
            instance.sendmail.return_value = {}

            service = EmailService()
            service.send("to@test.com", "Subject", "Body")

            instance.sendmail.assert_called_once()

    @patch.multiple(
        "myapp.services.user_service",
        requests=Mock(),
        cache=Mock(),
        logger=Mock(),
    )
    def test_multiple_patches(self, **mocks):
        # All three are patched simultaneously
        pass
```

### Mock Advanced Patterns
```python
class TestMockPatterns(unittest.TestCase):

    def test_mock_property(self):
        user = Mock()
        type(user).is_admin = PropertyMock(return_value=True)
        self.assertTrue(user.is_admin)

    def test_mock_spec(self):
        """spec=True restricts mock to real class interface."""
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find(1)  # OK - method exists
        with self.assertRaises(AttributeError):
            mock_repo.nonexistent_method()  # Fails - not in spec

    def test_mock_side_effect_function(self):
        def dynamic_response(user_id):
            if user_id == 1:
                return User(id=1, name="Alice")
            return None

        self.mock_repo.find.side_effect = dynamic_response
        self.assertIsNotNone(self.service.find(1))
        self.assertIsNone(self.service.find(999))

    def test_call_args_inspection(self):
        self.mock_repo.save(User(name="Alice", email="a@t.com"))
        self.mock_repo.save(User(name="Bob", email="b@t.com"))

        # Inspect all calls
        self.assertEqual(2, self.mock_repo.save.call_count)
        first_call_args = self.mock_repo.save.call_args_list[0]
        self.assertEqual("Alice", first_call_args[0][0].name)

    def test_any_matcher(self):
        from unittest.mock import ANY

        self.service.create("Alice", "alice@test.com")
        self.mock_repo.save.assert_called_once_with(ANY)

    def test_mock_async(self):
        """For async code testing."""
        mock_client = Mock()
        mock_client.fetch = Mock(return_value=asyncio.coroutine(lambda: {"data": "value"})())
        # Or use AsyncMock in Python 3.8+
        mock_client.fetch = AsyncMock(return_value={"data": "value"})
```

---

## §4 — SubTest & Parameterized

### subTest for Data-Driven
```python
class TestValidation(unittest.TestCase):

    def test_email_validation_multiple_cases(self):
        cases = [
            ("user@example.com", True, "standard email"),
            ("first.last@example.com", True, "dotted local"),
            ("user+tag@example.com", True, "plus tag"),
            ("user@sub.example.com", True, "subdomain"),
            ("userexample.com", False, "missing @"),
            ("user@", False, "missing domain"),
            ("@example.com", False, "missing local"),
            ("", False, "empty string"),
            ("  ", False, "whitespace only"),
        ]
        for email, expected, label in cases:
            with self.subTest(email=email, label=label):
                self.assertEqual(expected, is_valid_email(email))

    def test_password_strength(self):
        cases = {
            "too short": ("abc", False),
            "no uppercase": ("password123!", False),
            "no number": ("Password!!!", False),
            "valid strong": ("P@ssw0rd!Long", True),
            "just minimum length": ("P@ssw0rd", True),
        }
        for label, (password, expected) in cases.items():
            with self.subTest(label=label, password=password):
                self.assertEqual(expected, is_strong_password(password))

    def test_status_code_mapping(self):
        mappings = [
            (200, "ok"),
            (201, "created"),
            (400, "bad_request"),
            (404, "not_found"),
            (500, "server_error"),
        ]
        for code, expected_status in mappings:
            with self.subTest(code=code):
                self.assertEqual(expected_status, map_status_code(code))
```

### Using parameterized Library
```python
from parameterized import parameterized, parameterized_class


class TestCalculator(unittest.TestCase):

    @parameterized.expand([
        ("add_positive", 2, 3, 5),
        ("add_negative", -1, -1, -2),
        ("add_zero", 0, 0, 0),
        ("add_mixed", -1, 1, 0),
    ])
    def test_add(self, name, a, b, expected):
        self.assertEqual(expected, Calculator.add(a, b))

    @parameterized.expand([
        ("divide_normal", 10, 2, 5.0),
        ("divide_fraction", 1, 3, 0.333),
    ])
    def test_divide(self, name, a, b, expected):
        self.assertAlmostEqual(expected, Calculator.divide(a, b), places=3)

    @parameterized.expand([
        ("divide_by_zero",),
    ])
    def test_divide_by_zero(self, name):
        with self.assertRaises(ZeroDivisionError):
            Calculator.divide(1, 0)


# Parameterized test class
@parameterized_class([
    {"browser": "chrome", "headless": True},
    {"browser": "firefox", "headless": True},
    {"browser": "edge", "headless": False},
])
class TestCrossBrowser(unittest.TestCase):
    browser: str
    headless: bool

    def test_homepage_loads(self):
        driver = create_driver(self.browser, self.headless)
        try:
            driver.get("http://localhost:3000")
            self.assertIn("Welcome", driver.title)
        finally:
            driver.quit()
```

---

## §5 — Time & Environment Mocking

### FreezeGun for Time
```python
from freezegun import freeze_time
from datetime import datetime, timedelta


class TestTimeDependent(unittest.TestCase):

    @freeze_time("2025-01-15 10:00:00")
    def test_trial_not_expired(self):
        user = User(trial_start=datetime(2025, 1, 1))
        self.assertFalse(user.is_trial_expired())

    @freeze_time("2025-02-15 10:00:00")
    def test_trial_expired_after_30_days(self):
        user = User(trial_start=datetime(2025, 1, 1))
        self.assertTrue(user.is_trial_expired())

    def test_time_travel(self):
        with freeze_time("2025-01-01") as frozen:
            user = User(trial_start=datetime.now())
            self.assertFalse(user.is_trial_expired())

            frozen.tick(timedelta(days=31))
            self.assertTrue(user.is_trial_expired())

    @freeze_time("2025-03-15 09:00:00")
    def test_business_hours_check(self):
        self.assertTrue(is_business_hours())  # Saturday 9am

    @freeze_time("2025-03-15 22:00:00")
    def test_after_hours(self):
        self.assertFalse(is_business_hours())
```

### Environment Variables
```python
class TestConfiguration(unittest.TestCase):

    @patch.dict("os.environ", {"DATABASE_URL": "sqlite:///test.db", "DEBUG": "true"})
    def test_uses_test_database(self):
        config = AppConfig.load()
        self.assertEqual("sqlite:///test.db", config.database_url)
        self.assertTrue(config.debug)

    @patch.dict("os.environ", {}, clear=True)
    def test_defaults_when_env_missing(self):
        config = AppConfig.load()
        self.assertEqual("sqlite:///default.db", config.database_url)
        self.assertFalse(config.debug)

    @patch.dict("os.environ", {"API_KEY": ""})
    def test_empty_api_key_raises(self):
        with self.assertRaises(ConfigurationError):
            AppConfig.load()
```

---

## §6 — Custom TestCase & Mixins

### Custom Base TestCase
```python
import json
import os


class BaseTestCase(unittest.TestCase):
    """Base test case with shared utilities."""

    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

    def load_fixture(self, filename):
        path = os.path.join(self.FIXTURES_DIR, filename)
        with open(path) as f:
            if filename.endswith(".json"):
                return json.load(f)
            return f.read()

    def assertValidEmail(self, email):
        import re
        pattern = r'^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$'
        self.assertRegex(email, pattern, f"'{email}' is not a valid email")

    def assertDictSubset(self, subset, full_dict):
        """Assert that subset is contained within full_dict."""
        for key, value in subset.items():
            self.assertIn(key, full_dict, f"Key '{key}' not found")
            self.assertEqual(value, full_dict[key],
                f"Value mismatch for key '{key}': {value} != {full_dict[key]}")

    def assertEventually(self, condition_fn, timeout=5, interval=0.5, msg=None):
        """Poll until condition is true or timeout."""
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            if condition_fn():
                return
            time.sleep(interval)
        self.fail(msg or f"Condition not met within {timeout}s")

    def assertResponseOk(self, response):
        self.assertIn(response.status_code, range(200, 300),
            f"Expected 2xx, got {response.status_code}: {response.text[:200]}")
```

### Mixin for API Testing
```python
class APITestMixin:
    """Mixin for API test utilities."""

    BASE_URL = "http://localhost:3000/api"

    def api_get(self, path, **kwargs):
        import requests
        return requests.get(f"{self.BASE_URL}{path}", **kwargs)

    def api_post(self, path, data=None, **kwargs):
        import requests
        return requests.post(f"{self.BASE_URL}{path}", json=data, **kwargs)

    def assertJsonResponse(self, response, expected_keys):
        self.assertEqual("application/json", response.headers.get("Content-Type"))
        data = response.json()
        for key in expected_keys:
            self.assertIn(key, data, f"Missing key '{key}' in response")


class TestUserAPI(BaseTestCase, APITestMixin):

    def test_create_user_endpoint(self):
        response = self.api_post("/users", {"name": "Alice", "email": "alice@test.com"})
        self.assertResponseOk(response)
        self.assertJsonResponse(response, ["id", "name", "email"])
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: Python unittest Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install -e ".[test]"

      - name: Run tests with coverage
        run: |
          python -m coverage run -m unittest discover -s tests -p "test_*.py" -v
          python -m coverage report --fail-under=80
          python -m coverage xml -o coverage.xml

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}
          path: coverage.xml
```

### Running Tests
```bash
# Discover and run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run specific test module
python -m unittest tests.unit.test_user_service -v

# Run specific test class
python -m unittest tests.unit.test_user_service.TestUserService -v

# Run specific test method
python -m unittest tests.unit.test_user_service.TestUserService.test_create_user_returns_user_with_id

# With coverage
coverage run -m unittest discover -s tests -v
coverage report --show-missing
coverage html  # Generates htmlcov/index.html
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Test method not discovered | Name doesn't start with `test_` | Rename to `test_xxx`; unittest only runs `test_*` methods |
| 2 | `patch` doesn't work | Patching at definition site, not import site | Patch where it's used: `@patch("myapp.services.requests.get")` |
| 3 | `Mock` returns Mock for everything | No `spec` set; any attribute access succeeds | Use `Mock(spec=RealClass)` to restrict interface |
| 4 | `setUp` changes not visible | Using class-level `setUpClass` but need per-test | Use instance-level `setUp` for per-test isolation |
| 5 | `subTest` failures unclear | Missing label in subTest | Add `with self.subTest(label=label, input=x):` |
| 6 | `assertRaises` doesn't catch | Exception type mismatch or not raised | Verify exact exception class; ensure code path triggers |
| 7 | Coverage report shows 0% | Source path not configured | Set `source = ["src/myapp"]` in .coveragerc or pyproject.toml |
| 8 | `patch.dict` doesn't restore | Used outside context manager | Use `with patch.dict(...)` or `@patch.dict` decorator |
| 9 | Async test not awaited | Using `async def test_` without runner | Use `unittest.IsolatedAsyncioTestCase` for async tests |
| 10 | `freeze_time` not affecting code | Code uses `time.time()` not `datetime.now()` | freezegun patches both; verify import path in target code |
| 11 | Import error in test discovery | Circular import or missing `__init__.py` | Add `__init__.py` to all test directories; fix circular deps |
| 12 | `MagicMock` vs `Mock` confusion | `MagicMock` supports magic methods, `Mock` doesn't | Use `MagicMock` when code uses `len()`, `iter()`, `bool()` etc. |

---

## §9 — Best Practices Checklist

1. **`setUp`/`tearDown` for isolation** — each test gets fresh state; never rely on test order
2. **Patch where imported, not defined** — `@patch("myapp.module.dependency")` not `@patch("dep_lib.func")`
3. **`Mock(spec=Class)` always** — catches interface mismatches at test time
4. **`subTest` for parameterized** — each case runs independently with clear failure messages
5. **Custom assertions for domains** — `assertValidEmail()`, `assertResponseOk()` improve readability
6. **`assertRaises` as context manager** — access exception via `ctx.exception` for message checks
7. **Fixture files over inline data** — `tests/fixtures/` for JSON/YAML test data
8. **Coverage gating in CI** — `--fail-under=80` prevents coverage regression
9. **`freezegun` for time-dependent** — deterministic time testing without sleep
10. **`patch.dict` for env vars** — isolated environment variable testing
11. **Base TestCase for reuse** — shared helpers, fixtures, custom assertions in base class
12. **Separate unit/integration dirs** — run unit tests fast; integration tests with services
13. **`AsyncMock` for async code** — Python 3.8+ `unittest.mock.AsyncMock` for coroutines
14. **Consider pytest migration** — for new projects, pytest offers fixtures, markers, and plugins
