# Lettuce BDD — Advanced Patterns & Playbook

## Step Definitions with Context

```python
from lettuce import step, world, before, after
import requests

@before.all
def setup():
    world.base_url = "http://localhost:3000"
    world.session = requests.Session()

@after.all
def teardown():
    world.session.close()

@step(r'I am authenticated as "(.*)" with password "(.*)"')
def auth_step(step, username, password):
    resp = world.session.post(f"{world.base_url}/auth",
        json={"username": username, "password": password})
    world.token = resp.json()["token"]
    world.session.headers["Authorization"] = f"Bearer {world.token}"

@step(r'I send a (\w+) request to "(.*)"')
def send_request(step, method, endpoint):
    world.response = getattr(world.session, method.lower())(
        f"{world.base_url}{endpoint}")

@step(r'the response status should be (\d+)')
def check_status(step, status):
    assert world.response.status_code == int(status), \
        f"Expected {status}, got {world.response.status_code}"

@step(r'the response should contain "(.*)"')
def check_body(step, text):
    assert text in world.response.text
```

## Feature File Patterns

```gherkin
Feature: User Management
  As an admin I want to manage users

  Background:
    Given I am authenticated as "admin" with password "secret"

  Scenario Outline: Create users with different roles
    When I create a user with name "<name>" and role "<role>"
    Then the response status should be 201
    And the user should have role "<role>"

    Examples:
      | name    | role    |
      | Alice   | editor  |
      | Bob     | viewer  |
      | Charlie | admin   |

  Scenario: Delete user
    Given a user "test-user" exists
    When I send a DELETE request to "/api/users/test-user"
    Then the response status should be 204
```

## Terrain (Environment Setup)

```python
# terrain.py
from lettuce import before, after, world
from selenium import webdriver

@before.each_scenario
def setup_browser(scenario):
    world.browser = webdriver.Chrome()
    world.browser.implicitly_wait(10)

@after.each_scenario
def teardown_browser(scenario):
    if hasattr(world, 'browser'):
        world.browser.quit()

@before.each_feature
def setup_db(feature):
    world.db = connect_test_db()
    world.db.seed()

@after.each_feature
def teardown_db(feature):
    world.db.truncate_all()
    world.db.close()
```

## Anti-Patterns

- ❌ Steps that depend on global state without explicit setup
- ❌ Overly specific step definitions — prefer reusable parameterized steps
- ❌ Missing cleanup in `@after` hooks — leads to resource leaks
- ❌ Business logic in step definitions — delegate to page objects or service classes
