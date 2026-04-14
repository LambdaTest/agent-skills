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

### Install All Skills

```bash
npx skills add https://github.com/LambdaTest/agent-skills.git
```

The CLI auto-detects your AI tool and installs to the right directory. You can also specify it explicitly:

```bash
npx skills add https://github.com/LambdaTest/agent-skills.git --tool cursor
```

### Install a Specific Skill

```bash
# E2E Testing
npx skills add https://github.com/LambdaTest/agent-skills.git --skill selenium-skill
npx skills add https://github.com/LambdaTest/agent-skills.git --skill playwright-skill
npx skills add https://github.com/LambdaTest/agent-skills.git --skill cypress-skill

# Unit Testing
npx skills add https://github.com/LambdaTest/agent-skills.git --skill jest-skill
npx skills add https://github.com/LambdaTest/agent-skills.git --skill pytest-skill
npx skills add https://github.com/LambdaTest/agent-skills.git --skill junit-5-skill

# Mobile Testing
npx skills add https://github.com/LambdaTest/agent-skills.git --skill appium-skill

# BDD
npx skills add https://github.com/LambdaTest/agent-skills.git --skill cucumber-skill
```

### Browse Available Skills

```bash
npx skills list https://github.com/LambdaTest/agent-skills.git
```

### CLI Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--skill <name>` | Install a single skill | `--skill playwright-skill` |
| `--tool <name>` | Target a specific AI tool | `--tool claude` |
| `--dir <path>` | Custom installation directory | `--dir ./my-skills` |

> Supported tools: `claude` · `cursor` · `copilot` · `gemini` · `codex` · `opencode` · `windsurf`

---

Once installed, just ask your AI assistant naturally:

```
"Write Playwright tests for the login page and run them on TestMu AI cloud (Chrome + Firefox)"

"Set up Cypress component tests for the React dashboard and upload screenshots on failure"

"Create JUnit 5 tests for the payments service with Mockito and GitHub Actions CI"

"Run Playwright tests locally against http://localhost:3000 with trace and video enabled"
```

---

## Compatibility

These skills follow the open **[Agent Skills Standard](https://agentskills.io)** (`SKILL.md` format):

| Tool | Type | Support | `--tool` flag |
|------|------|---------|---------------|
| **Claude Code** | CLI | ✅ Full | `claude` |
| **GitHub Copilot** | Extension | ✅ Full | `copilot` |
| **Cursor** | IDE | ✅ Full | `cursor` |
| **Gemini CLI** | CLI | ✅ Full | `gemini` |
| **Codex CLI** | CLI | ✅ Full | `codex` |
| **OpenCode** | CLI | ✅ Full | `opencode` |
| **Windsurf** | IDE | ✅ Full | `windsurf` |
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

| Skill | Languages | Category | Quick Install |
|-------|-----------|----------|---------------|
| **[Selenium Skill](selenium-skill/)** | Java, Python, JS, C#, Ruby | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill selenium-skill` |
| **[Playwright Skill](playwright-skill/)** | JS, TS, Python, Java, C# | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill playwright-skill` |
| **[Cypress Skill](cypress-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill cypress-skill` |
| **[Jest Skill](jest-skill/)** | JS, TS | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill jest-skill` |
| **[JUnit 5 Skill](junit-5-skill/)** | Java | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill junit-5-skill` |
| **[pytest Skill](pytest-skill/)** | Python | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill pytest-skill` |
| **[TestNG Skill](testng-skill/)** | Java | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill testng-skill` |
| **[WebdriverIO Skill](webdriverio-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill webdriverio-skill` |
| **[Appium Skill](appium-skill/)** | Java, Python, JS, Ruby, C# | Mobile | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill appium-skill` |
| **[Puppeteer Skill](puppeteer-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill puppeteer-skill` |
| **[Test Framework Migration Skill](test-framework-migration-skill/)** | JS, TS, Java, Python, C# | Migration | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill test-framework-migration-skill` |
| **[Mocha Skill](mocha-skill/)** | JS, TS | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill mocha-skill` |
| **[Vitest Skill](vitest-skill/)** | JS, TS | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill vitest-skill` |
| **[Cucumber Skill](cucumber-skill/)** | Java, JS, Ruby, TS | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill cucumber-skill` |
| **[Espresso Skill](espresso-skill/)** | Java, Kotlin | Mobile | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill espresso-skill` |
| **[Nightwatch.js Skill](nightwatchjs-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill nightwatchjs-skill` |
| **[Flutter Testing Skill](flutter-testing-skill/)** | Dart | Mobile | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill flutter-testing-skill` |
| **[XCUITest Skill](xcuitest-skill/)** | Swift, Obj-C | Mobile | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill xcuitest-skill` |
| **[Detox Skill](detox-skill/)** | JS, TS | Mobile | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill detox-skill` |
| **[TestCafe Skill](testcafe-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill testcafe-skill` |
| **[xUnit Skill](xunit-skill/)** | C# | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill xunit-skill` |
| **[RSpec Skill](rspec-skill/)** | Ruby | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill rspec-skill` |
| **[NUnit Skill](nunit-skill/)** | C# | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill nunit-skill` |
| **[Karma Skill](karma-skill/)** | JS, TS | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill karma-skill` |
| **[MSTest Skill](mstest-skill/)** | C# | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill mstest-skill` |
| **[Jasmine Skill](jasmine-skill/)** | JS, TS | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill jasmine-skill` |
| **[PHPUnit Skill](phpunit-skill/)** | PHP | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill phpunit-skill` |
| **[Robot Framework Skill](robot-framework-skill/)** | Python, Robot | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill robot-framework-skill` |
| **[Behat Skill](behat-skill/)** | PHP | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill behat-skill` |
| **[Behave Skill](behave-skill/)** | Python | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill behave-skill` |
| **[Capybara Skill](capybara-skill/)** | Ruby | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill capybara-skill` |
| **[Codeception Skill](codeception-skill/)** | PHP | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill codeception-skill` |
| **[Gauge Skill](gauge-skill/)** | Java, Python, JS, Ruby, C# | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill gauge-skill` |
| **[Geb Skill](geb-skill/)** | Groovy | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill geb-skill` |
| **[Laravel Dusk Skill](laravel-dusk-skill/)** | PHP | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill laravel-dusk-skill` |
| **[Lettuce Skill](lettuce-skill/)** | Python | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill lettuce-skill` |
| **[Nemo.js Skill](nemojs-skill/)** | JS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill nemojs-skill` |
| **[Protractor Skill](protractor-skill/)** | JS, TS | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill protractor-skill` |
| **[Selenide Skill](selenide-skill/)** | Java | E2E | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill selenide-skill` |
| **[Serenity BDD Skill](serenity-bdd-skill/)** | Java | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill serenity-bdd-skill` |
| **[SmartUI Skill](smartui-skill/)** | JS, TS, Java | Visual | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill smartui-skill` |
| **[SpecFlow Skill](specflow-skill/)** | C# | BDD | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill specflow-skill` |
| **[Test::Unit Skill](testunit-skill/)** | Ruby | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill testunit-skill` |
| **[unittest Skill](unittest-skill/)** | Python | Unit | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill unittest-skill` |
| **[HyperExecute Skill](hyperexecute-skill/)** | YAML | Cloud | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill hyperexecute-skill` |
| **[CI/CD Pipeline Skill](cicd-pipeline-skill/)** | YAML | DevOps | `npx skills add https://github.com/LambdaTest/agent-skills.git --skill cicd-pipeline-skill` |

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
