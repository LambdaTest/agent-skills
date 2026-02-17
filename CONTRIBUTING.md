# Contributing to TestMu Skills

Thank you for your interest in contributing to the TestMu Skills repository! This guide will help you get started.

## Adding a New Skill

1. **Create a new directory** under the repository root:
   ```
   my-framework-skill/
   ├── SKILL.md           # Required — main skill file
   └── reference/
       ├── playbook.md    # Required — detailed implementation guide
       └── advanced-patterns.md  # Optional — advanced topics
   ```

2. **Write your SKILL.md** with proper YAML frontmatter:
   ```yaml
   ---
   name: my-framework-skill
   description: >
     Clear description of what the skill does and when to use it.
     Include trigger keywords in quotes.
   languages:
     - JavaScript
     - TypeScript
   category: e2e-testing
   license: MIT
   metadata:
     author: TestMu AI
     version: "1.0"
   ---
   ```

3. **Keep SKILL.md under 500 lines** — move detailed content to `reference/playbook.md`.

4. **Run validation** before submitting:
   ```bash
   python3 scripts/validate_skills.py
   ```

5. **Submit a Pull Request** with a clear description.

## Skill Structure Best Practices

- **SKILL.md**: Core workflow, decision trees, quick-reference patterns. Think "table of contents".
- **reference/playbook.md**: Complete code examples, debugging tables, CI/CD configs, best practices.
- **reference/advanced-patterns.md**: Advanced use cases, multi-language patterns.
- **reference/cloud-integration.md**: For E2E/browser skills that support TestMu AI cloud — framework-specific connection and capabilities. Link to `shared/testmu-cloud-reference.md` for full device/capability reference.

## Quality Standards

- All code examples must be syntactically correct and runnable
- Include both local and cloud (TestMu AI / LambdaTest) execution paths where applicable. E2E skills that support cloud should have `reference/cloud-integration.md` or link to `shared/testmu-cloud-reference.md`.
- Add a debugging table with at least 10 common problems (in playbook or `reference/debugging-*.md`)
- Include CI/CD integration (GitHub Actions preferred)
- Add a best practices checklist

## Code of Conduct

Be respectful, constructive, and inclusive. We're building tools to help the testing community.
