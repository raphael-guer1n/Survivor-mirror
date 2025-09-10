import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-home',
  imports: [RouterLink, CommonModule],
  standalone: true,
  templateUrl: './home-page.html',
  styleUrl: './home-page.css'
})
export class HomePage implements OnInit {
  startupsCount: number|null = null;
  partnersCount: number|null = null;
  eventsCount: number|null = null;
  loadingStats = true;

  mostViewedStartups: any[] = [];
  loadingMostViewed = true;
  infiniteMostViewed: any[] = [];
  private scrollInterval: any = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadingStats = true;
    this.loadingMostViewed = true;
    Promise.all([
      this.http.get<any[]>('/api/startups/').toPromise(),
      this.http.get<any[]>('/api/partners/').toPromise(),
      this.http.get<any[]>('/api/events/').toPromise(),
      this.http.get<any[]>('/api/startups/most-viewed?limit=10').toPromise(),
    ]).then(([startups, partners, events, mostViewed]) => {
      this.startupsCount = (startups ?? []).length;
      this.partnersCount = (partners ?? []).length;
      this.eventsCount = (events ?? []).length;
      this.mostViewedStartups = mostViewed ?? [];
      this.infiniteMostViewed = [...this.mostViewedStartups, ...this.mostViewedStartups];
      this.loadingStats = false;
      this.loadingMostViewed = false;
      setTimeout(() => this.startInfiniteScroll(), 500);
    }).catch(() => {
      this.loadingStats = false;
      this.loadingMostViewed = false;
    });
  }

  startInfiniteScroll() {
    const container = document.querySelector('.most-viewed-scroll') as HTMLElement | null;
    if (!container) return;
    let scrollAmount = 1.2;
    this.scrollInterval = setInterval(() => {
      if (container.scrollLeft + container.offsetWidth >= container.scrollWidth) {
        container.scrollLeft = 0;
      } else {
        container.scrollLeft += scrollAmount;
      }
    }, 18);
  }

  pauseInfiniteScroll() {
    if (this.scrollInterval) {
      clearInterval(this.scrollInterval);
      this.scrollInterval = null;
    }
  }
  resumeInfiniteScroll() {
    if (!this.scrollInterval) {
      this.startInfiniteScroll();
    }
  }
}
