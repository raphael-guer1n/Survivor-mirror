
import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BackendInterface } from '../../cores/interfaces/backend/backend-interface';
import { Partner } from '../../cores/interfaces/backend/dtos';
import { PartnerDetailsComponent } from './partner-details.component';

@Component({
  selector: 'app-partners-list',
  standalone: true,
  imports: [CommonModule, PartnerDetailsComponent],
  templateUrl: './partners-list.component.html',
  styleUrl: './partners-list.component.css'
})
export class PartnersListComponent implements OnInit {
  partners: Partner[] = [];
  loading = true;
  error: string | null = null;
  selectedPartner: Partner | null = null;

  private backend = inject(BackendInterface);

  ngOnInit() {
    this.backend.getPartners(0, 100).subscribe({
      next: (data) => {
        this.partners = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement des partenaires.';
        this.loading = false;
      }
    });
  }

  showDetails(partner: Partner) {
    this.selectedPartner = partner;
  }

  closeDetails() {
    this.selectedPartner = null;
  }
}
