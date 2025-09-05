import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterLink, Router} from "@angular/router";
import {firstValueFrom} from 'rxjs';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './register-page.html',
  styleUrls: ['./register-page.css', './../auth-shared.css'],
})
export class RegisterPage {
  role = '';
  name= '';
  email = '';
  password = '';
  confirm = '';

  loading = false;
  error: string | null = null;

  roles = ['investor', 'founder'];
  phase: 'request' | 'verify' | 'complete' = 'request';

  code = '';
  info: string | null = null;

  constructor(private backend: BackendInterface, private router: Router) {}

  get passwordsMatch() {
    return this.password && this.password === this.confirm;
  }

  private inferNameFromEmail(email: string): string {
    const local = email.split('@')[0] || '';
    return local || 'User';
  }

  async onSubmit() {
    this.error = null;
    this.info = null;

    if (this.phase === 'request') {
      if (!this.passwordsMatch) {
        this.error = 'Passwords do not match.';
        return;
      }
      this.loading = true;
      try {
        const email = this.email.trim();
        await firstValueFrom(this.backend.requestRegister(email));
        this.phase = 'verify';
        this.info = 'A verification code has been sent to your email. Please enter it below.';
      } catch (e: any) {
        const detail = e?.error?.detail || e?.message || 'Unknown error';
        this.error = 'Registration failed: ' + detail;
      } finally {
        this.loading = false;
      }
      return;
    }

    if (this.phase === 'verify') {
      if (!this.code) {
        this.error = 'Please enter the verification code.';
        return;
      }
      this.loading = true;
      try {
        const email = this.email.trim();

        const res = await firstValueFrom(
          this.backend.verifyRegisterCode({ email, code: this.code.trim() })
        );

        const pre = res?.pre_fill || {};
        this.name = (pre?.name ?? '')?.trim() || this.inferNameFromEmail(email);
        this.role = (pre?.role ?? '')?.trim() || '';

        this.phase = 'complete';
        this.info = res?.detail || 'Code verified. Please complete your profile.';
      } catch (e: any) {
        const detail = e?.error?.detail || e?.message || 'Unknown error';
        this.error = 'Registration failed: ' + detail;
      } finally {
        this.loading = false;
      }
      return;
    }

    if (this.phase === 'complete') {
      if (!this.name?.trim() || !this.role?.trim()) {
        this.error = 'Please provide a name and select a role.';
        return;
      }
      this.loading = true;
      try {
        const email = this.email.trim();

        await firstValueFrom(
          this.backend.completeRegister({
            email,
            code: this.code.trim(),
            name: this.name.trim(),
            password: this.password,
            role: this.role.trim()
          })
        );

        await this.router.navigateByUrl('/login');
      } catch (e: any) {
        const detail = e?.error?.detail || e?.message || 'Unknown error';
        this.error = 'Registration failed: ' + detail;
      } finally {
        this.loading = false;
      }
    }
  }
}