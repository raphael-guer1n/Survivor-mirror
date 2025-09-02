import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import type { StartupList as StartupListDTO } from '../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-startup-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './startup-list.html',
  styleUrl: './startup-list.css'
})
export class StartupList {
  @Input() items: StartupListDTO[] = [];

  query = '';
  maturityFilter: string = '';

  get maturities(): string[] {
    const set = new Set(
      this.items
        .map(s => (s.maturity || '').trim())
        .filter(v => !!v)
    );
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }

  get filtered(): StartupListDTO[] {
    const q = this.query.trim().toLowerCase();
    const mf = this.maturityFilter.trim().toLowerCase();

    return this.items.filter(s => {
      const matchesQuery =
        !q ||
        (s.name?.toLowerCase().includes(q)) ||
        (s.email?.toLowerCase().includes(q)) ||
        (s.sector?.toLowerCase().includes(q));

      const sMaturity = (s.maturity || '').trim().toLowerCase();
      const matchesMaturity = !mf || sMaturity === mf;

      return matchesQuery && matchesMaturity;
    });
  }
}
