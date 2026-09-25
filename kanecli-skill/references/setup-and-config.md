<!-- Read this for first-time install, auth flows (basic / OAuth / interactive), config commands, full variables precedence chain, global/local context files, the Chrome management notes, and the ~/.testmuai directory layout. Rarely needed once a user is set up. -->

# kane-cli Setup, Variables, and Config Reference

## Install and auth

Before first use, verify installation and auth.

> **Local mobile setup (macOS Apple Silicon)** is separate: install Xcode 16+ (iOS) or Android Studio with one `arm64-v8a` AVD (Android), then `kane-cli login` and `kane-cli doctor --target emulator|simulator --install` (installs kane-cli's managed test tooling); `kane-cli doctor --target <kind>` checks readiness. Not needed for `testrun run --remote`, which runs mobile suites on the cloud grid from any machine (see §Remote execution plugin). Read `references/mobile.md`.

### Install

```bash
npm install -g @testmuai/kane-cli
```

### Check Auth Status

The preflight script covers this along with credits and settings in one call (`references/ready-check.md`). On its own:

```bash
kane-cli whoami
```

`whoami` prints a box, not JSON, even when piped. Its `Expires` line is a short-lived token that renews itself: never show it to the person.

If this shows "not configured" or errors, run login:

### Login (Basic Auth)

```bash
kane-cli login --username <user> --access-key <key>
```

This creates the default profile with basic auth, auto-selects the KaneAI project, and marks setup complete. Credentials come from the user's TestmuAI dashboard (Settings → Keys).

Optional flag:
- `--profile <name>` — profile name (default: last selected profile check using `config show`)

### Login (OAuth)

```bash
kane-cli login --oauth
```

This opens the browser for OAuth consent and waits for the callback. Works in both TTY and non-TTY (agent) mode.

**This is the sign-in you run for the person.** Offer to open the sign-in page, then run the command yourself with a generous timeout: it returns once they finish in the browser. When there is no display (an SSH session, a container), ask them to run `kane-cli login` in their own terminal instead. **Never ask for an access key or password in chat**: it would land in the transcript. The full flow is in `references/ready-check.md` §5.

### Login (Interactive — TTY only)

In a terminal, run `kane-cli login` with no flags for the interactive wizard (auth method → project picker → folder picker). If the user needs this, ask them to run it directly:

> Please run `! kane-cli login` and complete the sign-in.

### Verify

```bash
kane-cli whoami          # Auth status
kane-cli config show     # Current configuration
```

## Variables — full precedence chain

Variables parameterize objectives with reusable values and secrets. Use `{{key}}` syntax in objectives.

**Format:**
```json
{
  "username": { "value": "alice", "secret": false },
  "password": { "value": "s3cret!", "secret": true }
}
```

`secret: true` masks the value in logs and routes it to TestmuAI's secrets store instead of being synced as plain TMS variables.

**Loading order** (later wins):
1. `~/.testmuai/kaneai/variables/*.json` (global, alphabetical)
2. `{cwd}/.testmuai/variables/*.json` (local project overrides)
3. `--variables-file <path>`
4. `--variables '{...}'` (inline JSON)

**Values (0.8.12+):** a string is a value when non-empty; a number is accepted and loaded as its string; a boolean, object or array is not a value. An empty `value` is a declared-but-unfilled key.

**Before a run (0.8.12+):** every `{{name}}` an authored step references must have a value — `run`, `testmd run` and `testrun run` refuse before launching anything otherwise (exit `2`; with `--agent`, one `error` event with `code: "unresolved_variables"` — SKILL.md §3). No bypass flag.

**`assurance.json`:** `kane-cli design tests` writes empty stubs (`{"name":{"value":"","secret":false,"description":"…"}}`) into `{cwd}/.testmuai/variables/assurance.json` for every variable it declares, never a value, and never over a key that already exists in any pool file. Fill those before authoring the designed tests.

**Always parameterize:** credentials, API keys, tokens, environment-specific URLs.
**OK to hardcode:** one-off URLs, static UI text, navigation paths.

## Context files

Context files provide additional instructions to the agent:
- **Global:** `~/.testmuai/kaneai/global-memory.md` — shared across all runs
- **Local:** `.testmuai/context.md` in cwd — project-specific

Override per-run with `--global-context` / `--local-context` flags.

## Config commands

```bash
kane-cli config show                          # Show all current settings (includes default_url)
kane-cli config set-window <W>x<H>           # Browser window size (e.g. 1920x1080)
kane-cli config set-url <url>                 # Default start URL (bare domains get https://; used when --url / test.md url: is absent)
kane-cli config set-bug-detection <mode>      # off | stop | continue (default off) — flag product bugs while authoring; per-run --bug-detection overrides
kane-cli config chrome-profile <path>         # Chrome profile path (or interactive picker in TTY)
kane-cli config project <project-id>          # TMS project ID (or interactive picker in TTY)
kane-cli config folder <folder-id>            # TMS folder ID (or interactive picker in TTY)
```

**Start URL resolution** (first match wins): `--url <url>` flag → (test.md only) `url:` frontmatter → config `default_url`. The built-in playground default counts as "unset". With none of these set, the agent uses a site named in the objective; if nothing supplies a URL, a TTY run asks and a non-TTY run fails — pass `--allow-missing-url` to a non-TTY run to start from the current page instead.

> **Project / folder management — Read `references/test-manager.md`** for the full agent surface: `kane-cli projects list|create` and `kane-cli folders list|create` (with `--search` / `--limit` / `--offset` / `--description`), the NDJSON wire shape for `--agent` callers, and the `project_folder_auto_defaulted` event the run-startup gate emits when nothing is configured.

### Feedback

Submit feedback on a completed test run:
```bash
kane-cli feedback --test-id <id> --feedback-type <positive|negative> --details "..."
```

## Directory structure

```text
~/.testmuai/kaneai/
├── tui-config.json              # Persistent CLI settings
├── config.json                  # Shared auth configuration
├── global-memory.md             # Global agent context
├── chrome-profile/              # Default Chrome user profile
├── profiles/                    # Stored credentials
│   └── {profile}/{env}/
│       └── credentials
├── sessions/                    # Session history
│   └── {session-id}/
│       ├── session.json         # Metadata, run list, upload status
│       ├── tui.log              # Session event log
│       ├── evidence/            # Sealed evidence pack — the ONLY home of run logs,
│       │                        #   actions, screenshots (see references/evidence.md)
│       └── code-export/         # (when --code-export) generated code files
└── variables/                   # Global variable files
    └── *.json

# Project-local overrides (in cwd):
.testmuai/
├── context.md                   # Project-specific agent context
├── evidence/                    # Sealed evidence packs for saved runs — do NOT commit
│   └── *.evidence
└── variables/
    └── *.json                   # Project-specific variables
```

Debugging env var: `KANE_TESTRUN_MEMBER_DEBUG=1` routes `testrun` members' otherwise-silent output to stderr (`[member]` prefix).

## Remote execution plugin (`testrun run --remote`)

`--remote` dispatches a `testrun` suite to LambdaTest HyperExecute — a grid browser for web members, a grid Android emulator / iOS simulator (on a macOS host) for mobile members, so mobile suites run **from any machine**. One-time setup, then readiness:

```bash
kane-cli plugin install remote-execution      # installs the plugin + the HyperExecute binary it owns
kane-cli plugin doctor remote-execution       # NDJSON checks: installed, binary-present, logged-in
kane-cli plugin list                          # {"type":"plugin_list","plugins":[{"name":"remote-execution",...}]}
kane-cli devices list --target emulator --remote --agent    # grid device catalog (name + os_versions); --os-version <v> filters
kane-cli apps list --target simulator --agent               # the account's uploaded builds (app_id is what app:/--app take)
```

Requirements: a LambdaTest plan with HyperExecute (macOS runners for mobile members); a LambdaTest username + access key (an OAuth profile is exchanged automatically; or `--username`/`--access-key`); any `APP…` id must belong to the same organisation. Runs are dispatched from the **cwd** (it becomes the payload; `.gitignore` is respected). Full flags, events, and refusal codes: `references/testrun.md` §Remote; mobile rules: `references/mobile.md` §Remote.

## Chrome management

kane-cli auto-launches Chrome with CDP (DevTools Protocol) on ports 9222–9230. Chrome runs as a detached process and outlives the CLI.

- `--headless` — runs Chrome in headless mode (no visible window)
- `--cdp-endpoint <url>` — connect to an already-running Chrome instance
- `--ws-endpoint <url>` — connect to a remote browser (LambdaTest grid)

If Chrome fails to launch, ensure Google Chrome is installed and no other process is using CDP ports 9222–9230.

### Chrome environment variables

Read from the process environment (not `tui-config.json`) — handy for CI:

| Variable | Effect |
|---|---|
| `KANE_CLI_CHROME_PATH` | Absolute path to the Chrome binary, for non-standard installs. |
| `KANE_CLI_SKIP_BROWSER_DOWNLOAD` | Truthy (`1`/`true`/`yes`) skips the Chrome-availability startup check; uses whatever `chrome` is on PATH. |
| `KANE_CLI_CDP_TIMEOUT_MS` | Per-attempt CDP readiness timeout in ms (default `30000`). Raise on slow/cold CI runners. |
| `KANE_CLI_CDP_RETRIES` | Extra Chrome launch attempts after the first on a CDP-readiness failure (default `2`; `0` = single attempt). |

CDP timeout/retries only help with transient startup slowness — a missing or invalid binary fails immediately without retrying.
