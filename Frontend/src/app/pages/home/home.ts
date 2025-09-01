import { Component } from '@angular/core';
import { ProjectCarousel } from '../../components/project-carousel/project-carousel';
import type { ProjectItem } from '../../components/project-card/project-card';
import {RouterLink} from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [ProjectCarousel, RouterLink],
  standalone: true,
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {
  projects: ProjectItem[] = [
    {
      id: 'h1',
      title: 'Portfolio',
      description: 'Sélection de travaux récents.',
      imageUrl: 'https://picsum.photos/seed/h1/800/450',
      linkUrl: 'https://example.com/portfolio',
      tags: ['UI', 'Branding']
    },
    {
      id: 'h2',
      title: 'Landing Marketing',
      description: 'Campagne produit avec A/B testing.',
      imageUrl: 'https://picsum.photos/seed/h2/800/450',
      linkUrl: 'https://example.com/landing',
      tags: ['Marketing', 'A/B']
    },
    {
      id: 'h3',
      title: 'SaaS Dashboard',
      description: 'KPI en temps réel et multi-tenant.',
      imageUrl: 'https://picsum.photos/seed/h3/800/450',
      linkUrl: 'https://example.com/saas',
      tags: ['SaaS', 'Charts']
    }
  ];
}
