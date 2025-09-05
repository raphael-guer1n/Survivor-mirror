import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserDashboardPage } from './user-dashboard-page';

describe('UserDashboardPage', () => {
  let component: UserDashboardPage;
  let fixture: ComponentFixture<UserDashboardPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserDashboardPage]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserDashboardPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
