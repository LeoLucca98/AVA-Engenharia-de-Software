import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="not-found-container">
      <mat-card class="not-found-card">
        <mat-card-content class="not-found-content">
          <mat-icon class="not-found-icon">error_outline</mat-icon>
          <h1>404</h1>
          <h2>Página não encontrada</h2>
          <p>A página que você está procurando não existe ou foi movida.</p>
          
          <div class="not-found-actions">
            <button mat-raised-button color="primary" (click)="goHome()">
              <mat-icon>home</mat-icon>
              Ir para o Dashboard
            </button>
            <button mat-button (click)="goBack()">
              <mat-icon>arrow_back</mat-icon>
              Voltar
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .not-found-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    
    .not-found-card {
      max-width: 500px;
      width: 100%;
    }
    
    .not-found-content {
      text-align: center;
      padding: 40px 20px;
    }
    
    .not-found-icon {
      font-size: 80px;
      width: 80px;
      height: 80px;
      color: #f44336;
      margin-bottom: 20px;
    }
    
    .not-found-content h1 {
      font-size: 4rem;
      font-weight: 300;
      margin: 0 0 16px 0;
      color: #333;
    }
    
    .not-found-content h2 {
      font-size: 1.5rem;
      font-weight: 400;
      margin: 0 0 16px 0;
      color: #666;
    }
    
    .not-found-content p {
      font-size: 1rem;
      color: #888;
      margin-bottom: 32px;
      line-height: 1.5;
    }
    
    .not-found-actions {
      display: flex;
      gap: 16px;
      justify-content: center;
      flex-wrap: wrap;
    }
    
    .not-found-actions button {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    @media (max-width: 768px) {
      .not-found-content h1 {
        font-size: 3rem;
      }
      
      .not-found-actions {
        flex-direction: column;
        align-items: center;
      }
      
      .not-found-actions button {
        width: 100%;
        max-width: 200px;
      }
    }
  `]
})
export class NotFoundComponent {
  constructor(private router: Router) {}

  goHome(): void {
    this.router.navigate(['/dashboard']);
  }

  goBack(): void {
    window.history.back();
  }
}
