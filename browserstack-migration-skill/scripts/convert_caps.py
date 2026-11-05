#!/usr/bin/env python3
"""Convert a BrowserStack or Sauce Labs capabilities JSON object into TestMu AI (LT:Options) form.

Usage:
    python3 convert_caps.py --from browserstack caps.json
    python3 convert_caps.py --from saucelabs caps.json
    echo '{"bstack:options": {...}, "browserName": "Chrome"}' | python3 convert_caps.py --from browserstack -
    python3 convert_caps.py --from browserstack browserstack.yml   # SDK config: one converted caps object per platforms[] entry (needs PyYAML)
    python3 convert_caps.py --from browserstack browserstack.yml --emit lambdatest-yml   # starting lambdatest.yml for the TestMu SDK

Handles Selenium (bstack:options / sauce:options / legacy flat), BrowserStack Playwright+Puppeteer flat caps,
and Appium caps. Prints the converted JSON plus a list of keys that were dropped or need manual attention.
Pure Python, no dependencies. The output is a starting point: review every "flag" line.
"""
import json
import sys

OLD_MAC = {"10.15": "Catalina", "10.14": "Mojave", "10.13": "High Sierra", "10.12": "Sierra", "10.11": "El Capitan"}
MAC_CODENAMES = {"11": "Big Sur", "12": "Monterey", "13": "Ventura", "14": "Sonoma", "15": "Sequoia", "26": "Tahoe"}
BROWSER_NAMES = {"chrome": "Chrome", "edge": "MicrosoftEdge", "microsoftedge": "MicrosoftEdge", "firefox": "Firefox", "safari": "Safari",
                 "ie": "Internet Explorer", "internet explorer": "Internet Explorer", "playwright-chromium": "pw-chromium",
                 "playwright-firefox": "pw-firefox", "playwright-webkit": "pw-webkit", "chromium": "pw-chromium", "webkit": "pw-webkit"}
CITY_TZ = {"New_York": "UTC-05:00", "Chicago": "UTC-06:00", "Denver": "UTC-07:00", "Los_Angeles": "UTC-08:00", "London": "UTC+00:00",
           "Paris": "UTC+01:00", "Berlin": "UTC+01:00", "Madrid": "UTC+01:00", "Rome": "UTC+01:00", "Moscow": "UTC+03:00", "Dubai": "UTC+04:00",
           "Kolkata": "UTC+05:30", "Singapore": "UTC+08:00", "Shanghai": "UTC+08:00", "Tokyo": "UTC+09:00", "Seoul": "UTC+09:00",
           "Sydney": "UTC+10:00", "Auckland": "UTC+12:00", "Sao_Paulo": "UTC-03:00", "Toronto": "UTC-05:00"}
DEVICE_PREFIXES = ("Samsung ", "Google ", "Apple ")


def norm_version(v):
    """Strip a trailing .0 only: '13.0' -> '13', '17.0.3' stays '17.0.3'."""
    v = str(v)
    return v[:-2] if v.endswith(".0") and v.count(".") == 1 else v


def to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() == "true"
    return bool(v)


def join_platform(os_name, os_version, flags):
    if not os_name:
        return None
    os_name = str(os_name).strip()
    v = str(os_version).strip() if os_version is not None else ""
    low = os_name.lower()
    if low == "windows":
        return f"Windows {v}".strip()
    if low in ("os x", "macos", "mac"):
        if v.replace(".", "").isdigit():
            code = MAC_CODENAMES.get(v.split(".")[0])
            if not code:
                flags.append(f"macOS version {v} has no known TestMu codename; check the platform list")
                return f"macOS {v}"
            return ("MacOS " if code == "Tahoe" else "macOS ") + code
        if v:
            return ("MacOS " if v == "Tahoe" else "macOS ") + v
        return "macOS"
    if low == "linux":
        return "Linux"
    return f"{os_name} {v}".strip()


def tz(value, flags):
    if value is None:
        return None
    value = str(value)
    if value.upper().startswith("UTC"):
        return value
    city = value.split("/")[-1]
    if city in CITY_TZ:
        flags.append(f"timezone {value} converted to {CITY_TZ[city]} (standard time; adjust for DST if tests depend on it)")
        return CITY_TZ[city]
    flags.append(f"timezone {value} needs manual conversion to UTC+HH:MM")
    return value


def device_name(v):
    v = str(v)
    for p in DEVICE_PREFIXES:
        if v.startswith(p):
            return v[len(p):]
    return v


def convert_browserstack(caps, force_playwright=False):
    flags, dropped = [], []
    out, lt = {}, {"w3c": True}
    bs = dict(caps.get("bstack:options") or {})
    # W3C Appium caps arrive as appium:deviceName etc.; strip the prefix so they map like flat keys
    flat = {(k[len("appium:"):] if k.startswith("appium:") else k): v for k, v in caps.items() if k != "bstack:options"}
    is_playwright = any(k in flat for k in ("browserstack.username", "browserstack.playwrightVersion", "client.playwrightVersion")) or (
        flat.get("browser") in ("playwright-chromium", "playwright-firefox", "playwright-webkit")) or (
        str(flat.get("browserName", "")).startswith("playwright-")) or force_playwright
    mobile = "deviceName" in bs or "device" in flat or "app" in flat or flat.get("platformName", "").lower() in ("android", "ios")

    # legacy flat keys folded into the same mapping
    legacy_map = {"browserstack.user": "userName", "browserstack.key": "accessKey", "browserstack.local": "local", "browserstack.localIdentifier": "localIdentifier",
                  "browserstack.debug": "debug", "browserstack.networkLogs": "networkLogs", "browserstack.consoleLogs": "consoleLogs", "browserstack.console": "consoleLogs",
                  "browserstack.video": "video", "browserstack.selenium_version": "seleniumVersion", "browserstack.idleTimeout": "idleTimeout",
                  "browserstack.geoLocation": "geoLocation", "browserstack.geolocation": "geoLocation", "browserstack.timezone": "timezone", "browserstack.maskCommands": "maskCommands",
                  "browserstack.appium_version": "appiumVersion", "browserstack.gpsLocation": "gpsLocation", "browserstack.resignApp": "resignApp",
                  "browserstack.deviceLogs": "deviceLogs", "browserstack.appiumLogs": "appiumLogs", "browserstack.username": "userName", "browserstack.accessKey": "accessKey",
                  "browserstack.playwrightVersion": "playwrightVersion", "client.playwrightVersion": "playwrightVersion", "browserstack.networkLogsOptions": "networkLogsOptions",
                  "browserstack.interactiveDebugging": "interactiveDebugging", "os": "os", "os_version": "osVersion", "project": "projectName", "build": "buildName",
                  "name": "sessionName", "buildTag": "buildTag", "resolution": "resolution", "device": "deviceName", "real_mobile": "real_mobile", "browser": "browser",
                  "browser_version": "browserVersion", "acceptSslCerts": "acceptSslCerts"}
    for k, v in list(flat.items()):
        if k in legacy_map:
            bs.setdefault(legacy_map[k], v)
            flat.pop(k)

    # W3C passthrough
    if "browserName" in flat:
        _bn = flat.pop("browserName")
        out["browserName"] = BROWSER_NAMES.get(str(_bn).lower(), _bn)
    if "browser" in bs:
        out["browserName"] = BROWSER_NAMES.get(str(bs.pop("browser")).lower(), out.get("browserName"))
    if "browserVersion" in flat:
        out["browserVersion"] = flat.pop("browserVersion")
    if "browserVersion" in bs:
        out["browserVersion"] = bs.pop("browserVersion")
    if "acceptInsecureCerts" in flat:
        out["acceptInsecureCerts"] = to_bool(flat.pop("acceptInsecureCerts"))
    if "acceptSslCerts" in bs:
        out["acceptInsecureCerts"] = to_bool(bs.pop("acceptSslCerts"))

    platform = join_platform(bs.pop("os", None), bs.pop("osVersion", None) if not mobile else None, flags)
    if platform:
        lt["platform" if is_playwright else "platformName"] = platform

    simple = {"userName": "username", "accessKey": "accessKey", "projectName": "project", "buildName": "build", "sessionName": "name",
              "localIdentifier": "tunnelName", "seleniumVersion": "selenium_version", "resolution": "resolution", "geoLocation": "geoLocation",
              "idleTimeout": "idleTimeout", "resignApp": "resignApp", "playwrightVersion": "playwrightClientVersion"}
    boolean = {"local": "tunnel", "debug": "visual", "networkLogs": "network", "video": "video", "deviceLogs": "devicelog", "telemetryLogs": None,
               "seleniumLogs": "verboseWebDriverLogging", "appiumLogs": None, "interactiveDebugging": None, "maskBasicAuth": None, "wsLocalSupport": None,
               "disableCorsRestrictions": None, "selfHeal": None, "testObservability": None, "appProfiling": None, "enablePasscode": None, "real_mobile": "isRealMobile"}
    for k, target in simple.items():
        if k in bs:
            lt[target] = bs.pop(k)
    for k, target in boolean.items():
        if k in bs:
            v = to_bool(bs.pop(k))
            if target:
                lt[target] = v
            else:
                dropped.append(k)
    if "appiumVersion" in bs:
        lt["appiumVersion"] = bs.pop("appiumVersion")
        flags.append(f"appiumVersion={lt['appiumVersion']} kept: confirm it is in the TestMu supported-appium-versions list (default 2.2.1)")
    if "buildTag" in bs:
        lt["buildTags"] = [bs.pop("buildTag")]
    if "consoleLogs" in bs:
        v = str(bs.pop("consoleLogs")).lower()
        lt["console"] = v not in ("disable", "false")
    if "networkLogsOptions" in bs:
        opts = bs.pop("networkLogsOptions") or {}
        if to_bool(opts.get("captureContent", False)):
            lt["network.full.har"] = True
            lt["network"] = True
    if "timezone" in bs:
        lt["timezone"] = tz(bs.pop("timezone"), flags)
    if "maskCommands" in bs:
        v = bs.pop("maskCommands")
        if is_playwright:
            lt["lambdaMaskCommands"] = [s.strip() for s in str(v).split(",")] if isinstance(v, str) else v
        else:
            flags.append("maskCommands has no Selenium equivalent on TestMu (Playwright has lambdaMaskCommands); dropped")
    if "deviceOrientation" in bs:
        lt["deviceOrientation"] = bs.pop("deviceOrientation")
    for k in ("chrome", "firefox", "safari", "edge", "ie"):
        if k in bs:
            sub = bs.pop(k) or {}
            if isinstance(sub, dict) and "driver" in sub:
                lt["driver_version"] = sub["driver"]
            flags.append(f"{k} browser sub-options other than driver have no TestMu equivalent")
    if "gpsLocation" in bs:
        lt["location"] = bs.pop("gpsLocation")
        flags.append("gpsLocation mapped to 'location'; verify format on TestMu")
    if "uploadMedia" in bs:
        lt["media"] = bs.pop("uploadMedia")
        flags.append("media ids must be re-uploaded to TestMu")
    if "midSessionInstallApps" in bs:
        lt["otherApps"] = bs.pop("midSessionInstallApps")
        flags.append("otherApps must be re-uploaded (lt:// ids)")
    for k in ("customNetwork", "networkProfile"):
        if k in bs:
            flags.append(f"{k}={bs.pop(k)} -> use the lambda-throttle-network hook at runtime")
    for k in ("hosts", "httpProxy", "httpsProxy"):
        if k in bs:
            flags.append(f"{k}={bs.pop(k)} -> configure on the LT tunnel (--dns / --proxy-host)")
    if "percy" in bs:
        bs.pop("percy"); bs.pop("percyCaptureMode", None)
        flags.append("Percy -> SmartUI: add smartUI.project cap or SmartUI SDK; re-baseline")
    if "accessibility" in bs:
        lt["accessibility"] = to_bool(bs.pop("accessibility"))
        a11y = bs.pop("accessibilityOptions", {}) or {}
        if "wcagVersion" in a11y:
            lt["accessibility.wcagVersion"] = a11y["wcagVersion"]
        iit = a11y.get("includeIssueType", {}) or {}
        if "bestPractice" in iit:
            lt["accessibility.bestPractice"] = to_bool(iit["bestPractice"])
        if "needsReview" in iit:
            lt["accessibility.needsReview"] = to_bool(iit["needsReview"])
        if "autoScanning" in a11y:
            lt["accessibility.autoscan"] = to_bool(a11y["autoScanning"])
    # mobile
    if "deviceName" in bs:
        lt["deviceName"] = device_name(bs.pop("deviceName"))
        lt.setdefault("isRealMobile", True)
        if "osVersion" in bs:
            lt["platformVersion"] = norm_version(bs.pop("osVersion"))
        flags.append("mobile web/app: hub is mobile-hub.lambdatest.com; verify deviceName against the device list API")
    for k in ("platformName", "deviceName", "platformVersion", "app", "automationName", "otherApps", "autoGrantPermissions", "autoAcceptAlerts",
              "autoDismissAlerts", "language", "locale", "appPackage", "appActivity", "bundleId", "noReset", "fullReset", "newCommandTimeout"):
        if k in flat:
            v = flat.pop(k)
            if k == "deviceName":
                v = device_name(v)
                lt.setdefault("isRealMobile", True)
            if k == "platformName":
                v = {"android": "Android", "ios": "iOS"}.get(str(v).lower(), v)
            if k == "platformVersion":
                v = norm_version(v)
            if k == "app" and str(v).startswith("bs://"):
                flags.append(f"app {v} must be re-uploaded to TestMu (lt:// id)")
            lt[k] = v
    if "disableAnimations" in flat:
        lt["disableAnimation"] = to_bool(flat.pop("disableAnimations"))
    if "buildIdentifier" in bs:
        flags.append(f"buildIdentifier {bs.pop('buildIdentifier')!r}: no TestMu key; append the CI run number to build yourself (e.g. build = name + '-' + os.environ['GITHUB_RUN_NUMBER'])")
    if "deviceName" in lt and "platformVersion" not in lt:
        flags.append("mobile entry without platformVersion: TestMu App Automation requires it; use a regex over recent majors (Android '1[3-5]', iOS '1[7-8]') or a fixed version")
    # mobile web (deviceName + browserName, no app): TestMu needs platformName
    if "deviceName" in lt and "platformName" not in lt:
        dn = str(lt["deviceName"]).lower()
        lt["platformName"] = "iOS" if dn.startswith(("iphone", "ipad")) else "Android"
        flags.append(f"platformName set to {lt['platformName']} from deviceName; check it")
    app = str(lt.get("app", ""))
    if app and not app.startswith(("lt://", "bs://")) and not app.startswith("http"):
        flags.append(f"app '{app}' is a local path: upload it in CI and pass the returned lt:// id, e.g. "
                     "APP=$(curl -s -u \"$LT_USERNAME:$LT_ACCESS_KEY\" -X POST https://manual-api.lambdatest.com/app/upload/realDevice "
                     f"-F \"appFile=@{app}\" -F name=app | jq -r .app_url)")
    if "timezone" in lt and mobile:
        pass
    # leftovers
    for k in list(bs.keys()):
        dropped.append(f"bstack:options.{k}")
    for k in list(flat.keys()):
        out[k] = flat[k]
        flags.append(f"top-level key {k} passed through unchanged; confirm TestMu honours it")
    if lt.get("tunnel") and "tunnelName" not in lt:
        flags.append("tunnel enabled without tunnelName: start the LT binary with --tunnelName and add it")
    if is_playwright:
        # Playwright on TestMu uses `user`, `projectName`, `platform`; w3c is a Selenium/Appium key
        if "username" in lt:
            lt["user"] = lt.pop("username")
        if "project" in lt:
            lt["projectName"] = lt.pop("project")
        if "platformName" in lt:
            lt["platform"] = lt.pop("platformName")
        lt.pop("w3c", None)
        flags.append("Playwright session: connect to wss://cdp.lambdatest.com/playwright?capabilities=<urlencoded JSON>; browserName/browserVersion go inside the capabilities object")
    if lt.get("isRealMobile") is not None and "app" in lt and not str(lt.get("app", "")).startswith("lt://"):
        flags.append("hub for this session: https://mobile-hub.lambdatest.com/wd/hub")
    if "app" in lt and lt.pop("console", None) is not None:
        flags.append("console logs apply to web sessions only; dropped for this native app session")
    for k, v in list(lt.items()):
        if isinstance(v, str) and ("${" in v or "BROWSERSTACK" in v.upper()):
            flags.append(f"{k} = {v!r} references a BrowserStack variable; read LT_USERNAME / LT_ACCESS_KEY (or your own var) instead")
    out["LT:Options"] = lt
    return out, flags, dropped


def convert_saucelabs(caps):
    flags, dropped = [], []
    out, lt = {}, {"w3c": True}
    sauce = dict(caps.get("sauce:options") or {})
    flat = {k: v for k, v in caps.items() if k != "sauce:options"}
    for k in ("browserName", "browserVersion", "acceptInsecureCerts"):
        if k in flat:
            v = flat.pop(k)
            out[k] = BROWSER_NAMES.get(str(v).lower(), v) if k == "browserName" else v
    if "platformName" in flat:
        p = str(flat.pop("platformName"))
        parts = p.split()
        if len(parts) >= 2 and parts[0].lower() in ("macos", "os") and (parts[-1] in OLD_MAC):
            p = "macOS " + OLD_MAC[parts[-1]]
            flags.append(f"{p}: pre-Big Sur macOS may not exist on TestMu; check GET https://api.lambdatest.com/automation/api/v1/platforms and fall back to the oldest available")
        elif parts and parts[0].lower() == "macos" and len(parts) > 1 and parts[1].split(".")[0] in MAC_CODENAMES:
            code = MAC_CODENAMES[parts[1].split(".")[0]]
            p = ("MacOS " if code == "Tahoe" else "macOS ") + code
        elif parts and parts[0].lower() == "macos" and len(parts) > 1:
            flags.append(f"platformName '{p}' has no known macOS codename mapping; pick a current TestMu macOS platform")
        if p.lower() in ("android", "ios"):
            lt["platformName"] = {"android": "Android", "ios": "iOS"}[p.lower()]
        else:
            out["platformName"] = p  # W3C key stays top-level for web sessions
    simple = {"username": "username", "accessKey": "accessKey", "name": "name", "build": "build", "tags": "tags", "custom-data": "customData",
              "tunnelName": "tunnelName", "screenResolution": "resolution", "seleniumVersion": "selenium_version", "idleTimeout": "idleTimeout"}
    for k, t in simple.items():
        if k in sauce:
            lt[t] = sauce.pop(k)
    if "appiumVersion" in sauce:
        _av = sauce.pop("appiumVersion")
        if str(_av).lower() in ("latest", "stable"):
            flags.append(f"appiumVersion={_av} dropped: TestMu needs an explicit version or uses its default (2.2.1)")
        else:
            lt["appiumVersion"] = _av
            flags.append(f"appiumVersion={_av} kept: confirm it is in the TestMu supported-appium-versions list")
    if "tunnelName" in lt:
        lt["tunnel"] = True
    for k in ("chromedriverVersion", "geckodriverVersion", "edgedriverVersion", "iedriverVersion"):
        if k in sauce:
            lt["driver_version"] = sauce.pop(k)
    if "extendedDebugging" in sauce and to_bool(sauce.pop("extendedDebugging")):
        lt["network"] = True
        lt["console"] = True
    if "recordVideo" in sauce:
        lt["video"] = to_bool(sauce.pop("recordVideo"))
    if "recordScreenshots" in sauce:
        lt["visual"] = to_bool(sauce.pop("recordScreenshots"))
    if "recordLogs" in sauce:
        lt["verboseWebDriverLogging"] = to_bool(sauce.pop("recordLogs"))
    if "networkCapture" in sauce:
        lt["network"] = to_bool(sauce.pop("networkCapture"))
    if "timeZone" in sauce:
        lt["timezone"] = tz(sauce.pop("timeZone"), flags)
    if "deviceOrientation" in sauce:
        lt["deviceOrientation"] = sauce.pop("deviceOrientation")
    if "resigningEnabled" in sauce:
        lt["resignApp"] = to_bool(sauce.pop("resigningEnabled"))
    if "imageInjection" in sauce:
        lt["enableImageInjection"] = to_bool(sauce.pop("imageInjection"))
    if "enableAnimations" in sauce:
        lt["disableAnimation"] = not to_bool(sauce.pop("enableAnimations"))
    if "sessionCreationTimeout" in sauce:
        ms = int(sauce.pop("sessionCreationTimeout"))
        lt["queueTimeout"] = max(300, min(900, ms // 1000))
    if "privateDevicesOnly" in sauce and to_bool(sauce.pop("privateDevicesOnly")):
        lt["privateCloud"] = True
    for k in ("logFilters", "filterSendKeys"):
        if k in sauce:
            sauce.pop(k)
            flags.append(f"{k} -> lambdaMaskCommands (Playwright) or drop")
    for k in ("networkProfile", "networkConditions"):
        if k in sauce:
            flags.append(f"{k}={sauce.pop(k)} -> lambda-throttle-network hook")
    if "tunnelOwner" in sauce:
        sauce.pop("tunnelOwner")
        flags.append("tunnelOwner dropped: use a shared LT tunnel under the org account with the same tunnelName")
    if "prerun" in sauce:
        sauce.pop("prerun")
        flags.append("prerun has no session-level equivalent; HyperExecute 'pre:' steps if orchestrating")
    for k in ("public", "videoUploadOnPass", "captureHtml", "commandTimeout", "maxDuration", "priority", "avoidProxy", "armRequired", "devTools",
              "capturePerformance", "cacheId", "allowCacheFallback", "phoneOnly", "tabletOnly", "publicDevicesOnly", "carrierConnectivityOnly",
              "sessionCreationRetry", "audioCapture", "vitals", "biometricsInterception", "crashReporting", "customLogFiles", "android.gpu.mode",
              "disableImmersiveModePopUp", "setupDeviceLock"):
        if k in sauce:
            sauce.pop(k)
            dropped.append(f"sauce:options.{k}")
    # appium: keys
    for k, v in list(flat.items()):
        key = k[len("appium:"):] if k.startswith("appium:") else k
        if key == "deviceName":
            v = device_name(v)
            if any(ch in str(v) for ch in ".*[]^$"):
                flags.append(f"deviceName '{v}' is a regex: TestMu App Automation supports regex; translate vendor prefixes to TestMu model names (Samsung.* -> Galaxy.*, Google.* -> Pixel.*, Apple iPhone.* -> iPhone.*)")
            if "Simulator" in str(v) or "Emulator" in str(v):
                lt["isRealMobile"] = False
                v = str(v).replace(" Simulator", "").replace(" GoogleAPI Emulator", "").replace(" Emulator", "")
            else:
                lt.setdefault("isRealMobile", True)
            lt["deviceName"] = v
        elif key == "app":
            if str(v).startswith("storage:"):
                flags.append(f"app {v} must be re-uploaded to TestMu (lt:// id)")
            elif str(v).startswith("http"):
                flags.append(f"app URL {v}: TestMu does not fetch apps from a URL at session start; upload it first (-F url=... -F name=... on /app/upload/realDevice) and use the lt:// id or custom_id")
            lt["app"] = v
        elif key in ("timeZone", "appTimeZone"):
            lt["timezone"] = tz(v, flags)
        elif key in ("platformVersion", "automationName", "otherApps", "bundleId", "appPackage", "appActivity", "noReset", "fullReset", "newCommandTimeout",
                     "autoGrantPermissions", "autoAcceptAlerts", "autoDismissAlerts", "language", "locale"):
            lt[key] = norm_version(v) if key == "platformVersion" else v
        else:
            out[k] = v
            flags.append(f"top-level key {k} passed through unchanged; confirm TestMu honours it")
        flat.pop(k)
    if str(lt.get("platformVersion", "")).lower() == "latest":
        lt.pop("platformVersion")
        flags.append("platformVersion 'latest' removed: TestMu picks a version when it is omitted; set a number or regex to pin one")
    if out.get("platformName", "").lower() in ("android", "ios"):
        lt["platformName"] = out.pop("platformName")
    for k in list(sauce.keys()):
        dropped.append(f"sauce:options.{k}")
    out["LT:Options"] = lt
    return out, flags, dropped


SDK_ONLY_KEYS = {"platforms", "parallelsPerPlatform", "browserstackLocal", "browserstackLocalOptions", "framework", "source", "testObservability",
                 "testObservabilityOptions", "testReporting", "percy", "percyCaptureMode", "percyOptions", "browserstackAutomation", "turboScale",
                 "accessibilityOptions", "testOrchestrationOptions", "userName", "accessKey", "debug_sdk", "logLevel", "CUSTOM_TAG_1", "CUSTOM_TAG_2"}


def convert_browserstack_yml(cfg):
    """browserstack.yml (SDK) -> list of converted caps, one per platforms[] entry."""
    flags = []
    common = {k: v for k, v in cfg.items() if k not in SDK_ONLY_KEYS and not k.startswith("CUSTOM_TAG")}
    top_app = common.pop("app", None)
    if cfg.get("browserstackLocal"):
        common["local"] = True
        flags.append("browserstackLocal: true -> tunnel: true; start the TestMu tunnel binary (testmu-target.md §7) and set tunnelName")
    if "parallelsPerPlatform" in cfg:
        flags.append(f"parallelsPerPlatform {cfg['parallelsPerPlatform']} -> test-runner parallelism (TestNG thread-count, pytest -n, workers) or HyperExecute parallelism/concurrency")
    if cfg.get("percy"):
        flags.append("percy: true -> migrate visual tests with the percy-migration-skill skill")
    if cfg.get("testObservability"):
        flags.append("testObservability -> TestMu AI Test Analytics (no config key; results appear on the dashboard)")
    if cfg.get("userName") or cfg.get("accessKey"):
        flags.append("credentials in browserstack.yml: read LT_USERNAME / LT_ACCESS_KEY from the environment instead; never commit them")
    pw = "playwright" in str(cfg.get("framework", "")).lower() or any(
        str(p.get("browserName", "")).startswith("playwright-") for p in (cfg.get("platforms") or []))
    if pw:
        flags.append("Playwright SDK config: default path is @lambdatest/playwright-node-sdk with lambdatest.yml (browserstack.md §5 path A; use --emit lambdatest-yml); only with path C does each platform become a playwright.config project using the lambdatest-setup fixture (testmu-target.md §3)")
    results = []
    for i, plat in enumerate(cfg.get("platforms") or [{}]):
        bs = dict(common)
        caps = {"app": top_app} if top_app else {}
        for k, v in plat.items():
            if k in ("browserName", "browserVersion", "app"):
                caps[k] = v
            else:
                bs[k] = v
        caps["bstack:options"] = bs
        out, f, dropped = convert_browserstack(caps, force_playwright=pw)
        f = [x for x in f if not x.startswith("tunnel enabled without tunnelName")]
        results.append({"platform_index": i, "source": plat, "capabilities": out, "flags": f, "dropped": dropped})
    if cfg.get("browserstackLocal") or any("tunnel" in r["capabilities"].get("LT:Options", {}) for r in results):
        flags.append("tunnel is on for every platform: start the LT binary with --tunnelName and set tunnelName (testmu-target.md §7)")
    return results, flags, pw


def to_lambdatest_yml(cfg, results, pw):
    """Starting lambdatest.yml for the TestMu Java SDK (Selenium) or the Playwright Node SDK."""
    lines = ["# Generated from browserstack.yml by convert_caps.py; review before use.",
             "# Credentials come from LT_USERNAME / LT_ACCESS_KEY; never write real values here."]
    first = results[0]["capabilities"].get("LT:Options", {}) if results else {}
    if pw:
        lines += ['user: "${LT_USERNAME}"   # env vars take precedence over file values', 'accessKey: "${LT_ACCESS_KEY}"']
    else:
        lines += ["username: ${LT_USERNAME}", "accesskey: ${LT_ACCESS_KEY}"]
    common_keys = ["build", "project" if not pw else "projectName", "video", "network", "console", "visual", "resolution", "tunnel"]
    for k in common_keys:
        if k in first:
            v = first[k]
            lines.append(f"{k}: {json.dumps(v) if isinstance(v, str) else str(v).lower()}")
    if "parallelsPerPlatform" in cfg and pw:
        lines.append(f"parallelsPerPlatform: {cfg['parallelsPerPlatform']}")
    lines.append("platforms:")
    for r in results:
        caps = r["capabilities"]; lt = caps.get("LT:Options", {})
        if "deviceName" in lt and not pw:
            lines.append(f"  # platform {r['platform_index']} ({lt['deviceName']}) is mobile web: not documented for the Java SDK; run it through an explicit driver factory (path C)")
            continue
        plat = lt.get("platform") or lt.get("platformName")
        if pw:
            lines.append(f"  - platform: {json.dumps(plat or lt.get('platformName', 'android'))}")
            lines.append(f"    browserName: {json.dumps(caps.get('browserName', 'chrome').replace('Chrome', 'chrome'))}")
            if caps.get("browserVersion"):
                lines.append(f"    browserVersion: {json.dumps(caps['browserVersion'])}")
            for k in ("deviceName", "platformVersion", "isRealMobile"):
                if k in lt:
                    lines.append(f"    {k}: {json.dumps(lt[k])}")
        else:
            lines.append(f"  - browserName: {caps.get('browserName', 'Chrome')}")
            if caps.get("browserVersion"):
                lines.append(f"    browserVersion: {caps['browserVersion']}")
            if plat:
                lines.append(f"    platformName: {plat}")
    return "\n".join(lines) + "\n"


def main():
    args = sys.argv[1:]
    if "--from" not in args or len(args) < 3:
        print(__doc__)
        sys.exit(1)
    source = args[args.index("--from") + 1].lower()
    emit_val = args[args.index("--emit") + 1] if "--emit" in args else None
    path = [a for a in args if a not in ("--from", source, "--emit", emit_val)][-1]
    raw = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    if path.endswith((".yml", ".yaml")):
        try:
            import yaml
        except ImportError:
            print("Reading browserstack.yml needs PyYAML: pip install pyyaml (or pip install --break-system-packages pyyaml)")
            sys.exit(3)
        cfg = yaml.safe_load(raw) or {}
        results, flags, pw = convert_browserstack_yml(cfg)
        if "--emit" in args and args[args.index("--emit") + 1] == "lambdatest-yml":
            print(to_lambdatest_yml(cfg, results, pw), end="")
        else:
            print(json.dumps(results, indent=2))
        if flags:
            print("\n# Review (whole file):", file=sys.stderr)
            for f in flags:
                print(f"#   {f}", file=sys.stderr)
        return
    caps = json.loads(raw)
    if source in ("browserstack", "bs"):
        out, flags, dropped = convert_browserstack(caps)
    elif source in ("saucelabs", "sauce"):
        out, flags, dropped = convert_saucelabs(caps)
    else:
        print(f"Unsupported source '{source}'. Use browserstack or saucelabs; for other vendors follow reference/<vendor>.md in the matching skill by hand.")
        sys.exit(2)
    print(json.dumps(out, indent=2))
    if dropped:
        print("\n# Dropped (no TestMu equivalent):", file=sys.stderr)
        for d in dropped:
            print(f"#   {d}", file=sys.stderr)
    if flags:
        print("\n# Review:", file=sys.stderr)
        for f in flags:
            print(f"#   {f}", file=sys.stderr)


if __name__ == "__main__":
    main()
