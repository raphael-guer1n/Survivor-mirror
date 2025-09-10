import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminInvestorEditPopup } from './admin-investor-edit-popup.component';

describe('AdminInverstorEditPopup', () => {
  let component: AdminInvestorEditPopup;
  let fixture: ComponentFixture<AdminInvestorEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminInvestorEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminInvestorEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
