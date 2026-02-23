# Selenium — Debugging Common Issues

## StaleElementReferenceException

**Cause**: DOM re-rendered after element was found.

```java
// ❌ Bad
WebElement el = driver.findElement(By.id("btn"));
// ... page reloads or AJAX updates ...
el.click(); // StaleElementReferenceException

// ✅ Good — Re-locate element
wait.until(ExpectedConditions.elementToBeClickable(By.id("btn"))).click();
```

## NoSuchElementException

**Cause**: Element not in DOM or not visible yet.

```java
// ❌ Bad
driver.findElement(By.id("dynamic-element")).click();

// ✅ Good — Wait for it
wait.until(ExpectedConditions.presenceOfElementLocated(By.id("dynamic-element"))).click();
```

## ElementClickInterceptedException

**Cause**: Another element covers the target.

```java
// ✅ Use JavaScript click
WebElement el = wait.until(ExpectedConditions.elementToBeClickable(By.id("btn")));
((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);

// ✅ Or scroll into view first
((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(true);", el);
el.click();
```

## Timeouts

```java
// Page load timeout
driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));

// Script timeout (for async JS)
driver.manage().timeouts().scriptTimeout(Duration.ofSeconds(30));

// Custom wait with polling
new WebDriverWait(driver, Duration.ofSeconds(15))
    .pollingEvery(Duration.ofMillis(500))
    .ignoring(NoSuchElementException.class)
    .until(ExpectedConditions.visibilityOfElementLocated(By.id("result")));
```

## Iframe Handling

```java
// Switch to iframe
driver.switchTo().frame("iframeName");
// or by index
driver.switchTo().frame(0);
// or by WebElement
driver.switchTo().frame(driver.findElement(By.cssSelector("iframe.content")));
// Switch back to main
driver.switchTo().defaultContent();
```

## Alert Handling

```java
wait.until(ExpectedConditions.alertIsPresent());
Alert alert = driver.switchTo().alert();
String alertText = alert.getText();
alert.accept(); // or alert.dismiss();
```

## File Upload

```java
WebElement upload = driver.findElement(By.cssSelector("input[type='file']"));
upload.sendKeys("/path/to/file.pdf");
```

## Screenshots on Failure

```java
@AfterEach
void tearDown(TestInfo testInfo) {
    if (driver != null) {
        try {
            File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            Files.copy(screenshot.toPath(),
                Path.of("screenshots/" + testInfo.getDisplayName() + ".png"));
        } catch (Exception e) { /* ignore */ }
        driver.quit();
    }
}
```
