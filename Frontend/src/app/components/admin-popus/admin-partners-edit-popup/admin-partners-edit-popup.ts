import {Component, EventEmitter, inject, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';
import type {Partner} from '../../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-admin-partners-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-partners-edit-popup.html',
  styleUrls: ['./admin-partners-edit-popup.css', './../admin-popups.css']
})
export class AdminPartnersEditPopup implements OnInit, OnChanges {
  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  @Input() partnerId!: number;
  @Input() partner?: Partner | null;

  @Output() closed = new EventEmitter<void>();
  @Output() saved = new EventEmitter<Partner>();

  saving = false;
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

  ngOnInit(): void {
    this.patchFromInput();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['partner'] || changes['partnerId']) {
      this.patchFromInput();
    }
  }

  private patchFromInput(): void {
    this.error = null;
    const d = this.partner;
    if (!d) return;
    this.form.patchValue({
      name: d.name ?? '',
      email: d.email ?? '',
      legal_status: d.legal_status ?? '',
      address: d.address ?? '',
      phone: d.phone ?? '',
      partnership_type: d.partnership_type ?? '',
      description: d.description ?? '',
    }, {emitEvent: false});
  }

  close(): void {
    if (this.saving) return;
    this.closed.emit();
  }

  save(): void {
    if (this.form.invalid || this.saving) return;
    this.saving = true;
    this.error = null;

    const v = this.form.value;
    this.backend.updatePartner(this.partnerId, {
      name: v.name ?? null,
      email: v.email ?? null,
      legal_status: v.legal_status ?? null,
      address: v.address ?? null,
      phone: v.phone ?? null,
      partnership_type: v.partnership_type ?? null,
      description: v.description ?? null,
    }).subscribe({
      next: (updated) => {
        this.saving = false;
        this.saved.emit(updated);
        this.closed.emit();
      },
      error: (e) => {
        this.saving = false;
        this.error = e?.message ?? 'Failed to save partner.';
      }
    });
  }
}