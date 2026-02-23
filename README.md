# TestMu AI Skills - Production-Grade Agent Skills for Test Automation

> **Battle-tested Agent Skills for Claude Code, Copilot, Cursor, Gemini CLI & more - covering every major test automation framework across 15+ languages.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/Skills-46-blue.svg)](#full-skill-registry)
[![Languages](https://img.shields.io/badge/Languages-15+-green.svg)](#languages-covered)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Standard-purple.svg)](https://agentskills.io)
[![LambdaTest](https://img.shields.io/badge/LambdaTest-Cloud_Ready-orange.svg)](https://www.lambdatest.com)

---

## What Is This?

TestMu AI Skills is a curated collection of **Agent Skills** that teach AI coding assistants how to write production-grade test automation. Each skill is a self-contained package of instructions, code patterns, debugging guides, and CI/CD configurations for a specific testing framework.

Instead of getting generic test code, your AI agent becomes a **Senior QA automation architect** that knows:
- The right project structure for each framework
- Correct dependency versions and configurations
- Both local and cloud (TestMu AI) execution patterns
- Common pitfalls and how to debug them
- CI/CD integration with GitHub Actions
- Best practices that ship in real-world codebases

## Quick Start

### Option 1: Install a Single Skill

```bash
# Clone the repo and copy the skill you need
git clone https://github.com/LambdaTest/agent-skills.git
cp -r agent-skills/selenium-skill .claude/skills/

# Or for Cursor / Copilot
cp -r agent-skills/playwright-skill .cursor/skills/
```

### Option 2: Install All Skills

```bash
# Claude Code
git clone https://github.com/LambdaTest/agent-skills.git .claude/skills/agent-skills

# Gemini CLI
git clone https://github.com/LambdaTest/agent-skills.git .gemini/skills/agent-skills

# Cursor
git clone https://github.com/LambdaTest/agent-skills.git .cursor/skills/agent-skills

# Universal (.agent/ works with most tools)
git clone https://github.com/LambdaTest/agent-skills.git .agent/skills/agent-skills
```

Then just ask your AI assistant naturally:

```
"Write Playwright tests for the login page and run them on TestMu AI cloud (Chrome + Firefox)"

"Set up Cypress component tests for the React dashboard and upload screenshots on failure"

"Create JUnit 5 tests for the payments service with Mockito and GitHub Actions CI"

"Run Playwright tests locally against http://localhost:3000 with trace and video enabled"

```

---

## 🔌 Compatibility

These skills follow the open **[Agent Skills Standard](https://agentskills.io)** (`SKILL.md` format):

| Tool | Type | Support | Installation Path |
|------|------|---------|-------------------|
| **Claude Code** | CLI | ✅ Full | `.claude/skills/` |
| **GitHub Copilot** | Extension | ✅ Full | `.github/skills/` |
| **Cursor** | IDE | ✅ Full | `.cursor/skills/` |
| **Gemini CLI** | CLI | ✅ Full | `.gemini/skills/` |
| **Codex CLI** | CLI | ✅ Full | `.codex/skills/` |
| **OpenCode** | CLI | ✅ Full | `.opencode/skills/` |
| **Claude.ai** | Web | ✅ Upload | Settings → Features → Skills |

---

## Features & Categories

| Category | Count | Frameworks |
|----------|-------|------------|
| 🌐 **E2E / Browser Testing** | 15 | Selenium, Playwright, Cypress, WebdriverIO, Puppeteer, TestCafe, Nightwatch.js, Capybara, Geb, Selenide, NemoJS, Protractor, Codeception, Laravel Dusk, Robot Framework |
| 🧪 **Unit Testing** | 15 | Jest, JUnit 5, pytest, TestNG, Vitest, Mocha, Jasmine, Karma, xUnit, NUnit, MSTest, RSpec, PHPUnit, Test::Unit, unittest |
| 📱 **Mobile Testing** | 5 | Appium, Espresso, XCUITest, Flutter, Detox |
| 📋 **BDD Testing** | 7 | Cucumber, SpecFlow, Serenity BDD, Behave, Behat, Gauge, Lettuce |
| 👁️ **Visual Testing** | 1 | SmartUI |
| ☁️ **Cloud Testing** | 1 | HyperExecute |
| 🔄 **Migration** | 1 | Selenium ↔ Playwright, Puppeteer, Cypress |
| 🔄 **DevOps / CI/CD** | 1 | GitHub Actions / Jenkins / GitLab CI |

### Languages Covered

`Java` · `Python` · `JavaScript` · `TypeScript` · `C#` · `Ruby` · `PHP` · `Kotlin` · `Swift` · `Objective-C` · `Dart` · `Groovy` · `YAML` · `XML` · `Robot Framework`

---

## Full Skill Registry (46/46)

| Skill | Languages | Category | Description |
|-------|-----------|----------|-------------|
| **[Selenium Skill](selenium-skill/)** | Java, Python, JS, C#, Ruby | E2E | Selenium WebDriver with cross-browser cloud support |
| **[Playwright Skill](playwright-skill/)** | JS, TS, Python, Java, C# | E2E | Playwright browser automation with API mocking |
| **[Cypress Skill](cypress-skill/)** | JS, TS | E2E | Cypress E2E and component testing |
| **[Jest Skill](jest-skill/)** | JS, TS | Unit | Jest unit/integration tests with mocking |
| **[JUnit 5 Skill](junit-5-skill/)** | Java | Unit | JUnit 5 with parameterized tests and extensions |
| **[pytest Skill](pytest-skill/)** | Python | Unit | pytest with fixtures, parametrize, and plugins |
| **[TestNG Skill](testng-skill/)** | Java | Unit | TestNG with data providers and parallel execution |
| **[WebdriverIO Skill](webdriverio-skill/)** | JS, TS | E2E | WebdriverIO with page objects and cloud integration |
| **[Appium Skill](appium-skill/)** | Java, Python, JS, Ruby, C# | Mobile | Appium mobile testing for iOS and Android |
| **[Puppeteer Skill](puppeteer-skill/)** | JS, TS | E2E | Puppeteer Chrome automation |
| **[Test Framework Migration Skill](test-framework-migration-skill/)** | JS, TS, Java, Python, C# | Migration | Convert tests between Selenium, Playwright, Puppeteer, Cypress |
| **[Mocha Skill](mocha-skill/)** | JS, TS | Unit | Mocha with Chai assertions |
| **[Vitest Skill](vitest-skill/)** | JS, TS | Unit | Vitest for Vite projects |
| **[Cucumber Skill](cucumber-skill/)** | Java, JS, Ruby, TS | BDD | Cucumber Gherkin BDD |
| **[Espresso Skill](espresso-skill/)** | Java, Kotlin | Mobile | Espresso Android UI testing |
| **[Nightwatch.js Skill](nightwatchjs-skill/)** | JS, TS | E2E | Nightwatch.js browser automation |
| **[Flutter Testing Skill](flutter-testing-skill/)** | Dart | Mobile | Flutter widget and integration tests |
| **[XCUITest Skill](xcuitest-skill/)** | Swift, Obj-C | Mobile | XCUITest iOS UI testing |
| **[Detox Skill](detox-skill/)** | JS, TS | Mobile | Detox React Native E2E testing |
| **[TestCafe Skill](testcafe-skill/)** | JS, TS | E2E | TestCafe cross-browser testing |
| **[xUnit Skill](xunit-skill/)** | C# | Unit | xUnit.net for .NET |
| **[RSpec Skill](rspec-skill/)** | Ruby | Unit | RSpec with shared examples |
| **[NUnit Skill](nunit-skill/)** | C# | Unit | NUnit for .NET |
| **[Karma Skill](karma-skill/)** | JS, TS | Unit | Karma test runner |
| **[MSTest Skill](mstest-skill/)** | C# | Unit | MSTest for .NET |
| **[Jasmine Skill](jasmine-skill/)** | JS, TS | Unit | Jasmine BDD-style testing |
| **[PHPUnit Skill](phpunit-skill/)** | PHP | Unit | PHPUnit with data providers |
| **[Robot Framework Skill](robot-framework-skill/)** | Python, Robot | E2E | Robot Framework keyword-driven testing |
| **[Behat Skill](behat-skill/)** | PHP | BDD | Behat BDD for PHP |
| **[Behave Skill](behave-skill/)** | Python | BDD | Behave Python BDD |
| **[Capybara Skill](capybara-skill/)** | Ruby | E2E | Capybara acceptance testing |
| **[Codeception Skill](codeception-skill/)** | PHP | E2E | Codeception full-stack PHP testing |
| **[Gauge Skill](gauge-skill/)** | Java, Python, JS, Ruby, C# | BDD | Gauge specification-based testing |
| **[Geb Skill](geb-skill/)** | Groovy | E2E | Geb Groovy browser automation |
| **[Laravel Dusk Skill](laravel-dusk-skill/)** | PHP | E2E | Laravel Dusk browser testing |
| **[Lettuce Skill](lettuce-skill/)** | Python | BDD | Lettuce Python BDD testing |
| **[Nemo.js Skill](nemojs-skill/)** | JS | E2E | Nemo.js PayPal browser automation |
| **[Protractor Skill](protractor-skill/)** | JS, TS | E2E | Protractor Angular E2E testing |
| **[Selenide Skill](selenide-skill/)** | Java | E2E | Selenide fluent Selenium wrapper |
| **[Serenity BDD Skill](serenity-bdd-skill/)** | Java | BDD | Serenity BDD with Screenplay pattern |
| **[SmartUI Skill](smartui-skill/)** | JS, TS, Java | Visual | SmartUI visual regression testing |
| **[SpecFlow Skill](specflow-skill/)** | C# | BDD | SpecFlow .NET BDD with Gherkin |
| **[Test::Unit Skill](testunit-skill/)** | Ruby | Unit | Test::Unit Ruby testing |
| **[unittest Skill](unittest-skill/)** | Python | Unit | Python unittest with mocking |
| **[HyperExecute Skill](hyperexecute-skill/)** | YAML | Cloud | HyperExecute cloud test orchestration |
| **[CI/CD Pipeline Skill](cicd-pipeline-skill/)** | YAML | DevOps | CI/CD pipeline integration |

---

## Skill Architecture

Each skill follows the Agent Skills Standard with progressive disclosure:

```
selenium-skill/
├── SKILL.md                          # Core instructions (<500 lines)
│   └── Workflow + decision trees     # When/how to use the skill
└── reference/
    ├── playbook.md                   # Complete implementation guide
    │   ├── Project setup & dependencies
    │   ├── Code patterns & page objects
    │   ├── Cloud integration (LambdaTest)
    │   ├── CI/CD configuration
    │   ├── Debugging table (12+ common problems)
    │   └── Best practices checklist (14+ items)
    ├── advanced-patterns.md          # Advanced topics
    └── cloud-integration.md          # Cloud-specific patterns
```

**How it works:**
1. **Metadata** (name + description) is always loaded — ~100 tokens per skill
2. **SKILL.md body** loads when triggered — core workflow and patterns
3. **Reference files** load on-demand — detailed code, debugging, CI/CD

---

## Cloud Testing with TestMu AI

Skills that support browser/device testing include **TestMu AI  cloud integration** out of the box.

### Get Your TestMu AI Credentials

Make sure you have your TestMu AI credentials with you to run test automation scripts on TestMu AI Selenium Grid. You can obtain these credentials from the [TestMu AI Automation Dashboard](https://automation.lambdatest.com/) or through [TestMu AI Profile](https://accounts.lambdatest.com/security).

Set TestMu AI `USERNAME` and `ACCESS_KEY` in environment variables.
- Copy `.env.example` to `.env` and fill in your credentials.


or add credentials directly from your terminal:

**For Linux/macOS:**
```bash
export LT_USERNAME="YOUR_USERNAME"
export LT_ACCESS_KEY="YOUR_ACCESS_KEY"
```

**For Windows:**
```bash
set LT_USERNAME="YOUR_USERNAME"
set LT_ACCESS_KEY="YOUR_ACCESS_KEY"
```

### Run Tests on the Cloud

Then ask your AI assistant naturally:
```
"Run my Selenium tests on Chrome, Firefox, and Safari on TestMu AI with OS versions Windows 11, macOS Sonoma, and Ubuntu 22.04"

"Execute Playwright tests across 5 browsers in parallel on TestMu AI, tag the build as 'release-1.8.2', and capture traces on failure"

"Set up Cypress on TestMu AI with video recording and JUnit reports, and upload artifacts to the dashboard"

"Test my localhost app through the TestMu AI tunnel (http://localhost:3000) using Playwright and validate login + checkout flows"

"Run mobile web tests on real devices via TestMu AI tunnel and verify the responsive layout on iPhone 15 and Pixel 8"
```

View your test results, logs, and video recordings on the [TestMu AI  Automation Dashboard](https://automation.lambdatest.com/).

---

## What Each Skill Includes

Every playbook follows a consistent structure:

| Section | What It Covers |
|---------|---------------|
| **Project Setup** | Dependencies, versions, config files, project structure |
| **Core Patterns** | Essential code patterns with complete, runnable examples |
| **Page Objects / Utilities** | Reusable abstractions for real-world projects |
| **Cloud Integration** | TestMu AI  RemoteWebDriver/capabilities configuration |
| **CI/CD Integration** | GitHub Actions workflow with reports and parallel execution |
| **Debugging Table** | 12+ common problems with cause → fix mappings |
| **Best Practices** | 14+ actionable items for production code |

---

## Repository Structure

```
agent-skills/
├── README.md                  # This file
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # How to contribute
├── skills_index.json          # Machine-readable skill registry
├── scripts/
│   └── validate_skills.py     # Validation script
├── shared/
│   ├── testmu-cloud-reference.md
│   └── scripts/
├── evals/                     # Evaluation test cases per skill
│   └── *-evals.json
└── <skill-name>/              # 46 skill directories
    ├── SKILL.md
    └── reference/
        ├── playbook.md
        └── advanced-patterns.md
```

---

## Validation

```bash
python3 scripts/validate_skills.py
```

Checks: YAML frontmatter, line counts, reference files, cross-references.

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your skill directory with `SKILL.md` and `reference/playbook.md`
3. Run `python3 scripts/validate_skills.py`
4. Submit a Pull Request

---

## Credits


- **[TestMu AI ](https://www.lambdatest.com)** — Power Your Software Testing with  AI Agents and Cloud
- **[Anthropic](https://anthropic.com)** — Agent Skills standard and Claude Code
- **[Agent Skills Standard](https://agentskills.io)** — Open standard for portable AI skills

---

## License

MIT License. See [LICENSE](LICENSE) for details.
