import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { Event } from '../../cores/interfaces/backend/dtos';

type DayCell = {
  date: Date;
  inCurrentMonth: boolean;
  iso: string; // YYYY-MM-DD
  hasEvent: boolean;
  count: number;
};

@Component({
  selector: 'app-event-calendar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './event-calendar.html',
  styleUrls: ['./event-calendar.css']
})
export class EventCalendar implements OnChanges {
  @Input() event: Event[] = [];
  @Input() initialMonth?: string; // YYYY-MM (optional)
  @Output() dateSelected = new EventEmitter<string>(); // emits YYYY-MM-DD

  viewYear!: number;
  viewMonth!: number; // 0-11

  weeks: DayCell[][] = [];
  monthLabel = '';
  private eventByDay = new Map<string, number>(); // YYYY-MM-DD -> count

  ngOnChanges(): void {
    this.indexEvent();
    if (this.viewYear == null || this.viewMonth == null) {
      const base = this.initialMonth ? new Date(this.initialMonth + '-01T00:00:00') : new Date();
      this.viewYear = base.getFullYear();
      this.viewMonth = base.getMonth();
    }
    this.buildCalendar();
  }

  prevMonth() {
    if (this.viewMonth === 0) {
      this.viewMonth = 11;
      this.viewYear -= 1;
    } else {
      this.viewMonth -= 1;
    }
    this.buildCalendar();
  }

  nextMonth() {
    if (this.viewMonth === 11) {
      this.viewMonth = 0;
      this.viewYear += 1;
    } else {
      this.viewMonth += 1;
    }
    this.buildCalendar();
  }

  selectDay(cell: DayCell) {
    if (!cell.inCurrentMonth) return;
    this.dateSelected.emit(cell.iso);
  }

  private indexEvent() {
    this.eventByDay.clear();
    for (const n of this.event) {
      const d = n.dates?.slice(0, 10);
      if (!d) continue;
      this.eventByDay.set(d, (this.eventByDay.get(d) ?? 0) + 1);
    }
  }

  private buildCalendar() {
    const firstOfMonth = new Date(this.viewYear, this.viewMonth, 1);
    const lastOfMonth = new Date(this.viewYear, this.viewMonth + 1, 0);
    const startDay = new Date(firstOfMonth);
    startDay.setDate(firstOfMonth.getDate() - ((firstOfMonth.getDay() + 6) % 7)); // Monday-first grid

    const endDay = new Date(lastOfMonth);
    endDay.setDate(lastOfMonth.getDate() + (7 - ((lastOfMonth.getDay() + 6) % 7) - 1));

    this.monthLabel = firstOfMonth.toLocaleString(undefined, { month: 'long', year: 'numeric' });

    const weeks: DayCell[][] = [];
    let cursor = new Date(startDay);
    while (cursor <= endDay) {
      const week: DayCell[] = [];
      for (let i = 0; i < 7; i++) {
        const iso = this.toISODate(cursor);
        const count = this.eventByDay.get(iso) ?? 0;
        week.push({
          date: new Date(cursor),
          inCurrentMonth: cursor.getMonth() === this.viewMonth,
          iso,
          hasEvent: count > 0,
          count,
        });
        cursor.setDate(cursor.getDate() + 1);
      }
      weeks.push(week);
    }
    this.weeks = weeks;
  }

  private toISODate(d: Date): string {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
}