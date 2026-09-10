import { Controller, Get } from '@nestjs/common';
import { AppService, type ServiceInfo } from './app.service.js';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getInfo(): ServiceInfo {
    return this.appService.getInfo();
  }
}
