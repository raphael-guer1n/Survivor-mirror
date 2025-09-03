import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import type { StartupDetail } from '../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-startup-popup',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './startup-popup.html',
  styleUrl: './startup-popup.css'
})
export class StartupPopup implements OnChanges {
  @Input() startupId!: number;
  @Output() closed = new EventEmitter<void>();

  loading = false;
  error: string | null = null;
  data: StartupDetail | null = null;

  constructor(private backend: BackendInterface) {}

  ngOnChanges(changes: SimpleChanges): void {
    if ('startupId' in changes && this.startupId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.data = null;

    this.backend.getStartup(this.startupId).subscribe({
      next: (d) => {
        this.data = d;
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Impossible de charger les détails de la startup.';
        this.loading = false;
        console.error(e);
      }
    });
  }

  close(): void {
    this.closed.emit();
  }
}