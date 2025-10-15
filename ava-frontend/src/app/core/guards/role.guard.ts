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
  // Nota: Esta implementação assume que o role está armazenado no token JWT
  // ou que há um endpoint para verificar o role do usuário
  const userRole = authService.getUserRole();
  
  if (!userRole || !requiredRoles.includes(userRole)) {
    router.navigate(['/dashboard']);
    return false;
  }

  return true;
};
