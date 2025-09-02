import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Startups } from './startups';

describe('Startups', () => {
  let component: Startups;
  let fixture: ComponentFixture<Startups>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Startups]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Startups);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
