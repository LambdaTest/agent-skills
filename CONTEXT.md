# Agent Skills

This context defines the language used to design and maintain reusable agent skills in this repository.

## Language

**HyperExecute Operator**:
A skill that supports end-to-end HyperExecute use: generating configuration, validating locally, running CLI jobs, debugging failures, and integrating CI workflows.
_Avoid_: Config-only skill, YAML generator

**First Successful HyperExecute Run**:
The default journey where an existing test project is detected, configured, validated, executed on HyperExecute, and debugged until one cloud job succeeds.
_Avoid_: One-off YAML generation

**Confirmation-Gated HyperExecute Job**:
A real HyperExecute cloud execution that uploads a project payload and may consume paid concurrency, so it requires explicit user confirmation before running.
_Avoid_: Fully autonomous cloud run

**Autonomous HyperExecute Session**:
An explicit opt-in mode where the agent may validate, run, debug, download logs/artifacts, and retry HyperExecute cloud jobs without asking before each execution.
_Avoid_: Default cloud execution

**HyperExecute Analyze**:
The canonical project detection step performed by `hyperexecute analyze`, used before custom repository detection when the CLI is available.
_Avoid_: Parallel framework detector

**HyperExecute CLI Download**:
Acquiring the official HyperExecute binary for the local operating system, which crosses a binary trust boundary and normally requires user approval.
_Avoid_: Silent binary install

**HyperExecute Credentials**:
The `LT_USERNAME` and `LT_ACCESS_KEY` values used by the HyperExecute CLI, supplied through local environment variables or CI secrets.
_Avoid_: Hardcoded credentials, committed `.env` credentials

**Job Secret File**:
A HyperExecute CLI secret file passed with `--job-secret-file` for additional job-scoped sensitive values that should be hidden from normal YAML and CLI vars.
_Avoid_: General credential store, committed secret file

**HyperExecute Helper Scripts**:
Small deterministic utilities that check readiness, lint generated config, or construct safe CLI commands while preserving the official HyperExecute CLI as the source of truth.
_Avoid_: Replacement CLI, parallel framework detector

**Dependency-Free Helper Script**:
A helper script written with runtime built-ins only, avoiding package installation and treating the HyperExecute CLI as authoritative for final validation.
_Avoid_: Script dependency tree, custom YAML authority

**Operator Helper Set**:
The v1 helper-script set: `doctor.js`, `validate-config.js`, `build-command.js`, and `summarize-artifacts.js`.
_Avoid_: Generator-heavy toolchain

**Template-Driven HyperExecute Config**:
A `hyperexecute.yaml` created by the agent from official CLI analysis, project context, and reference templates rather than a standalone generator script.
_Avoid_: Fully automated YAML generator

## Relationships

- A **HyperExecute Operator** may include migration workflows, but migration is not its primary scope.
- A **HyperExecute Operator** optimizes first for a **First Successful HyperExecute Run**, then supports troubleshooting, CI integration, and performance tuning as secondary workflows.
- A **First Successful HyperExecute Run** may include automatic local validation, but the real cloud job is either a **Confirmation-Gated HyperExecute Job** or part of an explicitly approved **Autonomous HyperExecute Session**.
- A **HyperExecute Operator** uses **HyperExecute Analyze** as the primary project detection path when the CLI is available.
- A **HyperExecute CLI Download** requires confirmation by default, but may be performed automatically inside an **Autonomous HyperExecute Session**.
- **HyperExecute Credentials** come from environment variables or CI secrets; a **Job Secret File** is only for additional job-scoped secrets.
- **HyperExecute Helper Scripts** support repeatable checks around the official CLI, but do not replace `hyperexecute analyze` or real CLI validation.
- A **HyperExecute Helper Script** should be a **Dependency-Free Helper Script** unless a deterministic task cannot be implemented safely with runtime built-ins.
- The **Operator Helper Set** supports readiness checks, lightweight config linting, safe CLI command construction, and downloaded artifact summarization.
- A **Template-Driven HyperExecute Config** is preferred over a generator script in v1 because project-specific test commands require judgment.

## Example dialogue

> **Dev:** "Should this skill only create `hyperexecute.yaml`?"
> **Domain expert:** "No, it should act as a **HyperExecute Operator** that can validate, run, and debug jobs as well."

> **Dev:** "What should the default workflow be when someone asks for HyperExecute help?"
> **Domain expert:** "Start from the existing test project and get to a **First Successful HyperExecute Run**."

> **Dev:** "Can the agent run the cloud job as soon as credentials are available?"
> **Domain expert:** "No — validation is allowed automatically, but the cloud execution is a **Confirmation-Gated HyperExecute Job**."

> **Dev:** "Can the agent keep running and debugging HyperExecute jobs without asking every time?"
> **Domain expert:** "Yes, but only inside an explicitly approved **Autonomous HyperExecute Session**."

> **Dev:** "Should we maintain our own framework detector?"
> **Domain expert:** "No — use **HyperExecute Analyze** first, then fall back to local inspection only when the CLI is unavailable."

> **Dev:** "Can the skill download the HyperExecute CLI if it is missing?"
> **Domain expert:** "Ask first by default; auto-download only inside an **Autonomous HyperExecute Session**."

> **Dev:** "Where should `LT_USERNAME` and `LT_ACCESS_KEY` come from?"
> **Domain expert:** "Use local environment variables or CI secrets; only use `--job-secret-file` for extra job-scoped secrets."

> **Dev:** "Should we build a wrapper that replaces HyperExecute CLI workflows?"
> **Domain expert:** "No — use **HyperExecute Helper Scripts** only for deterministic checks around the official CLI."

> **Dev:** "Can helper scripts depend on npm packages?"
> **Domain expert:** "Avoid that by default — use **Dependency-Free Helper Scripts** and leave final YAML validation to the HyperExecute CLI."

> **Dev:** "Which helper scripts belong in v1?"
> **Domain expert:** "Use the **Operator Helper Set**: readiness, linting, command construction, and artifact summarization."

> **Dev:** "Should v1 include a script that generates `hyperexecute.yaml` automatically?"
> **Domain expert:** "No — use **Template-Driven HyperExecute Config** guided by `hyperexecute analyze` and reference examples."

## Flagged ambiguities

- "HyperExecute skill" was ambiguous between a config generator, an operator, and a migration assistant. Resolved: the canonical scope is **HyperExecute Operator**.
- "Primary journey" was ambiguous between first-run setup, troubleshooting, CI integration, and performance tuning. Resolved: optimize for **First Successful HyperExecute Run** by default.
- "Run HyperExecute" was ambiguous between local validation and real cloud execution. Resolved: local validation can be automatic; cloud execution is confirmation-gated by default, with an explicit **Autonomous HyperExecute Session** opt-in.
- "Project detection" was ambiguous between a custom script and the official CLI. Resolved: **HyperExecute Analyze** is canonical when available.
- "Install the CLI" was ambiguous between giving instructions, asking to download, and silent download. Resolved: **HyperExecute CLI Download** is confirmation-gated by default, autonomous only after explicit opt-in.
- "Credentials" was ambiguous between env vars, generated secret files, and hardcoded YAML values. Resolved: **HyperExecute Credentials** use env/CI secrets; **Job Secret File** is for additional job-scoped secrets.
- "Tools" was ambiguous between no scripts, small helpers, and a full wrapper CLI. Resolved: add **HyperExecute Helper Scripts** that support but do not replace the official CLI.
- "Script implementation" was ambiguous between dependency-free utilities and npm-backed tooling. Resolved: use **Dependency-Free Helper Scripts** by default.
- "v1 scripts" was ambiguous between minimal, operator-oriented, and generator-heavy sets. Resolved: use the **Operator Helper Set**.
- "Config generation" was ambiguous between agent-authored YAML and a standalone generator. Resolved: use **Template-Driven HyperExecute Config** in v1.
