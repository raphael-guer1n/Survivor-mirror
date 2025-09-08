import {Component, EventEmitter, inject, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from "../../../cores/interfaces/backend/backend-interface";
import {Investor} from "../../../cores/interfaces/backend/dtos";

@Component({
  selector: 'app-admin-inverstor-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-investor-edit-popup.html',
  styleUrls: ['./admin-investor-edit-popup.css', './../admin-popups.css']
})
export class AdminInvestorEditPopup implements OnInit, OnChanges {
  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  @Input() investorId!: number;
  @Input() investor?: Investor | null;
  
  @Output() closed = new EventEmitter<void>();
  @Output() saved = new EventEmitter<Investor>();

  loading = false;
  saving = false;
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

  ngOnInit(): void {
    this.patchFromInput();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['investor'] || changes['investorId']) {
      this.patchFromInput();
    }
  }

  private patchFromInput(): void {
    this.error = null;
    const data = this.investor;
    if (!data) return;
    this.form.patchValue({
      name: data.name ?? '',
      email: data.email ?? '',
      legal_status: data.legal_status ?? '',
      address: data.address ?? '',
      phone: data.phone ?? '',
      investor_type: data.investor_type ?? '',
      investment_focus: data.investment_focus ?? '',
      description: data.description ?? '',
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
    this.backend.updateInvestor(this.investorId, {
      name: v.name ?? null,
      email: v.email ?? null,
      legal_status: v.legal_status ?? null,
      address: v.address ?? null,
      phone: v.phone ?? null,
      investor_type: v.investor_type ?? null,
      investment_focus: v.investment_focus ?? null,
      description: v.description ?? null,
    }).subscribe({
      next: (updated) => {
        this.saving = false;
        this.saved.emit(updated);
        this.closed.emit();
      },
      error: (e) => {
        this.saving = false;
        this.error = e?.message ?? 'Failed to save investor.';
      }
    });
  }
}