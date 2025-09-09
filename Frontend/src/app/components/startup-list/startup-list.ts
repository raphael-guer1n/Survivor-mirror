import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import type {StartupList as StartupListDTO} from '../../cores/interfaces/backend/dtos';
import {StartupPopup} from "../startup-popup/startup-popup";
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";

@Component({
  selector: 'app-startup-list',
  standalone: true,
  imports: [CommonModule, FormsModule, StartupPopup],
  templateUrl: './startup-list.html',
  styleUrl: './startup-list.css'
})
export class StartupList {
  @Input() items: StartupListDTO[] = [];

  query = '';
  filtersBy: string[] = ['sector', 'maturity'];
  filterValues: Record<string, string> = {};

  constructor(private backend: BackendInterface) {
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
        (s.address?.toLowerCase().includes(q));

      const matchesAllFilters = this.filtersBy.every(field => {
        const filterVal = (this.filterValues[field] ?? '').trim().toLowerCase();
        if (!filterVal) return true;
        const itemVal = (((s as any)?.[field] ?? '') as string).toString().trim().toLowerCase();
        return itemVal === filterVal;
      });

      return matchesQuery && matchesAllFilters;
    });
  }


  selectedId: number | null = null;

  openDetails(id: number): void {
    this.backend.incrementStartupView(id).subscribe();
    this.selectedId = id;
  }

  closeDetails(): void {
    this.selectedId = null;
  }

}