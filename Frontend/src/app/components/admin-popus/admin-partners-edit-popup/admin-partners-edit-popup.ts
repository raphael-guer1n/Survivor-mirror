import {Component, EventEmitter, inject, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-admin-partners-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-partners-edit-popup.html',
  styleUrls: ['./admin-partners-edit-popup.css', './../admin-popups.css']
})
export class AdminPartnersEditPopup implements OnChanges {
  @Input() partnerId!: number;
  @Output() closed = new EventEmitter<void>();

  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  loading = false;
  saving = false;
  deleting = false;
  error: string | null = null;

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255)]],
    email: ['', [Validators.email, Validators.maxLength(255)]],
    legal_status: [''],
    address: [''],
    phone: [''],
    partnership_type: [''],
    description: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if ('partnerId' in changes && this.partnerId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.backend.getPartner(this.partnerId).subscribe({
      next: (d: any) => {
        this.form.reset({
          name: d?.name ?? '',
          email: d?.email ?? '',
          legal_status: d?.legal_status ?? '',
          phone: d?.phone ?? '',
          address: d?.address ?? '',
          partnership_type: d?.partnership_type ?? '',
          description: d?.description ?? '',
        });
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Cannot load partner details.';
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
    this.backend.updatePartner(this.partnerId, payload).subscribe({
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
    if (!confirm('Delete partner ?')) return;
    this.deleting = true;
    this.error = null;
    this.backend.deletePartner(this.partnerId).subscribe({
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