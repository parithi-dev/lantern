import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard').then((c) => c.Dashboard),
  },
  {
    path: 'devices',
    loadComponent: () => import('./features/devices/devices').then((c) => c.Devices),
  },
  {
    path: 'bandwidth',
    loadComponent: () => import('./features/bandwidth/bandwidth').then((c) => c.Bandwidth),
  },
  {
    path: 'settings',
    loadComponent: () => import('./features/settings/settings').then((c) => c.Settings),
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];
