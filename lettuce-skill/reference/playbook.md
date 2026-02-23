# Lettuce — Advanced Implementation Playbook

> Lettuce is unmaintained. This playbook covers maintenance patterns for existing
> codebases and migration paths to Behave.

## §1 — Data-Driven Scenarios

```gherkin
Feature: User Registration
  Scenario Outline: Validate email formats
    Given I am on the registration page
    When I enter "<email>" as email
    And I submit the form
    Then I should see "<result>"

    Examples:
      | email            | result           |
      | user@example.com | Registration OK  |
      | invalid          | Invalid email    |
      | @nouser.com      | Invalid email    |
      | user@            | Invalid email    |
```

### Step with Table Data

```gherkin
  Scenario: Create multiple users
    Given the following users exist:
      | name    | email            | role   |
      | Alice   | alice@test.com   | admin  |
      | Bob     | bob@test.com     | user   |
    Then I should have 2 users in the system
```

```python
from lettuce import step, world

@step(r'the following users exist:')
def create_users(step):
    world.users = []
    for row in step.hashes:
        user = create_user(name=row['name'], email=row['email'], role=row['role'])
        world.users.append(user)

@step(r'I should have (\d+) users in the system')
def verify_user_count(step, count):
    assert len(world.users) == int(count), \
        f"Expected {count} users, got {len(world.users)}"
```

## §2 — Terrain Hooks with Error Handling

```python
# terrain.py
from lettuce import before, after, world
from selenium import webdriver
import os, time

@before.all
def setup():
    world.base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
    world.screenshots_dir = 'screenshots'
    os.makedirs(world.screenshots_dir, exist_ok=True)

@before.each_scenario
def before_scenario(scenario):
    options = webdriver.ChromeOptions()
    if os.environ.get('CI'):
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    world.browser = webdriver.Chrome(options=options)
    world.browser.implicitly_wait(10)
    world.browser.set_window_size(1920, 1080)

@after.each_scenario
def after_scenario(scenario):
    if hasattr(world, 'browser'):
        if scenario.failed:
            name = scenario.name.replace(' ', '_')
            ts = int(time.time())
            path = f"{world.screenshots_dir}/{name}_{ts}.png"
            world.browser.save_screenshot(path)
            print(f"Screenshot saved: {path}")
        world.browser.quit()

@after.all
def teardown(total):
    passed = total.scenarios_passed
    failed = total.scenarios_ran - passed
    print(f"\nResults: {passed} passed, {failed} failed out of {total.scenarios_ran}")
```

## §3 — API Testing Steps

```python
import requests

@step(r'I send a GET request to "([^"]*)"')
def send_get(step, endpoint):
    world.response = requests.get(world.base_url + endpoint,
        headers=getattr(world, 'headers', {}))

@step(r'I send a POST request to "([^"]*)" with:')
def send_post(step, endpoint):
    import json
    data = {row['key']: row['value'] for row in step.hashes}
    world.response = requests.post(world.base_url + endpoint,
        json=data, headers=getattr(world, 'headers', {}))

@step(r'the response status should be (\d+)')
def check_status(step, status):
    assert world.response.status_code == int(status), \
        f"Expected {status}, got {world.response.status_code}: {world.response.text}"

@step(r'the response should contain "([^"]*)"')
def check_body(step, text):
    assert text in world.response.text, \
        f"'{text}' not found in response: {world.response.text[:200]}"
```

## §4 — Debugging & Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `ImportError: No module named lettuce` | Not installed | `pip install lettuce` (Python 2.7/3.x) |
| Steps not discovered | Wrong directory | Steps must be in `features/steps/` or `features/steps.py` |
| `world` not shared | Scope issue | `world` persists across steps within a scenario |
| Browser not quitting | Missing cleanup | Always quit in `@after.each_scenario` |
| Unicode errors | Python 2 defaults | Use `# -*- coding: utf-8 -*-` at top of files |
| Feature not found | Wrong path | Run `lettuce features/specific.feature` |

## §5 — CI/CD Integration

```yaml
name: Lettuce Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: |
          pip install lettuce selenium requests
          pip install webdriver-manager
      - run: lettuce --verbosity=3
        env:
          CI: true
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: screenshots, path: screenshots/ }
```

## §6 — Migration to Behave (Recommended)

Lettuce → Behave mapping:

| Lettuce | Behave |
|---------|--------|
| `from lettuce import step, world` | `from behave import given, when, then` |
| `@step(r'pattern')` | `@given('pattern')`, `@when('pattern')`, `@then('pattern')` |
| `world.variable` | `context.variable` |
| `terrain.py` → `@before.all` | `environment.py` → `def before_all(context)` |
| `step.hashes` | `context.table` (with `table.rows`) |

### Migration Script

```python
#!/usr/bin/env python3
"""Convert Lettuce step files to Behave format."""
import re, sys

def convert(content):
    # Replace imports
    content = content.replace('from lettuce import step, world',
                              'from behave import given, when, then')
    content = content.replace('from lettuce import', 'from behave import')

    # Replace @step with appropriate BDD keyword
    content = re.sub(r"@step\(r?'I navigate", "@given('I navigate", content)
    content = re.sub(r"@step\(r?'I enter", "@when('I enter", content)
    content = re.sub(r"@step\(r?'I click", "@when('I click", content)
    content = re.sub(r"@step\(r?'I send", "@when('I send", content)
    content = re.sub(r"@step\(r?'I should", "@then('I should", content)
    content = re.sub(r"@step\(r?'the response", "@then('the response", content)

    # Replace world → context
    content = content.replace('world.', 'context.')

    # Replace step.hashes → context.table
    content = content.replace('step.hashes', 'context.table')

    return content

if __name__ == '__main__':
    for f in sys.argv[1:]:
        with open(f) as fh: original = fh.read()
        converted = convert(original)
        out = f.replace('.py', '_behave.py')
        with open(out, 'w') as fh: fh.write(converted)
        print(f"Converted: {f} → {out}")
```

### Feature files require NO changes — Gherkin syntax is identical.

## §7 — Best Practices

- Use `world` for shared state between steps (equivalent of Behave's `context`)
- Use terrain.py for all hooks — keep step files focused on step logic
- Always clean up browser in `@after.each_scenario`
- Take screenshots on failure for debugging
- Use Scenario Outline + Examples for data-driven tests
- Use step.hashes for table data
- **Plan migration to Behave** — Lettuce has no active development
- Keep features in business language, not technical implementation
