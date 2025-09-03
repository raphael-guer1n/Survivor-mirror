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
  templateUrl: './startups-page.html',
  styleUrl: './startups-page.css'
})
export class StartupsPage implements OnInit {
  startups: StartupListDTO[] = [];
  loading = true;
  error: string | null = null;

  MAX_STARTUPS_PER_CALL = 100;

  private backend = inject(BackendInterface);
  private destroyRef = inject(DestroyRef);

  ngOnInit(): void {
    this.getNextStartups();
  }

  getNextStartups() : void {
    this.backend
      .getStartups(this.startups.length, this.MAX_STARTUPS_PER_CALL)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: (data) => {
          this.startups = [...this.startups, ...data ?? []]
          if (data.length === this.MAX_STARTUPS_PER_CALL) {
            this.getNextStartups();
          } else {
            this.startups = this.startups.sort((a, b) => a.name.localeCompare(b.name));
            console.log(this.startups.length)
          }
        },
        error: (err) => (this.error = err?.message ?? 'Error during loading startups')
      })
  }

}