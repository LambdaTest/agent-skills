# CI/CD Integration

Use CI secrets for `LT_USERNAME` and `LT_ACCESS_KEY`. Add a validation stage before the real job.

## GitHub Actions

```yaml
name: HyperExecute

on:
  push:
    branches: [main]
  pull_request:

jobs:
  hyperexecute:
    runs-on: ubuntu-latest
    env:
      CI: "true"
      LT_USERNAME: ${{ secrets.LT_USERNAME }}
      LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
    steps:
      - uses: actions/checkout@v4
      - name: Download HyperExecute CLI
        run: |
          curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute
          chmod u+x ./hyperexecute
      - name: Validate HyperExecute config
        run: ./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --validate
      - name: Run HyperExecute job
        run: ./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --download-logs --download-artifacts
```

## Jenkins

```groovy
pipeline {
  agent any
  environment {
    CI = 'true'
    LT_USERNAME = credentials('lt-username')
    LT_ACCESS_KEY = credentials('lt-access-key')
  }
  stages {
    stage('Download HyperExecute CLI') {
      steps {
        sh 'curl -O https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute && chmod u+x ./hyperexecute'
      }
    }
    stage('Validate HyperExecute config') {
      steps {
        sh './hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --validate'
      }
    }
    stage('Run HyperExecute job') {
      steps {
        sh './hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --download-logs --download-artifacts'
      }
    }
  }
}
```

## CI Rules

- Keep credentials in CI secrets, not YAML.
- Prefer validation before execution.
- Set `CI=true` for quieter logs.
- Download logs and artifacts on failing workflows.
- Use `--target-path` for monorepos to avoid uploading unrelated files.
