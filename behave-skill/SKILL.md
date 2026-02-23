---
name: behave-skill
description: >
  Generates Behave BDD tests for Python with Gherkin feature files and step
  implementations. Use when user mentions "Behave", "Python BDD", "Python
  Gherkin". Triggers on: "Behave", "Python BDD", "behave test", "Python
  feature file".
languages:
  - Python
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Behave BDD Skill

## Core Patterns

### Feature File (features/login.feature)

```gherkin
Feature: User Login
  As a registered user
  I want to log into the application

  Background:
    Given I am on the login page

  Scenario: Successful login
    When I enter "user@test.com" as email
    And I enter "password123" as password
    And I click login
    Then I should see the dashboard
    And the welcome message should say "Welcome"

  Scenario: Invalid credentials
    When I enter "wrong@test.com" as email
    And I enter "wrong" as password
    And I click login
    Then I should see error "Invalid credentials"

  Scenario Outline: Login with various users
    When I enter "<email>" as email
    And I enter "<password>" as password
    And I click login
    Then I should see "<result>"

    Examples:
      | email          | password | result    |
      | admin@test.com | admin123 | Dashboard |
      | bad@test.com   | wrong    | Error     |
```

### Step Definitions (features/steps/login_steps.py)

```python
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@given('I am on the login page')
def step_on_login(context):
    context.browser.get(context.base_url + '/login')

@when('I enter "{text}" as email')
def step_enter_email(context, text):
    el = context.browser.find_element(By.ID, 'email')
    el.clear()
    el.send_keys(text)

@when('I enter "{text}" as password')
def step_enter_password(context, text):
    el = context.browser.find_element(By.ID, 'password')
    el.clear()
    el.send_keys(text)

@when('I click login')
def step_click_login(context):
    context.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

@then('I should see the dashboard')
def step_see_dashboard(context):
    WebDriverWait(context.browser, 10).until(
        EC.url_contains('/dashboard')
    )
    assert '/dashboard' in context.browser.current_url

@then('I should see error "{msg}"')
def step_see_error(context, msg):
    error = WebDriverWait(context.browser, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.error'))
    )
    assert msg in error.text
```

### Environment Hooks (features/environment.py)

```python
from selenium import webdriver

def before_all(context):
    context.base_url = 'http://localhost:3000'

def before_scenario(context, scenario):
    context.browser = webdriver.Chrome()
    context.browser.implicitly_wait(10)

def after_scenario(context, scenario):
    if scenario.status == 'failed':
        context.browser.save_screenshot(f'screenshots/{scenario.name}.png')
    context.browser.quit()
```

### Tags

```gherkin
@smoke
Feature: Login
  @critical
  Scenario: ...
```

```bash
behave --tags=@smoke
behave --tags="@smoke and not @slow"
```

## Setup: `pip install behave selenium`
## Run: `behave` or `behave features/login.feature`

### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```python
# environment.py
from selenium import webdriver
import os

def before_scenario(context, scenario):
    lt_options = {
        "user": os.environ["LT_USERNAME"],
        "accessKey": os.environ["LT_ACCESS_KEY"],
        "build": "Behave Build",
        "name": scenario.name,
        "platformName": "Windows 11",
        "video": True,
        "console": True,
        "network": True,
    }
    options = webdriver.ChromeOptions()
    options.set_capability("LT:Options", lt_options)
    context.driver = webdriver.Remote(
        command_executor=f"https://{os.environ['LT_USERNAME']}:{os.environ['LT_ACCESS_KEY']}@hub.lambdatest.com/wd/hub",
        options=options,
    )
```
## Report: `behave --format json -o report.json`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | behave.ini, project structure, dependencies |
| §2 Feature Files | Gherkin with Scenario Outline, data tables, Background |
| §3 Step Definitions | Type registration, API steps, common steps with PyHamcrest |
| §4 Environment Hooks | before_all/scenario/feature, screenshot on failure, DB isolation |
| §5 Page Objects | BasePage with waits, LoginPage, reusable components |
| §6 Fixtures & Test Data | DatabaseHelper, transaction rollback, JSON data loader |
| §7 LambdaTest Integration | Remote browser creation, cloud capabilities |
| §8 CI/CD Integration | GitHub Actions with Postgres, Selenium, Allure reports |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item BDD testing checklist |
