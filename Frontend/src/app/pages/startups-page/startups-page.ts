import {Component, inject, OnInit, DestroyRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {StartupList as StartupListDTO} from '../../cores/interfaces/backend/dtos';
import {StartupList} from '../../components/startup-list/startup-list';
import {finalize} from 'rxjs';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {DataCacheService} from "../../cores/services/data-cache-service/data-cache.service";

@Component({
  selector: 'app-startups',
  imports: [CommonModule, StartupList],
  standalone: true,
  templateUrl: './startups-page.html',
  styleUrl: './startups-page.css'
})
export class StartupsPage implements OnInit {
  startups: StartupListDTO[] = [];
  loading = true;
  error: string | null = null;

  private destroyRef = inject(DestroyRef);
  private dataCache = inject(DataCacheService);

  ngOnInit(): void {
    this.loadFromCache();
  }

  private loadFromCache(): void {
    this.loading = true;
    this.dataCache
      .getStartups$()
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => (this.loading = false)))
      .subscribe({
        next: (list) => {
          this.startups = list ?? [];
          this.error = null;
        },
        error: (err) => (this.error = err?.message ?? 'Error during loading startups')
      });
  }
}