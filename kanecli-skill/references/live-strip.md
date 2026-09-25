<!-- Read this when the person asks to watch runs live, asks about the status line, or right after a first run in Claude Code (to offer the strip). Owns what the live strip is, where it works, how it is turned on and off, and what to say about it. -->

# The live strip

While a run executes you cannot speak. In hosts with a status bar, the live strip fills that silence: one line that names the current step as it happens.

```text
◆ kane run ▸ step 7 · clicking "Add to cart"          0:42
◆ kane run ▸ step 8 · last: clicking "Add to cart"    0:47
◆ kane test ▸ step 3 "Search for headphones" · replaying   0:12
◆ kane suite ▸ 5 of 12 · 4 ✓ 1 ✗ · now: login_test.md      2:10
◆ kane run ✓ passed · 12 steps · 1:54 · 58 credits
◆ kane suite ✗ 11 of 12 · checkout_test.md failed at step 3 · 4:44
```

## 1. Where it works

| Needs | Why |
|---|---|
| **Claude Code** | The only host with a scriptable status line today. Other hosts have no strip: do not offer it there |
| **kane-cli 0.8.17 or newer** | Older versions do not write the run log the strip reads. Check the preflight's `## version` |
| **Node 18 or newer** | The strip is a small Node script. Check `node=` in the preflight's `## env` |

If any of these is missing, do not offer the strip. Nothing else changes: the strip is an extra, never a requirement.

## 2. How it behaves

- It **wraps the status line the person already has**: their line prints first, unchanged, and the kane line appears under it.
- It appears **only while a run is live, and for five minutes after it ends**. The rest of the time the person sees exactly what they had before.
- It appears **only in the Claude Code session that started the run**. Other sessions show nothing, even when they are open in the same project. The reader tells sessions apart by checking that the run descends from the same session process it was started by. A run the person starts by hand in a terminal is not shown. On Windows, where that check is not available yet, every session open in the run's project shows it.
- It reads two things kane-cli writes on its own: a small pointer file for each live run, and that run's event log. It starts no process besides the person's original status line command, makes no network calls, and sends nothing anywhere.
- **Typed text is never echoed.** A typing step shows as `typing in <field>`.
- It refreshes every two seconds. It starts showing a run once kane-cli has created the session, which takes roughly 10 to 30 seconds after launch (the browser has to start first). Until then the person sees their normal status line. While a step is still working, the line shows the last finished action, marked `last:`.

## 3. Asking for it: never on by default

The strip is **off until the person says yes**. Nothing turns it on for them: not the installer running unattended, not you. It is a recommended choice, and you ask it as one.

**When to ask.** Once, in Claude Code, in **any session** where section 1's needs are met and the agent config shows no `strip.claude-code.offered_at`. Do not tie it to the first session: onboarding is shared by every agent, so the person may have finished it in Codex or another host that has no status bar, and was never asked.

- On a first session it is the **fourth choice**, asked together with the three in `references/first-run.md` §4, right after the first result, when the person has just felt the wait.
- On any later session (onboarding done in another agent, or before the strip existed), ask it on its own after that session's first result card, as the last thing in your turn.

**How to ask.** With your question tool, recommended option first:

```text
Want to watch runs live in your status bar?
  1. Turn it on (Recommended): one line names the current step while kane-cli works. It keeps your current status line, shows only in the session that started the run, and turns off with one command. It edits ~/.claude/settings.json and keeps a backup.
  2. Not now
```

**Then.** On yes, run `strip enable` (section 4). On no, do nothing. Either way record `strip.claude-code.offered_at` in the agent config, so you never ask twice. The person can always turn it on later by asking, or with the command in section 4. If the installer already asked (it does so when run by hand in a terminal), `offered_at` is set and you do not ask again.

## 4. Turning it on and off

These commands change the person's Claude Code settings, so run them only after a clear yes. If you did not just ask the question above, tell them what will change first: `This edits ~/.claude/settings.json (a backup is kept) and adds one small script under ~/.testmuai/kaneai/bin/.`

```bash
npx @testmuai/kane-cli-skill strip enable      # turn it on
npx @testmuai/kane-cli-skill strip status      # is it on?
npx @testmuai/kane-cli-skill strip disable     # turn it off and restore the original status line
```

`enable` keeps a backup of the settings file, remembers the person's original status line, and restores it exactly on `disable`. The strip shows up in new Claude Code sessions, or after the person runs `/statusline` once or restarts.

If the person's environment blocks the command, give it to them to run in their own terminal. In Claude Code they can type `! npx @testmuai/kane-cli-skill strip enable`.

## 5. When the strip is on

Nothing about how you launch or report runs changes. Keep using one blocking call and the default output, and keep the launch line and the cards. Do not pass `--stream-members` on suites to feed the strip: it reads each test's own log by itself, and the extra output would only fill your context.
