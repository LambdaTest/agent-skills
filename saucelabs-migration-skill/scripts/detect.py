#!/usr/bin/env python3
"""Scan a repository and report which cloud vendor, test frameworks and languages it uses.

Usage:
    python3 detect.py <repo-path> [--json]

Prints a summary of vendor fingerprints (file:line hits), detected frameworks,
languages, config files and a suggested reading order for the migration references.
Read-only; makes no changes.
"""
import json
import os
import re
import sys
from collections import defaultdict

VENDORS = {
    "browserstack": [
        r"hub(-cloud)?\.browserstack\.com", r"cdp\.browserstack\.com", r"api(-cloud)?\.browserstack\.com",
        r"bstack:options", r"browserstack\.(user|key|local|debug|networkLogs|consoleLogs|console|video|selenium_version|idleTimeout|geoLocation|timezone|maskCommands|appium_version|localIdentifier|playwrightVersion)",
        r"browserstack_executor", r"BROWSERSTACK_USERNAME", r"BROWSERSTACK_ACCESS_KEY", r"browserstack-node-sdk", r"browserstack-sdk",
        r"browserstack-java-sdk", r"BrowserStack\.TestAdapter", r"browserstack-cypress-cli", r"browserstack-local", r"BrowserStackLocal",
        r"@wdio/browserstack-service", r"testcafe-browser-provider-browserstack", r"@nightwatch/browserstack", r"bs-local\.com", r"browserstackLocal|browserStackLocalOptions", r"buildIdentifier",
        r"\bbs://", r"media://",
    ],
    "saucelabs": [
        r"ondemand\.[a-z0-9-]+\.saucelabs\.com", r"ondemand\.saucelabs\.com", r"saucelabs\.com/wd/hub", r"sauce:options",
        r"SAUCE_USERNAME", r"SAUCE_ACCESS_KEY", r"SAUCE_REGION", r"SAUCE_TUNNEL_NAME", r"sauce:job-(result|name|tags|build|info)", r"sauce:context",
        r"saucectl", r"\.sauce/config\.yml", r"@wdio/sauce-service", r"@saucelabs/playwright-reporter", r"testcafe-browser-provider-saucelabs",
        r"\bsc run\b", r"sauce-connect", r"storage:filename=", r"saucelabs\.com/v1/storage", r"app\.([a-z0-9-]+\.)?saucelabs\.com",
        r"api\.[a-z0-9-]+\.saucelabs\.com", r"saucebindings|sauce_bindings|SauceSession|SauceBaseTest|SauceOptions|com\.saucelabs[:.]saucebindings|com\.saucelabs\.saucebindings", r"\.sauceignore",
    ],
    "percy": [r"percySnapshot|percyScreenshot|percy_snapshot|percy_screenshot|@percy/", r"PERCY_TOKEN", r"\bpercy (exec|snapshot|upload|app:exec|storybook)\b", r"io\.percy|PercyIO|percy-selenium|percy-playwright|percy-appium|percy-capybara"],
    "perfecto": [
        r"perfectomobile\.com", r"securityToken", r"perfecto:options", r"Perfecto-Authorization", r"PerfectoExecutionContext", r"ReportiumClient",
        r"reportium", r"perfectoconnect", r"driver\.capabilities\.model", r"report\.projectName",
    ],
    "kobiton": [r"api\.kobiton\.com", r"kobiton:", r"kobiton-store:", r"deviceGroup", r"KOBITON_USERNAME", r"KOBITON_API_KEY", r"/v2/apps/upload-url", r"captureScreenshots"],
    "headspin": [r"headspin\.io", r"/v0/[A-Za-z0-9-]+/wd/hub", r"headspin:", r"HEADSPIN_API_TOKEN", r"hs connect browser", r"automation-config"],
    "digitalai": [r"cloud\.seetest\.io", r"experitest\.com", r"digitalai:options", r"digital\.ai:options", r"deviceQuery", r"SEETEST_IO_ACCESS_KEY", r"seetest:client", r"\bcloud:[a-zA-Z0-9_.]+"],
    "aws-device-farm": [r"create_test_grid_url|CreateTestGridUrl", r"test_bundle\.zip|aws devicefarm|schedule-run|devicefarm:", r"DEVICEFARM_(DEVICE_NAME|DEVICE_UDID|APP_PATH|LOG_DIR|DEVICE_PLATFORM_NAME)", r"client\(\s*['\"]devicefarm['\"]|devicefarm\.[a-z0-9-]+\.amazonaws\.com|@aws-sdk/client-device-farm|DeviceFarmClient", r"APPIUM_BASE_PATH"],
    "firebase-test-lab": [r"gcloud firebase test", r"--type (instrumentation|robo|game-loop)", r"firebase.*test-lab|test-lab.*firebase"],
    "azure-playwright": [r"playwright\.service\.config", r"@azure/playwright", r"@azure/microsoft-playwright-testing", r"createAzurePlaywrightConfig", r"getServiceConfig", r"PLAYWRIGHT_SERVICE_URL", r"PLAYWRIGHT_SERVICE_ACCESS_TOKEN", r"api\.playwright\.microsoft\.com"],
    "cypress-cloud": [r"--record\b", r"CYPRESS_RECORD_KEY", r"\"projectId\"\s*:|projectId:\s*['\"]", r"^\s*record:\s*true", r"--ci-build-id", r"cypress run.*--group\b|^\s*group:\s*\S", r"COMMIT_INFO_[A-Z]+"],
    "selenoid": [r"selenoid:options", r"enableVNC", r"browsers\.json", r"aerokube/selenoid"],
    "moon": [r"moon:options", r"/playwright/(chrome|chromium|firefox|webkit)/playwright-", r"/devtools/chrome", r"@aerokube/cypress-moon", r"aerokube/moon"],
    "selenium-grid": [r"localhost:4444", r"127\.0\.0\.1:4444", r"selenium-hub:4444", r"selenium/(standalone-|hub|node-)", r"SE_EVENT_BUS_HOST", r"SE_NODE_MAX_SESSIONS", r"SELENIUM_REMOTE_URL", r"zalenium"],
    "local-runner": [r"chromium\.launch\(|firefox\.launch\(|webkit\.launch\(|puppeteer\.launch\(", r"\b(GRID_URL|HUB_URL|REMOTE_URL)\b\s*[:=]\s*['\"]?https?://(localhost|127\.0\.0\.1|selenium|[a-z0-9-]+:4444)", r"npx cypress run|cypress run(?!.*--record)"],
    "local-appium": [r"127\.0\.0\.1:4723", r"localhost:4723", r"appium:avd|\"avd\"|'avd'"],
    "lowcode": [r"\bmabl\b", r"@testim/testim-cli|testim --token|TESTIM_TOKEN", r"momentic\.config|momentic run|MOMENTIC_API_KEY", r"qawolf|@qawolf/", r"functionize", r"\.side\"?$|selenium-side-runner"],
    "lambdatest/testmu": [r"hub\.lambdatest\.com", r"cdp\.lambdatest\.com", r"LT:Options", r"LT_USERNAME", r"lambda-status", r"lambdatest_action", r"lambdatest-cypress", r"hyperexecute"],
}

FRAMEWORKS = {
    "selenium": [r"selenium-webdriver|from selenium|org\.openqa\.selenium|OpenQA\.Selenium|selenium/webdriver|php-webdriver|tebeka/selenium|RemoteWebDriver|webdriver\.Remote"],
    "appium": [r"io\.appium|from appium|appium-python-client|webdriverio.*appium|OpenQA\.Selenium\.Appium|UiAutomator2Options|XCUITestOptions|AndroidDriver|IOSDriver|appium:"],
    "playwright": [r"@playwright/test|from playwright|com\.microsoft\.playwright|Microsoft\.Playwright|chromium\.connect|connectOverCDP|playwright\.config"],
    "puppeteer": [r"puppeteer\.(connect|launch)|from puppeteer|require\(['\"]puppeteer"],
    "cypress": [r"cypress\.config\.(js|ts|mjs)|cypress\.json|\bcy\.(visit|get)\("],
    "webdriverio": [r"wdio\.conf|@wdio/cli|@wdio/local-runner|from ['\"]webdriverio['\"]"],
    "testcafe": [r"from ['\"]testcafe['\"]|require\(['\"]testcafe|(?<![\w.])fixture\s*(\(\s*['\"`]|`)|\.testcaferc"],
    "nightwatch": [r"nightwatch\.(conf|json)|@nightwatch/"],
    "robot": [r"\*\*\* Settings \*\*\*|SeleniumLibrary|AppiumLibrary"],
    "espresso": [r"androidx\.test\.espresso|androidTest/"],
    "xcuitest": [r"XCUIApplication|XCTest"],
    "cucumber": [r"io\.cucumber|cucumber-js|@cucumber/|from behave|import behave|^\s*behave\b|SpecFlow|Reqnroll|^\s*(Feature|Scenario( Outline)?):"],
    "testng": [r"org\.testng|testng\.xml"],
    "junit": [r"org\.junit"],
    "pytest": [r"pytest|conftest\.py"],
    "nunit": [r"NUnit\.Framework"],
    "xunit": [r"Xunit"],
    "mstest": [r"Microsoft\.VisualStudio\.TestTools"],
    "rspec": [r"RSpec\.describe|require 'rspec'"],
    "phpunit": [r"PHPUnit\\Framework"],
    "jest": [r"jest\.config|from ['\"]@jest/globals"],
    "mocha": [r"\.mocharc|require\(['\"]mocha"],
}

LANG_EXT = {
    ".java": "java", ".kt": "kotlin", ".scala": "scala", ".groovy": "groovy", ".py": "python", ".js": "javascript", ".mjs": "javascript",
    ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript", ".cs": "csharp", ".rb": "ruby", ".php": "php", ".go": "go",
    ".robot": "robot", ".feature": "gherkin", ".swift": "swift", ".dart": "dart", ".rs": "rust", ".ex": "elixir", ".exs": "elixir", ".clj": "clojure",
}

CONFIG_FILES = [
    "browserstack.yml", "browserstack.yaml", "browserstack.json", ".sauce/config.yml", "credentials.yml", "playwright.service.config.ts",
    "playwright.service.config.js", "lambdatest-config.json", "hyperexecute.yaml", "hyperexecute.yml", ".smartui.json", ".lt.yaml",
    "wdio.conf.js", "wdio.conf.ts", "nightwatch.conf.js", "nightwatch.json", "cypress.config.js", "cypress.config.ts", "cypress.json",
    "playwright.config.ts", "playwright.config.js", ".gitpod.yml", ".travis.yml", ".sauceignore", ".percy.yml", ".percy.yaml", ".percyrc", ".hyperexecuteignore", "testng.xml", "pom.xml", "build.gradle", "build.gradle.kts", "package.json",
    "requirements.txt", "pyproject.toml", "Gemfile", "composer.json", "go.mod", "docker-compose.yml", "docker-compose.yaml", "browsers.json",
    ".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml", ".circleci/config.yml",
]

SKIP_DIRS = {".git", "node_modules", "dist", "build", "target", "bin", "obj", ".venv", "venv", "__pycache__", ".idea", ".vscode", "vendor", "coverage", "out"}
MAX_BYTES = 2_000_000

READING_ORDER = {
    "browserstack": ("browserstack-migration-skill", "reference/browserstack.md"),
    "saucelabs": ("saucelabs-migration-skill", "reference/saucelabs.md"),
    "perfecto": ("perfecto-migration-skill", "reference/perfecto.md"),
    "kobiton": ("kobiton-migration-skill", "reference/kobiton.md"),
    "headspin": ("headspin-migration-skill", "reference/headspin.md"),
    "digitalai": ("digitalai-migration-skill", "reference/digitalai.md"),
    "aws-device-farm": ("aws-device-farm-migration-skill", "reference/aws-device-farm.md"),
    "firebase-test-lab": ("firebase-test-lab-migration-skill", "reference/firebase-test-lab.md"),
    "azure-playwright": ("azure-playwright-migration-skill", "reference/azure-playwright.md"),
    "cypress-cloud": ("cypress-cloud-migration-skill", "reference/cypress-cloud.md"),
    "selenoid": ("selfhosted-grid-migration-skill", "reference/selfhosted-grid.md"),
    "moon": ("selfhosted-grid-migration-skill", "reference/selfhosted-grid.md"),
    "selenium-grid": ("selfhosted-grid-migration-skill", "reference/selfhosted-grid.md"),
    "local-appium": ("selfhosted-grid-migration-skill", "reference/selfhosted-grid.md"),
    "local-runner": ("selfhosted-grid-migration-skill", "reference/selfhosted-grid.md"),
    "lowcode": ("lowcode-tools-migration-skill", "reference/lowcode-tools.md"),
    "percy": ("percy-migration-skill", "reference/percy.md"),
}

# Files and lines written by a migration; scanning them would report the old vendor as still present.
MIGRATION_ARTIFACTS = {"TESTMU_MIGRATION.md", "MIGRATION_RUN_NOTES.md"}
AGENT_FILES = {"AGENTS.md", "CLAUDE.md", ".cursorrules", "copilot-instructions.md"}
AGENT_BLOCK_START = re.compile(r"^#+\s*(Test platform|Visual testing): TestMu AI")
TESTMU_LINE = re.compile(r"lambdatest|testmu", re.I)
COMMENT_LINE = re.compile(r"^\s*(//|#|\*|/\*|<!--|--|;|'|REM\b)")
INFRA = {"selenium-grid", "selenoid", "moon", "local-appium", "local-runner"}
PRODUCTS = {"percy"}


def compile_all(table):
    return {k: [re.compile(p) for p in v] for k, v in table.items()}


def scan(root):
    vendors = compile_all(VENDORS)
    frameworks = compile_all(FRAMEWORKS)
    vendor_hits = defaultdict(list)
    framework_hits = defaultdict(int)
    languages = defaultdict(int)
    configs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        for name in filenames:
            if name in MIGRATION_ARTIFACTS:
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.normpath(os.path.join(rel_dir, name))
            ext = os.path.splitext(name)[1].lower()
            if ext in LANG_EXT:
                lang = LANG_EXT[ext]
                if ext == ".rs":  # Katalon Object Repository files use .rs but are XML
                    try:
                        with open(path, "rb") as fh:
                            if fh.read(64).lstrip().startswith(b"<"):
                                lang = "katalon-object-repository"
                    except OSError:
                        pass
                languages[lang] += 1
            if name in CONFIG_FILES or rel in CONFIG_FILES or any(rel.startswith(c) for c in CONFIG_FILES if c.endswith("workflows")):
                configs.append(rel)
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    in_agent_block = False
                    for lineno, line in enumerate(fh, 1):
                        if "TODO(testmu-migration)" in line:
                            continue
                        if name in AGENT_FILES:
                            if AGENT_BLOCK_START.search(line):
                                in_agent_block = True
                                continue
                            if in_agent_block and line.startswith("#"):
                                in_agent_block = False
                            if in_agent_block:
                                continue
                        testmu_line = bool(TESTMU_LINE.search(line))
                        for vendor, pats in vendors.items():
                            if vendor in INFRA and testmu_line:
                                continue  # e.g. HUB_URL = "https://hub.lambdatest.com/wd/hub"
                            for p in pats:
                                if p.search(line):
                                    vendor_hits[vendor].append((rel, lineno, line.strip()[:160], p.pattern))
                                    break
                        for fw, pats in frameworks.items():
                            if any(p.search(line) for p in pats):
                                framework_hits[fw] += 1
            except OSError:
                continue
    return vendor_hits, framework_hits, languages, configs


def per_file(hits):
    counts = defaultdict(int)
    for h in hits:
        counts[h[0]] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def read_next(sources):
    """Paths relative to the skill folder containing this script; names the sibling skill when the source is a different vendor."""
    skill_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = []
    for v in sources:
        if v not in READING_ORDER:
            continue
        skill, ref = READING_ORDER[v]
        if skill == skill_dir:
            out.append(ref)
        else:
            out.append(f"{ref} (in sibling skill {skill}; this skill is {skill_dir})")
    return out + ["reference/testmu-target.md", "reference/languages.md"]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    root = sys.argv[1]
    as_json = "--json" in sys.argv
    vendor_hits, framework_hits, languages, configs = scan(root)
    infra = INFRA
    def score(item):
        v, hits = item
        files = len({h[0] for h in hits})
        tier = 0 if v in infra else (1 if v in PRODUCTS else 2)
        return (tier, files, len(hits))  # cloud grids outrank product-only tools, which outrank infra noise
    ranked = sorted(vendor_hits.items(), key=score, reverse=True)
    sources = [v for v, _ in ranked if v != "lambdatest/testmu"]
    cloud = [v for v in sources if v not in infra and v not in PRODUCTS]
    products = [v for v in sources if v in PRODUCTS]
    infra_seen = [v for v in sources if v in infra]
    # a vendor whose every hit is a comment (typical after a migration) is not a live source
    live = [v for v in sources if not all(COMMENT_LINE.match(x[2]) for x in vendor_hits[v])]
    primary = live[0] if live else None
    mixed = cloud[1:]
    # With a cloud vendor present, localhost hubs / local launches are usually local-dev paths of the same suite, not a separate self-hosted grid.
    routed = cloud + products + ([] if cloud else infra_seen)
    result = {
        "root": os.path.abspath(root),
        "primary_source": primary,
        "vendors": {v: {"hits": len(h), "comment_only": all(COMMENT_LINE.match(x[2]) for x in h), "files": per_file(h), "samples": [f"{x[0]}:{x[1]}: {x[2]}" for x in h[:8]]} for v, h in ranked},
        "frameworks": dict(sorted(framework_hits.items(), key=lambda kv: -kv[1])),
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
        "config_files": sorted(set(configs)),
        "already_on_testmu": "lambdatest/testmu" in vendor_hits,
        "other_cloud_vendors": mixed,
        "product_migrations": products,
        "infra_also_seen": infra_seen if cloud else [],
        "read_next": read_next(routed),
    }
    if as_json:
        print(json.dumps(result, indent=2))
        return
    print(f"Repo: {result['root']}")
    print(f"Primary source vendor: {primary or 'none detected'}")
    if result["other_cloud_vendors"]:
        print(f"Note: other cloud vendors also present: {', '.join(result['other_cloud_vendors'])}. Ask which one is live.")
    if products:
        print(f"Note: product-level tools found: {', '.join(products)}. Migrate them with the matching product skill (percy -> percy-migration-skill) after or alongside the grid migration.")
    if result["infra_also_seen"]:
        print(f"Note: local/self-hosted patterns also seen ({', '.join(result['infra_also_seen'])}); with a cloud vendor present these are usually local-dev paths of the same suite. Keep them only if the code chooses them conditionally (env var, flag); a hard-coded localhost hub in a vendor-SDK repo is a placeholder the SDK overrode, so replace it.")
    if result["already_on_testmu"]:
        print("Note: TestMu/LambdaTest fingerprints already present (partial migration or mixed targets).")
    print("\nVendor fingerprints:")
    for v, info in result["vendors"].items():
        print(f"  {v}: {info['hits']} hits in {len(info['files'])} files" + ("  (comments only: leftovers, not a live source)" if info["comment_only"] else ""))
        for f, n in info["files"].items():
            print(f"    {n:4d}  {f}")
        print("    samples:")
        for s in info["samples"][:3]:
            print(f"      {s}")
    print("\nFrameworks (line hits):")
    for fw, n in result["frameworks"].items():
        print(f"  {fw}: {n}")
    print("\nLanguages (file counts):")
    for lang, n in result["languages"].items():
        print(f"  {lang}: {n}")
    print("\nConfig files:")
    for c in result["config_files"]:
        print(f"  {c}")
    print("\nRead next:")
    for r in result["read_next"]:
        print(f"  {r}")


if __name__ == "__main__":
    main()
