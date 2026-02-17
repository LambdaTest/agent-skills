#!/usr/bin/env python3
"""Validate all skills in the TestMu Skills repository."""

import os
import re
import sys
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'evals', 'shared', '.git', 'scripts', 'docs', '__pycache__'}
MAX_SKILL_LINES = 500

VALID_CATEGORIES = {
    'accessibility', 'api-testing', 'bdd-testing', 'cloud-testing',
    'devops', 'e2e-testing', 'mobile-testing', 'performance-testing',
    'security-testing', 'unit-testing', 'visual-testing',
}

errors = []
warnings = []
skills_found = 0


def validate_frontmatter(skill_dir, content):
    """Validate YAML frontmatter structure."""
    if not content.startswith('---\n'):
        errors.append(f"{skill_dir}: Missing opening --- in frontmatter")
        return False

    fm_end = content.find('\n---\n', 3)
    if fm_end == -1:
        fm_end = content.find('\n---', 3)
    if fm_end == -1:
        errors.append(f"{skill_dir}: Missing closing --- in frontmatter")
        return False

    fm = content[4:fm_end]

    if not re.search(r'^name:', fm, re.MULTILINE):
        errors.append(f"{skill_dir}: Missing 'name' in frontmatter")
    if not re.search(r'^description:', fm, re.MULTILINE):
        errors.append(f"{skill_dir}: Missing 'description' in frontmatter")
    if not re.search(r'^languages:', fm, re.MULTILINE):
        warnings.append(f"{skill_dir}: Missing 'languages' in frontmatter")
    if not re.search(r'^category:', fm, re.MULTILINE):
        warnings.append(f"{skill_dir}: Missing 'category' in frontmatter")
    else:
        cat = re.search(r'^category:\s*(.+)', fm, re.MULTILINE)
        if cat and cat.group(1).strip() not in VALID_CATEGORIES:
            warnings.append(f"{skill_dir}: Unknown category '{cat.group(1).strip()}'")

    if not re.search(r'^license:', fm, re.MULTILINE):
        warnings.append(f"{skill_dir}: Missing 'license' in frontmatter (e.g. license: MIT)")
    if not re.search(r'^metadata:', fm, re.MULTILINE):
        warnings.append(f"{skill_dir}: Missing 'metadata' in frontmatter")
    else:
        if not re.search(r'^\s+author:\s*TestMu AI', fm, re.MULTILINE):
            warnings.append(f"{skill_dir}: metadata should include author: TestMu AI")
        if not re.search(r'^\s+version:', fm, re.MULTILINE):
            warnings.append(f"{skill_dir}: metadata should include version")

    return True


def validate_skill(skill_dir):
    """Validate a single skill directory."""
    global skills_found
    skill_path = os.path.join(REPO_ROOT, skill_dir)
    skill_md = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md):
        errors.append(f"{skill_dir}: Missing SKILL.md")
        return

    skills_found += 1

    with open(skill_md) as f:
        content = f.read()

    # Check line count
    lines = len(content.split('\n'))
    if lines > MAX_SKILL_LINES:
        errors.append(f"{skill_dir}: SKILL.md is {lines} lines (max {MAX_SKILL_LINES})")

    # Validate frontmatter
    validate_frontmatter(skill_dir, content)

    # Check for reference directory
    ref_dir = os.path.join(skill_path, 'reference')
    if not os.path.isdir(ref_dir):
        warnings.append(f"{skill_dir}: No reference/ directory")
    else:
        playbook = os.path.join(ref_dir, 'playbook.md')
        if not os.path.exists(playbook):
            warnings.append(f"{skill_dir}: No reference/playbook.md")

    # Check that SKILL.md references its reference files
    if 'reference/' not in content and 'playbook.md' not in content:
        warnings.append(f"{skill_dir}: SKILL.md doesn't reference playbook.md")

    # Optional: E2E skills that support cloud should have cloud-integration or shared link
    cat_match = re.search(r'^category:\s*(\S+)', content[:2000], re.MULTILINE)
    category = cat_match.group(1).strip() if cat_match else ''
    if category == 'e2e-testing':
        has_cloud_ref = os.path.exists(os.path.join(ref_dir, 'cloud-integration.md')) if os.path.isdir(ref_dir) else False
        has_shared_link = 'testmu-cloud-reference' in content or 'shared/testmu-cloud-reference' in content
        if not has_cloud_ref and not has_shared_link:
            warnings.append(f"{skill_dir}: E2E skill has no reference/cloud-integration.md and no link to shared/testmu-cloud-reference.md (recommended for cloud-capable skills)")

    # Optional: playbook should contain a debugging section (CONTRIBUTING asks for debugging table)
    playbook_path = os.path.join(skill_path, 'reference', 'playbook.md')
    if os.path.exists(playbook_path):
        with open(playbook_path) as pf:
            playbook_content = pf.read()
        if 'debugging' not in playbook_content.lower():
            warnings.append(f"{skill_dir}: reference/playbook.md has no obvious debugging section (CONTRIBUTING recommends a debugging table)")


def validate_skills_index():
    """Validate skills_index.json matches filesystem: listed files exist, and index lists all reference files."""
    index_path = os.path.join(REPO_ROOT, 'skills_index.json')
    if not os.path.exists(index_path):
        warnings.append("skills_index.json: file not found")
        return
    try:
        with open(index_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"skills_index.json: invalid JSON ({e})")
        return
    skills_list = data.get('skills', [])
    for entry in skills_list:
        path = entry.get('path', '')
        skill_dir = path
        if not skill_dir:
            warnings.append("skills_index.json: entry missing 'path'")
            continue
        skill_md = entry.get('files', {}).get('skill_md', '')
        if skill_md and not os.path.exists(os.path.join(REPO_ROOT, skill_md)):
            errors.append(f"skills_index.json: {skill_dir}: listed file missing: {skill_md}")
        refs = entry.get('files', {}).get('reference', [])
        for ref_path in refs:
            full = os.path.join(REPO_ROOT, ref_path)
            if not os.path.exists(full):
                errors.append(f"skills_index.json: {skill_dir}: listed file missing: {ref_path}")
        # Optionally: warn if reference/*.md on disk is not in index
        ref_dir = os.path.join(REPO_ROOT, skill_dir, 'reference')
        if os.path.isdir(ref_dir):
            for name in os.listdir(ref_dir):
                if name.endswith('.md'):
                    rel = f"{skill_dir}/reference/{name}"
                    if refs and rel not in refs:
                        warnings.append(f"skills_index.json: {skill_dir}: reference file not in index: reference/{name}")


def main():
    print("=" * 60)
    print("TestMu Skills Validation")
    print("=" * 60)

    for item in sorted(os.listdir(REPO_ROOT)):
        item_path = os.path.join(REPO_ROOT, item)
        if os.path.isdir(item_path) and item not in SKIP_DIRS and not item.startswith('.'):
            if os.path.exists(os.path.join(item_path, 'SKILL.md')):
                validate_skill(item)

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


if __name__ == '__main__':
    sys.exit(main())
