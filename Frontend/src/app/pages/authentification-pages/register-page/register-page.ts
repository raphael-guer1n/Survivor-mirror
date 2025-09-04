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
  email = '';
  password = '';
  confirm = '';
  loading = false;
  error: string | null = null;
  phase: 'request' | 'verify' = 'request';
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
        const name = this.inferNameFromEmail(email);

        await firstValueFrom(this.backend.verifyRegisterCode({ email, code: this.code.trim() }));

        await firstValueFrom(
          this.backend.completeRegister({
            email,
            code: this.code.trim(),
            name,
            password: this.password
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