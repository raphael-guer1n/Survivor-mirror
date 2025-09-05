import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-admin-startup-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-startup-edit-popup.html',
  styleUrl: './admin-startup-edit-popup.css'
})
export class AdminStartupEditPopup implements OnChanges {
  @Input() startupId!: number;
  @Output() closed = new EventEmitter<void>();

  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  loading = false;
  saving = false;
  deleting = false;
  error: string | null = null;

  form: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: [''],
    sector: [''],
    maturity: [''],
    legal_status: [''],
    phone: [''],
    address: [''],
    website: [''],
    linkedin: [''],
    twitter: [''],
    description: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if ('startupId' in changes && this.startupId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.backend.getStartup(this.startupId).subscribe({
      next: (d: any) => {
        this.form.reset({
          name: d?.name ?? '',
          email: d?.email ?? '',
          sector: d?.sector ?? '',
          maturity: d?.maturity ?? '',
          legal_status: d?.legal_status ?? '',
          phone: d?.phone ?? '',
          address: d?.address ?? '',
          website: d?.website ?? '',
          linkedin: d?.linkedin ?? '',
          twitter: d?.twitter ?? '',
          description: d?.description ?? '',
        });
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Cannot load startup details.';
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
    this.backend.updateStartup(this.startupId, payload).subscribe({
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
    if (!confirm('Delete startup ?')) return;
    this.deleting = true;
    this.error = null;
    this.backend.deleteStartup(this.startupId).subscribe({
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