<!-- Read this when presenting the result of any kane-cli run, saved test or suite. Owns every result card: run passed, run failed, didn't start, stopped early, product bug, saved test, suite (local and cloud grid), plus the row vocabulary and the rules that keep cards consistent. -->

# Result cards

Every result is an emoji table. A one-line "Test passed" instead of the card is a bug. The ready card has its own page (`references/ready-check.md`).

## 1. Rules for every card

- **Same order every time:** verdict, task, duration, steps, credits, what happened, values or checks, links, next.
- **One short sentence per cell**, so the table holds its shape in a narrow terminal. Screenshots go under the card, never inside it.
- **Failures first.** Passing tests fold into a count and are never listed one by one.
- **➡️ Next is an offer**, not advice: two things at most, each something you can do right now.
- **Durations read like `1m 54s`** (or `21s` under a minute).
- **💳 Credits:** `<used> used · about <left> left`. `<used>` is the run's `credits_consumed`, rounded. `<left>` is the ready check balance minus what was used since: no extra call. Drop the second half when you have no balance.
- **Never show internals:** no event names, no field names, no paths the person does not own. File names they own (`checkout_test.md`, `output-checkout/`) are fine.
- **`🟡 Didn't start` is not `🔴 Failed`.** When nothing ran, say what to fix.
- **Secret-looking values never go in chat.** For a missing value whose name contains `password`, `secret`, `token` or `key`, add an empty entry to the variables file for the person to fill. Ask in chat only for plain values (a URL, a user name).
- If the run's output carried an update notice, add one quiet last line under the card: `kane-cli <version> is available.`

## 2. Run, passed

Fields: `run_end` `status`, `one_liner`, `duration`, `credits_consumed`, `summary`, `test_url`, `final_state`. Steps taken is the count of completed step lines (`done` or `failed`).

```markdown
| | |
|---|---|
| 🟢 **Result** | Passed |
| 🎯 **Task** | <one_liner> |
| ⏱️ **Duration** | <1m 54s> |
| 👣 **Steps taken** | <count> |
| 💳 **Credits** | <used> used · about <left> left |
| 📝 **What happened** | <summary, one or two sentences> |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| 🔗 **Test case** | [Open in Test Manager](<test_url>) |
| ➡️ **Next** | <offer one> · <offer two> |
```

On a first run the 📁 row carries the viewer link itself (`references/first-run.md` §3).

**If the run stored values** ("store X as 'name'"), add a second table. Leave out `url` unless the person asked for it.

```markdown
| 📦 What was found | Value |
|---|---|
| <name, humanized> | <value> |
```

**If the objective had checks** ("assert", "verify"), add one row per check:

```markdown
| ✅ Check | Result |
|---|---|
| The cart shows 1 item | Passed |
```

## 3. Run, failed

Exit code `1`, or `status: "failed"`. Show the failing step's screenshot under the card (extract it from the evidence pack, `references/debug.md`).

```markdown
| | |
|---|---|
| 🔴 **Result** | Failed at step <n> of <total> |
| 🎯 **Task** | <one_liner, or the objective in a few words> |
| ⏱️ **Duration** | <1m 12s> |
| 💳 **Credits** | <used> used |
| 📝 **What happened** | <the failing step in plain words> |
| 🔍 **Likely cause** | <your diagnosis: a popup over the button, a slow page, an auth wall, an ambiguous objective> |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| ➡️ **Next** | <a retry you can run now> · <walk through the failing step> |
```

## 4. Didn't start

Exit code `2`: nothing ran and no credits were used. Causes include missing variable values, no start URL, sign-in or setup errors, a test file that does not parse, an invalid suite plan, a cloud grid refusal.

```markdown
| | |
|---|---|
| 🟡 **Result** | Didn't start. Nothing ran, no credits used |
| ❓ **Missing** | <what is missing, by name> |
| ➡️ **Next** | <the one thing that unblocks it> |
```

Swap `❓ **Missing**` for `🔍 **Why**` when the cause is not a missing value (for example: `Two tests belong to another project, so they can't run together`). Never retry the same command unchanged.

## 5. Stopped early

Exit code `3` (timeout or cancelled).

```markdown
| | |
|---|---|
| 🟡 **Result** | Stopped after <2m 0s>, at step <n> |
| 📝 **What happened** | <what was done before it stopped> |
| ➡️ **Next** | Raise the time limit · Split the objective into two runs |
```

## 6. Possible product bug

When bug detection is on and the run confirms a product bug (`result_code` `740` with a verdict), it is its own verdict, apart from a test failure.

```markdown
| | |
|---|---|
| 🐞 **Result** | Possible product bug found |
| 📝 **What happened** | <the verdict's one-line description> |
| 🚦 **Severity** | <severity> · <confidence> confidence |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| ➡️ **Next** | File it with the evidence attached · Re-run to confirm |
```

## 7. Saved test (`testmd run`)

Fields: the summary event's step counts (`total`, `passed`, `failed`, `skipped`, plus how many steps replayed and how many were authored) and the completion event's `overall_status`, `duration_s`, `share_url`.

```markdown
| | |
|---|---|
| 🟢 **Result** | Passed · <passed> of <total> steps |
| 🧾 **Test** | <file name> |
| ⏱️ **Duration** | <21s> |
| 🔁 **How it ran** | <see below> |
| 🔗 **Share link** | [Open](<share_url>) · valid 7 days |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| ➡️ **Next** | <offer one> · <offer two> |
```

**🔁 How it ran**, from the replayed and authored counts:

| Counts | Say |
|---|---|
| All replayed | `Replayed from its recording, no AI cost` |
| All authored | `Recorded for the first time. The next run replays in seconds` |
| Both | `<r> steps replayed, <a> re-recorded because the test changed from there` |

The 🔗 row appears only when there is a share link (pure replays have none). After a first authoring run, a good ➡️ offer is: `Commit output-<stem>/ so teammates and CI replay the same recording`.

A failed saved test uses the failed-run rows (🔴 `Failed at step <n> of <total> · "<step heading>"`, 📝, 🔍) and says how many later steps were skipped. Failed replays are always investigated: read the finding from the evidence pack before you write 🔍.

## 8. Suite (`testrun run`), local or cloud grid

Fields: the summary's totals (`tests`, `passed`, `failed`, `broken`, `skipped`, `authored`), its duration, and each test's end event (`status`, `duration_s`, and on 0.8.17+ a failure reason with its step).

```markdown
| | |
|---|---|
| 🔴 **Suite** | <passed> of <tests> passed |
| ⏱️ **Duration** | <4m 44s> |
| 🧪 **Tests** | <p> passed · <f> failed · <b> broken · <s> skipped |
| 📁 **Evidence** | One pack for the whole suite · want to open it? |
| ➡️ **Next** | I can open the failed test's log and diagnose it · Re-run just that test |
```

Use 🟢 when every test passed. Then list **only** the tests that did not pass:

```markdown
| ❌ Failed test | Where | Why | Time |
|---|---|---|---|
| checkout_test.md | Step 3 | Cart total did not match | 41s |
```

On kane-cli older than 0.8.17 the end event has no reason: read it from the evidence pack, or leave `Where` and `Why` as `see evidence`.

**Cloud grid runs** add rows after 🧪:

```markdown
| 📱 **Device** | <device name> · <platform and OS version> · cloud grid |
| ☁️ **Grid job** | [Open the job](<job link>) · <build file> uploaded |
```

A test that comes back broken with zero steps on the grid was refused before it launched: say so, point to the job link, and suggest checking that the app id belongs to this account.

An invalid plan is a `🟡 Didn't start` card (§4) with one line per rejected test.
