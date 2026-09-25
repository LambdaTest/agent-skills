<!-- Read this when the agent config shows no completed onboarding (a first session). Owns the run-first rule and its detected defaults, the first-run tour (verbatim text), the first payoff's extra rows, and the three choices asked once after the first result. -->

# The first run

A person's first request should reach its first result with nothing standing in the way. The order is fixed:

1. Ready card (`references/ready-check.md`)
2. Launch line plus the tour, in one message
3. The run
4. The payoff card, with two extra rows on this first run
5. Save that the first run happened, with the defaults you used (`references/agent-config.md`)
6. The choices, asked once, as the very last thing in your turn
7. Save the answers when they arrive: in this turn, or in the person's next message

You are in a first session when the preflight's `## agent-config` section is `none`, or the file has no `onboarding.completed_at`.

## 1. Run first, ask after

Do not ask preference questions before the first result. Every choice has a default you can detect:

| Choice | Default for run one | How you know |
|---|---|---|
| Watch the browser? | Visible. Add `--headless` only when `display=no`, `ssh=yes`, or `ci` is set | Preflight `## env` |
| Where do results go? | Wherever kane-cli already points | Preflight `## settings`, shown on the ready card |
| What is this for? | Read it from the wording: "check that X works" is a one-off, "write a test for X" is a saved test | The request itself |

Ask up front only for something essential that you cannot detect: a start URL when the request names none and the preflight found no running app, or a login the flow needs. A login's secret never goes in chat: see the variables rules in `SKILL.md`.

**Launch the first run with a name**, so keeping it as a test afterwards costs nothing:

```bash
KANE_CLI_USER_AGENT=<your-runtime> kane-cli run "<objective>" --agent --name <short-slug>
```

`--name` takes letters, digits, `_` and `-`. On exit kane-cli writes `<cwd>/.testmuai/tests/<short-slug>_test.md`. If the person later says they only wanted a one-off, delete that file and its `output-<slug>/` folder.

When the preflight found the person's own app (`port=<n>`), propose the first objective against it: `http://localhost:<n>`. A result about their product lands better than a demo site.

## 2. The tour (first run only)

A run takes from 30 seconds to a few minutes, and you cannot speak while it executes. So send the tour in the same message as the launch line, right before you start the run. The person reads it while the browser works, and it costs no time.

Show the text below **as written**. Change only two things: the project name behind "the project shown above" if you need to name it, and where `← you are here` sits. Put it on **Runs** for a browser or mobile run, on **Authoring** when the first request is a saved test, and on **Assurance** when it is about requirement documents.

```markdown
While that runs, a quick tour, since this is your first time.

**What kane-cli does**
- **Runs:** you describe a goal in plain English, a real browser (or a mobile app) carries it out, and you get a pass or fail with proof. ← you are here
- **Authoring:** keep any flow as a `_test.md` file. Each step is plain English, and the file lives in your repo next to your code.
- **Replays:** the first run of a saved test records it. Every run after that replays the recording in seconds, with no AI cost. One test or a whole suite, on your machine or on the cloud grid.
- **Assurance:** start from a requirements doc instead. kane-cli extracts the use-cases, designs tests linked to each requirement, and reports what is proven and what is still owed.

**Test Manager:** every run is saved as a test case in your TestMu AI account, in the project shown above, with its screenshots and run details. Your team sees the history, and each run gets a link you can share.

**Evidence:** every run also seals an evidence pack. One file holding a screenshot of every step, a marked-up view of what was clicked, the browser's console and network logs, and a failure record if something breaks. I'll link yours when this run finishes.

Docs: [Running tests](https://github.com/LambdaTest/kane-cli/blob/main/docs/user-guide/running-tests.md) · [Saved tests](https://github.com/LambdaTest/kane-cli/blob/main/docs/user-guide/testmd/overview.md) · [Assurance](https://github.com/LambdaTest/kane-cli/blob/main/docs/user-guide/assurance/overview.md) · [Test Manager](https://github.com/LambdaTest/kane-cli/blob/main/docs/user-guide/test-manager-integration.md) · [Evidence](https://github.com/LambdaTest/kane-cli/blob/main/docs/user-guide/evidence.md)
```

Rules:

- **Once.** After showing it, record `onboarding.first_run_explained: true`. Show it again only when the person asks ("kane tour", "what can kane-cli do").
- **Honest about uploads.** The Test Manager paragraph says plainly that screenshots and run details are saved to the person's account. Do not soften or drop it.
- **Skip it** when no human is present (see `references/ready-check.md` §6).

## 3. The first payoff

Use the normal card from `references/cards.md`, and on this first run make two of the tour's ideas real:

- **📁 Evidence:** do not just offer. Start the local evidence server in the background and put the viewer link in the row (`references/evidence.md`). Add `· the proof file from the tour`.
- **🔗 Test case:** the Test Manager link from the run, plus `· saved to <project> / <folder>`.

From the second run on, the evidence viewer goes back to an offer.

## 4. Three choices, asked once, after the first result

Ask these after the first payoff card. They read as tailoring, not as a toll gate, because the person has already seen a result.

**Ask last.** The choices are the final thing in your turn: result card first, then one line saying the defaults are saved, then the choices. Put nothing after them, not even a summary, or they scroll out of sight and the person never sees them.

| # | Ask | Saved as |
|---|---|---|
| 1 | "That ran with the browser visible. Keep it that way?" Options: keep showing the window · run quietly in the background · just show me results | `preferences.watch` = `visible` · `quiet` · `results-only` |
| 2 | "Results went to <project> / <folder>. Keep it there?" Options: yes · change it (applies to every kane-cli session from now on) | Nothing here. A change goes through the flow in `references/test-manager.md`. Record only that you asked |
| 3 | "One-off checks while you code, or a saved suite you re-run?" Options: one-off checks · a saved suite · ask me each time | `preferences.purpose` = `one-off` · `suite` · `ask` |
| 4, Claude Code only | "Want to watch runs live in your status bar?" Options: turn it on (Recommended) · not now. Ask it only when `references/live-strip.md` §1 is met and it was never asked | On yes, turn the strip on. Record `strip.claude-code.offered_at` either way. It is never on by default |

How to ask:

- **Your environment has a question tool:** use it, all of them in one call, with the current value as the first option (for the live strip, the recommended option first).
- **Chat only:** one message, numbered, with the default marked on each, and say that replying "ok" keeps all three.

What the answers change:

- `watch`: `visible` means no `--headless`. `quiet` and `results-only` mean `--headless`. With `results-only`, skip the progress summary and show the card only.
- `purpose`: with `suite` or `ask`, **launch every one-off run with `--name <short-slug>`**, exactly like the first run, so it is recorded as it runs and keeping it costs nothing. `suite` means offer to keep each passing run as a saved test (and keep the first run's `<slug>_test.md`). `ask` means ask each time. If the person says no, delete that run's `<slug>_test.md` and its `output-<slug>/` folder. `one-off` means no `--name`, no offer, and remove the first run's test file. A run launched without a name cannot be kept afterwards: it would have to run again.
- Wrote "a saved suite" on the first run? Say so: `This run is kept as <slug>_test.md. Replays need no AI.`

### Save twice, so nothing depends on an answer

1. **Right after the result card, before you ask.** Write the config with `onboarding.completed_at`, `onboarding.first_run_explained: true`, `onboarding.asked: ["watch", "results", "purpose"]` (and `strip.<host>.offered_at` when you are about to ask the strip question), plus the defaults this run used: `preferences.watch` is what you ran with, `preferences.purpose` is `ask`. Tell the person in one line: `I've saved these defaults so I won't repeat the tour. Answer below to change them.` From this moment the tour and the choices never repeat, whatever happens next.
2. **When the answers arrive.** Update the preferences and write the file again.

The write is the only step that can hit a permission wall, which is why it sits after the result. If the write is refused, follow `references/agent-config.md` §4.

### When the answers do not come back in the same turn

Some hosts' question tools post the questions and hand control straight back, with no answers (Codex does this). Asking in chat works the same way. In both cases **end your turn right after the questions**. Then:

- The person's next message answers them ("ok", "1a 2c", or an option's words): save those answers, confirm in one line, and carry on.
- Their next message is about something else: keep the defaults, do the new request, and do not ask again. They can always say "kane preferences".

A question tool that does wait (Claude Code) gives you the answers in the same turn: save them straight away.

Mobile and cloud grid requests add at most one more choice, and only when you cannot detect the answer. A machine that is not an Apple Silicon Mac is never asked "local or grid": the grid is the only path, so say that instead.
