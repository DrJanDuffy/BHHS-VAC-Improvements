# BHHS VAC Architecture

## Overview

BHHS VAC is a **NestJS-based integrations service** that sits between the BHHS Nevada practice's business tools (CRM, scheduling, email, marketing) and the Virtual Assistant/Concierge platform.

```
┌──────────────────────────────────────┐
│   External Integrations              │
│  (CRM, Scheduling, Email, Marketing) │
└──────────────────────────────────────┘
            ↓ HTTP ↑
┌──────────────────────────────────────┐
│   BHHS VAC Service                   │
│  (NestJS + Express)                  │
│                                      │
│  • /health (liveness)                │
│  • / (identity)                      │
│  • Feature modules (TBD)             │
└──────────────────────────────────────┘
            ↓ RPC ↑
┌──────────────────────────────────────┐
│   Virtual Assistant/Concierge        │
│   (Claude Agent / LLM)               │
└──────────────────────────────────────┘
```

## Tech Stack

- **Runtime**: Node.js 22+ (ESM)
- **Framework**: NestJS 12 (opinionated, modular)
- **Language**: TypeScript 6 (strict mode)
- **HTTP**: Express.js (NestJS default)
- **Config**: @nestjs/config (environment-based)
- **Testing**: Vitest 4 (unit + e2e)
- **Linting**: oxlint (Rust-based, fast)
- **Formatting**: Prettier (strict code style)
- **CI/CD**: GitHub Actions (parallel jobs, caching)
- **Git Hooks**: husky + lint-staged (pre-commit validation)

## Project Structure

```
bhhs-vac/
├── src/
│   ├── main.ts                    # Bootstrap & server startup
│   ├── app.module.ts              # Root module (DI container)
│   ├── app.service.ts             # Root service (service info)
│   ├── app.controller.ts          # GET / endpoint
│   ├── app.controller.spec.ts     # Unit tests
│   └── health/
│       ├── health.module.ts       # Health module
│       ├── health.controller.ts   # GET /health endpoint
│       └── health.controller.spec.ts
│
├── test/
│   └── app.e2e-spec.ts            # End-to-end tests (full app)
│
├── .github/workflows/
│   └── ci.yml                     # GitHub Actions: lint, test, build
│
├── .husky/
│   └── pre-commit                 # Git hook: lint-staged validation
│
├── docs/
│   ├── integrations-overview.md   # Connector catalog (all available)
│   └── connector-roster.md        # Currently connected integrations
│
├── .env.example                   # Template for environment vars
├── .env.local.example             # Template for local overrides
├── .prettierrc                    # Code formatting rules
├── oxlint.json                    # Linting rules
├── tsconfig.json                  # TypeScript config
├── vitest.config.ts              # Unit test config
├── vitest.config.e2e.ts          # E2E test config
├── nest-cli.json                 # NestJS CLI config
├── package.json                  # Dependencies & scripts
│
├── CONTRIBUTING.md               # Developer guide
├── ARCHITECTURE.md               # This file
└── README.md                     # Quick start & overview
```

## Design Principles

### 1. **Modularity**

Every feature is a NestJS **module** containing:

- **Controller**: Handles HTTP routes
- **Service**: Business logic (can call external APIs, databases, etc.)
- **Module**: Declares what's exported/imported

```typescript
// src/example/example.module.ts
@Module({
  controllers: [ExampleController],
  providers: [ExampleService],
})
export class ExampleModule {}
```

Register in `app.module.ts`:

```typescript
@Module({
  imports: [ConfigModule, ExampleModule, ...],
})
export class AppModule {}
```

### 2. **Configuration Over Secrets**

- All config comes from **environment variables**
- Use `ConfigService`, never `process.env` directly
- Define in `.env.example` (committed), override in `.env` (local, git-ignored)

```typescript
constructor(private config: ConfigService) {
  const apiKey = this.config.get('MY_API_KEY');
}
```

### 3. **Health Checks**

- `GET /health` is a **dependency-free liveness probe**
- Reports: status, uptime, timestamp
- No external API calls, database queries, or side effects
- Kubernetes can use this for pod health decisions

### 4. **Dependency Injection**

NestJS uses constructor injection:

```typescript
constructor(
  private exampleService: ExampleService,
  private config: ConfigService,
) {}
```

### 5. **Error Handling**

- Throw `HttpException` or NestJS exceptions for HTTP responses
- Let NestJS handle error serialization
- Log errors (deployment platform captures logs)

```typescript
if (!found) {
  throw new NotFoundException('Resource not found');
}
```

## Data Flow

### Incoming Request

```
Client Request (HTTP)
    ↓
Middleware (parsing, logging, etc.)
    ↓
Guard (authentication, authorization)
    ↓
Interceptor (transform request)
    ↓
Controller Method
    ↓
Service (business logic)
    ↓
External API / Database (if needed)
    ↓
Response (DTO, serialized JSON)
```

### Adding an Integration

1. **Create a module**: `src/<integration>/<integration>.module.ts`
2. **Service**: Business logic to talk to the external API
3. **Controller**: HTTP endpoint to trigger the service
4. **Config**: Get credentials from `ConfigService`
5. **Tests**: Unit tests for service, e2e for controller
6. **Register**: Add to `AppModule.imports`

Example:

```typescript
// src/slack/slack.service.ts
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class SlackService {
  constructor(private config: ConfigService) {}

  async sendMessage(channel: string, text: string) {
    const token = this.config.get('SLACK_BOT_TOKEN');
    // Call Slack API with token
  }
}
```

## Performance Considerations

- **NestJS is lightweight**: ~50MB runtime (with deps)
- **Express is fast**: Suitable for most integrations workload
- **Async/await**: All I/O is non-blocking
- **Caching**: ConfigService caches values, add Redis if needed
- **Database**: Not included yet; add when needed (TypeORM, Prisma, etc.)

## Security

- **No credentials in code**: Use environment variables
- **CI token hardening**: `persist-credentials: false` on checkout
- **Port validation**: Boot fails if PORT is invalid
- **Input validation**: Add `ValidationPipe` when handling user input
- **HTTPS in production**: Reverse proxy (nginx, Cloudflare, etc.)

## Testing

### Unit Tests

- Live next to code: `*.spec.ts`
- Test service logic, mocking external calls
- Run: `npm test`

### E2E Tests

- In `test/` directory
- Test full HTTP flow (controller → service)
- Run: `npm run test:e2e`

### Coverage

- Target: >80% for critical paths
- Run: `npm run test:cov`
- Reports to codecov in CI

## Deployment

### Local

```bash
npm run build        # Compile to dist/
npm run start:prod   # Run dist/main.js
```

### Docker

See README.md for a basic Dockerfile example. Deploy with:

- **Heroku**: `Procfile` with `web: npm run start:prod`
- **Vercel**: Not suitable (serverless, needs always-on)
- **AWS**: ECS, Fargate, or EC2 + Node
- **Google Cloud**: Cloud Run, Compute Engine, or App Engine
- **Kubernetes**: Helm chart + Docker image

### Environment Variables

Set in deployment platform (e.g., GitHub Secrets for Actions):

```
PORT=3000
LOG_LEVEL=info
SLACK_BOT_TOKEN=xoxb-...
...
```

## Monitoring & Observability

- **Logs**: stdout (deployment platform captures)
- **Health**: `GET /health` for readiness
- **Uptime**: Reported in health endpoint
- **Metrics**: Can add Prometheus/StatsD later
- **Tracing**: Can add OpenTelemetry later

## Future Enhancements

- [ ] Database: PostgreSQL + TypeORM/Prisma
- [ ] Authentication: JWT, OAuth2
- [ ] Rate limiting: Built-in or via nginx
- [ ] Caching: Redis for config, session, API responses
- [ ] Queues: Bull/BullMQ for async jobs
- [ ] Webhooks: Incoming webhook handlers for integrations
- [ ] Observability: Prometheus metrics, OpenTelemetry tracing
- [ ] API Documentation: Swagger/OpenAPI
- [ ] Request validation: class-validator pipes

## Learning Resources

- [NestJS Docs](https://docs.nestjs.com)
- [Express Guide](https://expressjs.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Vitest Guide](https://vitest.dev)
