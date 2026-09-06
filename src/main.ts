import { Logger } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module.js';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const rawPort = process.env.PORT ?? '3000';
  const port = Number(rawPort);
  if (!Number.isInteger(port) || port < 1 || port > 65_535) {
    throw new Error(
      `Invalid PORT: must be an integer between 1 and 65535, got ${rawPort}`,
    );
  }
  await app.listen(port);
  Logger.log(`bhhs-vac listening on http://localhost:${port}`, 'Bootstrap');
}
await bootstrap();
