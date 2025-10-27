import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'auth',
    loadChildren: () => import('./auth/auth.routes').then(m => m.authRoutes)
  },
  // Cursos (lista)
  {
    path: 'courses',
    loadComponent: () => import('./courses/courses.component').then(m => m.CoursesComponent)
  },
  {
    path: 'courses/:id',
    redirectTo: 'courses'
  },
  // Meus cursos (requer login)
  {
    path: 'my-courses',
    loadComponent: () => import('./my-courses/my-courses.component').then(m => m.MyCoursesComponent),
    canActivate: [authGuard]
  },
  // Recomendações (requer login)
  {
    path: 'recommendations',
    loadComponent: () => import('./recommendations/recommendations.component').then(m => m.RecommendationsComponent),
    canActivate: [authGuard]
  },
  // Progresso (requer login)
  {
    path: 'progress',
    loadComponent: () => import('./progress/progress.component').then(m => m.ProgressComponent),
    canActivate: [authGuard]
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: '**',
    loadComponent: () => import('./shared/components/not-found/not-found.component').then(m => m.NotFoundComponent)
  }
];
