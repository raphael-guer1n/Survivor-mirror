import { Component } from '@angular/core';
import { DashboardComponent } from '../../components/dashboard/dashboard';

@Component({
  selector: 'app-user-dashboard-page',
  imports: [DashboardComponent],
  standalone: true,
  templateUrl: './user-dashboard-page.html',
  styleUrl: './user-dashboard-page.css'
})
export class UserDashboardPage {

}