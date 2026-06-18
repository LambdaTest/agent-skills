# HyperExecute CLI

Use the official HyperExecute CLI for project analysis, YAML validation, job execution, and result collection.

## Download

Ask before downloading the CLI unless the user explicitly approved an autonomous HyperExecute session.

| Platform | URL |
| --- | --- |
| Linux | `https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute` |
| macOS | `https://downloads.lambdatest.com/hyperexecute/darwin/hyperexecute` |
| Windows | `https://downloads.lambdatest.com/hyperexecute/windows/hyperexecute.exe` |

After download on Linux/macOS, run `chmod u+x ./hyperexecute`.

## Verify Binary

- Linux: download the official signature and public key, then run `openssl dgst -sha256 -verify <PUBLIC_KEY_PATH> -signature <SIGNATURE_PATH> <CLI_BINARY_PATH>`.
- macOS: run `codesign -dvvv <PATH_TO_CLI>` and inspect the signer.
- Windows: open file properties, inspect Digital Signatures, and verify the publisher.

## Core Commands

```bash
./hyperexecute analyze
./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --validate
./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml
./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --verbose
```

## Useful Flags

| Flag | Use |
| --- | --- |
| `analyze` | Detect language, framework, and environment details. |
| `--validate` | Validate YAML without running tests. |
| `--config` | Point to the HyperExecute YAML file. |
| `--user`, `--key` | Pass credentials from `LT_USERNAME` and `LT_ACCESS_KEY`. |
| `--runson` | Override OS; use comma-separated values for matrix/hybrid. |
| `--concurrency` | Override concurrent sessions. |
| `--vars` | Pass non-secret runtime variables. |
| `--job-secret-file` | Pass additional job-scoped secrets. |
| `--target-path` | Upload selected payload paths. |
| `--use-zip` | Upload an existing zip payload. Ensure `hyperexecute.yaml` is at zip root. |
| `--download-logs` | Download console logs for the job. |
| `--download-artifacts` | Download framework artifacts. |
| `--download-artifacts-path` | Choose artifact download directory. |
| `--download-artifacts-zip` | Download artifacts as a zip. |
| `--download-report` | Download reports. |
| `--force-clean-artifacts` | Replace stale local artifacts with current artifacts. |
| `--auto-proxy` | Use detected system proxy settings. |
| `--scan` | Show network logs locally. |
| `--tests-per-tunnel` | Limit tests through a tunnel. |
| `--no-track` | Disable job progress tracking. |
| `update` | Update the CLI binary. |
| `completion` | Generate shell completion. |

## Quiet CI Logs

Set `CI=true` before execution when CI logs are too noisy.

## Minimal Images

On Alpine/minimal Linux images, ensure required system tools are present, commonly `libc6-compat`, `git`, and `bash`.
