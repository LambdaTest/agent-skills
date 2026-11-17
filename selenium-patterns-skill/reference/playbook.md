# Selenium patterns playbook

Companion to `SKILL.md`. The rules live in `SKILL.md`; this page holds the debugging table and the CI setup.

For TestMu AI cloud capabilities and devices, see [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md). To scaffold a project or connect to the cloud grid, use `selenium-skill`.

## Debugging table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `NoSuchElementException` | element not rendered yet, or inside an iframe, shadow root or new window | wait with `visibility_of_element_located`; switch frame or window; use `shadow_root` |
| 2 | `StaleElementReferenceException` | the node was replaced after it was found | find the element again inside the wait; do not cache `WebElement` across a re-render |
| 3 | `ElementClickInterceptedException` | a banner, toast, spinner or sticky header covers the target | wait for `invisibility_of_element_located` on the cover, or close it |
| 4 | `ElementNotInteractableException` | element is hidden, disabled or zero-size | wait for `element_to_be_clickable`; check the window size in headless |
| 5 | `TimeoutException` with the right locator | implicit and explicit waits are mixed | set implicit wait to 0 and use `WebDriverWait` only |
| 6 | `SessionNotCreatedException` | browser and driver versions do not match | use Selenium 4.6 or later so Selenium Manager resolves the driver; remove pinned driver paths |
| 7 | Passes headed, fails headless | small default window changes the layout | `--headless=new` with `--window-size=1920,1080` |
| 8 | Browser processes pile up on the CI agent | `close()` used, or teardown skipped on failure | call `quit()` in teardown that always runs |
| 9 | Fails only in parallel | a static driver is shared across threads | `ThreadLocal<WebDriver>` in Java, function-scoped fixture in pytest |
| 10 | Text typed into a React input disappears | `clear()` did not fire change events | select all and type over, then assert the field value |
| 11 | `UnexpectedAlertPresentException` | an alert opened and was not handled | `wait.until(EC.alert_is_present())`, then `accept()` or `dismiss()` |
| 12 | `MoveTargetOutOfBoundsException` | the element is outside the viewport | scroll it into view before using `Actions` |

## Capture on failure

Save a screenshot, the page source and the browser console log in the teardown hook, named after the test. On a cloud grid, set the test name and build in the capabilities so the session video can be found.

## CI: GitHub Actions

```yaml
name: e2e
on: [pull_request]
jobs:
  selenium:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: pytest tests/e2e -n 4 --junitxml=results.xml
      - name: Verify the main flow with Kane CLI
        run: |
          npm install -g @testmuai/kane-cli
          kane-cli login --username "${{ secrets.LT_USERNAME }}" --access-key "${{ secrets.LT_ACCESS_KEY }}"
          kane-cli run "Go to ${{ vars.PREVIEW_URL }}/login and assert the sign in form is visible" --agent --headless --timeout 120
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: screenshots, path: artifacts/ }
```
