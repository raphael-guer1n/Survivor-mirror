import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface News {
  id: number;
  title: string;
  news_date?: string;
  category?: string;
  location?: string;
  startup_id?: number;
  description?: string;
}

@Component({
  selector: 'app-news-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './news-list.html',
  styleUrl: './news-list.css'
})
export class NewsList {
  @Input() items: News[] = [];
  @Input() openNews!: (news: News) => void;

  query = '';
  filterValues: { category: string } = { category: '' };
  sortOrder: 'desc' | 'asc' = 'desc';

  get categories(): string[] {
    const set = new Set(
      this.items.map(n => (n.category ?? '').toString().trim()).filter(v => !!v)
    );
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }

  get filtered(): News[] {
    const q = this.query.trim().toLowerCase();
    let filtered = this.items.filter(n => {
      const matchesQuery = !q || n.title?.toLowerCase().includes(q);
      const matchesCategory = !this.filterValues.category || (n.category?.toLowerCase() === this.filterValues.category.toLowerCase());
      return matchesQuery && matchesCategory;
    });
    filtered = filtered.slice().sort((a, b) => {
      const dateA = a.news_date ? new Date(a.news_date).getTime() : 0;
      const dateB = b.news_date ? new Date(b.news_date).getTime() : 0;
      return this.sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });
    return filtered;
  }
}
