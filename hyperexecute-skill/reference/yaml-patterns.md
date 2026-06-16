# YAML Patterns

Use these as templates, not generated truth. Adapt commands to the project.

## Autosplit

```yaml
version: 0.1
runson: linux
concurrency: 10
autosplit: true
retryOnFailure: true
maxRetries: 2

pre:
  - npm ci

testDiscovery:
  type: raw
  mode: dynamic
  command: find tests -name '*.spec.ts'

testRunnerCommand: npx playwright test $test
```

Use autosplit when tests can be split by file, class, or spec path.

## Matrix

```yaml
version: 0.1
runson: linux
concurrency: 10

matrix:
  browser: [chromium, firefox, webkit]

testSuites:
  - npx playwright test --project=$browser
```

Use matrix for browser, OS, environment, or capability combinations. Keep the cross-product small until one run succeeds.

## Manual Suites

```yaml
version: 0.1
runson: linux
concurrency: 3
autosplit: false

testSuites:
  - npm run test:smoke
  - npm run test:checkout
  - npm run test:account
```

Use manual suites when discovery is unreliable or suites map to business flows.

## Setup, Cache, And Artifacts

```yaml
pre:
  - npm ci

cacheKey: npm-{{ checksum "package-lock.json" }}
cacheDirectories:
  - node_modules

uploadArtefacts:
  - name: test-output
    path:
      - playwright-report/**
      - test-results/**
```

Only cache directories that are safe to reuse between jobs.

## Tunnel

```yaml
tunnel: true
tunnelOpts:
  global: true
```

Use tunnel for private staging environments. For corporate networks, combine with proxy options or CLI `--auto-proxy`.

## Timeouts

```yaml
globalTimeout: 120
testSuiteTimeout: 90
testSuiteStep: 90
```

Increase timeouts after confirming whether failures are slow tests, dependency setup, or cloud infrastructure delays.
