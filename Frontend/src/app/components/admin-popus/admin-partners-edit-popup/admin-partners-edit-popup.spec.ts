import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminPartnersEditPopup } from './admin-partners-edit-popup';

describe('AdminPartnersEditPopup', () => {
  let component: AdminPartnersEditPopup;
  let fixture: ComponentFixture<AdminPartnersEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminPartnersEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminPartnersEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
