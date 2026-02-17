---
name: lettuce-testing-skill
description: >
  Generates Lettuce BDD tests for Python with feature files and step definitions.
  Note: Lettuce is legacy/unmaintained; consider Behave for new projects. Use when
  user specifically mentions "Lettuce". Triggers on: "Lettuce", "lettuce test",
  "lettuce BDD".
languages:
  - Python
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Lettuce BDD Skill (Legacy)

> **Note:** Lettuce is largely unmaintained. For new Python BDD projects, use **Behave** instead.

## Core Patterns

### Feature File (features/login.feature)

```gherkin
Feature: User Login
  Scenario: Successful login
    Given I navigate to the login page
    When I enter "user@test.com" as email
    And I enter "password123" as password
    And I click login
    Then I should see the dashboard

  Scenario: Invalid login
    Given I navigate to the login page
    When I enter "bad@test.com" as email
    And I enter "wrong" as password
    And I click login
    Then I should see "Invalid credentials"
```

### Step Definitions (features/steps.py)

```python
from lettuce import step, world
from selenium import webdriver
from selenium.webdriver.common.by import By

@step(r'I navigate to the login page')
def navigate_to_login(step):
    world.browser = webdriver.Chrome()
    world.browser.get(world.base_url + '/login')

@step(r'I enter "([^"]*)" as email')
def enter_email(step, email):
    el = world.browser.find_element(By.ID, 'email')
    el.clear()
    el.send_keys(email)

@step(r'I enter "([^"]*)" as password')
def enter_password(step, password):
    el = world.browser.find_element(By.ID, 'password')
    el.clear()
    el.send_keys(password)

@step(r'I click login')
def click_login(step):
    world.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

@step(r'I should see the dashboard')
def see_dashboard(step):
    assert '/dashboard' in world.browser.current_url

@step(r'I should see "([^"]*)"')
def see_text(step, text):
    assert text in world.browser.page_source
```

### Terrain (Setup/Teardown — terrain.py)

```python
from lettuce import before, after, world

@before.all
def setup():
    world.base_url = 'http://localhost:3000'

@before.each_scenario
def before_scenario(scenario):
    pass

@after.each_scenario
def cleanup(scenario):
    if hasattr(world, 'browser'):
        world.browser.quit()

@after.all
def teardown(total):
    print(f"Ran {total.scenarios_ran} scenarios")
```

## Setup: `pip install lettuce selenium`
## Run: `lettuce` or `lettuce features/login.feature`

### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```python
# terrain.py
from selenium import webdriver
import os

@before.all
def setup():
    lt_options = {
        "user": os.environ["LT_USERNAME"],
        "accessKey": os.environ["LT_ACCESS_KEY"],
        "build": "Lettuce Build",
        "platformName": "Windows 11",
        "video": True,
        "console": True,
    }
    options = webdriver.ChromeOptions()
    options.set_capability("LT:Options", lt_options)
    world.browser = webdriver.Remote(
        command_executor=f"https://{os.environ['LT_USERNAME']}:{os.environ['LT_ACCESS_KEY']}@hub.lambdatest.com/wd/hub",
        options=options,
    )
```
## Migration: Consider switching to `behave` for active maintenance

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
