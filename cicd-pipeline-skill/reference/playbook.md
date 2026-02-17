# CI/CD Pipeline — Advanced Implementation Playbook

## §1 GitHub Actions — Production Workflows

### Complete Multi-Stage Pipeline
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '${{ env.NODE_VERSION }}' }
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  unit:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [18, 20, 22]
        shard: [1, 2, 3]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage --shard=${{ matrix.shard }}/3
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.node }}-${{ matrix.shard }}
          path: coverage/

  e2e:
    needs: unit
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    services:
      db:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: testdb }
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '${{ env.NODE_VERSION }}', cache: 'npm' }
      - run: npm ci
      - run: npx playwright install --with-deps ${{ matrix.browser }}
      - name: Run E2E
        run: npx playwright test --project=${{ matrix.browser }}
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/

  coverage:
    needs: unit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { pattern: coverage-*, merge-multiple: true }
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: true
          flags: unittests

  build:
    needs: [unit, e2e]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: |
          echo "Deploying ${{ github.sha }} to staging..."
          # kubectl set image deployment/app app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          echo "Deploying ${{ github.sha }} to production..."
```

---

## §2 Caching & Optimization

### Dependency Caching
```yaml
# Node.js
- uses: actions/setup-node@v4
  with: { node-version: '20', cache: 'npm' }

# Python
- uses: actions/setup-python@v5
  with: { python-version: '3.12', cache: 'pip' }

# Ruby
- uses: ruby/setup-ruby@v1
  with: { ruby-version: '3.3', bundler-cache: true }

# .NET
- uses: actions/cache@v4
  with:
    path: ~/.nuget/packages
    key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}

# Gradle
- uses: gradle/actions/setup-gradle@v3
  with: { cache-read-only: ${{ github.ref != 'refs/heads/main' }} }
```

### Playwright Browser Caching
```yaml
- name: Cache Playwright browsers
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
- run: npx playwright install --with-deps
```

### Docker Layer Caching
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

## §3 GitLab CI — Production Pipeline

```yaml
stages: [lint, test, build, deploy]

variables:
  NODE_IMAGE: node:20-alpine
  POSTGRES_DB: testdb
  POSTGRES_PASSWORD: test

.node_cache: &node_cache
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths: [node_modules/]
    policy: pull

lint:
  stage: lint
  image: $NODE_IMAGE
  <<: *node_cache
  script:
    - npm ci
    - npm run lint
    - npm run type-check

unit:
  stage: test
  image: $NODE_IMAGE
  <<: *node_cache
  parallel: 3
  script:
    - npm ci
    - npm test -- --coverage --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.42.0
  services:
    - name: postgres:16
      alias: db
  variables:
    DATABASE_URL: postgres://postgres:test@db:5432/testdb
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths: [playwright-report/]
    expire_in: 7 days

build:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only: [main]

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: production
    url: https://myapp.com
  only: [main]
  when: manual
```

---

## §4 Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        NODE_VERSION = '20'
        DOCKER_REGISTRY = 'ghcr.io/myorg/myapp'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Quality Gates') {
            parallel {
                stage('Lint') {
                    steps { sh 'npm run lint' }
                }
                stage('Type Check') {
                    steps { sh 'npm run type-check' }
                }
                stage('Unit Tests') {
                    steps {
                        sh 'npm test -- --coverage'
                        junit 'junit.xml'
                        publishCoverage adapters: [coberturaAdapter('coverage/cobertura-coverage.xml')]
                    }
                }
            }
        }

        stage('E2E Tests') {
            steps {
                sh 'npx playwright install --with-deps chromium'
                sh 'npx playwright test'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'playwright-report/**', allowEmptyArchive: true
                }
            }
        }

        stage('Build Image') {
            when { branch 'main' }
            steps {
                sh "docker build -t ${DOCKER_REGISTRY}:${env.GIT_COMMIT} ."
                sh "docker push ${DOCKER_REGISTRY}:${env.GIT_COMMIT}"
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            input { message 'Deploy to production?' }
            steps {
                sh "kubectl set image deployment/app app=${DOCKER_REGISTRY}:${env.GIT_COMMIT}"
            }
        }
    }

    post {
        failure {
            slackSend channel: '#ci-failures',
                message: "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        always {
            cleanWs()
        }
    }
}
```

---

## §5 Quality Gates & Checks

### Branch Protection Rules
```yaml
# Required checks before merge:
# - lint
# - unit (all matrix combinations)
# - e2e (all browsers)
# - coverage threshold met

# GitHub branch protection API:
# POST /repos/{owner}/{repo}/branches/{branch}/protection
# {
#   "required_status_checks": {
#     "strict": true,
#     "contexts": ["lint", "unit", "e2e"]
#   },
#   "required_pull_request_reviews": {
#     "required_approving_review_count": 1
#   }
# }
```

### Coverage Threshold Enforcement
```yaml
# In CI job:
- name: Check coverage threshold
  run: |
    COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
    echo "Coverage: $COVERAGE%"
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "Coverage below 80% threshold!"
      exit 1
    fi
```

### PR Comment with Results
```yaml
- uses: marocchino/sticky-pull-request-comment@v2
  if: github.event_name == 'pull_request'
  with:
    message: |
      ## Test Results
      - Unit: ✅ Passed
      - E2E: ✅ Passed
      - Coverage: ${{ steps.coverage.outputs.total }}%
```

---

## §6 Secrets & Environment Management

```yaml
# GitHub encrypted secrets
deploy:
  environment:
    name: production
  env:
    API_KEY: ${{ secrets.PROD_API_KEY }}
    DB_URL: ${{ secrets.PROD_DB_URL }}
  steps:
    - name: Deploy with secrets
      run: |
        echo "Deploying with secure credentials..."
        # Secrets are masked in logs

# Environment-specific variables
# Settings → Environments → production → Add secret

# OIDC for cloud providers (no stored credentials)
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-deploy
    aws-region: us-east-1
```

---

## §7 Docker Compose for Test Services

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  app:
    build: .
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
    environment:
      DATABASE_URL: postgres://postgres:test@db:5432/testdb
      REDIS_URL: redis://redis:6379
    command: npm test

  db:
    image: postgres:16
    environment: { POSTGRES_PASSWORD: test, POSTGRES_DB: testdb }
    healthcheck:
      test: pg_isready
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7

  playwright:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on: [app]
    environment:
      BASE_URL: http://app:3000
    command: npx playwright test
    volumes:
      - ./playwright-report:/app/playwright-report
```

```bash
docker compose -f docker-compose.test.yml run --rm app
docker compose -f docker-compose.test.yml run --rm playwright
```

---

## §8 Notification & Reporting

### Slack Notifications
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ CI Failed: ${{ github.repository }} (${{ github.ref_name }})",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>*"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Test Report Publishing
```yaml
- name: Publish Test Report
  uses: dorny/test-reporter@v1
  if: always()
  with:
    name: Test Results
    path: results/junit.xml
    reporter: java-junit
    fail-on-error: false
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Cache not restoring | Key mismatch after lockfile change | Verify `hashFiles()` targets correct lockfile path |
| 2 | Service container not reachable | Wrong hostname | Use `localhost` in GitHub Actions; service alias in GitLab CI |
| 3 | E2E tests timeout in CI | Slower CI runners | Increase timeouts; use `ubuntu-latest-4-cores` for larger runner |
| 4 | Artifacts not uploading | Path doesn't exist | Use `if: always()` and verify path; check for directory creation |
| 5 | Secrets showing in logs | Echoing secret in `run` | Never echo secrets; GitHub auto-masks `${{ secrets.* }}` |
| 6 | Parallel jobs interfere | Shared database without isolation | Use unique DB per job; or serialize with `needs:` |
| 7 | Docker build slow | No layer caching | Use `cache-from: type=gha` with `docker/build-push-action` |
| 8 | `concurrency` cancels needed runs | Wrong group key | Use `${{ github.workflow }}-${{ github.ref }}` for branch-level grouping |
| 9 | Coverage report not merging | Different artifact names | Use consistent naming; merge with `download-artifact` + `merge-multiple` |
| 10 | Deploy runs on PRs | Missing `if` condition | Add `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` |

---

## §10 Best Practices Checklist

1. ✅ Run lint/type-check before tests — fail fast on obvious errors
2. ✅ Use matrix strategy for multi-version/browser testing
3. ✅ Cache dependencies aggressively (npm, pip, Docker layers)
4. ✅ Upload artifacts on failure — screenshots, reports, logs
5. ✅ Use `concurrency` to cancel redundant runs on same branch
6. ✅ Use service containers for databases and caches in test jobs
7. ✅ Set coverage thresholds as quality gates — block merge if below
8. ✅ Use environments with approval gates for production deploys
9. ✅ Use OIDC (workload identity) over stored cloud credentials
10. ✅ Notify on failure via Slack/Teams — don't notify on success
11. ✅ Use `needs:` to define job dependencies — no unnecessary parallelism
12. ✅ Pin action versions: `actions/checkout@v4` not `@main`
13. ✅ Use sharding/parallelism for large test suites: `--shard=N/total`
14. ✅ Keep pipeline under 15 minutes — optimize or split if longer
