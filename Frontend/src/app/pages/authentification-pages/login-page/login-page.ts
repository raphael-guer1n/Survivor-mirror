import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../../cores/services/auth-service/auth';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './login-page.html',
  styleUrls: ['./login-page.css', './../auth-shared.css'],
})
export class LoginPage {
  email = '';
  password = '';
  loading = false;
  error: string | null = null;

  constructor(private auth: AuthService, private router: Router) {}

  async onSubmit() {
    this.error = null;
    this.loading = true;
    try {
      await firstValueFrom(
        this.auth.login(this.email.trim(), this.password)
      );
      await this.router.navigateByUrl('/');
    } catch (e: any) {
      const detail = e?.error?.detail || e?.message || 'Unknown error';
      this.error = 'Connexion failed: ' + detail;
    } finally {
      this.loading = false;
    }
  }
}