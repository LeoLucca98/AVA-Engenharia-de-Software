import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const requiredRoles = route.data?.['roles'] as string[];
  
  if (!requiredRoles || requiredRoles.length === 0) {
    return true;
  }

  if (!authService.isAuthenticated()) {
    router.navigate(['/auth/login'], { 
      queryParams: { returnUrl: state.url } 
    });
    return false;
  }

  const user = authService.getCurrentUser();
  if (!user) {
    router.navigate(['/auth/login']);
    return false;
  }

  // Verificar se o usuário tem pelo menos um dos roles necessários
  const userRoles = authService.getUserRoles();
  
  const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
  
  if (!hasRequiredRole) {
    router.navigate(['/dashboard']);
    return false;
  }

  return true;
};
