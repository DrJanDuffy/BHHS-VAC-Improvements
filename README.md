# BHHS VAC

**NestJS backend** for the BHHS Virtual Assistant/Concierge (VAC) — the
integrations service that will sit between the CRM (Follow Up Boss / Cloze),
scheduling, email, and marketing tools used by a BHHS Nevada REALTOR practice.

This repo also hosts a self-improving freshness loop that keeps the VAC
team's **Miscellaneous Tech Tips** sheet current (see
[Tech Tips Freshness Loop](#tech-tips-freshness-loop) below) — a separate,
Python-based tool that lives alongside the NestJS service.

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
.github/workflows/   CI, plus the tech-tips freshness loop (see below)

data/                tech tips: canonical CSV + generated xlsx deliverable
scripts/             tech tips: the freshness-loop scripts (Python)
config/              tech tips: tunable loop thresholds
state/               tech tips: metrics/flags/ledger for the self-improving loop
.claude/skills/      tech tips: the loop's judgment/diagnosis skill
```

Add a feature as `src/<feature>/<feature>.module.ts` and register it in
`AppModule.imports`. Anything that talks to an external system should get
its config from `ConfigService`, not `process.env` directly.

## Integrations

See [`docs/integrations-overview.md`](docs/integrations-overview.md) for the
connector catalog and [`docs/connector-roster.md`](docs/connector-roster.md)
for what's currently connected and the recommended set.

## Tech Tips Freshness Loop

A self-improving loop that keeps the VAC team's **Miscellaneous Tech Tips**
sheet (short tips pointing agents at BHHS tools like RealScout, ACE Social
Media, Maxa Design Studio, Skyslope, Breeze, etc.) from going stale, with
almost no manual upkeep:

- **`data/tech_tips.csv`** is the canonical, version-controlled source of truth.
- **`data/MISCELLANEOUS_TECH_TIPS.xlsx`** is generated from the CSV — hand
  this to the VAC team; don't hand-edit it, it gets overwritten.
- **`.github/workflows/tech-tips-loop.yml`** runs weekly (and on manual
  dispatch): dead-link check on every tip, a [Parallel Search](https://parallel.ai)
  call asking whether each tool is still current, and a discovery pass for
  tips the sheet is missing. It opens a **pull request** with anything it
  finds — nothing ever lands on `main` without a human merging the PR.
- **`.claude/skills/bhhs-vac-tech-tips-loop/SKILL.md`** is the judgment half:
  when a loop metric misbehaves for two runs running, it diagnoses why and
  proposes one small, falsifiable config tweak — gated behind its own PR,
  trialed for 3 runs, and reverted automatically if it doesn't pan out.

**Setup**: add a repo secret `PARALLEL_API_KEY` (Settings → Secrets and
variables → Actions) from [platform.parallel.ai](https://platform.parallel.ai).
Without it, the workflow still runs the dead-link check but skips every
Parallel Search call.

**Running it locally**:

```bash
pip install -r scripts/requirements.txt
export PARALLEL_API_KEY=...        # optional — omit to skip Parallel calls
cd scripts
python check_tips.py               # full run, writes data/ and state/
python check_tips.py --dry-run     # compute and print, write nothing
python check_tips.py --offline     # dead-link check only, no Parallel spend
```

Full mechanics, the loop's immutable rules, and failure modes are documented
in the skill file above.

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
