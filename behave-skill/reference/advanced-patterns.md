# Behave (Python BDD) — Advanced Patterns & Playbook

## Step Implementations with Context

```python
from behave import given, when, then, use_step_matcher
from hamcrest import assert_that, equal_to, has_entries

use_step_matcher("re")

@given('I am authenticated as "(?P<role>admin|user|guest)"')
def step_auth(context, role):
    context.session = context.api_client.authenticate(
        **context.test_data.credentials[role])

@when('I send a (?P<method>GET|POST|PUT|DELETE) request to "(?P<endpoint>.*)"')
def step_request(context, method, endpoint):
    fn = getattr(context.session, method.lower())
    body = json.loads(context.text) if context.text else None
    context.response = fn(f"{context.base_url}{endpoint}", json=body)

@then('the response status should be {status:d}')
def step_status(context, status):
    assert_that(context.response.status_code, equal_to(status))

@then('the response should contain')
def step_response_contains(context):
    expected = json.loads(context.text)
    assert_that(context.response.json(), has_entries(**expected))
```

## Environment Setup

```python
# features/environment.py
from selenium import webdriver

def before_all(context):
    context.config.setup_logging()
    context.base_url = os.getenv("APP_URL", "http://localhost:3000")

def before_scenario(context, scenario):
    if "ui" in scenario.tags:
        context.browser = webdriver.Chrome()
        context.browser.implicitly_wait(10)
    if "db" in scenario.tags:
        context.db = TestDatabase()
        context.db.begin_transaction()

def after_scenario(context, scenario):
    if hasattr(context, 'browser'):
        if scenario.status == "failed":
            context.browser.save_screenshot(f"screenshots/{scenario.name}.png")
        context.browser.quit()
    if hasattr(context, 'db'):
        context.db.rollback()

def before_tag(context, tag):
    if tag == "fixture.users":
        context.users = seed_users(context.db)
```

## Table & Outline Patterns

```gherkin
Feature: Shopping Cart
  Background:
    Given I am authenticated as "user"

  Scenario Outline: Add products
    When I add "<product>" with quantity <qty>
    Then the cart should have <expected> items

    Examples:
      | product  | qty | expected |
      | Widget   | 2   | 2        |
      | Gadget   | 3   | 3        |

  Scenario: Bulk add from table
    When I add the following products:
      | name    | quantity | price |
      | Widget  | 2        | 9.99  |
      | Gadget  | 1        | 19.99 |
    Then the cart total should be "39.97"
```

## Anti-Patterns

- ❌ Complex logic in step definitions — delegate to page objects / service classes
- ❌ `context` as arbitrary dict — use typed attributes consistently
- ❌ `time.sleep()` in steps — use explicit waits
- ❌ Steps that combine Given+When+Then — keep steps single-purpose
