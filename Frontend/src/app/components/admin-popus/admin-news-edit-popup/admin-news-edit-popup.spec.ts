import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminNewsEditPopup } from './admin-news-edit-popup';

describe('AdminNewsEditPopup', () => {
  let component: AdminNewsEditPopup;
  let fixture: ComponentFixture<AdminNewsEditPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminNewsEditPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminNewsEditPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
