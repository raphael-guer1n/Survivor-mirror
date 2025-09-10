import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-home',
  imports: [RouterLink],
  standalone: true,
  templateUrl: './home-page.html',
  styleUrl: './home-page.css'
})
export class HomePage implements OnInit {
  startupsCount: number|null = null;
  partnersCount: number|null = null;
  eventsCount: number|null = null;
  loadingStats = true;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadingStats = true;
    Promise.all([
      this.http.get<any[]>('/api/startups/').toPromise(),
      this.http.get<any[]>('/api/partners/').toPromise(),
      this.http.get<any[]>('/api/events/').toPromise(),
    ]).then(([startups, partners, events]) => {
      this.startupsCount = (startups ?? []).length;
      this.partnersCount = (partners ?? []).length;
      this.eventsCount = (events ?? []).length;
      this.loadingStats = false;
    }).catch(() => {
      this.loadingStats = false;
    });
  }
}
