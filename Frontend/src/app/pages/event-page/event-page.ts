import { marked } from 'marked';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EventList } from '../../components/event-list/event-list';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";
import {Event} from "../../cores/interfaces/backend/dtos";
import {EventCalendar} from "../../components/event-calendar/event-calendar";

@Component({
  selector: 'app-event-page',
  templateUrl: './event-page.html',
  styleUrls: ['./event-page.css'],
  standalone: true,
  imports: [CommonModule, EventList, EventCalendar, EventCalendar]
})
export class eventDashboardComponent implements OnInit {
  eventList: Event[] = [];
  selectedEvent: Event | null = null;
  selectedEventHtml: string = '';
  loading = true;
  viewMode: 'list' | 'calendar' = 'list';
  selectedDateISO: string | null = null;
  filteredEvent: Event[] | null = null;

  constructor(private backend: BackendInterface) {}

  ngOnInit() {
    this.backend.getEvents().subscribe({
      next: (data) => {
        this.eventList = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    })
  }

  async openEvent(event: Event) {
    this.loading = true;
    this.backend.getEvent(event.id).subscribe({
      next: async (fullEvent) => {
        this.selectedEvent = { ...event, ...fullEvent };
        this.selectedEventHtml = await marked.parse(this.selectedEvent.description || '');
        this.loading = false;
      },
      error: async () => {
        this.selectedEvent = event;
        this.selectedEventHtml = await marked.parse(event.description || '');
        this.loading = false;
      }
    });
  }

  closeEvent() {
    this.selectedEvent = null;
    this.selectedEventHtml = '';
  }

  onCalendarDateSelected(dateISO: string) {
    this.selectedDateISO = dateISO;
    this.selectedEvent = null;
    this.selectedEventHtml = '';
    this.filteredEvent = this.eventList.filter(n => {
      const nd = n.dates?.slice(0, 10) || null;
      return nd === dateISO;
    });
    this.viewMode = 'list';
  }

  clearDateFilter() {
    this.selectedDateISO = null;
    this.filteredEvent = null;
  }

  get activeEventList(): Event[] {
    return this.filteredEvent ?? this.eventList;
  }
}
