import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartupList } from './startup-list';

describe('StartupList', () => {
  let component: StartupList;
  let fixture: ComponentFixture<StartupList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StartupList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StartupList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
