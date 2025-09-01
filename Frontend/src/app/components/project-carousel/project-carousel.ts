import { Component, Input, ViewChild, ElementRef, AfterViewInit, signal, OnChanges, SimpleChanges, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProjectCard, ProjectItem } from '../project-card/project-card';

@Component({
  selector: 'app-project-carousel',
  standalone: true,
  imports: [CommonModule, ProjectCard],
  templateUrl: './project-carousel.html',
  styleUrl: './project-carousel.css'
})
export class ProjectCarousel implements AfterViewInit, OnChanges, OnDestroy {
  @Input() projects: ProjectItem[] = [];
  @Input() cardWidth = 320;
  @Input() gap = 16;
  @Input() ariaLabel = 'Carrousel des projets';

  @ViewChild('track', { static: true }) trackRef!: ElementRef<HTMLDivElement>;
  @ViewChild('viewport', { static: true }) viewportRef!: ElementRef<HTMLDivElement>;

  private ro?: ResizeObserver;

  private visibleCount = 1;

  pageIndex = signal(0);

  constructor(private cdr: ChangeDetectorRef) {}

  ngAfterViewInit(): void {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        this.recalculateAndSync({ keepPage: true });
      });
    });

    const viewport = this.viewportRef?.nativeElement;
    if (viewport && 'ResizeObserver' in window) {
      this.ro = new ResizeObserver(() => {
        this.recalculateAndSync({ keepPage: true });
      });
      this.ro.observe(viewport);
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['projects'] || changes['cardWidth'] || changes['gap']) {
      this.recalculateAndSync({ keepPage: false });
    }
  }

  ngOnDestroy(): void {
    if (this.ro) {
      this.ro.disconnect();
      this.ro = undefined;
    }
  }

  get pageCount(): number {
    const total = this.projects?.length ?? 0;
    return Math.max(1, Math.ceil(total / this.visibleCount));
  }

  get canNavigate(): boolean {
    return this.pageCount > 1;
  }

  get pages(): number[] {
    return Array.from({ length: this.pageCount }, (_, i) => i);
  }

  prev(): void {
    this.scrollToPage(this.pageIndex() - 1);
  }

  next(): void {
    this.scrollToPage(this.pageIndex() + 1);
  }

  goToPage(index: number): void {
    this.scrollToPage(index);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      this.prev();
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      this.next();
    }
  }

  updatePageFromScroll(): void {
    const viewport = this.viewportRef?.nativeElement;
    if (!viewport) return;
    const perCard = this.cardWidth + this.gap;
    const approxFirstIndex = Math.round(viewport.scrollLeft / perCard);
    const newPage = Math.floor(approxFirstIndex / Math.max(1, this.visibleCount));
    if (newPage !== this.pageIndex()) {
      this.pageIndex.set(newPage);
      this.cdr.detectChanges();
    }
  }

  private scrollToPage(index: number): void {
    const clamped = Math.max(0, Math.min(index, this.pageCount - 1));
    this.pageIndex.set(clamped);

    const viewport = this.viewportRef?.nativeElement;
    if (!viewport) return;

    const firstItemIndex = clamped * this.visibleCount;
    const x = firstItemIndex * (this.cardWidth + this.gap);
    viewport.scrollTo({ left: x, behavior: 'smooth' });

    this.cdr.detectChanges();
  }

  private recalculateAndSync(options: { keepPage: boolean }): void {
    const prevVisible = this.visibleCount;
    this.updateVisibleCount();

    if (!options.keepPage || this.visibleCount !== prevVisible) {
      this.pageIndex.set(Math.min(this.pageIndex(), this.pageCount - 1));
      this.scrollToPage(this.pageIndex());
    } else {
      this.cdr.detectChanges();
    }
  }

  private updateVisibleCount(): void {
    const viewport = this.viewportRef?.nativeElement;
    if (!viewport) {
      this.visibleCount = 1;
      return;
    }
    const perCard = this.cardWidth + this.gap;
    this.visibleCount = Math.max(1, Math.floor((viewport.clientWidth + this.gap) / perCard));
  }
}
