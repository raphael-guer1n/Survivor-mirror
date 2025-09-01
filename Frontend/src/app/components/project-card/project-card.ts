import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ProjectItem {
  id: string;
  title: string;
  description?: string;
  imageUrl?: string;
  linkUrl?: string;
  tags?: string[];
}

@Component({
  selector: 'app-project-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './project-card.html',
  styleUrl: './project-card.css'
})
export class ProjectCard {
  @Input({ required: true }) project!: ProjectItem;
}
