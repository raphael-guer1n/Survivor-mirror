import { marked } from 'marked';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface News {
  id: number;
  title: string;
  news_date?: string;
  category?: string;
  location?: string;
  startup_id?: number;
  description?: string;
}

@Component({
  selector: 'app-news-dashboard',
  templateUrl: './news-dashboard.html',
  styleUrls: ['./news-dashboard.css'],
  standalone: true,
  imports: [CommonModule]
})
export class NewsDashboardComponent implements OnInit {
  newsList: News[] = [];
  selectedNews: News | null = null;
  selectedNewsHtml: string = '';
  loading = true;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<News[]>('/api/news/').subscribe({
      next: (data) => {
        this.newsList = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  async openNews(news: News) {
    this.loading = true;
    this.http.get<News>(`/api/news/${news.id}/`).subscribe({
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
}
