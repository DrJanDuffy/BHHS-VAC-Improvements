import { Injectable } from '@nestjs/common';

export interface ServiceInfo {
  service: string;
  status: 'ok';
}

@Injectable()
export class AppService {
  getInfo(): ServiceInfo {
    return { service: 'bhhs-vac', status: 'ok' };
  }
}
