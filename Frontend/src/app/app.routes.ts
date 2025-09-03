import {Routes} from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/home-page/home-page').then((m) => m.HomePage),
  },
  {
    path: 'startups',
    loadComponent: () =>
      import('./pages/startups-page/startups-page').then((m) => m.StartupsPage),
  },
];
