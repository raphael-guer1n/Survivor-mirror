import {ApplicationConfig, APP_INITIALIZER} from "@angular/core";
import {provideRouter} from '@angular/router';
import {routes} from './app.routes';
import {AppConfigService} from "./cores/config/app-config.service";
import {provideHttpClient} from '@angular/common/http';

function loadAppConfig() {
  return () => fetch('/app-config.json', { cache: 'no-cache' })
    .then(res => {
      if (!res.ok) throw new Error('Cannot load app config');
      return res.json();
    })
    .then((cfg: { apiBaseUrl?: string, authToken?: string }) => {
      if (cfg.apiBaseUrl) {
        (globalThis as any).__API_BASE_URL = String(cfg.apiBaseUrl).replace(/\/+$/, '');
      }
      if (cfg.authToken) {
        (globalThis as any).__AUTH_TOKEN = String(cfg.authToken).trim();
      }
    })
    .catch(err => {
      console.warn('Default config', err);
    });
}

export function initAppConfig(config: AppConfigService) {
  return () => config.load();
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    AppConfigService,
    {
      provide: APP_INITIALIZER,
      useFactory: loadAppConfig,
      multi: true
    },
    {
      provide: APP_INITIALIZER,
      useFactory: initAppConfig,
      deps: [AppConfigService],
      multi: true
    },
  ],
}