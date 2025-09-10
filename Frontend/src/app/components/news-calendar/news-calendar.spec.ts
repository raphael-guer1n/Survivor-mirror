import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewsCalendar } from './news-calendar';

describe('NewsCalendar', () => {
  let component: NewsCalendar;
  let fixture: ComponentFixture<NewsCalendar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewsCalendar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewsCalendar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
