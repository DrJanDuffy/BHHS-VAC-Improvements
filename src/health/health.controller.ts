import { Controller, Get } from '@nestjs/common';

export interface HealthReport {
  status: 'ok';
  uptimeSeconds: number;
  timestamp: string;
}

/**
 * Liveness probe. Deliberately dependency-free so it stays green even when
 * a downstream integration (CRM, calendar, etc.) is misbehaving — readiness
 * checks for those belong on their own endpoint once they exist.
 */
@Controller('health')
export class HealthController {
  @Get()
  check(): HealthReport {
    return {
      status: 'ok',
      uptimeSeconds: Math.round(process.uptime()),
      timestamp: new Date().toISOString(),
    };
  }
}
