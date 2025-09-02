import { Injectable } from "@angular/core";

export interface AppConfig {
    apiBaseUrl?: string;
    authToken?: string;
}

@Injectable({ providedIn: "root" })
export class AppConfigService {
    private config: AppConfig = {};

    async load(): Promise<void> {
        const res = await fetch("/app-config.json", { cache: "no-cache" });
        if (!res.ok) return;
        this.config = await res.json();
    }

    get<T extends keyof AppConfig>(key: T): AppConfig[T] {
        return this.config[key];
    }
}