import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs/operators';
import {DataCacheService} from "../../cores/services/data-cache-service/data-cache.service";
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import { of } from 'rxjs';
import { switchMap, shareReplay } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent {
  private dataCache = inject(DataCacheService);
  private backend = inject(BackendInterface);
  projectViews = signal(this.seededMetric(1500, 4500, 'views'));

  totalStartups$ = this.dataCache.getStartups$().pipe(map(list => list.length));

  totalSiteViews$ = this.backend.getTotalStartupsViews().pipe(
    map(r => r?.total_views ?? 0),
    shareReplay(1)
  );

  private me$ = this.backend.me().pipe(shareReplay(1));
  isFounder$ = this.me$.pipe(map(u => u?.role === 'founder'));

  founderStartupViews$ = this.me$.pipe(
    switchMap(u => {
      if (!u?.id || u.role !== 'founder') return of(0);
      return this.backend.getUserStartup(u.id).pipe(
        switchMap(link => {
          const sid = link?.startup_id;
          if (!sid) return of(0);
          return this.backend.getStartup(sid).pipe(
            map(s => s?.view_count ?? 0)
          );
        })
      );
    }),
    shareReplay(1)
  );
  founderNewsViews$ = this.me$.pipe(
    switchMap(u => {
      if (!u?.id || u.role !== 'founder') return of(0);
      return this.backend.getUserStartup(u.id).pipe(
        switchMap(link => {
          const sid = link?.startup_id;
          if (!sid) return of(0);
          return this.backend.getStartupNews(sid).pipe(
            map(newsList => (newsList ?? []).reduce((sum, n) => sum + (n.view_count ?? 0), 0))
          );
        })
      );
    }),
    shareReplay(1)
  );

  engagementRate = signal(this.seededMetric(2.3, 8.7, 'engagement', true)); // percent
  avgTimeOnPage = signal(this.seededMetric(45, 210, 'time')); // seconds

  private seededMetric(min: number, max: number, key: string, isFloat = false): number {
    let h = 0;
    for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) | 0;
    const r = Math.abs(Math.sin(h)) % 1;
    const value = min + r * (max - min);
    return isFloat ? Math.round(value * 10) / 10 : Math.round(value);
  }
}