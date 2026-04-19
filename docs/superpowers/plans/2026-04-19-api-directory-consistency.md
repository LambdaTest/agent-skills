# API Directory Consistency Improvements

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize the `api/` directory to follow consistent naming conventions, add proper YAML frontmatter to all skills, register api skills in `skills_index.json`, and update the validation script to handle nested api skills.

**Architecture:** The `api/` directory currently has 24 SKILL.md files across 21 directories with inconsistent naming (spaces in some dir names, hyphens in others), incomplete frontmatter (missing `languages`, `category`, `license`, `metadata`), and zero presence in `skills_index.json`. We will: (1) rename directories to use hyphen-case, (2) standardize all frontmatter, (3) add api skills to the index, (4) update validation to handle nested skills. The `api/` directory also has two parent dirs (Newman, Postman) with nested child skills — we preserve this nesting.

**Tech Stack:** Bash (renames), Markdown (frontmatter), JSON (`skills_index.json`), Python (validation script)

---

### Task 1: Rename directories with spaces to hyphen-case

**Files:**
- Rename: `api/API Analyzer` → `api/api-analyzer`
- Rename: `api/API Designer` → `api/api-designer`
- Rename: `api/API Documentation` → `api/api-documentation`
- Rename: `api/API Health Monitoring` → `api/api-health-monitoring`
- Rename: `api/API Inference From Files` → `api/api-inference-from-files`
- Rename: `api/API-SDK Generator` → `api/api-sdk-generator`
- Rename: `api/API-To-Test Case Generator` → `api/api-to-testcase-generator`
- Rename: `api/AI-Based-API` → `api/ai-based-api`
- Rename: `api/API-Compliance` → `api/api-compliance`
- Rename: `api/API-Integration-Helper` → `api/api-integration-helper`
- Rename: `api/API-Mocking` → `api/api-mocking`
- Rename: `api/API-Ratelimit-Helper` → `api/api-ratelimit-helper`
- Rename: `api/API-Security-Patterns` → `api/api-security-patterns`
- Rename: `api/API-Versioning-Helper` → `api/api-versioning-helper`
- Rename: `api/OpenAPI-Spec-Generator` → `api/openapi-spec-generator`
- Rename: `api/Popular-API-Fetcher` → `api/popular-api-fetcher`
- Rename: `api/Newman` → `api/newman`
- Rename: `api/Postman` → `api/postman`

- [ ] **Step 1: Rename all directories to lowercase hyphen-case**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git mv "api/API Analyzer" "api/api-analyzer"
git mv "api/API Designer" "api/api-designer"
git mv "api/API Documentation" "api/api-documentation"
git mv "api/API Health Monitoring" "api/api-health-monitoring"
git mv "api/API Inference From Files" "api/api-inference-from-files"
git mv "api/API-SDK Generator" "api/api-sdk-generator"
git mv "api/API-To-Test Case Generator" "api/api-to-testcase-generator"
git mv "api/AI-Based-API" "api/ai-based-api"
git mv "api/API-Compliance" "api/api-compliance"
git mv "api/API-Integration-Helper" "api/api-integration-helper"
git mv "api/API-Mocking" "api/api-mocking"
git mv "api/API-Ratelimit-Helper" "api/api-ratelimit-helper"
git mv "api/API-Security-Patterns" "api/api-security-patterns"
git mv "api/API-Versioning-Helper" "api/api-versioning-helper"
git mv "api/OpenAPI-Spec-Generator" "api/openapi-spec-generator"
git mv "api/Popular-API-Fetcher" "api/popular-api-fetcher"
git mv "api/Newman" "api/newman"
git mv "api/Postman" "api/postman"
```

- [ ] **Step 2: Verify all renames succeeded**

```bash
ls api/
```

Expected: All lowercase, hyphen-separated directory names. No directories with spaces or uppercase.

- [ ] **Step 3: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add -A api/
git commit -m "refactor(api): normalize directory names to lowercase hyphen-case

Renames all 18 api/ skill directories from mixed-case with spaces
(e.g., 'API Documentation', 'API-SDK Generator') to consistent
lowercase hyphen-case (e.g., 'api-documentation', 'api-sdk-generator')."
```

---

### Task 2: Standardize YAML frontmatter for all api skills

**Files:**
- Modify: All 24 `SKILL.md` files under `api/`

Every api skill SKILL.md currently has `name` and `description` but is missing `languages`, `category`, `license`, and `metadata` fields. Add these to match the test skill standard.

- [ ] **Step 1: Add missing frontmatter fields to each SKILL.md**

For each of the 24 SKILL.md files under `api/`, add the missing frontmatter fields after the existing `description` field. The exact values per skill:

**Top-level api skills (14 skills):**

| Skill (new dir name) | `name` (existing) | `languages` | `category` |
|---|---|---|---|
| ai-based-api | api-ai-augmented | `[JavaScript, TypeScript, Python]` | api-testing |
| api-analyzer | api-analyzer | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-designer | api-designer | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-documentation | api-documentation | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-health-monitoring | api-health-monitoring | `[JavaScript, TypeScript, Python, Java]` | api-testing |
| api-inference-from-files | api-inferrer-from-files | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-compliance | api-compliance-checker | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-integration-helper | api-integration | `[JavaScript, TypeScript, Python, Java]` | api-testing |
| api-mocking | api-mock-helper | `[JavaScript, TypeScript, Python, Java]` | api-testing |
| api-ratelimit-helper | api-rate-limiting-helper | `[JavaScript, TypeScript, Python, Java]` | api-testing |
| api-sdk-generator | api-sdk-generator | `[JavaScript, TypeScript, Python, Java, C#, Ruby, Go]` | api-testing |
| api-security-patterns | api-security-auth-pattern | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-to-testcase-generator | api-to-testcase-generator | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| api-versioning-helper | api-versioning-helper | `[JavaScript, TypeScript, Python, Java, C#]` | api-testing |
| graphql-grpc-helper | api-graphql-grpc | `[JavaScript, TypeScript, Python, Java, Go]` | api-testing |
| openapi-spec-generator | openapi-spec-generator | `[YAML, JSON]` | api-testing |
| popular-api-fetcher | api-fetcher-specific-domains | `[JavaScript, TypeScript, Python, Java]` | api-testing |

**Newman child skills (3 skills):**

| Skill dir | `name` (existing) | `languages` | `category` |
|---|---|---|---|
| newman/newman-cicd-helper | newman-cicd-integration | `[JavaScript, YAML]` | api-testing |
| newman/newman-report-analyzer | newman-report-analyzer | `[JavaScript]` | api-testing |
| newman/newman-script-helper | newman-script-helper | `[JavaScript]` | api-testing |

**Postman child skills (4 skills):**

| Skill dir | `name` (existing) | `languages` | `category` |
|---|---|---|---|
| postman/postman-collection-generator | postman-collection-generator | `[JSON, JavaScript]` | api-testing |
| postman/postman-openapi-converter | postman-openapi-converter | `[JSON, YAML]` | api-testing |
| postman/postman-testcase-generator | postman-test-script-generator | `[JavaScript]` | api-testing |
| postman/postman-to-newman | postman-newman-automation | `[JavaScript, YAML]` | api-testing |

For **every** skill, insert these fields right after the `description` field (before the closing `---`):

```yaml
languages:
  - <from table above>
category: api-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
```

- [ ] **Step 2: Verify a sample skill frontmatter looks correct**

Read `api/api-analyzer/SKILL.md` and confirm it now has all 6 fields: `name`, `description`, `languages`, `category`, `license`, `metadata`.

- [ ] **Step 3: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add api/
git commit -m "feat(api): standardize YAML frontmatter for all 24 api skills

Adds languages, category (api-testing), license (MIT), and metadata
(author: TestMu AI, version: 1.0) to all api/ SKILL.md files to match
the test skill frontmatter standard."
```

---

### Task 3: Add `api-testing` to the validation script's valid categories

**Files:**
- Modify: `scripts/validate_skills.py`

- [ ] **Step 1: Add `api-testing` to `VALID_CATEGORIES`**

In `scripts/validate_skills.py`, find the `VALID_CATEGORIES` set and add `'api-testing'`:

```python
VALID_CATEGORIES = {
    'accessibility', 'api-testing', 'bdd-testing', 'cloud-testing',
    'devops', 'e2e-testing', 'mobile-testing', 'performance-testing',
    'security-testing', 'unit-testing', 'visual-testing',
}
```

- [ ] **Step 2: Update the main loop to also scan `api/` subdirectories recursively**

Replace the main loop in `main()` that iterates `os.listdir(REPO_ROOT)` with one that also walks into `api/`:

```python
def main():
    print("=" * 60)
    print("TestMu Skills Validation")
    print("=" * 60)

    # Validate top-level skill directories
    for item in sorted(os.listdir(REPO_ROOT)):
        item_path = os.path.join(REPO_ROOT, item)
        if os.path.isdir(item_path) and item not in SKIP_DIRS and not item.startswith('.'):
            if os.path.exists(os.path.join(item_path, 'SKILL.md')):
                validate_skill(item)

    # Validate api/ skill directories (nested)
    api_dir = os.path.join(REPO_ROOT, 'api')
    if os.path.isdir(api_dir):
        for root, dirs, files in os.walk(api_dir):
            if 'SKILL.md' in files:
                rel = os.path.relpath(root, REPO_ROOT)
                validate_skill(rel)

    validate_skills_index()

    # Print results
    print(f"\nSkills found: {skills_found}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\n❌ ERRORS:")
        for e in errors:
            print(f"  {e}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"  {w}")

    if not errors:
        print("\n✅ All skills pass validation!")
        return 0
    else:
        print("\n❌ Validation failed!")
        return 1
```

- [ ] **Step 3: Run validation to confirm api skills are now scanned**

Run: `cd /Users/mia/myspace/opensource-work/agent-skills && python3 scripts/validate_skills.py`
Expected: `Skills found: 70` (46 test + 24 api), `Errors: 0`. Warnings about missing `reference/playbook.md` for api skills are acceptable since api skills are simpler and don't require playbooks.

- [ ] **Step 4: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add scripts/validate_skills.py
git commit -m "feat(validation): scan api/ skills and add api-testing category

Updates validate_skills.py to walk api/ subdirectories for SKILL.md
files and adds 'api-testing' to the valid categories set."
```

---

### Task 4: Add all api skills to `skills_index.json`

**Files:**
- Modify: `skills_index.json`

- [ ] **Step 1: Update total_skills count and categories**

Change `"total_skills": 46` to `"total_skills": 70`.
Add `"api-testing"` to the `"categories"` array.

- [ ] **Step 2: Add all 24 api skill entries to the skills array**

Append entries for each api skill to the `"skills"` array. Each entry follows this format:

```json
{
  "name": "<name from frontmatter>",
  "path": "api/<dir-name>",
  "description": "<description from frontmatter, first sentence>",
  "languages": ["<from frontmatter>"],
  "category": "api-testing",
  "files": {
    "skill_md": "api/<dir-name>/SKILL.md",
    "reference": []
  }
}
```

For the 2 skills that have `references/` directories (api-to-testcase-generator, openapi-spec-generator), list those reference files. For newman and postman child skills, use paths like `api/newman/newman-cicd-helper/SKILL.md`.

- [ ] **Step 3: Run validation**

Run: `cd /Users/mia/myspace/opensource-work/agent-skills && python3 scripts/validate_skills.py`
Expected: `Skills found: 70`, `Errors: 0`

- [ ] **Step 4: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add skills_index.json
git commit -m "feat(index): register all 24 api skills in skills_index.json

Adds entries for all api/ skills including newman and postman child
skills. Updates total_skills to 70 and adds api-testing category."
```

---

### Task 5: Update `api/README.md` to reflect new structure

**Files:**
- Modify: `api/README.md`

- [ ] **Step 1: Update the directory structure section and fix references**

Update the repository structure section to show the actual (renamed) directory layout. Fix the incomplete sentence on line 58 (`> More skills are being added regularly. See ___ for the full list.`). Update to reference the new consistent naming.

```markdown
## Repository Structure

```
api/
├── ai-based-api/              # AI-powered API features and LLM tool schemas
├── api-analyzer/              # Validate and debug API requests
├── api-compliance/            # GDPR, PCI-DSS, HIPAA compliance patterns
├── api-designer/              # REST API endpoint specification design
├── api-documentation/         # Generate API docs from specs or code
├── api-health-monitoring/     # Health checks, SLA, alerting, observability
├── api-inference-from-files/  # Infer endpoints from file/project structure
├── api-integration-helper/    # Webhooks, event-driven, API chaining
├── api-mocking/               # Mock servers, sandboxes, test fixtures
├── api-ratelimit-helper/      # Rate limiting, throttling, backoff
├── api-sdk-generator/         # Client SDK and API wrapper generation
├── api-security-patterns/     # Auth, OAuth, JWT, RBAC patterns
├── api-to-testcase-generator/ # Generate test cases from API definitions
├── api-versioning-helper/     # Versioning strategies and migration guides
├── graphql-grpc-helper/       # GraphQL schemas and gRPC protobuf
├── newman/                    # Newman CLI helpers
│   ├── newman-cicd-helper/    # CI/CD pipeline configs for Newman
│   ├── newman-report-analyzer/# Analyze Newman test results
│   └── newman-script-helper/  # Generate Newman CLI commands
├── openapi-spec-generator/    # Generate OpenAPI 3.x / Swagger specs
├── popular-api-fetcher/       # Real-world API examples by domain
├── postman/                   # Postman collection tools
│   ├── postman-collection-generator/  # Generate Postman collections
│   ├── postman-openapi-converter/     # OpenAPI to Postman conversion
│   ├── postman-testcase-generator/    # Write Postman test scripts
│   └── postman-to-newman/             # Postman to Newman automation
├── installer/                 # Bulk skill installer script
└── README.md
```

Replace the `> More skills are being added regularly. See ___ for the full list.` line with:

```markdown
> See the root [skills_index.json](../skills_index.json) for the complete machine-readable registry of all skills.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/mia/myspace/opensource-work/agent-skills
git add api/README.md
git commit -m "docs(api): update README with renamed directories and fix broken ref

Reflects the new lowercase hyphen-case directory names and replaces
the placeholder '___' link with a reference to skills_index.json."
```
