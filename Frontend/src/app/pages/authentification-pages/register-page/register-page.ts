import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterLink} from "@angular/router";

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

  get passwordsMatch() {
    return this.password && this.password === this.confirm;
  }

  async onSubmit() {
    this.error = null;
    if (!this.passwordsMatch) {
      this.error = 'Passwords do not match.';
      return;
    }
    this.loading = true;
    try {
      await new Promise((r) => setTimeout(r, 600));
    } catch (e: any) {
      this.error = 'Registration failed: ' + e.message;
    } finally {
      this.loading = false;
    }
  }
}