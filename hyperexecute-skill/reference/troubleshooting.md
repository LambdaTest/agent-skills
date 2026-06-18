# Troubleshooting

Debug one failure class at a time. Prefer official CLI validation before cloud execution.

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| CLI not executable | Missing execute bit | Run `chmod u+x ./hyperexecute`. |
| macOS blocks CLI | Gatekeeper/security prompt | Allow the binary in Security & Privacy, then retry. |
| Alpine/minimal image fails | Missing system libraries/tools | Install `libc6-compat`, `git`, and `bash`. |
| Credentials missing | Env/CI secrets absent | Export `LT_USERNAME` and `LT_ACCESS_KEY` or configure CI secrets. |
| YAML validation fails | Missing/invalid YAML fields | Check `version`, `runson`, and either `testSuites` or `testDiscovery` plus `testRunnerCommand`. |
| No tests discovered | Discovery command returns empty | Run the discovery command locally and fix paths/globs. |
| Browser not found | Browser install missing | Add Playwright/Cypress browser install commands to `pre`. |
| Payload cannot find config | Bad zip layout | Put `hyperexecute.yaml` at the root of the zip payload. |
| Proxy/network failure | Corporate proxy/firewall | Try `--auto-proxy`, `--scan`, or tunnel/proxy options. |
| Artifacts missing | Wrong upload/download paths | Verify framework output paths and `uploadArtefacts` globs. |
| Logs too noisy in CI | Normal CLI progress output | Set `CI=true`. |
| Matrix too large | Cross-product explosion | Reduce dimensions or use narrower configs. |
| Autosplit uneven | Large test files or poor discovery unit | Split large files or use finer discovery units. |

## Debug Loop

1. Run `node scripts/doctor.js --config hyperexecute.yaml`.
2. Run `node scripts/validate-config.js hyperexecute.yaml`.
3. Run official validation with `--validate`.
4. Re-run with `--verbose` only when extra logs are useful.
5. Download logs/artifacts/reports after a real job failure.
6. Fix the smallest likely cause and retry only after validation passes.
