<!-- Read this for the Test Manager (TMS) agent surface — what gets uploaded, where the run lands, the `projects` / `folders` subcommands and their NDJSON wire shape, and the run-startup auto-default event. Non-TTY surface only; the human config flow / interactive picker lives in the public user guide. -->

# Test Manager Reference — Agent Surface

Every kane-cli session uploads to a TestmuAI **Test Manager (TMS)** test case. The session lands inside a **project** (required) and optionally a **folder** inside that project. This page is the agent-facing surface for everything that touches TMS: where the run ends up, how to browse and create projects/folders programmatically, and the event the run-startup gate emits when nothing is configured.

Field names below are for parsing only — translate to plain language for the user, per the §5 rule in `SKILL.md`.

---

## 1. Where a run lands

After a successful upload, the terminal `run_end` event (`testmd_done` for `testmd run`) carries the dashboard link:

```json
{"type":"run_end","status":"passed", "test_url":"https://test-manager.lambdatest.com/projects/<id>/test-cases/<id>", ...}
```

For `testmd run`, the `test_md_summary` / `test_md_done` events also carry a `share_url` — a 7-day, no-login link suitable for CI artifacts.

Surface `test_url` (and `share_url` when present) as a "View in Test Manager" line per the §1.4 results table in `SKILL.md`. Never paste raw URLs into the middle of a summary — they belong in the results table.

**Replays publish evidence, not uploads.** A pure replay of an authored `testmd` test skips the upload pipeline (and skips the project/folder gate entirely — no `project_folder_auto_defaulted` event fires for it), but its sealed evidence pack still publishes to the test's own project automatically (`test_md_evidence_ingest` event, informational). The dashboard therefore shows execution history even for cache-replayed runs. `testrun` executions publish one pack for the whole batch the same way.

---

## 2. Projects & folders — selecting where uploads land

Two ways an agent influences placement:

- **Programmatically**, via the `projects` / `folders` subcommands (§3 + §4) — list, search, create, then persist with `kane-cli config project <id>` / `kane-cli config folder <id>`.
- **Passively**, by observing the `project_folder_auto_defaulted` event the run-startup gate emits when nothing is configured (§5).

In a non-TTY context (CI, pipes, every `--agent` caller), the no-arg form of `config project` / `config folder` will not prompt — always pass an explicit `<id>`. The interactive picker is the human-facing path and is documented in the user guide.

---

## 3. Listing — `projects list` / `folders list`

```bash
kane-cli projects list [--search <q>] [--limit <n>] [--offset <n>] --agent
kane-cli folders  list --project <id> [--search <q>] [--limit <n>] [--offset <n>] --agent
```

| Flag | Purpose |
|---|---|
| `--search <q>` | Filter by name (substring match). |
| `--limit <n>` | Page size. Default is small (~10). Very large values are capped. |
| `--offset <n>` | Skip the first N rows. |
| `--agent` | Force NDJSON. Auto-on when stdout is piped/redirected, but pass it explicitly anyway. |

`folders list` and `folders create` need the project passed in: `--project <id>` is **required** on both. Take the id from `projects list`, or from `project_id` in `kane-cli config show`.

### Wire shape

Each result line:

```json
{"id":"01J69X773TSY9TCHZY4VAT9VBH","name":"KaneAI Generated"}
```

Just `id` + `name`. The terminal line on every page:

```json
{"_meta":"page","limit":10,"offset":0,"returned":10,"has_more":true}
```

| Field | Meaning |
|---|---|
| `_meta: "page"` | Discriminator — distinguishes pagination metadata from a result row. Skip when collecting results. |
| `limit` / `offset` | Echoed from the request. |
| `returned` | Number of result rows on this page (≤ `limit`). |
| `has_more` | `true` if another page exists. There is no `total` — only a "more remaining" signal, so don't promise an exact count to the user. |

### Pagination idiom

```bash
offset=0; limit=10
while :; do
  page=$(kane-cli projects list --limit "$limit" --offset "$offset" --agent)
  echo "$page" | jq -c 'select(._meta != "page")'    # result rows
  more=$(echo "$page" | jq -r 'select(._meta == "page") | .has_more')
  [ "$more" = "true" ] || break
  offset=$((offset + limit))
done
```

Same pattern for `folders list`.

---

## 4. Creating — `projects create` / `folders create`

```bash
kane-cli projects create "<name>" [--description "<text>"] --agent
kane-cli folders  create "<name>" --project <id> [--description "<text>"] --agent
```

NDJSON: one line describing the new id + name. `folders create` files the folder inside the project you pass with `--project <id>`.

To use the result for subsequent runs, persist with `kane-cli config project <id>` / `kane-cli config folder <id>` — non-interactive when called with an explicit `<id>`.

---

## 5. The run-startup auto-default event

`kane-cli run`, `kane-cli testmd run`, and `kane-cli generate` all validate the cached project/folder before launching anything. Three outcomes:

1. **Cached project/folder still valid** → run proceeds. No event.
2. **Nothing configured, or the cached IDs are gone / inaccessible** → kane-cli resolves a sensible project/folder headlessly (find-or-create), then emits a typed event before the run starts:

   ```
   {"type": "project_folder_auto_defaulted", ...}
   ```

   The event carries the resolved project + folder so the caller knows what was picked. Translate it for the human user — for example:

   > kane-cli auto-selected project **<name>** / folder **<name>** for this run.

   Don't surface raw field names.

3. **No usable credentials in a non-TTY context** → exit code `2` with an auth/setup error.

### Self-healing for stale IDs

If a previously-configured project/folder becomes unusable (deleted, renamed, access revoked, or a typo was saved as the ID), TMS returns a `4xx` for the validation call and the gate treats both as **missing** — it clears the stale value and re-resolves via auto-default. The run is not aborted for this.

Transient validation failures (`5xx`, network, timeout) are treated as **error** and the gate fails open with the cached IDs so brief upstream hiccups don't block a run.

### When you see the event

Surface it as a one-line note, then continue parsing the run normally. If the user wants their runs in a different project, walk them through §6.

---

## 6. Changing where results go (a global setting)

The results project and folder belong to kane-cli, not to the agent config. A change applies to **every later kane-cli session for the current sign-in**: every project folder, every agent, and the terminal. Say so in the question itself, so the person's pick is their consent and no second confirmation is needed.

**When to raise it.** The ready card always states the location with a standing offer that never stops the run (`references/ready-check.md`). Ask outright only once, after the first result (`references/first-run.md` §4), or whenever the person says "change project".

**The flow.** Listing projects takes a few seconds, so do it only now, never in the preflight.

1. `kane-cli projects list --limit 10 --agent`. Show the names with the current one marked. If the page says more exist, offer a search by name (`--search <text>`) instead of paging. Never promise a count: the CLI only says whether more exist.
2. Let the person pick one, search, create a new one, or keep the current one. For a new project suggest the repo's name: `kane-cli projects create "<name>" --agent`.
3. `kane-cli folders list --project <id> --agent`. Exactly one folder: take it without asking. Otherwise let them pick, or create one with `kane-cli folders create "<name>" --project <id> --agent`.
4. Save the project first, then the folder, always as a pair, so the two never mismatch:

   ```bash
   kane-cli config project <project-id>
   kane-cli config folder <folder-id>
   ```

5. Confirm in one line: `Results now go to <project> / <folder>, for every kane-cli session from here on.`
6. In the agent config record only that you asked (`"results"` in `onboarding.asked`). The value stays with kane-cli.

**Before switching, warn when it matters.** If the preflight's `## tests` section found saved tests in this folder, say first: cloud grid suites compare each test's project with the configured one and refuse on a mismatch, so switching can make an existing grid suite refuse until it is switched back. Tests that already ran keep their original project.

**Always visible.** The one-line ready card shows the location at the start of every session, so a global setting never surprises anyone.

---

## 7. Exit codes (TMS subcommands only)

| Code | Meaning |
|---|---|
| 0 | OK |
| 2 | Auth/setup error (missing or invalid credentials) or unknown subcommand |

Other codes are run-specific (`run` / `testmd run` / `generate`) and don't apply to `projects` / `folders`.
