import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/home/home').then((m) => m.Home),
  },
  {
    path: 'projects',
    loadComponent: () =>
      import('./pages/project/project').then((m) => m.Project),
  },
];
