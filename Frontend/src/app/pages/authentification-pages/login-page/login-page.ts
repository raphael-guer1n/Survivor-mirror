import {Component} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {RouterLink, Router} from "@angular/router";
import {firstValueFrom} from 'rxjs';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

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

  constructor(private backend: BackendInterface, private router: Router) {}

  async onSubmit() {
    this.error = null;
    this.loading = true;
    try {
      await firstValueFrom(
        this.backend.login({ email: this.email.trim(), password: this.password })
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