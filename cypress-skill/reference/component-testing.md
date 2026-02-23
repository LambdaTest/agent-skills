# Cypress — Component Testing

## React Setup

```bash
npm install cypress @cypress/react --save-dev
```

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite', // or 'webpack'
    },
  },
});
```

## React Component Test

```javascript
import { mount } from '@cypress/react';
import Button from './Button';

describe('Button', () => {
  it('renders with text', () => {
    mount(<Button label="Click Me" />);
    cy.get('button').should('contain', 'Click Me');
  });

  it('calls onClick handler', () => {
    const onClick = cy.stub().as('click');
    mount(<Button label="Click" onClick={onClick} />);
    cy.get('button').click();
    cy.get('@click').should('have.been.calledOnce');
  });
});
```

## Vue Component Test

```javascript
import { mount } from '@cypress/vue';
import Counter from './Counter.vue';

describe('Counter', () => {
  it('increments count', () => {
    mount(Counter);
    cy.get('[data-cy="count"]').should('contain', '0');
    cy.get('[data-cy="increment"]').click();
    cy.get('[data-cy="count"]').should('contain', '1');
  });
});
```

## Run Component Tests

```bash
npx cypress run --component
npx cypress open --component  # interactive
```
