import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartupsPage } from './startups-page.component';

describe('Startups', () => {
  let component: StartupsPage;
  let fixture: ComponentFixture<StartupsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StartupsPage]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StartupsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
