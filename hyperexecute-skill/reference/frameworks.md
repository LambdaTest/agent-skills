# Framework Recipes

Run `hyperexecute analyze` first when possible. Use these recipes to author or repair `hyperexecute.yaml`.

## Playwright

Signals: `playwright.config.*`, `@playwright/test`, `tests/**/*.spec.*`.

```yaml
pre:
  - npm ci
  - npx playwright install --with-deps
testDiscovery:
  type: raw
  mode: dynamic
  command: find tests -name '*.spec.ts' -o -name '*.spec.js'
testRunnerCommand: npx playwright test $test --reporter=list
framework:
  name: playwright
uploadArtefacts:
  - name: playwright-output
    path: [playwright-report/**, test-results/**]
```

Common fixes: install browsers in `pre`, constrain projects with `--project`, upload `test-results/**` for traces.

## Cypress

Signals: `cypress.config.*`, `cypress/e2e`, `cypress/integration`.

```yaml
pre:
  - npm ci
  - npx cypress install
testDiscovery:
  type: raw
  mode: dynamic
  command: find cypress/e2e -name '*.cy.js' -o -name '*.cy.ts'
testRunnerCommand: npx cypress run --spec $test
framework:
  name: cypress
uploadArtefacts:
  - name: cypress-output
    path: [cypress/screenshots/**, cypress/videos/**, cypress/reports/**]
```

Common fixes: verify spec path quoting, install Cypress binary, upload screenshots/videos.

## Selenium Java Maven

Signals: `pom.xml`, `src/test/java`, JUnit/TestNG dependencies.

```yaml
pre:
  - mvn -Dmaven.test.skip=true clean install
testDiscovery:
  type: raw
  mode: dynamic
  command: find src/test/java -name '*Test.java'
testRunnerCommand: mvn test -Dtest=$test
framework:
  name: selenium
uploadArtefacts:
  - name: java-test-output
    path: [target/surefire-reports/**, target/failsafe-reports/**, target/allure-results/**]
```

Common fixes: align discovery output with `-Dtest`, handle modules with `-pl`, use TestNG suite XML when classes are not enough.

## Pytest

Signals: `pytest.ini`, `pyproject.toml`, `requirements.txt`, `tests/test_*.py`.

```yaml
pre:
  - pip install -r requirements.txt
testDiscovery:
  type: raw
  mode: dynamic
  command: find tests -name 'test_*.py' -o -name '*_test.py'
testRunnerCommand: pytest $test -v
uploadArtefacts:
  - name: pytest-output
    path: [reports/**, htmlcov/**, .pytest_cache/**]
```

Common fixes: install browser/system dependencies for Selenium or Playwright Python tests, verify marker filters.

## WebdriverIO

Signals: `wdio.conf.*`, `@wdio/cli`, `specs` in config.

```yaml
pre:
  - npm ci
testDiscovery:
  type: raw
  mode: dynamic
  command: find test specs tests -name '*.spec.js' -o -name '*.spec.ts'
testRunnerCommand: npx wdio run wdio.conf.js --spec $test
framework:
  name: webdriverio
uploadArtefacts:
  - name: wdio-output
    path: [allure-results/**, reports/**, screenshots/**]
```

Common fixes: avoid excessive WebDriver calls, use stable selectors, and preserve screenshots/reports for failures.
