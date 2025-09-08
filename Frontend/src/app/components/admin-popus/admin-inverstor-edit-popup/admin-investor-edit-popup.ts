import {Component, EventEmitter, inject, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-admin-investor-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-investor-edit-popup.html',
  styleUrls: ['./admin-investor-edit-popup.css', './../admin-popups.css']
})
export class AdminInvestorEditPopup implements OnChanges {
  @Input() investorId!: number;
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
    investor_type: [''],
    investment_focus: [''],
    description: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if ('investorId' in changes && this.investorId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.backend.getInvestor(this.investorId).subscribe({
      next: (d: any) => {
        this.form.reset({
          name: d.name ?? '',
          email: d.email ?? '',
          legal_status: d.legal_status ?? '',
          address: d.address ?? '',
          phone: d.phone ?? '',
          investor_type: d.investor_type ?? '',
          investment_focus: d.investment_focus ?? '',
          description: d.description ?? '',
        });
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Cannot load inverstor details.';
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
    this.backend.updateInvestor(this.investorId, payload).subscribe({
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
    if (!confirm('Delete investor ?')) return;
    this.deleting = true;
    this.error = null;
    this.backend.deleteInvestor(this.investorId).subscribe({
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