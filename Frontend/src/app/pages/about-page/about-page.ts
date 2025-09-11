
import { Component } from '@angular/core';
import { PartnersListComponent } from '../../components/partners-list/partners-list.component';

@Component({
  selector: 'app-about-page',
  standalone: true,
  imports: [PartnersListComponent],
  templateUrl: './about-page.html',
  styleUrl: './about-page.css'
})
export class AboutPage {

}
