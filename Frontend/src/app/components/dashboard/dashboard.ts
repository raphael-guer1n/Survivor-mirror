import { Component, computed, effect, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { map } from 'rxjs/operators';
import {DataCacheService} from "../../cores/services/data-cache-service/data-cache.service";

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent {
  private dataCache = inject(DataCacheService);

  totalStartups$ = this.dataCache.getStartups$().pipe(map(list => list.length));

  projectViews = signal(this.seededMetric(1500, 4500, 'views'));
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