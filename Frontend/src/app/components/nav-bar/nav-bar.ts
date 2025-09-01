import { Component, Input, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar {
  @Input() title = 'App';
  readonly menuOpen = signal(false);

  toggleMenu() {
    this.menuOpen.update(v => !v);
  }
  closeMenu() {
    this.menuOpen.set(false);
  }
}
