---
name: behat-automation-skill
description: >
  Generates Behat BDD tests for PHP with Gherkin feature files and MinkContext
  for browser testing. Use when user mentions "Behat", "PHP BDD", "Mink",
  "behat.yml". Triggers on: "Behat", "PHP BDD", "Mink", "behat.yml",
  "FeatureContext PHP".
languages:
  - PHP
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Behat BDD Skill

## Core Patterns

### Feature File (features/login.feature)

```gherkin
Feature: User Login
  As a user I want to log in

  Scenario: Successful login
    Given I am on "/login"
    When I fill in "email" with "user@test.com"
    And I fill in "password" with "password123"
    And I press "Login"
    Then I should see "Dashboard"
    And I should be on "/dashboard"

  Scenario: Invalid credentials
    Given I am on "/login"
    When I fill in "email" with "wrong@test.com"
    And I fill in "password" with "wrong"
    And I press "Login"
    Then I should see "Invalid credentials"
```

### Custom Context (features/bootstrap/LoginContext.php)

```php
<?php
use Behat\MinkExtension\Context\MinkContext;
use Behat\Behat\Context\Context;

class LoginContext extends MinkContext implements Context
{
    /**
     * @When I login as :email with password :password
     */
    public function iLoginAs(string $email, string $password): void
    {
        $this->visit('/login');
        $this->fillField('email', $email);
        $this->fillField('password', $password);
        $this->pressButton('Login');
    }

    /**
     * @Then I should see the dashboard
     */
    public function iShouldSeeTheDashboard(): void
    {
        $this->assertSession()->addressEquals('/dashboard');
        $this->assertSession()->pageTextContains('Welcome');
    }

    /**
     * @Then the response time should be under :ms milliseconds
     */
    public function responseUnder(int $ms): void
    {
        // Custom performance assertion
    }
}
```

### Built-in MinkContext Steps

```gherkin
# Navigation
Given I am on "/path"
When I go to "/path"
When I reload the page

# Forms
When I fill in "field" with "value"
When I select "option" from "select"
When I check "checkbox"
When I uncheck "checkbox"
When I press "button"
When I attach the file "path" to "field"

# Assertions
Then I should see "text"
Then I should not see "text"
Then I should be on "/path"
Then the response status code should be 200
Then the "field" field should contain "value"
Then I should see an "css-selector" element
Then print current URL
```

### behat.yml

```yaml
default:
  suites:
    default:
      contexts:
        - LoginContext
        - Behat\MinkExtension\Context\MinkContext
  extensions:
    Behat\MinkExtension:
      base_url: 'http://localhost:3000'
      sessions:
        default:
          selenium2:
            browser: chrome
            wd_host: 'http://localhost:4444/wd/hub'
```

### Tags

```bash
./vendor/bin/behat --tags=@smoke
./vendor/bin/behat --tags="@smoke&&~@slow"
```

## Setup: `composer require --dev behat/behat behat/mink-extension behat/mink-selenium2-driver`
## Init: `./vendor/bin/behat --init`

### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```yaml
# behat.yml
default:
  extensions:
    Behat\MinkExtension:
      base_url: 'https://your-app.com'
      selenium2:
        wd_host: 'https://hub.lambdatest.com/wd/hub'
        capabilities:
          browser: 'chrome'
          extra_capabilities:
            'LT:Options':
              user: '%env(LT_USERNAME)%'
              accessKey: '%env(LT_ACCESS_KEY)%'
              build: 'Behat Build'
              name: 'Behat Test'
              platformName: 'Windows 11'
              video: true
              console: true
              network: true
```
## Run: `./vendor/bin/behat` or `./vendor/bin/behat features/login.feature`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | behat.yml with suites, Mink extension, profiles, project structure |
| §2 Feature Files | Gherkin with Scenario Outline, Background, TableNode data |
| §3 Context Classes | Step definitions, dependency injection, API context, assertions |
| §4 Hooks | BeforeSuite/Scenario/Step, screenshot on failure, transaction rollback |
| §5 Page Objects | Page Object pattern with elements map, reusable components |
| §6 LambdaTest Integration | Remote Selenium config, cloud browser profiles |
| §7 Custom Formatters | HTML report formatter, result collection |
| §8 CI/CD Integration | GitHub Actions with MySQL, Selenium, JUnit reports |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item BDD testing checklist |
