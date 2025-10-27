import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router, RouterModule } from '@angular/router';

import { RecApiService } from '../core/services/rec-api.service';
import { AuthService } from '../core/services/auth.service';
import { Recommendation } from '../shared/models/recommendation.model';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title"><mat-icon>recommend</mat-icon> Recomendações</h1>

      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div *ngIf="!isLoading && recommendations.length === 0" class="empty-state">
        <mat-icon>psychology</mat-icon>
        <p>Não há recomendações no momento.</p>
      </div>

      <div *ngIf="!isLoading && recommendations.length > 0" class="recommendations-list">
        <mat-card *ngFor="let rec of recommendations" class="rec-card">
          <mat-card-title>{{ rec.title }}</mat-card-title>
          <mat-card-subtitle>
            <mat-icon>star</mat-icon>
            {{ (rec.score * 100).toFixed(0) }}% de compatibilidade
          </mat-card-subtitle>
          <mat-card-content>
            <p>{{ rec.reason }}</p>
          </mat-card-content>
          <mat-card-actions>
            <a mat-button color="primary" [routerLink]="['/courses', rec.course_id]">
              Ver curso
            </a>
          </mat-card-actions>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .page-container { max-width: 900px; margin: 0 auto; padding: 20px; }
    .page-title { display: flex; align-items: center; gap: 8px; font-weight: 400; }
    .loading-container { display: flex; justify-content: center; align-items: center; height: 200px; }
    .empty-state { text-align: center; padding: 40px 20px; color: #666; }
    .empty-state mat-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 16px; color: #ccc; }
    .recommendations-list { display: flex; flex-direction: column; gap: 12px; }
  `]
})
export class RecommendationsComponent implements OnInit {
  recommendations: Recommendation[] = [];
  isLoading = false;

  constructor(private recApi: RecApiService, private auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.loadRecommendations();
  }

  loadRecommendations(): void {
    this.isLoading = true;
    const user = this.auth.getCurrentUser();
    if (!user?.id) {
      this.recommendations = [];
      this.isLoading = false;
      return;
    }

    this.recApi.getUserRecommendations(user.id, 10).subscribe({
      next: (res) => {
        this.recommendations = res.recommendations || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar recomendações', err);
        this.recommendations = [];
        this.isLoading = false;
      }
    });
  }
}
