# E2E Testing with Cypress

This directory contains end-to-end tests for the LegiSync frontend application.

## Setup

Cypress is already installed as a dev dependency. The configuration is set up in `cypress.config.ts`.

## Running Tests

### Prerequisites

1. **Start the backend server:**

   ```bash
   cd backend
   ./venv/bin/python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server:**
   ```bash
   cd frontend
   pnpm dev
   ```

### Running Tests

**Open Cypress Test Runner (Interactive):**

```bash
pnpm e2e:open
# or
pnpm cypress:open
```

**Run tests in headless mode:**

```bash
pnpm e2e
# or
pnpm cypress:run
```

## Test Structure

### Current Tests (`cypress/e2e/chat.cy.ts`)

1. **Component Visibility**: Checks that main UI elements are visible
2. **Query Submission**: Tests submitting queries and receiving responses (mocked)
3. **Empty Input Handling**: Tests behavior with empty input
4. **Multiple Queries**: Tests handling multiple sequential queries
5. **Real Backend Test** (skipped): Optional test with real backend integration

### Mocking vs Real Requests

**Mocked Tests** (default):

- Use `cy.intercept()` to mock API responses
- Fast and reliable
- Don't require backend to be running
- Good for testing UI behavior

**Real Backend Tests** (optional):

- Remove `.skip` from the last test
- Requires both backend and frontend to be running
- Tests full integration
- Slower but tests complete flow

## Configuration

- **Base URL**: `http://localhost:3000` (Next.js dev server)
- **API Route**: `/api/rag` (proxies to backend)
- **Backend URL**: `http://localhost:8000` (from `.env.local`)

## Test Files

- `cypress.config.ts` - Main Cypress configuration
- `cypress/e2e/chat.cy.ts` - Main test suite
- `cypress/support/e2e.ts` - Global test setup
- `cypress/support/commands.ts` - Custom commands
- `cypress.d.ts` - TypeScript definitions

## Tips

1. **Debug Tests**: Use `cy.pause()` to pause execution and inspect
2. **Slow Network**: Increase timeouts with `{ timeout: 10000 }`
3. **Custom Commands**: Add reusable commands in `cypress/support/commands.ts`
4. **Environment Variables**: Access with `Cypress.env('VARIABLE_NAME')`
