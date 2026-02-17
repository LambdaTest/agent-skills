#!/bin/bash
set -e
PROJECT_NAME="${1:-cypress-project}"
if [ -d "$PROJECT_NAME" ]; then echo "Error: Directory exists"; exit 2; fi
command -v npx >/dev/null 2>&1 || { echo "Error: npx not found"; exit 1; }

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"
npm init -y > /dev/null 2>&1
npm install cypress --save-dev
mkdir -p cypress/e2e cypress/support cypress/fixtures

cat > cypress.config.js << 'EOF'
const { defineConfig } = require('cypress');
module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
  },
});
EOF

cat > cypress/e2e/example.cy.js << 'EOF'
describe('Example', () => {
  it('visits the app', () => {
    cy.visit('/');
    cy.get('h1').should('be.visible');
  });
});
EOF

echo "✅ Cypress project '$PROJECT_NAME' created"
exit 0
