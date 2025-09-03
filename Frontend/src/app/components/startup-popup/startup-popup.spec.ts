import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartupPopup } from './startup-popup';

describe('StartupPopup', () => {
  let component: StartupPopup;
  let fixture: ComponentFixture<StartupPopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StartupPopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StartupPopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
