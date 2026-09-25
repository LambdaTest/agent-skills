# Execution controls

## Assertion controls and current-page analysis

`run` and `testmd run` support `--assertion-mode dom|visual` (default `dom` with vision fallback) and `--final-validation on|off` (default off). Persist with `config set-assertion-mode` and `config set-final-validation`. Final validation controls the synthesized `cp_final` checkpoint independently of action/testing mode; keep explicit terminal assertions in objectives.

`run --analyzer-only --condition "<condition>"` checks the current desktop browser page without an objective, action steps or saved test. Repeat `--condition` for multiple checks. Use `--agent` or non-TTY input. Results contain `condition_results: boolean[]`; exit `0` means all conditions were judged, **not** that all are true. Exit `1` means a result was missing, and `3` means cancelled. This mode rejects mobile target/app/device options and code-export/name options.

Experimental `run --network-ws` and `run --network-sse` enable WebSocket and SSE capture; both default off. Persist with `config set-network-ws on|off` and `config set-network-sse on|off`. SSE capture is Chromium-only. Do not copy these run-only flags onto `testmd` or `testrun` commands.

Code export defaults to enabled, subject to saved configuration, and supports `python` (default) or `javascript`. `run`/`testmd run` use `--code-language`; `testmd export` uses `--language`. Upload eligibility is independent of action/testing mode.