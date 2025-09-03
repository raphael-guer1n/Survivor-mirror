import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BackendInterface} from '../../cores/interfaces/backend/backend-interface';
import type {StartupDetail} from '../../cores/interfaces/backend/dtos';

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
  founderImages: Record<number, string> = {};

  constructor(private backend: BackendInterface) {
  }

  ngOnChanges(_changes: SimpleChanges): void {
    if ('startupId' in _changes && this.startupId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.data = null;
    this.clearFounderImages();

    this.backend.getStartup(this.startupId).subscribe({
      next: (d) => {
        this.data = d;
        this.loading = false;
        this.loadFounderImages();
      },
      error: (e) => {
        this.error = 'Cannot load startup details.';
        this.loading = false;
        console.error(e);
      }
    });
  }

  private loadFounderImages(): void {
    if (!this.data?.founders?.length) return;

    for (const f of this.data.founders) {
      this.backend.getFounderImage(this.startupId, f.id).subscribe({
        next: (blob: Blob) => {
          this.founderImages[f.id] = URL.createObjectURL(blob);
        },
        error: (e) => {
          console.warn('Founder image not found', f.id, e);
        }
      });
    }
  }

  private clearFounderImages(): void {
    for (const id of Object.keys(this.founderImages)) {
      const url = this.founderImages[+id];
      if (url?.startsWith('blob:')) {
        URL.revokeObjectURL(url);
      }
    }
    this.founderImages = {};
  }

  close(): void {
    this.clearFounderImages();
    this.closed.emit();
  }
}