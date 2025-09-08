import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminUsersEditPopup } from './admin-users-edit-popup';

describe('AdminUsersEditPopup', () => {
  let component: AdminUsersEditPopup;
  let fixture: ComponentFixture<AdminUsersEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminUsersEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminUsersEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
