import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, tap, switchMap, catchError, of } from 'rxjs';
import {BackendInterface} from "../../interfaces/backend/backend-interface";
import {User} from "../../interfaces/backend/dtos";

@Injectable({ providedIn: 'root' })
export class AuthService {
  private backend = inject(BackendInterface);

  private tokenKey = 'access_token';
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

  get user(): User | null {
    return this.userSubject.value;
  }

  get isAuthenticated(): boolean {
    return !!this.getToken();
  }

  setSession(token: string | null, user: User | null) {
    if (token) {
      localStorage.setItem(this.tokenKey, token);
    } else {
      localStorage.removeItem(this.tokenKey);
    }
    this.userSubject.next(user);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  clearSession() {
    localStorage.removeItem(this.tokenKey);
    this.userSubject.next(null);
  }

  refreshMe(): Observable<User> {
    return this.backend.me().pipe(tap((u) => this.userSubject.next(u)));
  }

  login(email: string, password: string): Observable<User | null> {
    return this.backend.login({ email, password }).pipe(
      switchMap((res: any) => {
        const token =
          res?.access_token ??
          res?.token ??
          res?.accessToken ??
          null;
        const user = (res?.user as User | null) ?? null;

        if (token) {
          this.setSession(token, user);
          if (!user) {
            return this.refreshMe().pipe(
              catchError(() => of(null))
            );
          }
          return of(user);
        }

        return this.refreshMe().pipe(
          catchError(() => of(null))
        );
      })
    );
  }
}