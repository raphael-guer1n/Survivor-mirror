import { Injectable } from '@angular/core';
import {
    HttpClient,
    HttpErrorResponse,
    HttpHeaders,
    HttpParams,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface RequestOptions {
    headers?: HttpHeaders | Record<string, string>;
    params?: HttpParams | Record<string, string | number | boolean>;
}

@Injectable({ providedIn: 'root' })
export class HttpInterface {
    private baseUrl = '/api';

    private defaultHeaders = new HttpHeaders({
        'Content-Type': 'application/json',
    });

    constructor(private http: HttpClient) {}

    setBaseUrl(url: string): void {
        this.baseUrl = (url || '').replace(/\/+$/, '');
    }

    get<T>(path: string, options?: RequestOptions): Observable<T> {
        const url = this.buildUrl(path);
        const httpOptions = this.buildOptions(options);
        return this.http.get<T>(url, httpOptions).pipe(
            catchError((err) => this.handleError<T>('GET', url, err))
        );
    }

    post<T>(path: string, body?: unknown, options?: RequestOptions): Observable<T> {
        const url = this.buildUrl(path);
        const httpOptions = this.buildOptions(options);
        return this.http.post<T>(url, body ?? null, httpOptions).pipe(
            catchError((err) => this.handleError<T>('POST', url, err))
        );
    }

    put<T>(path: string, body?: unknown, options?: RequestOptions): Observable<T> {
        const url = this.buildUrl(path);
        const httpOptions = this.buildOptions(options);
        return this.http.put<T>(url, body ?? null, httpOptions).pipe(
            catchError((err) => this.handleError<T>('PUT', url, err))
        );
    }

    delete<T>(path: string, options?: RequestOptions): Observable<T> {
        const url = this.buildUrl(path);
        const httpOptions = this.buildOptions(options);
        return this.http.delete<T>(url, httpOptions).pipe(
            catchError((err) => this.handleError<T>('DELETE', url, err))
        );
    }

    private buildUrl(path: string): string {
        const cleanBase = this.baseUrl.replace(/\/+$/, '');
        const cleanPath = (path || '').replace(/^\/+/, '');
        return cleanPath ? `${cleanBase}/${cleanPath}` : cleanBase;
    }

    private buildOptions(options?: RequestOptions) {
        const headers = this.mergeHeaders(this.defaultHeaders, options?.headers);
        const params = this.mergeParams(options?.params);
        return { headers, params };
    }

    private mergeHeaders(
        base: HttpHeaders,
        extra?: HttpHeaders | Record<string, string>
    ): HttpHeaders {
        if (!extra) return base;
        if (extra instanceof HttpHeaders) {
            let merged = base;
            extra.keys().forEach((k) => {
                const v = extra.get(k);
                if (v !== null) merged = merged.set(k, v);
            });
            return merged;
        }
        let merged = base;
        Object.entries(extra).forEach(([k, v]) => {
            if (v !== undefined && v !== null) merged = merged.set(k, String(v));
        });
        return merged;
    }

    private mergeParams(
        extra?: HttpParams | Record<string, string | number | boolean>
    ): HttpParams | undefined {
        if (!extra) return undefined;
        if (extra instanceof HttpParams) return extra;

        let params = new HttpParams();
        Object.entries(extra).forEach(([k, v]) => {
            if (v !== undefined && v !== null) params = params.set(k, String(v));
        });
        return params;
    }

    private handleError<T>(
        method: string,
        url: string,
        error: HttpErrorResponse
    ): Observable<T> {
        console.error(`[BackendInterface] ${method} ${url} a échoué`, {
            status: error.status,
            message: error.message,
            error,
        });
        return throwError(() => error);
    }
}
