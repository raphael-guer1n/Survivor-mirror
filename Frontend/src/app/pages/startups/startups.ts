import { Component, inject, OnInit, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StartupList as StartupListDTO } from '../../cores/interfaces/backend/dtos';
import { StartupList } from '../../components/startup-list/startup-list';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import { finalize } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-startups',
  imports: [CommonModule, StartupList],
  standalone: true,
  templateUrl: './startups.html',
  styleUrl: './startups.css'
})
export class Startups implements OnInit {
  startups: StartupListDTO[] = [];
  loading = true;
  error: string | null = null;

  private backend = inject(BackendInterface);
  private destroyRef = inject(DestroyRef);

  ngOnInit(): void {
    console.log('Startups');
    this.backend
      .getStartups(0, 100)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: (data) => (this.startups = data ?? []),
        error: (err) => (this.error = err?.message ?? 'Une erreur est survenue lors du chargement des startups.')
      });
  }
}