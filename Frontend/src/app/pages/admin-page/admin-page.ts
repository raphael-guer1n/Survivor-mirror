import {Component, inject, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BackendInterface} from '../../cores/interfaces/backend/backend-interface';
import {AdminStartupEditPopup} from "../../components/admin-startup-edit-popup/admin-startup-edit-popup";
import {FormsModule} from "@angular/forms";

type EntityType = 'startups' | 'investors' | 'partners' | 'news' | 'events' | 'users';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [CommonModule, AdminStartupEditPopup, FormsModule],
  templateUrl: './admin-page.html',
  styleUrl: './admin-page.css'
})
export class AdminPage implements OnInit {
  private backend = inject(BackendInterface);

  entities: EntityType[] = ['startups', 'investors', 'partners', 'news', 'events', 'users'];
  selectedEntity = signal<EntityType>('startups');

  loading = signal<boolean>(false);
  errorMsg = signal<string | null>(null);

  startups: any[] = [];
  query = '';
  filtersBy: string[] = ['sector', 'maturity'];
  filterValues: Record<string, string> = {};
  selectedStartupId: number | null = null;

  ngOnInit(): void {
    this.filtersBy.forEach(k => (this.filterValues[k] ??= ''));
    this.loadForCurrentTab();
  }

  onEntityChange(entity: EntityType) {
    this.selectedEntity.set(entity);
    this.errorMsg.set(null);
    this.loading.set(false);
    this.selectedStartupId = null;
    this.loadForCurrentTab();
  }

  private loadForCurrentTab() {
    const entity = this.selectedEntity();
    if (entity === 'startups') {
      this.loadStartups();
      return;
    }
  }

  private loadStartups() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getStartups(0, 500).subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.startups = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Erreur lors du chargement des startups.');
        this.loading.set(false);
      }
    });
  }

  private normalizeListResponse(res: any): any[] {
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.items)) return res.items;
    if (res && Array.isArray(res.data)) return res.data;
    return [];
  }

  get startupFilters(): string[][] {
    return this.filtersBy.map(field => {
      const set = new Set(
        this.startups
          .map(s => ((s as any)?.[field] ?? '').toString().trim())
          .filter(v => !!v)
      );
      const values = Array.from(set).sort((a, b) => a.localeCompare(b));
      return [field, ...values];
    });
  }

  get filteredStartups(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.startups.filter(s => {
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

  openStartup(id: number) {
    this.selectedStartupId = id;
  }

  closeStartup() {
    this.selectedStartupId = null;
  }

  trackById = (_: number, el: any) => el?.id ?? _;
}