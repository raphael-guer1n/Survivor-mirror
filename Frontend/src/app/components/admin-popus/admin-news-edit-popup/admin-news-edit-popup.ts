import {Component, EventEmitter, inject, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {BackendInterface} from '../../../cores/interfaces/backend/backend-interface';

@Component({
  selector: 'app-admin-news-edit-popup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './admin-news-edit-popup.html',
  styleUrls: ['./admin-news-edit-popup.css', './../admin-popups.css']
})
export class AdminNewsEditPopup implements OnChanges {
  @Input() newsId!: number;
  @Output() closed = new EventEmitter<void>();

  private backend = inject(BackendInterface);
  private fb = inject(FormBuilder);

  loading = false;
  saving = false;
  deleting = false;
  error: string | null = null;

  form = this.fb.group({
    title: ['', [Validators.required, Validators.maxLength(255)]],
    news_date: [''],
    location: [''],
    category: [''],
    startup_id: [0],
    description: [''],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if ('newsId' in changes && this.newsId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.backend.getNewsItem(this.newsId).subscribe({
      next: (d: any) => {
        this.form.reset({
          title: d?.title ?? '',
          news_date: d?.news_date ?? '',
          location: d?.location ?? '',
          category: d?.category ?? '',
          startup_id: d?.startup_id ?? '',
          description: d?.description ?? '',
        });
        this.loading = false;
      },
      error: (e) => {
        this.error = 'Cannot load news details.';
        this.loading = false;
        console.error(e);
      }
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving = true;
    this.error = null;
    const payload = this.form.value;
    this.backend.updateNews(this.newsId, payload).subscribe({
      next: () => {
        this.saving = false;
        this.close();
      },
      error: (e) => {
        this.error = e?.message ?? 'Save failed.';
        this.saving = false;
      }
    });
  }

  remove(): void {
    if (!confirm('Delete news ?')) return;
    this.deleting = true;
    this.error = null;
    this.backend.deleteNews(this.newsId).subscribe({
      next: () => {
        this.deleting = false;
        this.close();
      },
      error: (e) => {
        this.error = e?.message ?? 'Delete failed.';
        this.deleting = false;
      }
    });
  }

  close(): void {
    this.closed.emit();
  }
}