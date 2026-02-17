---
name: cicd-pipeline-skill
description: >
  Generates CI/CD pipeline configurations for test automation with GitHub Actions,
  Jenkins, GitLab CI, and Azure DevOps. Includes TestMu AI cloud integration.
  Use when user mentions "CI/CD", "pipeline", "GitHub Actions", "Jenkins",
  "GitLab CI". Triggers on: "CI/CD", "pipeline", "GitHub Actions", "Jenkins",
  "GitLab CI", "Azure DevOps", "automated testing pipeline".
languages:
  - YAML
category: devops
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# CI/CD Pipeline Skill

## Core Patterns

### GitHub Actions

```yaml
name: Test Automation
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx playwright install --with-deps

      # Local tests
      - run: npx playwright test --project=chromium

      # Cloud tests on TestMu AI
      - run: npx playwright test --project="chrome:latest:Windows 11@lambdatest"
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results/
```

### Jenkins (Jenkinsfile)

```groovy
pipeline {
    agent any
    environment {
        LT_USERNAME = credentials('lt-username')
        LT_ACCESS_KEY = credentials('lt-access-key')
    }
    stages {
        stage('Install') { steps { sh 'npm ci' } }
        stage('Test') {
            parallel {
                stage('Unit') { steps { sh 'npx jest' } }
                stage('E2E') { steps { sh 'npx playwright test' } }
                stage('Cloud') { steps { sh 'npx playwright test --project="chrome:latest:Windows 11@lambdatest"' } }
            }
        }
    }
    post {
        always { junit 'test-results/**/*.xml' }
        failure { emailext to: 'team@example.com', subject: 'Tests Failed' }
    }
}
```

### GitLab CI

```yaml
stages: [install, test]

install:
  stage: install
  script: npm ci
  cache: { paths: [node_modules/] }

test:
  stage: test
  parallel:
    matrix:
      - PROJECT: [chromium, firefox, webkit]
  script:
    - npx playwright install --with-deps
    - npx playwright test --project=$PROJECT
  artifacts:
    when: always
    paths: [test-results/]
    reports:
      junit: test-results/**/*.xml
```

## Quick Reference

| CI System | Config File | Secrets |
|-----------|------------|---------|
| GitHub Actions | `.github/workflows/test.yml` | Settings → Secrets |
| Jenkins | `Jenkinsfile` | Credentials store |
| GitLab CI | `.gitlab-ci.yml` | Settings → CI/CD → Variables |
| Azure DevOps | `azure-pipelines.yml` | Library → Variable Groups |

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
