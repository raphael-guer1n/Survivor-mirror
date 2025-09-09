import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {BackendInterface} from '../../cores/interfaces/backend/backend-interface';
import type {StartupDetail} from '../../cores/interfaces/backend/dtos';
import {ElementRef, ViewChild} from '@angular/core';

@Component({
  selector: 'app-startup-popup',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './startup-popup.html',
  styleUrl: './startup-popup.css'
})
export class StartupPopup implements OnChanges {
  @Input() startupId!: number;
  @Output() closed = new EventEmitter<void>();

  loading = false;
  error: string | null = null;
  data: StartupDetail | null = null;
  founderImages: Record<number, string> = {};
  @ViewChild('printSection') private printSection?: ElementRef<HTMLElement>;

  constructor(private backend: BackendInterface) {
  }

  ngOnChanges(_changes: SimpleChanges): void {
    if ('startupId' in _changes && this.startupId != null) {
      this.fetch();
    }
  }

  private fetch(): void {
    this.loading = true;
    this.error = null;
    this.data = null;
    this.clearFounderImages();

    this.backend.getStartup(this.startupId).subscribe({
      next: (d) => {
        this.data = d;
        this.loading = false;
        this.loadFounderImages();
      },
      error: (e) => {
        this.error = 'Cannot load startup details.';
        this.loading = false;
        console.error(e);
      }
    });
  }

  private loadFounderImages(): void {
    if (!this.data?.founders?.length) return;

    for (const f of this.data.founders) {
      this.backend.getFounderImage(this.startupId, f.id).subscribe({
        next: (blob: Blob) => {
          this.founderImages[f.id] = URL.createObjectURL(blob);
        },
        error: (e) => {
          console.warn('Founder image not found', f.id, e);
        }
      });
    }
  }

  private clearFounderImages(): void {
    for (const id of Object.keys(this.founderImages)) {
      const url = this.founderImages[+id];
      if (url?.startsWith('blob:')) {
        URL.revokeObjectURL(url);
      }
    }
    this.founderImages = {};
  }

  close(): void {
    this.clearFounderImages();
    this.closed.emit();
  }

  exportPdf(event?: MouseEvent): void {
    event?.stopPropagation();
    const section = this.printSection?.nativeElement;
    if (!section) return;

    const title = this.data?.name ? `Startup - ${this.data.name}` : 'Startup détails';
    const printWindow = window.open('', '_blank', 'width=900,height=1000');
    if (!printWindow) return;

    const styles = `
      :root { --text: #111; --muted: #555; }
      * { box-sizing: border-box; }
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: var(--text); }
      h3 { margin: 0 0 16px; }
      .modal { border: none; box-shadow: none; width: auto; max-height: none; }
      .modal-header, .modal-footer, .icon-btn { display: none !important; }
      .modal-body { padding: 0; }
      .row { display: grid; grid-template-columns: 160px 1fr; gap: 8px; padding: 6px 0; border-bottom: 1px dashed #ddd; }
      .row:last-child { border-bottom: none; }
      .label { font-weight: 600; }
      .muted { color: var(--muted); }
      .founders ul { margin: 0; padding-left: 18px; }
      .founder-photo { vertical-align: middle; border-radius: 50%; margin-right: 8px; }
      a { color: inherit; text-decoration: none; }
      @page { margin: 16mm; }
    `;

    const htmlContent = section.outerHTML;

    const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${title}</title>
  <style>${styles}</style>
</head>
<body>
${htmlContent}
</body>
</html>`;

    const htmlBlob = new Blob([html], {type: 'text/html'});
    const htmlUrl = URL.createObjectURL(htmlBlob);

    const waitForImages = async () => {
      const image = Array.from(printWindow.document.images || []);
      if (image.length === 0) return Promise.resolve();
      await Promise.allSettled(
        image.map(img => new Promise<void>(resolve => {
          if (img.complete) return resolve();
          img.onload = () => resolve();
          img.onerror = () => resolve();
        }))
      );
      return undefined;
    };

    printWindow.addEventListener('load', async () => {
      try {
        await waitForImages();
      } finally {
        printWindow.focus();
        printWindow.print();
        setTimeout(() => {
          try {
            printWindow.close();
          } catch {
          }
          URL.revokeObjectURL(htmlUrl);
        }, 300);
      }
    });

    printWindow.location.href = htmlUrl;
  }
}