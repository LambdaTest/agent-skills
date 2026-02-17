---
name: hyperexecute-skill
description: >
  Generates HyperExecute YAML configurations for blazing-fast test orchestration
  on LambdaTest's TestMu AI cloud. Framework-agnostic — works with any test
  framework. Use when user mentions "HyperExecute", "fast test execution",
  "test orchestration", "hyperexecute.yaml". Triggers on: "HyperExecute",
  "hyperexecute.yaml", "test orchestration", "HE", "fast parallel tests".
languages:
  - YAML
category: cloud-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# HyperExecute Skill

## Core Patterns

### Basic YAML Configuration

```yaml
---
version: 0.1
globalTimeout: 90
testSuiteTimeout: 90
testSuiteStep: 90

runson: linux  # or win, mac

autosplit: true
retryOnFailure: true
maxRetries: 2

concurrency: 10

pre:
  - npm install
  - npx playwright install

testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn 'test(' tests/ --include='*.spec.ts' -l

testRunnerCommand: npx playwright test $test --project=chromium

framework:
  name: playwright
  args:
    buildName: "HyperExecute Build"

env:
  LT_USERNAME: ${LT_USERNAME}
  LT_ACCESS_KEY: ${LT_ACCESS_KEY}
```

### Matrix Mode (Cross-Browser)

```yaml
version: 0.1
runson: linux
concurrency: 10

matrix:
  browser: ["chromium", "firefox", "webkit"]
  os: ["linux"]

pre:
  - npm install
  - npx playwright install

testSuites:
  - npx playwright test --project=$browser
```

### Hybrid Mode

```yaml
version: 0.1
runson: linux
concurrency: 5

testDiscovery:
  type: raw
  mode: static
  command: cat testSuites.txt

testRunnerCommand: mvn test -Dtest=$test

pre:
  - mvn compile -DskipTests

post:
  - cat target/surefire-reports/*.txt
```

### Upload & Run

```bash
# Download CLI
curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
chmod +x hyperexecute

# Execute
./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY \
  --config hyperexecute.yaml
```

### Framework Examples

**Selenium + Java:**
```yaml
pre:
  - mvn compile -DskipTests
testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn '@Test' src/test --include='*.java' -l | sed 's|src/test/java/||;s|.java||;s|/|.|g'
testRunnerCommand: mvn test -Dtest=$test
```

**Cypress:**
```yaml
pre:
  - npm install
testDiscovery:
  type: raw
  mode: dynamic
  command: find cypress/e2e -name '*.cy.js' | sed 's|cypress/e2e/||'
testRunnerCommand: npx cypress run --spec "cypress/e2e/$test"
```

**Pytest:**
```yaml
pre:
  - pip install -r requirements.txt
testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn 'def test_' tests/ --include='*.py' -l
testRunnerCommand: pytest $test -v
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| Low concurrency | `concurrency: 10+` | Underusing HE speed |
| No `pre` step | Install deps in `pre` | Missing dependencies |
| Static discovery only | `mode: dynamic` with autosplit | Better parallelism |
| No retries | `retryOnFailure: true` | Flaky test resilience |

## Quick Reference

| Task | Command |
|------|---------|
| Run | `./hyperexecute --config hyperexecute.yaml` |
| With vars | `./hyperexecute --config he.yaml --vars "browser=chrome"` |
| Debug | `--verbose` flag |
| Download CLI | `https://downloads.lambdatest.com/hyperexecute/<os>/hyperexecute` |

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
