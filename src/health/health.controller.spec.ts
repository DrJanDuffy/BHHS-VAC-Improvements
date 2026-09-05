import { HealthController } from './health.controller.js';

describe('HealthController', () => {
  const controller = new HealthController();

  it('reports ok with a non-negative uptime and an ISO timestamp', () => {
    const report = controller.check();

    expect(report.status).toBe('ok');
    expect(report.uptimeSeconds).toBeGreaterThanOrEqual(0);
    expect(new Date(report.timestamp).toISOString()).toBe(report.timestamp);
  });
});
