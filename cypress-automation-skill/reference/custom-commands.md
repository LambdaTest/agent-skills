# Cypress — Custom Commands

## Basic Custom Command

```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-cy="email"]').type(email);
    cy.get('[data-cy="password"]').type(password);
    cy.get('[data-cy="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

// API-based login (faster)
Cypress.Commands.add('loginViaApi', (email, password) => {
  cy.request('POST', '/api/auth/login', { email, password }).then((response) => {
    window.localStorage.setItem('token', response.body.token);
  });
});
```

## TypeScript Support

```typescript
// cypress/support/index.d.ts
declare namespace Cypress {
  interface Chainable {
    login(email: string, password: string): Chainable<void>;
    loginViaApi(email: string, password: string): Chainable<void>;
    getByDataCy(selector: string): Chainable<JQuery<HTMLElement>>;
  }
}
```

## Utility Commands

```javascript
Cypress.Commands.add('getByDataCy', (selector) => {
  cy.get(`[data-cy="${selector}"]`);
});

Cypress.Commands.add('shouldBeAccessible', () => {
  cy.injectAxe();
  cy.checkA11y();
});
```
