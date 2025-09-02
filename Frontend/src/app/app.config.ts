import { ApplicationConfig, APP_INITIALIZER, inject } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { HttpInterface } from './cores/interfaces/http/http-interface';

function loadAppConfig() {
    const httpInterface = inject(HttpInterface);
    return () => fetch('/app-config.json')
        .then(res => {
            if (!res.ok) throw new Error('Impossible de charger app-config.json');
            return res.json();
        })
        .then((cfg: { apiBaseUrl?: string }) => {
            if (cfg.apiBaseUrl) httpInterface.setBaseUrl(cfg.apiBaseUrl);
        })
        .catch(err => {
            console.warn('Config non chargée, utilisation du baseUrl par défaut:', err);
        });
}

export const appConfig: ApplicationConfig = {
    providers: [
        provideRouter(routes),
        provideHttpClient(),
        {
            provide: APP_INITIALIZER,
            useFactory: loadAppConfig,
            multi: true
        }
    ]
};