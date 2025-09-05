import { Injectable, inject } from '@angular/core';
import { Observable, ReplaySubject, of, EMPTY } from 'rxjs';
import { catchError, expand, map, reduce, shareReplay, switchMap, tap } from 'rxjs/operators';
import {BackendInterface} from "../../interfaces/backend/backend-interface";
import {StartupList} from "../../interfaces/backend/dtos";

@Injectable({ providedIn: 'root' })
export class DataCacheService {
  private backend = inject(BackendInterface);

  private startupsCache$?: Observable<StartupList[]>;
  private readonly PAGE_SIZE = 100;

  getStartups$(): Observable<StartupList[]> {
    if (!this.startupsCache$) {
      this.startupsCache$ = this.loadAllStartups$().pipe(
        shareReplay({ bufferSize: 1, refCount: false })
      );
    }
    return this.startupsCache$;
  }

  refreshStartups(): void {
    this.startupsCache$ = this.loadAllStartups$().pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private loadAllStartups$(): Observable<StartupList[]> {
    const firstPage$ = this.backend.getStartups(0, this.PAGE_SIZE).pipe(
      catchError(() => of([] as StartupList[]))
    );

    return firstPage$.pipe(
      expand((page, i) => {
        if (!page || page.length < this.PAGE_SIZE) return EMPTY;
        const nextSkip = (i + 1) * this.PAGE_SIZE;
        return this.backend.getStartups(nextSkip, this.PAGE_SIZE).pipe(
          catchError(() => of([] as StartupList[]))
        );
      }),
      reduce((acc, page) => acc.concat(page ?? []), [] as StartupList[]),
      map((all) => [...all].sort((a, b) => a.name.localeCompare(b.name)))
    );
  }

}