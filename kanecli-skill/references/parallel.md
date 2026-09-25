<!-- Read this when the user asks for multiple independent browser tasks (suite/batch). Owns the decomposition rules (when to split, how to make sub-objectives self-contained), the per-agent prompt template, and the final batch summary markdown. -->

# Parallel Execution

For multiple independent browser tasks, decompose and run in parallel using the Agent tool.

> **Saved tests? Use testrun instead.** If the tasks are committed `_test.md` files, do NOT hand-roll parallelism — `kane-cli testrun run --parallel N` gives you isolated Chromes, a pooled scheduler, one rollup, and one evidence pack. Read `references/testrun.md`. This reference is for **ad-hoc `run` objectives** only.

## When to Split

- **>15 steps** — long runs drift and get stuck
- **Independent flows** — login test and search test don't depend on each other
- **Different pages/features** — settings vs checkout vs admin
- **Different user roles** — admin flow vs regular user flow

## How to Split

Each sub-objective must be **self-contained**: navigates to its own URL, authenticates independently, asserts its own outcomes. No sub-objective depends on another having run first.

## Execution Pattern

1. Decompose the user's request into N independent sub-objectives
2. Spawn N Agent tool calls in a **single message** — each runs:
   ```bash
   kane-cli run "Go to <url> and <sub-objective>" --agent --headless --timeout 120
   ```
3. Each agent parses the NDJSON output, waits for `run_end`, returns: status, steps, duration, summary, session path
4. After ALL agents complete, format the batch summary

## Agent Prompt Template

```text
Run this kane-cli browser test and report results:

    kane-cli run "Go to <url> and <objective>" --agent --headless --timeout 120

After the command completes:
1. Capture the exit code
2. Parse the run_end NDJSON event from stdout
3. If failed, extract the failing step's screenshot from the run's evidence pack (see references/debug.md)
4. Return: {status, steps, duration, summary, session_dir, failure_step, screenshot_path}
```

## Batch Summary Format

```markdown
## 🧪 Test Suite: <suite name>

| # | Test | Status | Steps | Time | What happened |
|---|------|--------|-------|------|---------|
| 1 | Login + dashboard | ✅ | 5 | 12s | Welcome banner visible |
| 2 | Product search | ✅ | 7 | 18s | 3 results for 'shoes' |
| 3 | Checkout flow | ❌ | 9 | 25s | Payment form did not load |
| 4 | Admin CSV export | ✅ | 6 | 15s | CSV downloaded (42 rows) |

### 📊 Overall
- **Pass rate:** 3/4 (75%)
- **Total steps:** 27 · **Total time:** 1m10s

### ❌ Failures
**#3 Checkout flow** — Payment form did not load after clicking "Credit Card".
📸 [screenshot of the failure shown inline]
```

Status icons: ✅ passed · ❌ failed · ⚠️ stuck/timeout

**Do not** show raw file paths (like `~/.testmuai/kaneai/sessions/...`) in the summary. Instead, read the screenshot and show it inline, or offer to inspect logs only if the user asks.
