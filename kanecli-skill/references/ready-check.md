<!-- Read this at the start of every session that will use kane-cli. Owns the preflight script, the ready check card (full, one-line and problem versions), which problems stop a run, the sign-in flow, and the rules for what the card may show. -->

# Ready check: preflight and the ready card

Every session that uses kane-cli starts with one preflight call and one ready card. The person sees that everything is in place before anything launches, and a missing sign-in or an empty balance shows up here with its fix instead of two minutes into a run.

## 1. Run the preflight (one command)

The skill ships a script next to this file's parent: `scripts/preflight.sh` (macOS, Linux) and `scripts/preflight.ps1` (Windows). Run it with your shell tool from the person's project directory:

```bash
sh "<skill dir>/scripts/preflight.sh"
```

```powershell
powershell -ExecutionPolicy Bypass -File "<skill dir>\scripts\preflight.ps1"
```

`<skill dir>` is the directory that holds this skill's `SKILL.md` (for example `~/.claude/skills/kane-cli`, `~/.agents/skills/kane-cli`, `~/.gemini/skills/kane-cli`). It is one short, readable command, so the person approves it once and can allow it for later sessions.

Add a flag only when the request needs it:

| Request | Flag | Extra section |
|---|---|---|
| A local mobile run | `--mobile emulator` or `--mobile simulator` | `## mobile` (device tooling readiness) |
| A cloud grid suite (`--remote`) | `--grid` | `## grid` (grid plugin readiness) |

The script only reads status. It changes nothing, takes about two seconds, and always exits `0`. If the script is missing (an older skill install), run `kane-cli whoami`, `kane-cli balance` and `kane-cli config show` yourself and build the same card.

## 2. What the script prints

Plain text in `## <section>` blocks, always in this order. Command blocks end with `exit=<code>`.

| Section | Content | What you take from it |
|---|---|---|
| `## version` | kane-cli version, or `missing` | Installed or not. Compare with the minimum version this skill notes for a feature |
| `## whoami` | The sign-in box | `Authenticated` plus `User`, `Environment`. **Ignore `Expires`**: it is a short-lived token that renews itself, never show it |
| `## balance` | `Available credits` and `Total credits` | Credits left, rounded to a whole number |
| `## settings` | Settings as JSON | `project_name`, `folder_name`, `target`, `default_url` |
| `## agent-config` | The preferences file, or `none` | See `references/agent-config.md`. `none` or no `onboarding.completed_at` means this is a first session |
| `## env` | `ci`, `ssh`, `display`, `os`, `arch`, `node` | Watch-mode default and whether a human is present |
| `## chrome` | `found=<path>` and `override=<path>` | Chrome present for local browser runs |
| `## app` | `port=<n>` per listening dev port | The person's own app is up (offer it as the start URL) |
| `## tests` | `count=<n>` saved tests nearby | Whether this folder already holds saved tests |
| `## mobile`, `## grid` | Only with the flags above | Readiness rows for those requests |

## 3. The ready card

Send the card in the same message as the launch line, so it costs no extra turn. Every card is an emoji table. Keep each cell to one short sentence.

**First session, everything in place** (no `onboarding.completed_at` in the agent config):

```markdown
| | |
|---|---|
| 🟢 **kane-cli** | Ready |
| 👤 **Signed in** | <user> |
| 💳 **Credits** | <available, whole number, with thousands separators> available |
| 🌐 **Chrome** | Found |
| 🚀 **Your app** | Running at localhost:<port> |
| 🗂️ **Results go to** | <project> / <folder> · say the word to change it, now or later |
| 👀 **This run** | Browser visible, so you can watch |
```

**Every later session, everything in place:** one line, no table.

```text
🟢 kane-cli ready · 💳 <credits> credits · 🗂️ <project> / <folder>
```

**Something is wrong:** the table again, with every problem shown at once and each failing row carrying its fix. Rows that are fine show ✅.

```markdown
| | |
|---|---|
| 🔴 **kane-cli** | Needs one thing before we start |
| 👤 **Signed in** | ❌ Not signed in. I can open the sign-in page now. Want me to? |
| 🌐 **Chrome** | ✅ Found |
```

Row rules:

- **🚀 Your app** appears only when the `app` section found a port. No row when nothing was found: never show a negative row for an optional finding. Ask for a URL only when the request lacks one.
- **🌐 Chrome** appears only for local browser runs. Skip it for mobile and cloud grid requests.
- **🗂️ Results go to** comes from `project_name` / `folder_name`. When they are empty, say `kane-cli will pick a default project on this run, and I'll tell you where it landed`. The offer to change it never stops the run. The change flow is in `references/test-manager.md`.
- **👀 This run** states the watch mode you are about to use: the saved `preferences.watch`, or the detected default (see `references/first-run.md`).
- Name the environment (for example `stage`) only when it is not production.
- For mobile or grid requests add a `📱 **Device tooling**` or `☁️ **Cloud grid**` row from the extra section.

## 4. Problems: which ones stop the run

| Problem | How you see it | Stops the run? | The fix the card offers |
|---|---|---|---|
| kane-cli not installed | `## version` is `missing` | Yes | Offer to run `npm install -g @testmuai/kane-cli` (or Homebrew) |
| Not signed in, or token not valid | `whoami` shows no `Authenticated`, or `exit` is not 0 | Yes | Sign-in flow below |
| No credits left | Available credits is 0 | Yes | Point to https://www.testmuai.com/pricing/ to pick a plan |
| Chrome missing | `found=` is empty, local browser run | Yes | Install hint for the platform, or `KANE_CLI_CHROME_PATH` for a custom location |
| Low credits | Available credits under 100 | No | One warning line on the card |
| Could not check credits | `balance` failed, sign-in is fine | No | Say `couldn't check`, then carry on |
| CLI older than this skill needs | Version below a minimum the skill notes | No | `npm install -g @testmuai/kane-cli@latest` |
| Mobile tooling or grid plugin not ready | A failing row in `## mobile` / `## grid` | Yes, for that request | The fix line the doctor output names |

When a problem stops the run, do not launch. Show the card, offer the fix, and wait.

## 5. Sign-in

- **Default:** offer to open the sign-in page, then run `kane-cli login --oauth` yourself with a generous timeout. It opens the browser, waits for the person to finish, and returns. It works without a TTY.
- **No display** (`ssh=yes`, or `display=no`): the browser cannot open here. Ask the person to run `kane-cli login` in their own terminal. In Claude Code they can type `! kane-cli login`.
- **Never ask for an access key or password in chat.** It would land in the transcript. Sign-in is the browser flow you start, or a command the person runs themselves.
- After sign-in, run the preflight again and show the card.

## 6. No human present

If `ci` is set, or your environment cannot ask the person a question (a cloud agent, headless mode), skip the card's offers and questions, use defaults, run headless, and never write the agent config. Still stop on the blocking problems above and report them plainly.
