import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const httpErrorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);
  const router = inject(Router);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Ocorreu um erro inesperado';

      if (error.error instanceof ErrorEvent) {
        // Erro do cliente
        errorMessage = `Erro: ${error.error.message}`;
      } else {
        // Erro do servidor
        switch (error.status) {
          case 400:
            errorMessage = error.error?.message || 'Dados inválidos';
            break;
          case 401:
            errorMessage = 'Não autorizado. Faça login novamente.';
            authService.logout();
            router.navigate(['/auth/login']);
            break;
          case 403:
            errorMessage = 'Acesso negado. Você não tem permissão para esta ação.';
            break;
          case 404:
            errorMessage = 'Recurso não encontrado';
            break;
          case 409:
            errorMessage = error.error?.message || 'Conflito de dados';
            break;
          case 422:
            errorMessage = error.error?.message || 'Dados inválidos';
            break;
          case 500:
            errorMessage = 'Erro interno do servidor';
            break;
          case 503:
            errorMessage = 'Serviço temporariamente indisponível';
            break;
          default:
            errorMessage = error.error?.message || `Erro ${error.status}: ${error.statusText}`;
        }
      }

      // Mostrar notificação de erro
      snackBar.open(errorMessage, 'Fechar', {
        duration: 5000,
        panelClass: ['error-snackbar']
      });

      return throwError(() => error);
    })
  );
};
