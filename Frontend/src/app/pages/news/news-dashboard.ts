import { marked } from 'marked';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NewsList } from '../../components/news-list/news-list';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";
import {News} from "../../cores/interfaces/backend/dtos";


@Component({
  selector: 'app-news-dashboard',
  templateUrl: './news-dashboard.html',
  styleUrls: ['./news-dashboard.css'],
  standalone: true,
  imports: [CommonModule, NewsList]
})
export class NewsDashboardComponent implements OnInit {
  newsList: News[] = [];
  selectedNews: News | null = null;
  selectedNewsHtml: string = '';
  loading = true;

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
}
