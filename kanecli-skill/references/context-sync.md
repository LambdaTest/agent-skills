<!-- kane-cli skill reference: context sync (share the .context/ store with a team through a location; publishing, taking teammates' records, cloning, the rebase walk and its decisions). Read when the user wants to share the context store, join a teammate's, keep two stores level, or resolve a sync conflict. Requires kane-cli 0.8.14+. -->

# Context sync — Agent Surface

The assurance store (`.context/`, `references/assurance.md` §8) is one person's. **Context sync** shares it with a team through a **location**: a GitHub repository, an S3-compatible bucket, or a folder. Each person keeps their own store and publishes to the location; nothing on a location is ever overwritten or deleted. Reach for this reference when the user wants to share their context store, join a teammate's, get two stores level, or resolve a sync conflict. Sync never calls the KaneAI service — no credits, no model.

**Version gate.** `kane-cli context sync`, `kane-cli context push`, `kane-cli context pull` and `kane-cli context clone` exist on **kane-cli 0.8.14 and later**. On an older CLI they fail as an *unknown command* (exit 2, a "did you mean" line) — the CLI is too old, not a typo. Confirm with `kane-cli --version`, have the user update, stop.

## 1. Vocabulary — use these words

| Word | Means |
|---|---|
| **store** | the `.context/` directory on one machine |
| **location** | where a store is shared through — a GitHub repository, an S3-compatible bucket, or a folder. Bound to a store under a **name** (`origin`, `team`) |
| **local** | this store's side of anything |
| **the location's name** | the other side: "`origin`'s version", "`team` has 3 records you have not pulled". The two sides of every decision are **local** and the location's name |
| **record N** | the Nth record of the shared history. The CLI prints `position N` for it; say "record N" |
| **level** | local and the location hold the same records |
| **rebase** | both sides added work after the last shared record: the local records are saved, the location's are taken, the saved ones are reapplied on top — a real disagreement becomes a **decision** |
| **can publish / download only** | what a location allows this account. In the events, `tier` `1` = can publish; `2` or `3` = clone and pull only |

## 2. Commands

Every command takes `--mode agent` (NDJSON, stderr byte-empty, `done` last). `[name]` defaults to the only location; with several, to the one called `origin`; otherwise the command refuses and asks for a name.

| Command | Does |
|---|---|
| `kane-cli context sync setup` | guided Share / Join — **terminal only**; under `--mode agent` refuses `TTY_REQUIRED`. Never run it from an agent: `kane-cli context sync add` shares, `kane-cli context clone` joins |
| `kane-cli context sync add <name> <location>` | checks the location and binds this store to it. S3 keys: `--credential-env <VAR>` (reads `$VAR_ID`, `$VAR_SECRET`) or `--credential-file <path>` (a JSON file: `{"accessKeyId":"<id>","secretAccessKey":"<secret>"}`); GitHub: the user's existing Git sign-in, or `KANE_SYNC_GIT_TOKEN` in CI. Keys are saved under the *name* (`~/.testmuai/kaneai/context-sync/<name>.json`) and shared by every store on the machine that uses that name. Re-running with the same name replaces the address, and the saved keys only when new ones are passed |
| `kane-cli context sync list` | the bound locations |
| `kane-cli context sync remove <name>` | forget a location; for an S3 location its saved key pair is deleted too |
| `kane-cli context sync status [name]` | how local stands against the location + the open decisions; `--show <n>` prints one saved record in full. **Never writes** — safe any time |
| `kane-cli context sync doctor` | every rebase with its id and state; `--abort` undoes a rebase interrupted before its import, otherwise closes the open rebase; `--export <dir> [--from <rebase-id>]` builds the pre-rebase store beside (default: the open rebase, else the only one) |
| `kane-cli context push [name]` | publishes local records the location lacks; refuses when the location has records local has not pulled |
| `kane-cli context pull [name]` | takes the location's new records; finishes an open rebase first; `--rebase --yes` starts one when the sides diverged. Never pushes |
| `kane-cli context sync [name]` | finish an open rebase, pull, then push — the everyday command |
| `kane-cli context clone <location> [dir]` | creates a new store in `dir` (default: the location's last name part) from a location, bound as `origin`; takes the same `--credential-env` / `--credential-file` as `kane-cli context sync add` |
| `--answer <id>=<choice>` | on `kane-cli context sync` and `kane-cli context pull` only: answers one open decision headless (§5); repeatable |

Location forms: `https://github.com/<owner>/<repo>.git` or `git@github.com:<owner>/<repo>.git` (optional `?prefix=<path>#<branch>`); `s3://<bucket>/<prefix>?endpoint=<https://host:port>&region=<region>` (`endpoint` only for a non-AWS service); a folder path.

## 3. The stream — the minimum an agent parses

Envelope `{"type":…,"v":1,"verb":"sync",…}`; a write verb refused by the fence stamps its own name (`"verb":"name"`). **The vocabulary is open — tolerate unknown event types and fields, never fail on them.** Events not listed (`sync_locations`, `sync_removed`, `sync_rebase_item`, `gitignore_updated`, …) are informational — summarize or ignore. Two are not: a `warning{message}` (a `.gitignore` that could not be written, a lifecycle note) is relayed to the user, and `sync_doctor` after `kane-cli context sync doctor --abort` carries `aborted` and a `detail` that names the next step (§4).

| type | fields | handle |
|---|---|---|
| `sync_probe_started` | `name`, `kind` (`git`/`s3`/`dir`) | "checking `<name>`…" — a first GitHub check can take minutes |
| `sync_probe` | `name`, `kind`, `tier` (1 = can publish; 2/3 = download only), `detail` | one line: bound, and whether it can publish |
| `sync_status` | `name`, `relation{kind, local, storage, at?}` — `local` and `storage` are `{seq, hash}` of that side's last record, or null when that side is empty; `at` (only on `diverged`) is the first record where the sides differ, so the last shared record is `at - 1`; `rebase_id` (or null); `decisions[]` (each a `sync_rebase_decision` payload); with `--show <n>`: `record[]` (the record in full, as lines) + `decision` (or null), and `name`/`relation` are then null | translate `relation.kind`: `up-to-date` · `behind` (pull) · `ahead` (push) · `diverged` (rebase) · `empty-storage` (push first) · `empty-local` · `foreign-lineage` (a different history — clone it instead) |
| `sync_pull_done` | `name`, `imported`, `from`, `to`, `blobs`, `proposals`; `clone` adds `dir` | "pulled N records from `<name>`" |
| `sync_push_done` | `name`, `from`, `to`, `pushed`, `blobs`, `proposals`, `already_there` | "published N records to `<name>`" |
| `sync_rebase_started` | `name`, `rebase_id`, `from`, `backup_path`, `moved[]`, `quarantined_tests[]` | "N local records saved; taking `<name>`'s version, then reapplying" |
| `sync_rebase_decision` | `rebase_id`, `decision_id` (`h<n>`), `kind`, `intent`, `seq`, `label`, `location`, `mine`, `theirs`, `answers[{answer, consequence}]` | THE deliverable when paused — one per open decision, all emitted before the walk stops (§5) |
| `sync_rebase_done` | `rebase_id`, `reapplied`, `already_present`, `not_reapplied`, `decisions_open`, `status` (`complete`/`paused`/`aborted`) | the walk's summary; `kane-cli context sync doctor --abort` emits it too, with `aborted`, when it closes a readable rebase |
| `sync_rebase_open` | `rebase_id`, `decisions_open`, `pending` | a push met an open rebase; a `sync_error` follows |
| `sync_behind` | `name`, `local_seq`, `storage_seq`, `text` | rides `kane-cli context extract`, `kane-cli design tests`, `kane-cli maintain reconcile` streams: `<name>` has records local has not pulled. One advisory line, not a failure |
| `sync_error` | `code` (§6), `detail`, `remedy`, `diagnostic?` | a sync refusal — always carries the code; map it; offer `remedy` verbatim |
| `error` | `message`, with optional `code` (`USAGE`, `MODE_USAGE`, `CREDENTIALS_MISSING`, `TTY_REQUIRED`) and `remedy`; a message-only event is either a refusal (a missing store) or a runtime failure | `done.exit_code` tells them apart: `2` = a refusal — fix the command line, never retry unchanged; `1` = a failure — do not retry blindly. Relay `message`, and `remedy` when present |
| `done` | `status` (`complete` 0 · `refused` 2 or 3 · `paused` 3 · `interrupted` 130 · `error` 1), `exit_code` | **always last** — build post-run logic on it. `paused` = decisions are waiting: after a walk the rebase is open; after `kane-cli context sync doctor --abort` it is closed and the unanswered decisions stayed in the backup — the `sync_rebase_done` before it says which. No `sync_rebase_done` before it means doctor set aside a rebase it could not read: `sync_doctor.detail` says the backup is reapplied by the next `kane-cli context sync` — relay it |

Captured shapes (real runs):

```json
{"type":"sync_error","v":1,"verb":"sync","code":"SYNC_DIVERGED","detail":"you and origin both added work after position 2; nothing was pushed","remedy":"run kane-cli context pull origin --rebase to save your local work, take the team version from origin, and then reapply yours"}
{"type":"sync_rebase_decision","v":1,"verb":"sync","rebase_id":"2026-09-14T10-47-54-074Z-reset","decision_id":"h3","kind":"slug","intent":"names","seq":3,"label":"names spec","location":"origin","mine":"named prd \"spec\" at 2026-09-14T10:47:50.866Z","theirs":"\"spec\" names brief on origin (by bob at 2026-09-14T10:47:47.857Z)","answers":[{"answer":"keep-theirs","consequence":"the local change stays in the backup"},{"answer":"apply-mine","consequence":"the name moves to the local node; the node that holds it on origin is reached by its id again"}]}
{"type":"done","v":1,"verb":"sync","status":"paused","exit_code":3}
```

## 4. Exit codes (these verbs only)

| Code | Meaning |
|---|---|
| `0` | complete |
| `2` | refused — usage, credentials, no terminal, a precondition (`SYNC_REBASE_PENDING`, `SYNC_READ_ONLY`, `SYNC_LOCATION_*`, `SYNC_GIT_REQUIRED`, `SYNC_LOCAL_BLOB_CORRUPT`, …), or a publication whose outcome is unknown (`SYNC_PUBLICATION_UNKNOWN`) |
| `3` | **a decision or a pull is needed — not a failure.** `SYNC_BEHIND` / `SYNC_DIVERGED` / `SYNC_POSITION_TAKEN` / `SYNC_LOCAL_MOVED` refusals, `done{paused}` from a walk with decisions open, and `kane-cli context sync doctor --abort` that left decisions unresolved |
| `1` | a failure: a record that cannot be used (`SYNC_REMOTE_CHAIN_BROKEN` or `SYNC_OBJECT_CORRUPT` on the location, `SYNC_LOCAL_RECORD_CORRUPT` in this store — a person has to look), or a runtime error reported as `error{message}` |
| `130` | interrupted; the rebase state is on disk — `kane-cli context sync doctor --mode agent` shows it, and the next `kane-cli context sync` or `kane-cli context pull` resumes the rebase. No `session_paused` is involved |

A nonzero exit says what stopped, not that nothing happened: `kane-cli context sync` finishes its pull before its push can be refused, and a push can land before its confirmation is lost. The events before the `sync_error` say what completed; its `detail` says what did not.

## 5. Decisions — how to answer

A rebase starts only with `kane-cli context pull <name> --rebase --yes --mode agent`, and only on the user's explicit instruction (without a terminal `--yes` is required — otherwise `SYNC_DIVERGED` with that exact line as the `remedy`). The walk reapplies what it can, emits one `sync_rebase_decision` per real disagreement, then `sync_rebase_done{paused}` + `done{paused}`, exit 3. The rebase stays **open** until every decision is answered or it is aborted.

- **One decision at a time, never guess.** Present each card in plain words: what local did (`mine`), what `<name>` holds (`theirs`), the offered answers with their `consequence`. If the user's instruction clearly settles it, answer; otherwise ask. Never pass an answer the card did not offer.
- **Answer by id**, only with an answer from that card's `answers[]`: `kane-cli context sync <name> --answer h3=keep-theirs --mode agent` (repeatable; also on `kane-cli context pull`). `keep-theirs` writes nothing — the local change stays in the backup, and a later saved record built on it is looked at again; `apply-mine` lands the local version on top of the location's; `apply-mine-as-new` (offered only for newly created items) adds the local content as a new item.
- **Some cards offer only `keep-theirs`**: a record this build cannot read or replay, one that refers to an item the location no longer has, or one the store's own checks refuse. Tell the user that piece of work stays in the backup and has to be done again after the rebase.
- After an answer the stream re-emits the decisions still open and `done{paused}` again. When the last one lands, on `kane-cli context sync`: `sync_rebase_done{complete}` → `sync_pull_done` → `sync_push_done` → `done{complete}`; on `kane-cli context pull`: `sync_rebase_done{complete}` → `sync_pull_done` → `done{complete}` — pull never pushes, so publish afterwards with `kane-cli context push` or `kane-cli context sync`.
- **Decide later** = do not answer; the rebase stays open. `kane-cli context sync status <name> --mode agent` lists the open decisions whenever the location can be reached (when it cannot, the command refuses and lists nothing); `kane-cli context sync status --show <n> --mode agent` prints one saved record in full and needs no location.
- An unknown id, an answer the card does not offer, or `--answer` with no open rebase → `error{USAGE}` naming the fix; an answer checked against decisions that have since moved → `SYNC_REBASE_PENDING` — read `kane-cli context sync status` again.

## 6. Refusal codes — map to plain words, remedy verbatim

| Code | Say | Then |
|---|---|---|
| `SYNC_BEHIND` (3) | `<name>` has records this store has not pulled; nothing was published | `kane-cli context pull <name>` — never `kane-cli context push` to work around it: a push never overwrites anything, so there is nothing to force |
| `SYNC_DIVERGED` (3) | local and `<name>` both added work after the last shared record; nothing moved | the remedy's `kane-cli context pull <name> --rebase` line — with `--yes` under agent mode, and only with the user's go-ahead |
| `SYNC_POSITION_TAKEN` (3) | someone published to `<name>` while this push was in flight; nothing lost | `kane-cli context pull <name> --rebase`; at the very first record: clone the location into a new folder instead |
| `SYNC_LOCAL_MOVED` (3) | this store changed while the pull was being prepared or landing; `detail` says whether nothing was imported or names the range that landed (a valid prefix, kept) | run the pull again |
| `SYNC_REBASE_PENDING` (2) | a rebase is open on this store; it takes no other change until it is finished | `kane-cli context sync` or `kane-cli context pull` to continue, or `kane-cli context sync doctor --abort` to close it — the user's call |
| `SYNC_RESET_IMPORTED` (2) | `kane-cli context sync doctor --abort` met a rebase whose import has already landed; it can only be finished | `kane-cli context sync` or `kane-cli context pull` finishes it; close the open rebase afterwards if the user still wants to |
| `SYNC_LOCATION_UNREACHABLE` (2) | nothing answered at the address (missing folder, unreachable host, no repository there) | check the address, run again |
| `SYNC_LOCATION_DENIED` (2) | `<name>` refused this account even a read | follow `remedy` — it names the case: a bucket wants the right key pair (`kane-cli context sync add <name> <location> --credential-env <VAR>`), an SSH key must be loaded (`ssh-add`), a host key accepted (`ssh -T git@<host>` once, on a terminal), or a Git sign-in done; otherwise ask the owner for access. Never apply S3 key flags to a Git or folder location |
| `SYNC_LOCATION_EMPTY` (2) | `kane-cli context clone` found nothing to join yet | ask the teammate to `kane-cli context push <name>` first, then clone again |
| `SYNC_LOCATION_REFUSED_WRITE` (2) | the location refused the publication (permissions, branch policy, a named setting) | relay the remedy; do not retry unchanged |
| `SYNC_READ_ONLY` (2) | this account can only download from `<name>`; `kane-cli context sync` meets it after its pull has already landed | `kane-cli context pull` from it, or publish to a location the account can write |
| `SYNC_GIT_REQUIRED` (2) | Git is missing or older than 2.31 | install or update Git, then run again |
| `SYNC_PUBLICATION_UNKNOWN` (2) | the push may or may not have landed (a lost response) | keep the local work; check connectivity; run the same command again — it reconciles, never duplicates |
| `SYNC_COPIED_STORE_UNRESOLVED` (2) | this store is a copy or a moved directory, not the one `<name>` was bound from | `kane-cli context sync add <name> <location>` from this directory to bind it, then run again |
| `SYNC_FOREIGN_LINEAGE` (2) | `<name>` holds another store's history (its first record is not this store's); there is no merge | to work on it, `kane-cli context clone <location> <dir>`; to share this store, bind an empty location — the user's call |
| `SYNC_CLIENT_TOO_OLD` (2) | `<name>` holds records from a newer kane-cli than this one | tell the user to update kane-cli (`kane-cli --version`), then run again — never work around it |
| `SYNC_STORE_BUSY` (2) | the rebase could not start: `detail` names a live session, a held lock, a reset in progress, or a store that changed while the rebase was being prepared | follow `detail`: finish or pause the live session; wait for the command holding the lock; `kane-cli context sync doctor` for a reset in progress; run `kane-cli context pull <name> --rebase` again when the store changed during preparation |
| `SYNC_LOCAL_RECORD_CORRUPT` (1), `SYNC_LOCAL_BLOB_CORRUPT` (2) | a record or blob *in this store* is damaged; this says nothing about the location's copy | `kane-cli context fsck`, then restore it from a backup or a clone of this store — never repair by hand |
| `SYNC_REMOTE_HOLE` (2) | either `<name>` kept growing while its tail was being read (`detail` says so; nothing was changed here), or a record or blob is missing at `<name>` | growing: run the same command again in a moment. Missing: a person restores the location from a copy that holds the missing records |
| `SYNC_REMOTE_CHAIN_BROKEN` (1) | either the last record at `<name>` read back with different contents during this pull (`remedy` says to pull again), or two records there do not link — its history was edited outside kane-cli | changed tail: `kane-cli context pull <name>` again. Broken link: a person has to look at the location |
| `SYNC_OBJECT_CORRUPT` (1), `SYNC_REMOTE_ROLLED_BACK` (2) | an object at `<name>` is damaged, or `<name>` was restored from an older snapshot or rebuilt; nothing was changed here | a person has to look at the location: restore it from a copy that holds the records this machine saw; for a rollback done on purpose, `kane-cli context sync remove <name>` then `kane-cli context sync add <name> <location>` — the user's call |
| any other `SYNC_*` | read `detail` + `remedy` — every refusal carries the next command | relay both; never improvise a workaround |

## 7. The fence

While a rebase is open, the store takes writes from the walk only. Every other write verb — `kane-cli context name`, `kane-cli context retire`, `kane-cli context revert`, `kane-cli context ingest`, `kane-cli context extract`, `kane-cli design tests`, `kane-cli maintain reconcile`, `kane-cli context review` — refuses `SYNC_REBASE_PENDING` (exit 2; a `sync_error` under `--mode agent`, stamped with that verb's name); `kane-cli context push` emits `sync_rebase_open` then the same refusal; a test run does not refuse — its results wait to the side and land on the first run after the rebase is finished. Reads (`kane-cli context sync status`, `kane-cli context sync doctor`, `kane-cli context sync list`, `kane-cli context explain`, `kane-cli context fsck`, `kane-cli context view`) never block. Two ways out, both the user's call and never taken on the agent's own initiative: **finish it** (`kane-cli context sync <name>`, answering decisions per §5) or **close it** (`kane-cli context sync doctor --abort` — reapplied items stay, unresolved local changes stay in the backup, `sync_rebase_done{aborted}` when a readable rebase is closed, otherwise `sync_doctor.detail` says what was set aside; exit 3 when decisions were left). **Never delete a lock, a backup or anything under `.context/sync/`, and never delete files under `.context/` to lift the fence** — the backup and the rebase record are the way back.

## 8. Never

- Never edit, copy around, or hand-repair anything under `.context/`; never `git add`/`git merge` `.context/` — keep it gitignored. Sharing happens through a location, even when the location is a Git repository.
- Never put a secret in a location address or on the command line: S3 keys go through `--credential-env`/`--credential-file` (or `KANE_SYNC_S3_ACCESS_KEY_ID` + `KANE_SYNC_S3_SECRET_ACCESS_KEY` at use time), a GitHub token through `KANE_SYNC_GIT_TOKEN`. An address is safe to paste; it grants nothing by itself.

## 9. Narration

- Translate codes; never show event or field names, ids, hashes or raw NDJSON. Name the location by its name: "origin has 3 records you have not pulled", "published 2 records to team".
- One line per decision, from `label` + `mine` + `theirs` + the offered answers; one line per answer landed ("kept origin's version for the name `spec`"). The id stays in the command (`--answer h3=…`), out of the narration.
- On exit 3 say what is waiting (a pull, or N decisions) and the exact next command; it is not a failure. On exit 2 relay `remedy` verbatim (or `message` when there is none), and say what did complete before it.
- `sync_behind` on an assurance stream is one advisory line ("origin has moved past this machine — pull when convenient"); the run continues.
