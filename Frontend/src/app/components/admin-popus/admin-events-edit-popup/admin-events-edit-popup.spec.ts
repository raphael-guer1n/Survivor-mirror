import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminEventsEditPopup } from './admin-events-edit-popup';

describe('AdminEventsEditPopup', () => {
  let component: AdminEventsEditPopup;
  let fixture: ComponentFixture<AdminEventsEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminEventsEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminEventsEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
