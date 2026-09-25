<!-- Read this when the user wants to run or author a test against a mobile app (Android emulator or iOS simulator) instead of the browser. Owns mobile availability (local = macOS Apple Silicon; remote grid = any machine), the target axis, target/device/app selection on `run`, the app-under-test requirement, mobile setup (login + doctor --install), doctor flags, the testmd flat `target:` + `app:` (+ `device_name:`/`os_version:`) frontmatter keys, mobile members in testrun (local and `--remote`), and what objective grammar carries over to mobile. Desktop (browser) stays the default; this is the scoped mobile branch. -->

# Mobile testing (local on macOS Apple Silicon, or on the cloud grid from any machine)

Desktop (the browser) is the **default** target and the primary use of kane-cli. Mobile is a **scoped addition**: kane-cli can also drive a native app on a virtual Android or iOS device — on this machine, or on a LambdaTest HyperExecute macOS host via `testrun run --remote`. Nothing about web runs changes. A run with no mobile flags still drives Chrome exactly as before.

## Availability (read first)

| Where the device runs | Host | Commands |
|---|---|---|
| **Local** (a simulator/emulator on this machine) | **macOS on Apple Silicon (arm64) only** — not Intel Macs, Linux, or Windows | `run --target …`, `testmd run`, `testrun run` |
| **Cloud grid** (a virtual device on a HyperExecute macOS host) | **Any machine** — no Xcode / Android Studio needed. The account needs a HyperExecute plan with macOS runners | `testrun run <paths> --remote …` — see §Remote below |

- **Desktop stays the default.** The `--target` axis is what selects mobile. Leave it off and you get the browser.
- If the user is not on mac-arm64, local mobile is not an option — **offer the grid**: save the objective as a `_test.md` (`target: emulator|simulator` + `app:`) and run it with `kane-cli testrun run <path> --remote --device-name "<grid device>" --os-version <v>`. Do not tell them mobile is unavailable.

## The three targets

`--target` picks what the run drives:

| Target | Drives | Notes |
|---|---|---|
| `desktop` | The browser (Chrome) | **Default.** Everything in the rest of the skill applies unchanged. |
| `emulator` | A virtual **Android** device | Runs an Android app you provide. |
| `simulator` | A virtual **iOS** device | Runs an iOS app you provide. |

`emulator` = Android, `simulator` = iOS. There is no mobile-web or URL target: a mobile run always drives an **app**. (WebViews inside that app are handled, but you never point a mobile run at a website.)

## Selecting a target on `run`

```bash
kane-cli run "<objective>" --agent --target emulator --app ./builds/app-debug.apk
kane-cli run "<objective>" --agent --target simulator --app ./builds/MyApp.zip
```

| Flag | Purpose |
|---|---|
| `--target desktop\|emulator\|simulator` | Pick the target. Default is the saved session target, else `desktop`. |
| `--device-name <name>` | Which device, as `kane-cli devices list --target emulator\|simulator` prints it. Needs `--os-version`. In a TTY, omitting it opens a one-time picker whose answer is saved; in `--agent`/non-TTY runs a device must already be set (flags, `config set-device-name` + `set-os-version`, or the file's `device_name:`/`os_version:`) or the run exits 2 naming the fix. |
| `--os-version <version>` | The device's OS version (`14`, `17.5`). Alone = any device on that version. |
| `--app <path\|APPid>` | The app under test. **Required for every mobile run** (see below). |

On **desktop**, the device flags and `--app` are ignored. They only apply to `emulator`/`simulator`.

In the interactive TUI, switch with `/mobile` and `/desktop`; `/doctor` runs readiness checks. The first-run chooser offers Desktop / Emulator / Simulator. Persist defaults with `kane-cli config set-target`, `config set-device-name`, `config set-os-version`, `config set-app`. (The separate `config set-mode action|testing` is an unrelated axis: it controls auth-wall behavior, not the target.)

## The app under test: required, and its formats

Every mobile run needs an app. Provide it one of two ways:

1. **A local build** passed to `--app` (or `app:` in a `_test.md`):
   - Android (`emulator`): a `.apk`
   - iOS (`simulator`): a `.zip`
2. **An uploaded app id** from a previous upload: `APP` followed by 6 or more digits (e.g. `APP123456`).

kane-cli installs that app on the device and runs the objective against it. `kane-cli apps list --target emulator|simulator --agent` lists the account's uploads (NDJSON; the `app_id` field is what `--app`/`app:` take). There is no upload subcommand: any run with a local build — local or `--remote` — uploads it to the account (once per build; a per-machine cache skips a build the account already has) and prints the `APP…` id. Uploads belong to an organisation — `apps list` for the active profile is the authority.

**Not accepted:** a package/bundle id (e.g. `com.example.app`), a bare `.ipa`, or a `.app` bundle. There is no default app: a mobile run without a valid build or `APP…` id cannot start.

## Setup path

Two halves, and kane-cli owns the second:

1. **You provide the virtual device** (one-time, per platform):
   - **iOS:** install the full **Xcode** app (version 16 or newer). It bundles the iOS Simulator.
   - **Android:** install **Android Studio** (or the command-line SDK) and create one AVD from an **`arm64-v8a`** system image. x86/x86_64 images do not run natively on Apple Silicon.
   - You only need the platform you intend to test. Set up both if you test both.
2. **kane-cli installs its own test tooling and drives the device.** Sign in, then install:

   ```bash
   kane-cli login
   kane-cli doctor --target emulator --install     # or --target simulator
   ```

   `doctor --install` downloads the test tooling kane-cli manages. From then on kane-cli discovers the device, boots it, installs your app, and runs the test. **You do not boot the simulator or emulator by hand.** None of this is needed for `--remote` runs.

## `kane-cli doctor` and `kane-cli devices list`: readiness

`kane-cli doctor --target emulator|simulator` (the target is required) prints one line per required check, each failing row carrying its fix. Run it any time to see what is ready and what is missing.

| Command | Effect |
|---|---|
| `kane-cli doctor --target <kind>` | Readiness checks for that toolchain. |
| `kane-cli doctor --target <kind> --install` | Install or repair kane-cli's managed test tooling (the one-time setup step above). |
| `kane-cli devices list --target <kind> --agent` | The devices on this machine kane-cli can run against (name + OS version — the `--device-name`/`--os-version` vocabulary). |
| `kane-cli devices list --target <kind> --remote --agent` | The devices the **cloud grid** can provision (needs auth, not a mobile host). Add `--os-version <v>` to filter. |
| `kane-cli plugin doctor remote-execution` | Readiness for `--remote`: plugin installed, HyperExecute binary present, logged in. |

## `target:` in a `_test.md`

The `target:` frontmatter key is **one scalar**, sharing the `--target` vocabulary. Browser transports and mobile targets are the same key; the app rides beside it as its own root key:

- `chrome`, `cdp`, `ws` — the browser (desktop path).
- `emulator` (Android), `simulator` (iOS) — mobile:

  ```yaml
  ---
  target: emulator              # emulator (Android) | simulator (iOS)
  app: ./builds/app-debug.apk   # a build (.apk / .zip) or an APP… id, never a package id
  device_name: Pixel 7          # optional per-test default (local list or grid catalog vocabulary)
  os_version: "14"              # optional; --device-name / --os-version override both
  no_reset: false               # optional
  ---
  ```

  `app:` follows the same rule as `--app` and is **required** with a mobile target — and refused with a browser one; `no_reset:`, `device_name:` and `os_version:` pair with a mobile target the same way. The platform never appears in the file: `emulator` is Android, `simulator` is iOS. The nested form (`target: {platform, app}`) is not accepted — the parser refuses it and spells out this flat shape.

Everything else about `_test.md` (step bodies, replay/cascade, commands) is unchanged. See `references/testmd.md`. Run a mobile test with `kane-cli testmd run <path> --agent`.

## Mobile members in testrun (local and remote)

`kane-cli testrun run` accepts mobile `_test.md` members (0.8.7+):

- **Locally** (mac-arm64 with the setup above): `kane-cli testrun run <paths> --device-name "<name>" --os-version <v>` — the device as `kane-cli devices list --target <kind>` prints it, or the members' own `device_name:`/`os_version:`.
- **On the cloud grid, from any machine**: add `--remote` — next section. Full testrun flags, events, and rollup: `references/testrun.md`.

## Remote: mobile suites on the cloud grid (`testrun run --remote`)

One command turns a mobile suite into a HyperExecute job on a macOS host that boots the emulator/simulator, installs the app, runs the members, and returns the recordings (`output-<stem>/`) and the sealed evidence pack to the project. The user's machine needs **no** Xcode, Android Studio, or Chrome.

```bash
kane-cli plugin install remote-execution                                    # once; then `kane-cli plugin doctor remote-execution`
kane-cli devices list --target emulator --remote --agent                    # grid catalog: name + os_versions per row
kane-cli testrun run tests/app/ --remote --device-name "Pixel 7" --os-version 14 --dry-run   # validate + resolve device, no job
kane-cli testrun run tests/app/ --remote --device-name "Pixel 7" --os-version 14
kane-cli testrun run tests/ios/ --remote --device-name "iPhone 15" --os-version 17.5
```

**Always `--dry-run` first** — it runs the remote preflight and resolves the device against the catalog at no cost. Use `Bash` with a long timeout (up to 600000 ms) for the real run: device setup + app install + members take several minutes.

Rules that differ from a local run (each violation is a `remote_error` before dispatch, exit 2, with the offending paths and the fix):

| Rule | Detail | Preflight code |
|---|---|---|
| **Device comes from the grid catalog** | `--device-name` must match a `devices list … --remote` row (validated before dispatch); `--os-version` alone = any device on that version; `_test.md` `device_name:`/`os_version:` are the fallback; neither → a catalog default, reported in the `remote_device` event. **Emulator**: one device is allocated for the whole job, and a local AVD name in a file is ignored (`remote_device_hint` reason `device_name_ignored`). **Simulator**: each member binds its own `device_name:`/`os_version:` inside its task's VM (validated against the catalog); the flags, when passed, apply to every member. | — |
| **One job = one platform, one pool** | Split emulator vs simulator and web vs device into separate runs (`--match`/`--tags`). Emulator members must agree on one Android version, or force one with `--os-version`. Simulator members may ask for different iOS versions as long as their iOS majors map to one HyperExecute pool (the catalog decides; today 17 and 18 share one, 26 is another) — otherwise split, or force one with `--os-version`. | `mobile_remote_mixed_platform`, `mobile_remote_mixed`, `mobile_os_version_split`, `mobile_pool_split` |
| **App** | A local build anywhere on disk — `.apk` for an emulator, `.zip` of the `.app` for a simulator — is **uploaded from the laptop at preflight** (once per distinct file; a per-machine cache skips a build the account already has) and handed to the grid as `--app <id>`. It never rides the payload, so it may be gitignored or outside the project. An `APP…` id is used as-is. Each member gets its own id, so members naming different builds may share a run. A `.ipa` is refused (device build). `--dry-run` uploads nothing. | `mobile_app_missing`, `mobile_app_not_uploadable`, `mobile_app_upload_failed` |
| **Payload** | Members must live under the cwd being dispatched, and recordings must not be gitignored (un-ignore with `!output-*/`). Builds are not payload. | `member_outside_payload`, `gitignored_inputs` |
| **Auth** | HyperExecute needs a LambdaTest username + access key; an OAuth profile is exchanged automatically, or pass `--username`/`--access-key`. Any `APP…` id must belong to the same organisation. | `no_basic_auth` |

What to present after `testrun_done`/`remote_done`: the suite rollup (per `references/testrun.md`), the device line (name + OS from `remote_device`; for simulators the pool, and each member's own pair), each build the laptop uploaded (`remote_app` path → `app_id`), and the job link (`remote_dispatched.job_url`) for the dashboard's stage logs. If a member comes back `broken` with zero steps, the grid-side run refused before launching — check the app id belongs to this account (`apps list` for the active profile) and the job's scenario log at the job link.

## What works on mobile

The **same natural-language objective grammar** applies (`references/objectives-cookbook.md`): action verbs, assertions, extractions ("store as"), if/else, chaining, and variables all carry over. A mobile run just drives an app instead of a page.

Mobile capability depends on the platform and app. The implementation includes native network operations and Android cookie/storage access for visible Chrome or debuggable WebViews. This does not establish full desktop DevTools parity, general native DOM support, or equivalent iOS support. Verify device/app prerequisites and the specific checkpoint before relying on it; live platform parity remains unverified.

Write mobile objectives around what the app shows and does (open a screen, tap, type, assert visible text/state, store a value). And never point a mobile run at a URL: a mobile run drives an app, not a website.

In the interactive TUI, `/mobile` and `/desktop` can switch targets before the first dispatch. The target locks after dispatch; use `/new` to start a new session before switching.
