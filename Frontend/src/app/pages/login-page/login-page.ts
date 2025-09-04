import {Component} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {RouterLink} from "@angular/router";

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css'
})
export class LoginPage {
  email = '';
  password = '';
  loading = false;
  error: string | null = null;

  async onSubmit() {
    this.error = null;
    this.loading = true;
    try {
      await new Promise((r) => setTimeout(r, 600));
    } catch (e: any) {
      this.error = 'Connexion failed: ' + e.message;
    } finally {
      this.loading = false;
    }
  }
}