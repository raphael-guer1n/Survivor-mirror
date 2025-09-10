import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {Event} from "../../cores/interfaces/backend/dtos";

@Component({
  selector: 'app-event-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './event-list.html',
  styleUrl: './event-list.css'
})
export class EventList {
  @Input() items: Event[] = [];
  @Output() eventClicked = new EventEmitter<Event>();

  query = '';
  filterValues: { category: string } = { category: '' };
  sortOrder: 'desc' | 'asc' = 'desc';

  get categories(): string[] {
    const set = new Set(
      this.items.map(n => (n.event_type ?? '').toString().trim()).filter(v => !!v)
    );
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }

  get filtered(): Event[] {
    const q = this.query.trim().toLowerCase();
    let filtered = this.items.filter(n => {
      const matchesQuery = !q || n.name?.toLowerCase().includes(q);
      const matchesCategory = !this.filterValues.category || (n.event_type?.toLowerCase() === this.filterValues.category.toLowerCase());
      return matchesQuery && matchesCategory;
    });
    filtered = filtered.slice().sort((a, b) => {
      const dateA = a.dates ? new Date(a.dates).getTime() : 0;
      const dateB = b.dates ? new Date(b.dates).getTime() : 0;
      return this.sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });
    return filtered;
  }
}
