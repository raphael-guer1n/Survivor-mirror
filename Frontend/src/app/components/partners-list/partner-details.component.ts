import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Partner } from '../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-partner-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './partner-details.component.html',
  styleUrl: './partner-details.component.css'
})
export class PartnerDetailsComponent {
  @Input() partner: Partner | null = null;
}
