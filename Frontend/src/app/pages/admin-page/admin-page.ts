import { Component, inject, signal } from '@angular/core';
import { CommonModule, JsonPipe } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";

type EntityType = 'startups' | 'investors' | 'partners' | 'news' | 'events' | 'users';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, JsonPipe],
  templateUrl: './admin-page.html',
  styleUrl: './admin-page.css'
})
export class AdminPage {
  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  entities: EntityType[] = ['startups', 'investors', 'partners', 'news', 'events', 'users'];
  selectedEntity = signal<EntityType>('startups');

  listResult = signal<any>(null);
  itemResult = signal<any>(null);
  actionResult = signal<any>(null);
  errorMsg = signal<string | null>(null);
  loading = signal<boolean>(false);

  form: FormGroup = this.fb.group({
    id: [''],
    skip: [0],
    limit: [20],
    payload: ['{\n  \n}', Validators.required]
  });

  onEntityChange(entity: EntityType) {
    this.selectedEntity.set(entity);
    this.clearResults();
  }

  list() {
    this.clearResults();
    const skip = Number(this.form.value.skip ?? 0) || 0;
    const limit = Number(this.form.value.limit ?? 20) || 20;
    this.loading.set(true);

    const entity = this.selectedEntity();
    let obs: Observable<any>;
    switch (entity) {
      case 'startups':
        obs = this.backend.getStartups(skip, limit);
        break;
      case 'investors':
        obs = this.backend.getInvestors(skip, limit);
        break;
      case 'partners':
        obs = this.backend.getPartners(skip, limit);
        break;
      case 'news':
        obs = this.backend.getNews(skip, limit);
        break;
      case 'events':
        obs = this.backend.getEvents(skip, limit);
        break;
      case 'users':
        obs = this.backend.getUsers();
        break;
      default:
        this.loading.set(false);
        return;
    }

    obs
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.listResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  getById() {
    this.clearResults();
    const id = Number(this.form.value.id);
    if (!id && id !== 0) {
      this.errorMsg.set('Veuillez renseigner un ID valide.');
      return;
    }
    this.loading.set(true);

    const entity = this.selectedEntity();
    let obs: Observable<any>;
    switch (entity) {
      case 'startups':
        obs = this.backend.getStartup(id);
        break;
      case 'investors':
        obs = this.backend.getInvestor(id);
        break;
      case 'partners':
        obs = this.backend.getPartner(id);
        break;
      case 'news':
        obs = this.backend.getNewsItem(id);
        break;
      case 'events':
        obs = this.backend.getEvent(id);
        break;
      case 'users':
        obs = this.backend.getUser(id);
        break;
      default:
        this.loading.set(false);
        return;
    }

    obs
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.itemResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  create() {
    this.clearResults();
    const payload = this.parsePayload();
    if (payload == null) return;

    this.loading.set(true);
    const entity = this.selectedEntity();
    let obs: Observable<any>;
    switch (entity) {
      case 'startups':
        obs = this.backend.createStartup(payload);
        break;
      case 'investors':
        obs = this.backend.createInvestor(payload);
        break;
      case 'partners':
        obs = this.backend.createPartner(payload);
        break;
      case 'news':
        obs = this.backend.createNews(payload);
        break;
      case 'events':
        obs = this.backend.createEvent(payload);
        break;
      case 'users':
        obs = this.backend.createUser(payload);
        break;
      default:
        this.loading.set(false);
        return;
    }

    obs
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.actionResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  update() {
    this.clearResults();
    const id = Number(this.form.value.id);
    if (!id && id !== 0) {
      this.errorMsg.set('Veuillez renseigner un ID valide pour la mise à jour.');
      return;
    }
    const payload = this.parsePayload();
    if (payload == null) return;

    this.loading.set(true);
    const entity = this.selectedEntity();
    let obs: Observable<any>;
    switch (entity) {
      case 'startups':
        obs = this.backend.updateStartup(id, payload);
        break;
      case 'investors':
        obs = this.backend.updateInvestor(id, payload);
        break;
      case 'partners':
        obs = this.backend.updatePartner(id, payload);
        break;
      case 'news':
        obs = this.backend.updateNews(id, payload);
        break;
      case 'events':
        obs = this.backend.updateEvent(id, payload);
        break;
      case 'users':
        obs = this.backend.updateUser(id, payload);
        break;
      default:
        this.loading.set(false);
        return;
    }

    obs
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.actionResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  delete() {
    this.clearResults();
    const id = Number(this.form.value.id);
    if (!id && id !== 0) {
      this.errorMsg.set('Veuillez renseigner un ID valide pour la suppression.');
      return;
    }

    this.loading.set(true);
    const entity = this.selectedEntity();
    let obs: Observable<any>;
    switch (entity) {
      case 'startups':
        obs = this.backend.deleteStartup(id);
        break;
      case 'investors':
        obs = this.backend.deleteInvestor(id);
        break;
      case 'partners':
        obs = this.backend.deletePartner(id);
        break;
      case 'news':
        obs = this.backend.deleteNews(id);
        break;
      case 'events':
        obs = this.backend.deleteEvent(id);
        break;
      case 'users':
        obs = this.backend.deleteUser(id);
        break;
      default:
        this.loading.set(false);
        return;
    }

    obs
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.actionResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  sync() {
    this.clearResults();
    this.loading.set(true);
    this.backend.adminSync()
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (res: any) => this.actionResult.set(res),
        error: (err: any) => this.handleError(err)
      });
  }

  private parsePayload(): any | null {
    const raw = this.form.value.payload;
    if (!raw || typeof raw !== 'string') {
      this.errorMsg.set('Veuillez fournir un JSON valide dans le payload.');
      return null;
    }
    try {
      return JSON.parse(raw);
    } catch (e: any) {
      this.errorMsg.set('Payload JSON invalide: ' + (e?.message ?? e));
      return null;
    }
  }

  private handleError(err: any) {
    const msg = typeof err === 'string'
      ? err
      : (err?.message || err?.error?.detail || 'Une erreur est survenue.');
    this.errorMsg.set(msg);
  }

  private clearResults() {
    this.listResult.set(null);
    this.itemResult.set(null);
    this.actionResult.set(null);
    this.errorMsg.set(null);
  }

  protected readonly HTMLSelectElement = HTMLSelectElement;
}