import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import { BehaviorSubject, Subscription } from 'rxjs';
import { User } from '../../cores/interfaces/backend/dtos';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import {AuthService} from "../../cores/services/auth-service/auth";
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-account-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './account-page.html',
})
export class AccountPage {
  private auth = inject(AuthService);
  private router = inject(Router);
  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

  editing = false;
  loading = false;
  saving = false;
  error: string | null = null;

  form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.email]],
  });

  private sub?: Subscription;

  constructor() {
    this.sub = this.auth.user$.subscribe(u => this.userSubject.next(u));
  }

  logout() {
    this.auth.clearSession();
    this.router.navigateByUrl('/login');
  }

  startupLoading = false;
  startupSaving = false;
  startupError: string | null = null;
  startupId: number | null = null;
  editingStartup = false;

  startupForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.email]],
    phone: [''],
    legal_status: [''],
    address: [''],
    sector: [''],
    maturity: [''],
    description: [''],
    website_url: [''],
    social_media_url: [''],
    project_status: [''],
    needs: [''],
  });

  ngOnInit() {
    this.user$.subscribe(user => {
      if (user?.id && user.role === 'founder') {
        this.fetchFounderStartup(user.id);
      } else {
        // Clear any founder state if role changes
        this.startupId = null;
        this.editingStartup = false;
      }
    });
  }

  private fetchFounderStartup(userId: number) {
    this.startupLoading = true;
    this.startupError = null;

    this.backend.getUserStartup(userId).subscribe({
      next: us => {
        const sid = us?.startup_id ?? null;
        this.startupId = sid;
        if (!sid) {
          this.startupLoading = false;
          return;
        }
        this.backend.getStartup(sid).subscribe({
          next: s => {
            this.startupForm.reset({
              name: s?.name ?? '',
              email: s?.email ?? '',
              phone: s?.phone ?? '',
              legal_status: s?.legal_status ?? '',
              address: s?.address ?? '',
              sector: s?.sector ?? '',
              maturity: s?.maturity ?? '',
              description: s?.description ?? '',
              website_url: s?.website_url ?? '',
              social_media_url: s?.social_media_url ?? '',
              project_status: s?.project_status ?? '',
              needs: s?.needs ?? '',
            });
            this.startupLoading = false;
          },
          error: (e) => {
            this.startupError = 'Cannot load startup details.';
            this.startupLoading = false;
            console.error(e);
          }
        });
      },
      error: (e) => {
        this.startupError = 'Cannot determine linked startup.';
        this.startupLoading = false;
        console.error(e);
      }
    });
  }

  startEditStartup() {
    if (!this.startupId) return;
    this.editingStartup = true;
    this.startupError = null;
  }

  cancelEditStartup() {
    this.editingStartup = false;
    this.startupError = null;
    const u = this.auth.user;
    if (u?.id) this.fetchFounderStartup(u.id);
  }

  saveStartup() {
    if (!this.startupId) return;
    if (this.startupForm.invalid) {
      this.startupForm.markAllAsTouched();
      return;
    }
    this.startupSaving = true;
    this.startupError = null;

    const payload = {
      name: this.startupForm.value.name ?? null,
      legal_status: this.startupForm.value.legal_status ?? null,
      address: this.startupForm.value.address ?? null,
      email: this.startupForm.value.email ?? null,
      phone: this.startupForm.value.phone ?? null,
      sector: this.startupForm.value.sector ?? null,
      maturity: this.startupForm.value.maturity ?? null,
      description: this.startupForm.value.description ?? null,
      website_url: this.startupForm.value.website_url ?? null,
      social_media_url: this.startupForm.value.social_media_url ?? null,
      project_status: this.startupForm.value.project_status ?? null,
      needs: this.startupForm.value.needs ?? null,
    };

    this.backend.updateStartup(this.startupId, payload).subscribe({
      next: () => {
        this.startupSaving = false;
        this.editingStartup = false;
      },
      error: (e) => {
        this.startupError = e?.message ?? 'Failed to save startup changes.';
        this.startupSaving = false;
      }
    });
  }

  startEdit(user: User | null) {
    if (!user) return;
    this.form.reset({
      name: user.name ?? '',
      email: user.email ?? '',
    });
    this.error = null;
    this.editing = true;
  }

  cancelEdit() {
    this.editing = false;
    this.error = null;
  }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const current = this.userSubject.value;
    if (!current) return;

    this.saving = true;
    this.error = null;

    const payload = {
      name: this.form.value.name ?? null,
      email: this.form.value.email ?? null,
    };

    this.backend.updateUser(current.id, payload).subscribe({
      next: (updated) => {
        this.userSubject.next(updated);
        this.saving = false;
        this.editing = false;
      },
      error: (e) => {
        this.error = e?.message ?? 'Failed to save your changes.';
        this.saving = false;
      }
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }
}