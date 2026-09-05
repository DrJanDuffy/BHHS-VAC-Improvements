# BHHS VAC

NestJS backend for the BHHS Virtual Assistant/Concierge (VAC) — the
integrations service that will sit between the CRM (Follow Up Boss / Cloze),
scheduling, email, and marketing tools used by a BHHS Nevada REALTOR practice.

Right now it is a skeleton: a `/` identity endpoint, a `/health` liveness
probe, global config loading, and CI. Feature modules land on top of this.

## Stack

- Node 22 (`.nvmrc`), TypeScript 6, ESM
- NestJS 12 on Express
- `@nestjs/config` for environment variables
- vitest for unit + e2e tests, oxlint + prettier for hygiene

## Getting started

```bash
nvm use            # or any Node >= 22
npm ci
cp .env.example .env
npm run start:dev  # http://localhost:3000
```

| Endpoint  | Purpose |
|-----------|---------|
| `GET /`       | Service identity — `{ service, status }` |
| `GET /health` | Liveness probe — `{ status, uptimeSeconds, timestamp }` |

## Scripts

| Script | What it does |
|---|---|
| `npm run check` | Everything CI runs: lint, format check, typecheck, unit, e2e |
| `npm run lint` / `npm run format` | oxlint / prettier |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` / `npm run test:e2e` | vitest unit / e2e |
| `npm run build` → `npm run start:prod` | Compile to `dist/` and run |

## Layout

```
src/
  main.ts            bootstrap
  app.module.ts      root module — imports ConfigModule + feature modules
  app.controller.ts  GET /
  health/            GET /health (dependency-free liveness probe)
test/                e2e specs (supertest against a real Nest app)
docs/                integration catalog + connector roster audit
.github/workflows/   CI
```

Add a feature as `src/<feature>/<feature>.module.ts` and register it in
`AppModule.imports`. Anything that talks to an external system should get
its config from `ConfigService`, not `process.env` directly.

## Integrations

See [`docs/integrations-overview.md`](docs/integrations-overview.md) for
the connector catalog and [`docs/connector-roster.md`](docs/connector-roster.md)
for what's currently connected and the recommended lean set.

## License

MIT — see [LICENSE](LICENSE).
