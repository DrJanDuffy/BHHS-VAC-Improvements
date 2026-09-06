# BHHS VAC

**NestJS backend** for the BHHS Virtual Assistant/Concierge (VAC) — the
integrations service that will sit between the CRM (Follow Up Boss / Cloze),
scheduling, email, and marketing tools used by a BHHS Nevada REALTOR practice.

**Status**: Skeleton service with identity and health endpoints, global configuration,
automated CI/CD, and ready for feature development.

**Contributing?** See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, workflow, and code standards.

## Stack

- Node 22 (`.nvmrc`), TypeScript 6, ESM
- NestJS 12 on Express
- `@nestjs/config` for environment variables
- vitest for unit + e2e tests, oxlint + prettier for hygiene

## Quick Start

```bash
nvm use            # Activate Node 22 (or any >= 22)
npm ci             # Clean install dependencies
cp .env.example .env
npm run start:dev  # Start dev server → http://localhost:3000
```

**Verify it's running:**

```bash
curl http://localhost:3000
# {"service":"bhhs-vac","status":"ok"}

curl http://localhost:3000/health
# {"status":"ok","uptimeSeconds":5,"timestamp":"2026-09-06T19:48:00.000Z"}
```

## Endpoints

| Endpoint      | Purpose                                                 |
| ------------- | ------------------------------------------------------- |
| `GET /`       | Service identity — `{ service, status }`                |
| `GET /health` | Liveness probe — `{ status, uptimeSeconds, timestamp }` |

## Scripts

| Script                                 | What it does                                                        |
| -------------------------------------- | ------------------------------------------------------------------- |
| `npm run check`                        | Everything CI runs: lint, format check, typecheck, build, unit, e2e |
| `npm run lint` / `npm run format`      | oxlint / prettier                                                   |
| `npm run typecheck`                    | `tsc --noEmit`                                                      |
| `npm test` / `npm run test:e2e`        | vitest unit / e2e                                                   |
| `npm run build` → `npm run start:prod` | Compile to `dist/` and run                                          |

## Layout

```text
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

See [`docs/integrations-overview.md`](docs/integrations-overview.md) for the
connector catalog and [`docs/connector-roster.md`](docs/connector-roster.md)
for what's currently connected and the recommended set.

## Deployment

### Production Build

```bash
npm run build       # Compile to dist/
npm run start:prod  # Run compiled code
```

### Docker (optional, not included)

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

## Observability

- **Health checks**: `GET /health` for liveness probes (e.g. Kubernetes)
- **Logs**: Sent to stdout; capture in deployment platform
- **Uptime**: Health endpoint reports `uptimeSeconds` and `timestamp`

## Support

- **Issues**: Open a GitHub issue
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation**: See `docs/` for integrations and connectors

## License

MIT — see [LICENSE](LICENSE).
