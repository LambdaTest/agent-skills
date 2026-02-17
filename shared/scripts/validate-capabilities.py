#!/usr/bin/env python3
"""validate-capabilities.py — Validate TestMu AI capabilities JSON.

Usage:
    python validate-capabilities.py capabilities.json
    python validate-capabilities.py --inline '{"browserName": "Chrome", ...}'

Exit codes:
    0 = valid
    1 = validation errors found
    2 = missing input / parse error
"""

import json
import sys
import os

VALID_BROWSERS = {"Chrome", "MicrosoftEdge", "pw-chromium", "pw-firefox", "pw-webkit", "Firefox", "Safari"}
VALID_PLATFORMS = {
    "Windows 11", "Windows 10",
    "macOS Sequoia", "macOS Sonoma", "macOS Ventura",
    "macOS Monterey", "macOS Big Sur", "macOS Catalina"
}
VALID_MOBILE_PLATFORMS = {"android", "ios"}

VALID_LT_OPTIONS = {
    "platform", "build", "name", "user", "accessKey",
    "network", "video", "console", "tunnel", "tunnelName",
    "geoLocation", "resolution", "playwrightClientVersion",
    "platformName", "deviceName", "platformVersion",
    "isRealMobile", "isPwMobileWebviewTest"
}

def validate(caps: dict) -> list[str]:
    errors = []
    warnings = []

    # browserName
    browser = caps.get("browserName")
    if not browser:
        errors.append("Missing 'browserName'. Valid: " + ", ".join(sorted(VALID_BROWSERS)))
    elif browser not in VALID_BROWSERS:
        errors.append(f"Invalid browserName '{browser}'. Valid: " + ", ".join(sorted(VALID_BROWSERS)))

    # LT:Options
    lt = caps.get("LT:Options", {})
    if not lt:
        errors.append("Missing 'LT:Options' object")
        return errors

    # Unknown keys
    unknown = set(lt.keys()) - VALID_LT_OPTIONS
    if unknown:
        warnings.append(f"Unknown LT:Options keys (may be ignored): {', '.join(unknown)}")

    # Auth
    user = lt.get("user", "")
    key = lt.get("accessKey", "")
    if not user or user == "None":
        errors.append("Missing LT:Options.user — set LT_USERNAME env var")
    if not key or key == "None":
        errors.append("Missing LT:Options.accessKey — set LT_ACCESS_KEY env var")

    # Mobile vs Desktop
    platform_name = lt.get("platformName", "").lower()
    if platform_name in VALID_MOBILE_PLATFORMS:
        # Mobile validation
        if not lt.get("deviceName"):
            errors.append(f"Mobile test requires 'deviceName' (e.g., 'Pixel 7', 'iPhone 16')")
        if not lt.get("platformVersion"):
            errors.append(f"Mobile test requires 'platformVersion' (e.g., '14', '18')")
        if not lt.get("isRealMobile"):
            warnings.append("isRealMobile not set — add isRealMobile: true for real device testing")
        if platform_name == "ios" and browser and browser.lower() != "pw-webkit" and browser.lower() != "webkit":
            errors.append(f"iOS MUST use webkit/pw-webkit browser, not '{browser}'")
    else:
        # Desktop validation
        platform = lt.get("platform")
        if not platform:
            errors.append("Desktop test requires LT:Options.platform (e.g., 'Windows 11')")
        elif platform not in VALID_PLATFORMS:
            errors.append(f"Invalid platform '{platform}'. Valid: " + ", ".join(sorted(VALID_PLATFORMS)))

    # Recommendations
    if not lt.get("build"):
        warnings.append("Consider adding 'build' to group tests in dashboard")
    if not lt.get("video"):
        warnings.append("Consider adding 'video: true' for debugging")
    if not lt.get("network"):
        warnings.append("Consider adding 'network: true' for network logs")

    # Print warnings
    for w in warnings:
        print(f"⚠️  {w}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-capabilities.py <file.json>")
        print("       python validate-capabilities.py --inline '<json>'")
        sys.exit(2)

    try:
        if sys.argv[1] == "--inline":
            caps = json.loads(sys.argv[2])
        else:
            with open(sys.argv[1]) as f:
                caps = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IndexError) as e:
        print(f"❌ Failed to parse input: {e}")
        sys.exit(2)

    errors = validate(caps)

    if errors:
        print(f"\n❌ {len(errors)} validation error(s):")
        for e in errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("\n✅ Capabilities are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
