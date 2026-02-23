# Cypress — Debugging Flaky Tests

## Retry-ability

Cypress automatically retries `.should()` assertions. But NOT action commands.

```javascript
// ✅ This retries automatically
cy.get('.loading').should('not.exist');
cy.get('.results').should('have.length.greaterThan', 0);

// ❌ This does NOT retry — if element not found, it fails immediately
cy.get('.results').click(); // fails if not ready
```

## Common Causes

1. **Race conditions with API calls**
```javascript
// ❌ Bad
cy.visit('/dashboard');
cy.get('.data-table'); // might not be loaded yet

// ✅ Good
cy.intercept('GET', '/api/data').as('getData');
cy.visit('/dashboard');
cy.wait('@getData');
cy.get('.data-table').should('exist');
```

2. **Detached from DOM**
```javascript
// ❌ Element re-rendered by React
cy.get('.item').then($el => {
  // ... page re-renders ...
  cy.wrap($el).click(); // detached!
});

// ✅ Re-query after action
cy.get('.item').first().click();
cy.get('.item').first().should('have.class', 'selected');
```

3. **Animation interference**
```javascript
// cypress.config.js
module.exports = defineConfig({
  e2e: {
    // Disable CSS animations in test
    setupNodeEvents(on, config) {
      on('before:browser:launch', (browser, launchOptions) => {
        // disable animations
      });
    },
  },
  // Or add to test
  animationDistanceThreshold: 20,
});
```

## Debug Tools

```bash
npx cypress open              # Interactive mode with time travel
DEBUG=cypress:* npx cypress run  # Verbose logging
```

```javascript
// In test
cy.pause();  // Pause test execution
cy.debug();  // Open DevTools debugger
```
