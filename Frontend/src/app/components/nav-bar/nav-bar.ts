import { Component, Input, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../cores/services/auth-service/auth';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import {NgOptimizedImage} from "@angular/common";

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, NgOptimizedImage],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar {
  @Input() title = 'App';
  readonly menuOpen = signal(false);

  constructor(private auth: AuthService) {
    this.isAuth = toSignal(
      this.auth.user$.pipe(map(u => !!u)),
      { initialValue: this.auth.isAuthenticated }
    );
    this.isAdmin = toSignal(
      this.auth.user$.pipe(map(u => u?.role === 'admin')),
      { initialValue: false }
    );
  }

  readonly isAuth;
  readonly isAdmin;

  toggleMenu() {
    this.menuOpen.update(v => !v);
  }
  closeMenu() {
    this.menuOpen.set(false);
  }
}