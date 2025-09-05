import {Routes} from '@angular/router';
import {authGuard} from "./cores/guard/auth-guard/auth-guard";

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
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/authentification-pages/login-page/login-page').then((m) => m.LoginPage),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./pages/authentification-pages/register-page/register-page').then((m) => m.RegisterPage),
  },
  {
    path: 'account', canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/account-page/account-page').then((m) => m.AccountPage),
  },
  {
    path: 'news',
    loadComponent: () =>
      import('./pages/news/news-dashboard').then((m) => m.NewsDashboardComponent),
  },
];