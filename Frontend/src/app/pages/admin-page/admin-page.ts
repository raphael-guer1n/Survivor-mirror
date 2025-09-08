import {Component, inject, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BackendInterface} from '../../cores/interfaces/backend/backend-interface';
import {AdminStartupEditPopup} from "../../components/admin-popus/admin-startup-edit-popup/admin-startup-edit-popup";
import {FormsModule} from "@angular/forms";
import {
  AdminInvestorEditPopup
} from "../../components/admin-popus/admin-inverstor-edit-popup/admin-investor-edit-popup";
import {AdminPartnersEditPopup} from "../../components/admin-popus/admin-partners-edit-popup/admin-partners-edit-popup";
import {AdminNewsEditPopup} from "../../components/admin-popus/admin-news-edit-popup/admin-news-edit-popup";
import {AdminEventsEditPopup} from "../../components/admin-popus/admin-events-edit-popup/admin-events-edit-popup";
import {AdminUsersEditPopup} from "../../components/admin-popus/admin-users-edit-popup/admin-users-edit-popup";

type EntityType = 'startups' | 'investors' | 'partners' | 'news' | 'events' | 'users';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [CommonModule, AdminStartupEditPopup, FormsModule, AdminPartnersEditPopup, AdminInvestorEditPopup, AdminPartnersEditPopup, AdminNewsEditPopup, AdminInvestorEditPopup, AdminEventsEditPopup, AdminUsersEditPopup],
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
  selectedStartupId = signal<number | null>(null);
  selectedInvestorId = signal<number | null>(null);
  selectedPartnerId = signal<number | null>(null);
  selectedNewsId = signal<number | null>(null);
  selectedEventId = signal<number | null>(null);
  selectedUserId = signal<number | null>(null);
  investors: any[] = [];
  partners: any[] = [];
  news: any[] = [];
  events: any[] = [];
  users: any[] = [];

  ngOnInit(): void {
    this.filtersBy.forEach(k => (this.filterValues[k] ??= ''));
    this.loadForCurrentTab();
  }

  onEntityChange(entity: EntityType) {
    this.selectedEntity.set(entity);
    this.errorMsg.set(null);
    this.loading.set(false);
    this.selectedStartupId.set(null);
    this.selectedInvestorId.set(null);
    this.selectedPartnerId.set(null);
    this.loadForCurrentTab();
  }

  private loadForCurrentTab() {
    const entity = this.selectedEntity();
    if (entity === 'startups') {
      this.loadStartups();
      return;
    }

    if (entity === 'investors') {
      this.loadInvestors();
      return;
    }
    if (entity === 'partners') {
      this.loadPartners();
      return;
    }
    if (entity === 'news') {
      this.loadNews();
      return;
    }
    if (entity === 'events') {
      this.loadEvents();
      return;
    }
    if (entity === 'users') {
      this.loadUsers();
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
        this.errorMsg.set(e?.message ?? 'Failed to load startups.');
        this.loading.set(false);
      }
    });
  }

  private loadInvestors() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getInvestors(0, 500).subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.investors = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Failed to load investors.');
        this.loading.set(false);
      }
    });
  }

  private loadPartners() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getPartners(0, 500).subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.partners = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Failed to load partners.');
        this.loading.set(false);
      }
    });
  }

  private loadNews() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getNews(0, 500).subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.news = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Failed to load news.');
        this.loading.set(false);
      }
    });
  }

  private loadEvents() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getEvents(0, 500).subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.events = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Failed to load events.');
        this.loading.set(false);
      }
    });
  }

  private loadUsers() {
    this.loading.set(true);
    this.errorMsg.set(null);
    this.backend.getUsers().subscribe({
      next: (res: any) => {
        const items = this.normalizeListResponse(res);
        this.users = items ?? [];
        this.loading.set(false);
      },
      error: (e) => {
        this.errorMsg.set(e?.message ?? 'Failed to load users.');
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

  get filteredInvestors(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.investors.filter(i =>
      !q ||
      i.name?.toLowerCase().includes(q) ||
      i.email?.toLowerCase().includes(q) ||
      i.address?.toLowerCase().includes(q) ||
      i.investor_type?.toLowerCase().includes(q) ||
      i.investment_focus?.toLowerCase().includes(q)
    );
  }

  get filteredPartners(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.partners.filter(p =>
      !q ||
      p.name?.toLowerCase().includes(q) ||
      p.email?.toLowerCase().includes(q) ||
      p.address?.toLowerCase().includes(q) ||
      p.partnership_type?.toLowerCase().includes(q)
    );
  }

  get filteredNews(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.news.filter(n =>
      !q ||
      n.title?.toLowerCase().includes(q) ||
      n.location?.toLowerCase().includes(q) ||
      n.category?.toLowerCase().includes(q) ||
      n.description?.toLowerCase().includes(q)
    );
  }

  get filteredEvents(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.events.filter(e =>
      !q ||
      e.name?.toLowerCase().includes(q) ||
      e.location?.toLowerCase().includes(q) ||
      e.event_type?.toLowerCase().includes(q) ||
      e.target_audience?.toLowerCase().includes(q) ||
      e.description?.toLowerCase().includes(q)
    );
  }

  get filteredUsers(): any[] {
    const q = this.query.trim().toLowerCase();
    return this.users.filter(u =>
      !q ||
      u.name?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      u.role?.toLowerCase().includes(q)
    );
  }

  openStartup(id: number) {
    console.debug('[AdminPage] openStartup', id);
    this.selectedStartupId.set(id);
  }

  closeStartup() {
    console.debug('[AdminPage] closeStartup');
    this.selectedStartupId.set(null);
  }

  openInvestor(id: number) {
    console.debug('[AdminPage] openInvestor', id);
    this.selectedInvestorId.set(id);
  }

  closeInvestor() {
    console.debug('[AdminPage] closeInvestor');
    this.selectedInvestorId.set(null);
  }

  openPartner(id: number) {
    console.debug('[AdminPage] openPartner', id);
    this.selectedPartnerId.set(id);
  }

  closePartner() {
    console.debug('[AdminPage] closePartner');
    this.selectedPartnerId.set(null);
  }

  openNews(id: number) {
    console.debug('[AdminPage] openNews', id);
    this.selectedNewsId.set(id);
  }

  closeNews() {
    console.debug('[AdminPage] closeNews');
    this.selectedNewsId.set(null);
  }

  openEvent(id: number) {
    console.debug('[AdminPage] openEvent', id);
    this.selectedEventId.set(id);
  }

  closeEvent() {
    console.debug('[AdminPage] closeEvent');
    this.selectedEventId.set(null);
  }

  openUser(id: number) {
    console.debug('[AdminPage] openUser', id);
    this.selectedUserId.set(id);
  }

  closeUser() {
    console.debug('[AdminPage] closeUser');
    this.selectedUserId.set(null);
  }
  trackById = (_: number, el: any) => el?.id ?? _;
}