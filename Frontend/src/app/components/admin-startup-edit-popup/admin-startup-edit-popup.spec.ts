import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminStartupEditPopup } from './admin-startup-edit-popup';

describe('AdminStartupEditPopup', () => {
  let component: AdminStartupEditPopup;
  let fixture: ComponentFixture<AdminStartupEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminStartupEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminStartupEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
