# Security

## Credentials

- Read `LT_USERNAME` and `LT_ACCESS_KEY` from environment variables or CI secrets.
- Never hardcode access keys in `hyperexecute.yaml`, shell scripts, docs, or committed `.env` files.
- Do not print secret values. Commands should reference `$LT_USERNAME` and `$LT_ACCESS_KEY` rather than embedding values.

## Job Secret Files

Use `--job-secret-file` for extra job-scoped secrets that should not appear in YAML or `--vars`.

Recommended:

- Store the file outside the repository when possible.
- If it must be inside the repo, add it to `.gitignore` and `.hyperexecuteignore`.
- Treat the file as sensitive and never commit sample real values.

## CLI Binary

Downloading the CLI crosses a binary trust boundary. Ask before download unless the user approved an autonomous HyperExecute session.

Verify the binary when security matters:

- Linux: verify signature with `openssl`.
- macOS: inspect code signing with `codesign -dvvv`.
- Windows: verify the digital signature publisher.

## Payload Hygiene

- Use `.hyperexecuteignore` to keep local secrets, large artifacts, and unrelated directories out of uploaded payloads.
- In monorepos, prefer `--target-path` to limit uploaded files.
- When using `--use-zip`, ensure `hyperexecute.yaml` is at the root of the unzipped payload.
