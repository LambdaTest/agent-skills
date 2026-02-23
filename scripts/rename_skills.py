#!/usr/bin/env python3
"""Rename skill directories and update references (e.g. selenium-automation-skill -> selenium-skill)."""

import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# old_dir -> new_dir (only those that change)
DIR_RENAMES = {
    "appium-automation-skill": "appium-skill",
    "behat-automation-skill": "behat-skill",
    "behave-automation-skill": "behave-skill",
    "capybara-automation-skill": "capybara-skill",
    "codeception-testing-skill": "codeception-skill",
    "cucumber-automation-skill": "cucumber-skill",
    "cypress-automation-skill": "cypress-skill",
    "detox-automation-skill": "detox-skill",
    "espresso-automation-skill": "espresso-skill",
    "gauge-automation-skill": "gauge-skill",
    "geb-automation-skill": "geb-skill",
    "jasmine-testing-skill": "jasmine-skill",
    "jest-testing-skill": "jest-skill",
    "junit-testing-skill": "junit-5-skill",
    "karma-testing-skill": "karma-skill",
    "lettuce-testing-skill": "lettuce-skill",
    "mocha-testing-skill": "mocha-skill",
    "mstest-testing-skill": "mstest-skill",
    "nemojs-automation-skill": "nemojs-skill",
    "nightwatchjs-automation-skill": "nightwatchjs-skill",
    "nunit-testing-skill": "nunit-skill",
    "phpunit-testing-skill": "phpunit-skill",
    "playwright-automation-skill": "playwright-skill",
    "protractor-automation-skill": "protractor-skill",
    "puppeteer-automation-skill": "puppeteer-skill",
    "pytest-testing-skill": "pytest-skill",
    "rspec-testing-skill": "rspec-skill",
    "selenide-automation-skill": "selenide-skill",
    "selenium-automation-skill": "selenium-skill",
    "smartui-testing-skill": "smartui-skill",
    "specflow-automation-skill": "specflow-skill",
    "testcafe-automation-skill": "testcafe-skill",
    "testng-testing-skill": "testng-skill",
    "testunit-ruby-skill": "testunit-skill",
    "unittest-testing-skill": "unittest-skill",
    "vitest-testing-skill": "vitest-skill",
    "webdriverio-automation-skill": "webdriverio-skill",
    "xcuitest-automation-skill": "xcuitest-skill",
    "xunit-testing-skill": "xunit-skill",
}


def replace_path(s, renames):
    for old, new in renames.items():
        s = s.replace(old, new)
    return s


def main():
    os.chdir(REPO_ROOT)

    # 1. Rename directories
    for old_name, new_name in DIR_RENAMES.items():
        old_path = os.path.join(REPO_ROOT, old_name)
        if os.path.isdir(old_path):
            new_path = os.path.join(REPO_ROOT, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed {old_name} -> {new_name}")

    # 2. Update skills_index.json
    index_path = os.path.join(REPO_ROOT, "skills_index.json")
    with open(index_path) as f:
        data = json.load(f)
    for skill in data["skills"]:
        old_name = skill["name"]
        new_name = DIR_RENAMES.get(old_name, old_name)
        skill["name"] = new_name
        skill["path"] = new_name
        skill["files"]["skill_md"] = replace_path(skill["files"]["skill_md"], DIR_RENAMES)
        skill["files"]["reference"] = [replace_path(p, DIR_RENAMES) for p in skill["files"]["reference"]]
    with open(index_path, "w") as f:
        json.dump(data, f, indent=2)
    print("Updated skills_index.json")

    # 3. Update name: in each SKILL.md frontmatter
    for old_name, new_name in DIR_RENAMES.items():
        skill_md = os.path.join(REPO_ROOT, new_name, "SKILL.md")
        if os.path.isfile(skill_md):
            with open(skill_md) as f:
                content = f.read()
            content = re.sub(r"^name:\s*" + re.escape(old_name) + r"\s*$", f"name: {new_name}", content, count=1, flags=re.MULTILINE)
            with open(skill_md, "w") as f:
                f.write(content)
    for unchanged in ["cicd-pipeline-skill", "flutter-testing-skill", "hyperexecute-skill", "laravel-dusk-skill", "robot-framework-skill", "serenity-bdd-skill", "test-framework-migration-skill"]:
        skill_md = os.path.join(REPO_ROOT, unchanged, "SKILL.md")
        if os.path.isfile(skill_md):
            pass  # name stays same
    print("Updated SKILL.md frontmatter (name) in renamed skills")

    # 4. Rename evals files
    evals_dir = os.path.join(REPO_ROOT, "evals")
    if os.path.isdir(evals_dir):
        for old_name, new_name in DIR_RENAMES.items():
            old_file = os.path.join(evals_dir, f"{old_name}-evals.json")
            if os.path.isfile(old_file):
                new_file = os.path.join(evals_dir, f"{new_name}-evals.json")
                os.rename(old_file, new_file)
                print(f"Renamed evals {old_name}-evals.json -> {new_name}-evals.json")
    print("Done.")


if __name__ == "__main__":
    main()
