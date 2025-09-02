import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import type {StartupList as StartupListDTO} from '../../cores/interfaces/backend/dtos';

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
  filtersBy: string[] = ['name', 'email', 'sector', 'maturity'];
  filterValues: Record<string, string> = {};

  constructor() {
    this.filtersBy.forEach(k => (this.filterValues[k] ??= ''));
  }

  get filters(): string[][] {
    return this.filtersBy.map(field => {
      const set = new Set(
        this.items
          .map(s => {
            return ((s as any)?.[field] ?? '').toString().trim();
          })
          .filter(v => !!v)
      );
      const values = Array.from(set).sort((a, b) => a.localeCompare(b));
      return [field, ...values];
    });
  }

  get filtered(): StartupListDTO[] {
    const q = this.query.trim().toLowerCase();

    return this.items.filter(s => {
      const matchesQuery =
        !q ||
        (s.name?.toLowerCase().includes(q)) ||
        (s.email?.toLowerCase().includes(q)) ||
        (s.sector?.toLowerCase().includes(q));

      const matchesAllFilters = this.filtersBy.every(field => {
        const filterVal = (this.filterValues[field] ?? '').trim().toLowerCase();
        if (!filterVal) return true;
        const itemVal = (((s as any)?.[field] ?? '') as string).toString().trim().toLowerCase();
        return itemVal === filterVal;
      });

      return matchesQuery && matchesAllFilters;
    });
  }
}