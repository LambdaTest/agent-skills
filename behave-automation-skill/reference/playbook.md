# Behave — Advanced Playbook

## §1 Project Setup & Configuration

### Installation
```bash
pip install behave
pip install behave-html-formatter     # HTML reports
pip install selenium                  # Web UI testing
pip install requests                  # API testing
pip install allure-behave             # Allure reports
pip install PyHamcrest                # Better assertions
```

### Project Structure
```
features/
├── login.feature
├── checkout.feature
├── api/
│   ├── users.feature
│   └── products.feature
├── steps/
│   ├── login_steps.py
│   ├── checkout_steps.py
│   ├── api_steps.py
│   └── common_steps.py
├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   └── dashboard_page.py
├── environment.py
├── behave.ini
└── fixtures.py
```

### behave.ini
```ini
[behave]
paths = features
format = pretty
         json
         html
outfiles =
    reports/results.json
    reports/report.html
color = true
show_timings = true
junit = true
junit_directory = reports/junit
log_capture = true
logging_level = INFO
default_tags = ~@wip ~@skip
```

### setup.cfg (Alternative Config)
```ini
[behave]
paths = features
format = progress3
junit = true
junit_directory = reports/junit
show_timings = true
```

---

## §2 Feature Files — Gherkin Patterns

### UI Feature with Scenario Outline
```gherkin
# features/login.feature
@ui @smoke
Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access my dashboard

  Background:
    Given the test database is ready
    And I am on the login page

  @critical
  Scenario: Successful login
    When I enter "user@test.com" as email
    And I enter "ValidPass123" as password
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see "Welcome back, Test User"

  @negative
  Scenario Outline: Login with invalid credentials
    When I enter "<email>" as email
    And I enter "<password>" as password
    And I click the login button
    Then I should see error message "<error>"

    Examples: Invalid credentials
      | email            | password     | error                      |
      | wrong@test.com   | ValidPass123 | Invalid email or password  |
      | user@test.com    | wrong        | Invalid email or password  |
      |                  | ValidPass123 | Email is required          |
      | user@test.com    |              | Password is required       |
```

### API Feature with Data Tables
```gherkin
# features/api/users.feature
@api
Feature: Users API
  As an API consumer
  I want to manage users via REST API

  Background:
    Given I am authenticated as admin

  Scenario: Create a new user
    When I send a POST request to "/api/users" with:
      | name  | Test User              |
      | email | newuser@test.com       |
      | role  | viewer                 |
    Then the response status should be 201
    And the response should contain "id"
    And the response field "name" should be "Test User"

  Scenario: List users with pagination
    When I send a GET request to "/api/users?page=1&limit=10"
    Then the response status should be 200
    And the response should contain at most 10 items

  Scenario: Delete user returns 204
    Given a user exists with email "delete-me@test.com"
    When I send a DELETE request to the user endpoint
    Then the response status should be 204
```

---

## §3 Step Definitions — Production Patterns

### Common Steps with Type Registration
```python
# features/steps/common_steps.py
from behave import given, when, then, register_type, step
from hamcrest import assert_that, equal_to, contains_string, greater_than
import parse


def parse_boolean(text):
    return text.strip().lower() in ('true', 'yes', '1')


register_type(Boolean=parse_boolean)


@given('the test database is ready')
def step_setup_db(context):
    context.db_helper.reset_and_seed()


@given('I am on the "{page_name}" page')
def step_navigate(context, page_name):
    pages = {
        'login': '/login',
        'register': '/register',
        'dashboard': '/dashboard',
        'products': '/products',
    }
    url = pages.get(page_name, f'/{page_name}')
    context.browser.get(f"{context.base_url}{url}")


@then('I should see "{text}"')
def step_see_text(context, text):
    assert_that(context.browser.page_source, contains_string(text))


@then('I should see error message "{message}"')
def step_see_error(context, message):
    error_el = context.browser.find_element("css selector", ".error-message")
    assert_that(error_el.text, contains_string(message))
```

### API Steps
```python
# features/steps/api_steps.py
from behave import given, when, then
from hamcrest import assert_that, equal_to, has_key, has_length, less_than_or_equal_to
import requests
import json


@given('I am authenticated as {role}')
def step_auth(context, role):
    credentials = {
        'admin': ('admin@test.com', 'AdminPass123'),
        'user': ('user@test.com', 'UserPass123'),
    }
    email, password = credentials[role]
    response = requests.post(f"{context.api_url}/auth/login", json={
        'email': email, 'password': password,
    })
    context.auth_token = response.json()['token']
    context.auth_headers = {
        'Authorization': f'Bearer {context.auth_token}',
        'Content-Type': 'application/json',
    }


@given('a user exists with email "{email}"')
def step_create_user(context, email):
    response = requests.post(f"{context.api_url}/users",
        json={'name': 'Temp User', 'email': email, 'role': 'viewer'},
        headers=context.auth_headers)
    context.created_user_id = response.json()['id']
    context.created_user_url = f"/api/users/{context.created_user_id}"


@when('I send a {method} request to "{url}"')
def step_send_request(context, method, url):
    full_url = f"{context.api_url}{url.replace('/api', '')}"
    context.response = requests.request(
        method, full_url, headers=context.auth_headers)


@when('I send a {method} request to "{url}" with')
def step_send_request_with_table(context, method, url):
    data = dict(context.table.rows)
    full_url = f"{context.api_url}{url.replace('/api', '')}"
    context.response = requests.request(
        method, full_url, json=data, headers=context.auth_headers)


@when('I send a DELETE request to the user endpoint')
def step_delete_user(context):
    url = f"{context.api_url}/users/{context.created_user_id}"
    context.response = requests.delete(url, headers=context.auth_headers)


@then('the response status should be {status:d}')
def step_check_status(context, status):
    assert_that(context.response.status_code, equal_to(status))


@then('the response should contain "{field}"')
def step_response_has_field(context, field):
    body = context.response.json()
    assert_that(body, has_key(field))


@then('the response field "{field}" should be "{value}"')
def step_response_field_value(context, field, value):
    body = context.response.json()
    assert_that(str(body[field]), equal_to(value))


@then('the response should contain at most {count:d} items')
def step_response_count(context, count):
    body = context.response.json()
    data = body.get('data', body)
    assert_that(data, has_length(less_than_or_equal_to(count)))
```

---

## §4 Environment Hooks — Lifecycle

```python
# features/environment.py
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger('behave')


def before_all(context):
    """Global setup — runs once before everything."""
    context.base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
    context.api_url = os.environ.get('API_URL', 'http://localhost:3000/api')
    context.screenshots_dir = 'reports/screenshots'
    os.makedirs(context.screenshots_dir, exist_ok=True)

    # Database helper
    from features.fixtures import DatabaseHelper
    context.db_helper = DatabaseHelper()


def before_feature(context, feature):
    """Runs before each feature file."""
    logger.info(f"Starting feature: {feature.name}")


def before_scenario(context, scenario):
    """Runs before each scenario."""
    # Start browser for UI tests
    if 'ui' in scenario.effective_tags:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        remote_url = os.environ.get('SELENIUM_URL')
        if remote_url:
            context.browser = webdriver.Remote(
                command_executor=remote_url,
                options=chrome_options)
        else:
            context.browser = webdriver.Chrome(options=chrome_options)

        context.browser.implicitly_wait(10)

    # Database transaction for isolation
    context.db_helper.begin_transaction()


def after_scenario(context, scenario):
    """Runs after each scenario."""
    # Screenshot on failure
    if scenario.status == 'failed' and hasattr(context, 'browser'):
        safe_name = scenario.name.replace(' ', '_')[:50]
        filepath = f"{context.screenshots_dir}/{safe_name}.png"
        context.browser.save_screenshot(filepath)
        logger.error(f"Screenshot saved: {filepath}")

    # Close browser
    if hasattr(context, 'browser'):
        context.browser.quit()
        del context.browser

    # Rollback database
    context.db_helper.rollback()


def after_all(context):
    """Global teardown."""
    context.db_helper.close()
```

---

## §5 Page Objects

### Base Page
```python
# features/pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BasePage:
    def __init__(self, browser, base_url):
        self.browser = browser
        self.base_url = base_url
        self.wait = WebDriverWait(browser, 15)

    def navigate(self, path=''):
        self.browser.get(f"{self.base_url}{path}")

    def find(self, by, value):
        return self.wait.until(EC.visibility_of_element_located((by, value)))

    def click(self, by, value):
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def type_text(self, by, value, text):
        element = self.find(by, value)
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        return self.find(by, value).text


class LoginPage(BasePage):
    URL = '/login'
    EMAIL_INPUT = (By.ID, 'email')
    PASSWORD_INPUT = (By.ID, 'password')
    SUBMIT_BTN = (By.ID, 'login-submit')
    ERROR_MSG = (By.CSS_SELECTOR, '.error-message')

    def open(self):
        self.navigate(self.URL)

    def login(self, email, password):
        self.type_text(*self.EMAIL_INPUT, email)
        self.type_text(*self.PASSWORD_INPUT, password)
        self.click(*self.SUBMIT_BTN)

    def get_error(self):
        return self.get_text(*self.ERROR_MSG)
```

---

## §6 Fixtures & Test Data

```python
# features/fixtures.py
import os
import json
import psycopg2
from contextlib import contextmanager


class DatabaseHelper:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ.get(
            'DATABASE_URL', 'postgresql://test:test@localhost/testdb'))
        self.conn.autocommit = False

    def begin_transaction(self):
        self.conn.rollback()  # Clear any pending

    def rollback(self):
        self.conn.rollback()

    def reset_and_seed(self):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM orders")
            cur.execute("DELETE FROM cart_items")
            cur.execute("DELETE FROM users WHERE email LIKE '%@test.com'")
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES
                    ('Admin', 'admin@test.com', '$hash', 'admin'),
                    ('Test User', 'user@test.com', '$hash', 'user')
            """)
        self.conn.commit()

    def close(self):
        self.conn.close()


class TestDataLoader:
    @staticmethod
    def load_json(filename):
        path = os.path.join('features', 'data', filename)
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def load_users():
        return TestDataLoader.load_json('test_users.json')
```

---

## §7 LambdaTest Integration

```python
# features/environment.py — LambdaTest section
def _create_lambdatest_browser(context, scenario):
    """Create browser on LambdaTest cloud."""
    lt_options = {
        'name': scenario.name,
        'build': os.environ.get('BUILD_NAME', 'Behave-Build'),
        'project': 'MyProject',
        'platformName': 'Windows 11',
        'w3c': True,
        'video': True,
        'network': True,
        'console': True,
    }
    chrome_options = Options()
    chrome_options.set_capability('LT:Options', lt_options)

    username = os.environ['LT_USERNAME']
    access_key = os.environ['LT_ACCESS_KEY']
    hub_url = f'https://{username}:{access_key}@hub.lambdatest.com/wd/hub'

    context.browser = webdriver.Remote(
        command_executor=hub_url, options=chrome_options)
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: Behave Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  behave:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s
      selenium:
        image: selenium/standalone-chrome:latest
        ports: ['4444:4444']

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - run: pip install behave selenium requests PyHamcrest allure-behave behave-html-formatter

      - name: Run Behave Tests
        run: |
          behave \
            --format=pretty \
            --format=allure_behave.formatter:AllureFormatter \
            --outfile=reports/allure \
            --junit \
            --junit-directory=reports/junit \
            --tags="~@wip" \
            --no-capture
        env:
          BASE_URL: http://localhost:3000
          API_URL: http://localhost:3000/api
          SELENIUM_URL: http://localhost:4444/wd/hub
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: behave-results
          path: reports/
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `NotImplementedError` for step | Step definition not found | Run `behave --snippets-type=parse` to generate stubs |
| 2 | `context.browser` not available | Missing `@ui` tag on scenario | Add `@ui` tag; check `before_scenario` creates browser for tag |
| 3 | `StaleElementReferenceException` | Page reloaded after finding element | Re-find element after page changes; use explicit waits |
| 4 | Tests pass alone, fail together | Shared state via `context` leaking | Reset `context` attributes in `before_scenario`; use transaction rollback |
| 5 | Scenario Outline shows wrong data | Mismatch between placeholder and Examples column | Column names must match `<placeholder>` names exactly |
| 6 | `before_scenario` not firing | Wrong function signature | Must be `def before_scenario(context, scenario):` with both args |
| 7 | Screenshots not saved | Directory doesn't exist or wrong path | Use `os.makedirs(dir, exist_ok=True)` in `before_all` |
| 8 | `context.table` is None | Step pattern doesn't expect table data | Use `table` in step text: `When I send a POST with:` (colon triggers table) |
| 9 | Allure report empty | Formatter not installed or wrong output path | Verify `allure-behave` installed; check `--outfile` path |
| 10 | CI fails with `selenium.common.exceptions` | Chrome/ChromeDriver version mismatch | Use `selenium/standalone-chrome:latest` Docker image |
| 11 | Tags not filtering | Wrong tag syntax in `behave.ini` | Use `--tags="@smoke"` not `--tags="smoke"` (include `@`) |
| 12 | Import errors in steps | Step files not in `features/steps/` directory | All step files must be in `features/steps/` subdirectory |

---

## §10 Best Practices Checklist

1. Use Background for shared Given steps — avoid repetition across scenarios
2. Use Scenario Outline with Examples — parameterize without duplicating
3. Use `context` for sharing state — never use global variables
4. Use `environment.py` hooks — setup/teardown at correct scope
5. Use transaction rollback — fastest isolation between scenarios
6. Use Page Objects — abstract browser interaction from step definitions
7. Use `register_type()` for custom step parsers — `{count:d}`, `{Boolean}`
8. Use PyHamcrest matchers — readable assertions: `assert_that(x, equal_to(y))`
9. Use tags for organization — `@smoke`, `@api`, `@ui`, `@wip`, `@slow`
10. Use `--tags="~@wip"` in CI — exclude incomplete scenarios
11. Use screenshot on failure — attach to Allure or HTML reports
12. Use JUnit output for CI — standard format for test report publishing
13. Keep step definitions reusable — one step per action, not per scenario
14. Write features in business language — domain experts should review Gherkin
