import { marked } from 'marked';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NewsList } from '../../components/news-list/news-list';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";
import {News} from "../../cores/interfaces/backend/dtos";
import {NewsCalendar} from "../../components/news-calendar/news-calendar";

@Component({
  selector: 'app-news-dashboard',
  templateUrl: './news-dashboard.html',
  styleUrls: ['./news-dashboard.css'],
  standalone: true,
  imports: [CommonModule, NewsList, NewsCalendar]
})
export class NewsDashboardComponent implements OnInit {
  newsList: News[] = [];
  selectedNews: News | null = null;
  selectedNewsHtml: string = '';
  loading = true;
  viewMode: 'list' | 'calendar' = 'list';
  selectedDateISO: string | null = null;
  filteredNews: News[] | null = null;

  constructor(private backend: BackendInterface) {}

  ngOnInit() {
    this.backend.getNews().subscribe({
      next: (data) => {
        this.newsList = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    })
  }

  async openNews(news: News) {
    this.loading = true;
    this.backend.getNewsItem(news.id).subscribe({
      next: async (fullNews) => {
        this.selectedNews = { ...news, ...fullNews };
        this.selectedNewsHtml = await marked.parse(this.selectedNews.description || '');
        this.loading = false;
      },
      error: async () => {
        this.selectedNews = news;
        this.selectedNewsHtml = await marked.parse(news.description || '');
        this.loading = false;
      }
    });
  }

  closeNews() {
    this.selectedNews = null;
    this.selectedNewsHtml = '';
  }

  onCalendarDateSelected(dateISO: string) {
    this.selectedDateISO = dateISO;
    this.selectedNews = null;
    this.selectedNewsHtml = '';
    this.filteredNews = this.newsList.filter(n => {
      const nd = n.news_date?.slice(0, 10) || null;
      return nd === dateISO;
    });
    this.viewMode = 'list';
  }

  clearDateFilter() {
    this.selectedDateISO = null;
    this.filteredNews = null;
  }

  get activeNewsList(): News[] {
    return this.filteredNews ?? this.newsList;
  }
}
