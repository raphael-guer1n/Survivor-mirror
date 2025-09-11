import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import { BehaviorSubject, Subscription } from 'rxjs';
import { User } from '../../cores/interfaces/backend/dtos';
import {AuthService} from "../../cores/services/auth-service/auth";

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