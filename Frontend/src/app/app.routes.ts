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
  {
    path: 'event',
    loadComponent: () =>
      import('./pages/event-page/event-page').then((m) => m.eventDashboardComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./pages/user-dashboard-page/user-dashboard-page').then((m) => m.UserDashboardPage),
  },
  {
    path: 'admin',
    loadComponent: () =>
      import('./pages/admin-page/admin-page').then((m) => m.AdminPage),
  },
  {
    path: 'about',
    loadComponent: () =>
      import('./pages/about-page/about-page').then((m) => m.AboutPage),
  }
];