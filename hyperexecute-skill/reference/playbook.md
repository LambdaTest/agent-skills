# HyperExecute — Advanced Implementation Playbook

## §1 Core Configuration

### hyperexecute.yaml — Playwright
```yaml
version: 0.1
globalTimeout: 120
testSuiteTimeout: 120
testSuiteStep: 120

runson: linux
concurrency: 15
autosplit: true

pre:
  - npm ci
  - npx playwright install --with-deps chromium firefox webkit

testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn 'test\(' tests/ --include='*.spec.ts' -l

testRunnerCommand: npx playwright test $test --reporter=list

framework:
  name: playwright
  args:
    playwrightVersion: "1.42"

uploadArtefacts:
  - name: Playwright Reports
    path: [playwright-report/**, test-results/**]

cacheKey: npm-{{ checksum "package-lock.json" }}
cacheDirectories: [node_modules]

env:
  LT_USERNAME: ${LT_USERNAME}
  LT_ACCESS_KEY: ${LT_ACCESS_KEY}

retryOnFailure: true
maxRetries: 2
smartOrdering: true
```

### hyperexecute.yaml — Cypress
```yaml
version: 0.1
globalTimeout: 90
testSuiteTimeout: 90
runson: linux
concurrency: 10
autosplit: true

pre:
  - npm ci
  - npx cypress install

testDiscovery:
  type: raw
  mode: dynamic
  command: find cypress/e2e -name '*.cy.ts' -o -name '*.cy.js'

testRunnerCommand: npx cypress run --spec $test --reporter mochawesome --reporter-options reportDir=mochawesome-report,overwrite=false,json=true

framework:
  name: cypress
  args:
    cypressVersion: "13"

uploadArtefacts:
  - name: Cypress Reports
    path: [cypress/screenshots/**, cypress/videos/**, mochawesome-report/**]

cacheKey: npm-{{ checksum "package-lock.json" }}
cacheDirectories: [node_modules, ~/.cache/Cypress]
```

### hyperexecute.yaml — Selenium Java
```yaml
version: 0.1
globalTimeout: 90
testSuiteTimeout: 90
runson: linux
concurrency: 10
autosplit: true

pre:
  - mvn -Dmaven.test.skip=true clean install

testDiscovery:
  type: raw
  mode: dynamic
  command: grep -rn '@Test' src/test --include='*.java' -l | sed 's/.*\///' | sed 's/\.java//'

testRunnerCommand: mvn test -Dtest=$test -pl module-name

framework:
  name: selenium
  args:
    seleniumVersion: "4.18"

uploadArtefacts:
  - name: Test Reports
    path: [target/surefire-reports/**, target/allure-results/**]

cacheKey: mvn-{{ checksum "pom.xml" }}
cacheDirectories: [~/.m2/repository]
```

---

## §2 Matrix Configuration

### Cross-Browser / Cross-OS Matrix
```yaml
matrix:
  browser: ["chromium", "firefox", "webkit"]
  os: ["linux", "win", "mac"]

# In testRunnerCommand, use matrix vars:
testRunnerCommand: npx playwright test $test --project=$browser

# Filter matrix combinations
combineTasksInMatrixLevel: 2
```

### Multi-Environment Matrix
```yaml
matrix:
  env: ["staging", "production"]
  browser: ["chrome", "firefox"]

testRunnerCommand: BASE_URL=$env_url npx cypress run --spec $test --browser $browser

env:
  staging_url: https://staging.myapp.com
  production_url: https://myapp.com
```

---

## §3 Advanced Features

### Tunnel for Private Environments
```yaml
tunnel: true
tunnelOpts:
  global: true
  # tunnelName: "my-tunnel"
  # proxyHost: "proxy.internal.com"
  # proxyPort: "8080"
```

### Smart Ordering & Flaky Test Management
```yaml
smartOrdering: true           # runs recently failed tests first
retryOnFailure: true
maxRetries: 2

# Quarantine flaky tests
# Tests that fail intermittently are auto-identified and retried
```

### Test Sharding
```yaml
autosplit: true               # automatic distribution across machines
concurrency: 20              # up to 20 parallel executions

# OR manual sharding:
autosplit: false
testSuites:
  - tests/auth/*.spec.ts
  - tests/checkout/*.spec.ts
  - tests/dashboard/*.spec.ts
```

### Pre/Post Commands
```yaml
pre:
  - npm ci
  - npx playwright install --with-deps
  - node scripts/setup-test-data.js
  - docker compose -f docker-compose.test.yml up -d

post:
  - node scripts/cleanup-test-data.js
  - docker compose -f docker-compose.test.yml down

# Conditional commands
preDirectives:
  commands:
    - npm ci
  shell: bash
  maxRetries: 2
  workingDirectory: /home/user/project
```

### Environment Variables
```yaml
env:
  LT_USERNAME: ${LT_USERNAME}
  LT_ACCESS_KEY: ${LT_ACCESS_KEY}
  BASE_URL: https://staging.myapp.com
  NODE_ENV: test
  DATABASE_URL: ${DATABASE_URL}
  API_KEY: ${API_KEY}
```

---

## §4 CLI Usage & Execution

### Installation
```bash
# Linux
curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
chmod +x hyperexecute

# macOS
curl -O https://downloads.lambdatest.com/hyperexecute/darwin/hyperexecute
chmod +x hyperexecute

# Windows
curl -O https://downloads.lambdatest.com/hyperexecute/windows/hyperexecute.exe
```

### Execution
```bash
# Basic run
./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml

# With overrides
./hyperexecute \
  --user $LT_USERNAME \
  --key $LT_ACCESS_KEY \
  --config hyperexecute.yaml \
  --vars "BASE_URL=https://staging.myapp.com" \
  --force-clean-artifacts

# Verbose logging
./hyperexecute \
  --user $LT_USERNAME \
  --key $LT_ACCESS_KEY \
  --config hyperexecute.yaml \
  --verbose

# Specific tests only
./hyperexecute \
  --user $LT_USERNAME \
  --key $LT_ACCESS_KEY \
  --config hyperexecute.yaml \
  --test-discovery-command "echo tests/smoke/login.spec.ts"
```

---

## §5 CI/CD Integration

### GitHub Actions
```yaml
name: HyperExecute Tests
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  hyperexecute:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download HyperExecute CLI
        run: |
          curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
          chmod +x hyperexecute

      - name: Run tests
        run: |
          ./hyperexecute \
            --user ${{ secrets.LT_USERNAME }} \
            --key ${{ secrets.LT_ACCESS_KEY }} \
            --config hyperexecute.yaml
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}

  hyperexecute-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        config: [hyperexecute-smoke.yaml, hyperexecute-regression.yaml]
    steps:
      - uses: actions/checkout@v4
      - run: |
          curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
          chmod +x hyperexecute
      - run: |
          ./hyperexecute \
            --user ${{ secrets.LT_USERNAME }} \
            --key ${{ secrets.LT_ACCESS_KEY }} \
            --config ${{ matrix.config }}
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    environment {
        LT_USERNAME = credentials('lt-username')
        LT_ACCESS_KEY = credentials('lt-access-key')
    }
    stages {
        stage('HyperExecute') {
            steps {
                sh '''
                    curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
                    chmod +x hyperexecute
                    ./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml
                '''
            }
        }
    }
}
```

---

## §6 Multiple Config Files Strategy

```bash
# Smoke tests — fast, critical paths
# hyperexecute-smoke.yaml
concurrency: 5
testDiscovery:
  command: find tests/smoke -name '*.spec.ts'

# Regression tests — comprehensive
# hyperexecute-regression.yaml
concurrency: 20
testDiscovery:
  command: find tests -name '*.spec.ts'

# Visual regression
# hyperexecute-visual.yaml
concurrency: 10
testDiscovery:
  command: find tests/visual -name '*.spec.ts'
```

---

## §7 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests not discovered | `testDiscovery.command` returns empty | Run discovery command locally; verify grep/find pattern matches test files |
| 2 | `pre` commands fail | Dependency installation error | Check logs; ensure `pre` commands work locally; verify node/java version |
| 3 | Tunnel not connecting | Firewall or proxy blocking | Use `tunnelOpts.proxyHost/proxyPort`; check corporate firewall rules |
| 4 | Timeout before tests complete | `globalTimeout` too low | Increase `globalTimeout` and `testSuiteTimeout` values |
| 5 | Cache not working | `cacheKey` not matching | Verify `{{ checksum }}` targets correct lockfile; check file exists |
| 6 | Artifacts not uploaded | Path pattern mismatch | Use `**` glob pattern; verify report files are generated in expected path |
| 7 | Matrix generates too many combinations | Unconstrained cross-product | Use `combineTasksInMatrixLevel` to limit; or use `exclude` list |
| 8 | Tests fail with "browser not found" | Browser not installed in `pre` | Add explicit install: `npx playwright install --with-deps` |
| 9 | Environment variables not set | Missing `env` section or CLI `--vars` | Add vars to `env:` in YAML; or pass `--vars "KEY=value"` in CLI |
| 10 | `autosplit` distributes unevenly | Some test files much larger than others | Split large test files; or use `testSuiteStep` for finer granularity |

---

## §8 Best Practices Checklist

1. ✅ Use `autosplit: true` for automatic test distribution across machines
2. ✅ Use caching for dependencies: `cacheKey: npm-{{ checksum "package-lock.json" }}`
3. ✅ Use matrix for cross-browser/OS coverage
4. ✅ Use tunnel for private/staging environments
5. ✅ Use `smartOrdering` to prioritize recently-failed tests
6. ✅ Use `retryOnFailure: true` with bounded `maxRetries` for flaky tests
7. ✅ Set appropriate timeouts: `globalTimeout`, `testSuiteTimeout`, `testSuiteStep`
8. ✅ Upload artifacts: reports, screenshots, videos for debugging
9. ✅ Use multiple config files: smoke, regression, visual
10. ✅ Store credentials as CI secrets — never hardcode `LT_USERNAME`/`LT_ACCESS_KEY`
11. ✅ Use `pre`/`post` commands for setup/cleanup of test data
12. ✅ Monitor concurrency — match to your LambdaTest plan limits
13. ✅ Use `--verbose` CLI flag for troubleshooting failed runs
