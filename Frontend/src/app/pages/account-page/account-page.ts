import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import {AuthService} from "../../cores/services/auth-service/auth";

@Component({
  selector: 'app-account-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './account-page.html',
})
export class AccountPage {
  private auth = inject(AuthService);
  private router = inject(Router);

  user$ = this.auth.user$;

  logout() {
    this.auth.clearSession();
    this.router.navigateByUrl('/login');
  }
}