# Python unittest — Advanced Patterns & Playbook

## Test Organization with Suites

```python
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock, call

class TestUserService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Once per class — DB connection, expensive resources."""
        cls.db = DatabaseConnection('test')
        cls.db.migrate()

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all()
        cls.db.close()

    def setUp(self):
        """Before each test — fresh state."""
        self.service = UserService(self.db)
        self.db.begin_transaction()

    def tearDown(self):
        self.db.rollback()

    def test_create_user(self):
        user = self.service.create("Alice", "alice@test.com")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, "Alice")
        self.assertRegex(user.email, r'^[\w.]+@[\w.]+$')

    def test_duplicate_email_raises(self):
        self.service.create("Alice", "alice@test.com")
        with self.assertRaises(ValueError) as ctx:
            self.service.create("Bob", "alice@test.com")
        self.assertIn("already exists", str(ctx.exception))
```

## Advanced Mocking

```python
class TestAPIClient(unittest.TestCase):
    @patch('myapp.client.requests.Session')
    def test_retries_on_failure(self, MockSession):
        session = MockSession.return_value
        session.get.side_effect = [
            ConnectionError("timeout"),
            ConnectionError("timeout"),
            MagicMock(status_code=200, json=lambda: {"ok": True})
        ]
        client = APIClient(retries=3)
        result = client.fetch("/data")
        self.assertEqual(session.get.call_count, 3)
        self.assertTrue(result["ok"])

    @patch.multiple('myapp.config', API_URL='http://test', API_KEY='fake-key')
    def test_uses_config(self):
        client = APIClient()
        self.assertEqual(client.base_url, 'http://test')

    def test_context_manager_mock(self):
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.read.return_value = '{"key": "value"}'
        with patch('builtins.open', return_value=mock_file):
            result = load_config('config.json')
            self.assertEqual(result['key'], 'value')

    @patch.object(UserService, 'validate', return_value=True)
    @patch.object(UserService, 'save')
    def test_chained_patches(self, mock_save, mock_validate):
        mock_save.return_value = User(id=1, name="Alice")
        user = UserService().create_user("Alice")
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
```

## Subtests for Data-Driven Testing

```python
class TestValidator(unittest.TestCase):
    def test_email_validation(self):
        cases = [
            ("user@example.com", True),
            ("invalid", False),
            ("@missing.com", False),
            ("user@.com", False),
            ("a@b.c", True),
        ]
        for email, expected in cases:
            with self.subTest(email=email):
                self.assertEqual(validate_email(email), expected)
```

## Async Testing (Python 3.11+)

```python
class TestAsyncService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncClient()
        await self.client.connect()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_fetch_data(self):
        result = await self.client.fetch("/api/data")
        self.assertEqual(result["status"], "ok")

    async def test_concurrent_operations(self):
        import asyncio
        results = await asyncio.gather(
            self.client.fetch("/a"), self.client.fetch("/b")
        )
        self.assertTrue(all(r["status"] == "ok" for r in results))
```

## Custom Test Runner & Discovery

```python
# Custom runner with XML output
import xmlrunner

if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='reports'),
        verbosity=2,
        failfast=True
    )

# Custom discovery
loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTests(loader.discover('tests', pattern='test_*.py'))
suite.addTests(loader.loadTestsFromName('tests.integration.test_api'))
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```

## Anti-Patterns

- ❌ `assertEqual(result, True)` → use `assertTrue(result)`
- ❌ Bare `except` in tests — let exceptions propagate to test runner
- ❌ Complex `setUp` that tests depend on implicitly — make dependencies explicit
- ❌ Using `print()` for debugging — use `self.assertEqual` with descriptive messages
- ❌ Tests that depend on execution order within a class
