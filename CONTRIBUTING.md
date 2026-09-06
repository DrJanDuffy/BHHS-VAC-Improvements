# Contributing to BHHS VAC

Thanks for your interest in contributing! This document outlines the development workflow and standards.

## Setup

```bash
# Install dependencies
npm ci

# Copy environment template
cp .env.example .env

# Optionally, create local overrides (git-ignored)
cp .env.local.example .env.local

# Start development server
npm run start:dev
```

## Development

### Scripts

- `npm run start:dev` — Run with file watch and reload
- `npm run start:debug` — Run with debugger attached
- `npm test` — Run unit tests
- `npm test:watch` — Run tests with file watch
- `npm test:cov` — Run tests with coverage report
- `npm run test:e2e` — Run end-to-end tests
- `npm run lint` — Check code style with oxlint
- `npm run format` — Auto-format code with prettier
- `npm run typecheck` — Type-check without compiling
- `npm run build` — Compile to `dist/`
- `npm run check` — Run all validations (lint, format check, typecheck, tests)
- `npm run clean` — Delete build artifacts, coverage, node_modules

### Code Style

- **Linting**: oxlint (configured in `oxlint.json`)
- **Formatting**: Prettier (configured in `.prettierrc`)
- **Type checking**: TypeScript with strict mode

All files are automatically checked on commit via husky/lint-staged. You can run them manually:

```bash
npm run lint      # Check without fixes
npm run format    # Auto-fix formatting
```

### Testing

- Unit tests live next to code: `*.spec.ts`
- E2E tests live in `test/`
- Coverage reports are generated to `coverage/`

Test locally before pushing:

```bash
npm run test           # Unit tests
npm run test:e2e       # E2E tests
npm run test:cov       # Coverage report
```

### Git Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit with meaningful messages
3. Push your branch and open a PR
4. CI runs automatically; all checks must pass
5. Request review from maintainers
6. After approval, squash and merge to main

### Project Structure

```
src/
  main.ts                  — Bootstrap and server startup
  app.module.ts            — Root module, imports features
  app.service.ts           — Root service (service identity)
  app.controller.ts        — Root controller (GET /)
  app.controller.spec.ts   — Unit tests for root controller
  health/
    health.module.ts       — Health check module
    health.controller.ts   — GET /health endpoint
    health.controller.spec.ts — Unit tests

test/
  app.e2e-spec.ts          — End-to-end tests

.github/workflows/
  ci.yml                   — GitHub Actions CI pipeline
```

### Adding a Feature

1. Create `src/<feature>/<feature>.module.ts`
2. Export the module from `src/app.module.ts` → `imports: [...]`
3. Add unit tests: `src/<feature>/<feature>.spec.ts`
4. Use `ConfigService` for environment variables, not `process.env`
5. Add integration tests to `test/` if needed

Example:

```typescript
// src/example/example.module.ts
import { Module } from '@nestjs/common';
import { ExampleService } from './example.service.js';
import { ExampleController } from './example.controller.js';

@Module({
  controllers: [ExampleController],
  providers: [ExampleService],
})
export class ExampleModule {}
```

### Environment Variables

- Define in `.env.example` (committed)
- Load via `ConfigService` in modules, not `process.env`
- Override locally in `.env.local` (git-ignored)

## Debugging

### VS Code

Add this to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Launch Program",
      "program": "${workspaceFolder}/dist/main.js",
      "preLaunchTask": "npm: build",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    }
  ]
}
```

Then use `npm run start:debug` or press F5 in VS Code.

### Remote Debugging

```bash
node --inspect=0.0.0.0:9229 dist/main.js
```

Then connect your debugger to `http://localhost:9229`.

## Troubleshooting

### Husky pre-commit hook fails

Run checks manually:

```bash
npm run lint
npm run format
npm run typecheck
```

Fix issues and try committing again.

### Tests fail locally but pass in CI

Ensure you're running the same Node version:

```bash
nvm use  # Uses .nvmrc
npm ci   # Clean install
npm test
```

### Build fails

Try a clean rebuild:

```bash
npm run clean
npm ci
npm run build
```

## Questions?

Open an issue or contact the maintainers. Thanks for contributing!
