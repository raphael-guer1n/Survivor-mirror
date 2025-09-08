import {Component, EventEmitter, inject, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-admin-events-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-events-edit-popup.html',
  styleUrls: ['./admin-events-edit-popup.css', './../admin-popups.css']
})
export class AdminEventsEditPopup implements OnChanges {
  @Input() eventsId!: number;
  @Output() closed = new EventEmitter<void>();

  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  loading = false;
  saving = false;
  deleting = false;
  error: string | null = null;

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255)]],
    dates: [''],
    location: [''],
    description: [''],
    event_type: [''],
    target_audience: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if ('eventsId' in changes && this.eventsId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.backend.getEvent(this.eventsId).subscribe({
      next: (d: any) => {
        this.form.reset({
          name: d.name ?? '',
          dates: d.dates ?? '',
          location: d.location ?? '',
          event_type: d.event_type ?? '',
          target_audience: d.target_audience ?? '',
          description: d.description ?? '',
        });
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Cannot load event details.';
        this.loading = false;
        console.error(e);
      }
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving = true;
    this.error = null;
    const payload = this.form.value;
    this.backend.updateEvent(this.eventsId, payload).subscribe({
      next: () => {
        this.saving = false;
        this.close();
      },
      error: (e) => {
        this.error = e?.message ?? 'Save failed.';
        this.saving = false;
      }
    });
  }

  remove(): void {
    if (!confirm('Delete event ?')) return;
    this.deleting = true;
    this.error = null;
    this.backend.deleteInvestor(this.eventsId).subscribe({
      next: () => {
        this.deleting = false;
        this.close();
      },
      error: (e) => {
        this.error = e?.message ?? 'Delete failed.';
        this.deleting = false;
      }
    });
  }

  close(): void {
    this.closed.emit();
  }
}