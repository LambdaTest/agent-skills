# Python Patterns — Playwright

## Table of Contents
- Setup
- Sync vs Async API
- pytest-playwright Integration
- POM in Python
- Cloud Integration (Python)
- conftest.py Fixtures

## Setup

```bash
pip install pytest-playwright
playwright install
```

## Sync vs Async API

Default to **sync** unless user explicitly asks for async.

### Sync (Default)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")
    assert page.title() == "Example Domain"
    browser.close()
```

### Async

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        assert await page.title() == "Example Domain"
        await browser.close()

asyncio.run(main())
```

## pytest-playwright Integration

Tests get `page`, `browser`, `context` fixtures automatically:

```python
# tests/test_login.py
import pytest
from playwright.sync_api import Page, expect

def test_login_success(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_label("Password").fill("password123")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

def test_login_invalid(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("bad@example.com")
    page.get_by_label("Password").fill("wrong")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("alert")).to_have_text("Invalid credentials")
```

### pytest.ini / pyproject.toml

```ini
# pytest.ini
[pytest]
addopts = --headed --browser chromium
base-url = http://localhost:3000
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--headed --browser chromium"
base_url = "http://localhost:3000"
```

## POM in Python

```python
# pages/login_page.py
from playwright.sync_api import Page, Locator

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input: Locator = page.get_by_label("Email")
        self.password_input: Locator = page.get_by_label("Password")
        self.submit_button: Locator = page.get_by_role("button", name="Sign in")
        self.error_message: Locator = page.get_by_role("alert")

    def goto(self):
        self.page.goto("/login")

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
```

### Fixture in conftest.py

```python
# conftest.py
import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@pytest.fixture
def login_page(page):
    return LoginPage(page)

@pytest.fixture
def dashboard_page(page):
    return DashboardPage(page)
```

```python
# tests/test_auth.py
from playwright.sync_api import expect

def test_login(login_page, dashboard_page):
    login_page.goto()
    login_page.login("user@example.com", "password123")
    expect(dashboard_page.welcome_heading).to_be_visible()
```

## Cloud Integration (Python)

### Standalone Script

```python
import os, json
from playwright.sync_api import sync_playwright

capabilities = {
    "browserName": "Chrome",
    "browserVersion": "latest",
    "LT:Options": {
        "platform": "Windows 11",
        "build": "Python Build",
        "name": "Python Test",
        "user": os.environ["LT_USERNAME"],
        "accessKey": os.environ["LT_ACCESS_KEY"],
        "network": True,
        "video": True,
    },
}

with sync_playwright() as p:
    browser = p.chromium.connect(
        f"wss://cdp.lambdatest.com/playwright?capabilities="
        f"{json.dumps(capabilities)}"
    )
    page = browser.new_page()

    try:
        page.goto("https://example.com")
        assert page.title() == "Example Domain"
        status = "passed"
        remark = "OK"
    except Exception as e:
        status = "failed"
        remark = str(e)
        raise
    finally:
        page.evaluate(
            "_ => {}",
            f'lambdatest_action: {json.dumps({"action": "setTestStatus", "arguments": {"status": status, "remark": remark}})}'
        )
        browser.close()
```

### pytest Fixture for Cloud

```python
# conftest.py
import os, json, pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def cloud_browser():
    caps = {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "LT:Options": {
            "platform": "Windows 11",
            "user": os.environ["LT_USERNAME"],
            "accessKey": os.environ["LT_ACCESS_KEY"],
            "network": True,
            "video": True,
        },
    }
    pw = sync_playwright().start()
    browser = pw.chromium.connect(
        f"wss://cdp.lambdatest.com/playwright?capabilities={json.dumps(caps)}"
    )
    yield browser
    browser.close()
    pw.stop()

@pytest.fixture
def cloud_page(cloud_browser):
    context = cloud_browser.new_context()
    page = context.new_page()
    yield page
    context.close()
```

Run: `pytest tests/ --browser chromium` (local) or use `cloud_page` fixture (cloud).
