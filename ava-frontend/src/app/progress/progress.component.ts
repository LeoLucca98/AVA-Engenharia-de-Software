import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LearningApiService } from '../core/services/learning-api.service';
import { Progress } from '../shared/models/progress.model';

@Component({
  selector: 'app-progress',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title"><mat-icon>trending_up</mat-icon> Meu Progresso</h1>

      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div *ngIf="!isLoading && progress.length === 0" class="empty-state">
        <mat-icon>hourglass_empty</mat-icon>
        <p>Nenhum progresso encontrado ainda.</p>
      </div>

      <div *ngIf="!isLoading && progress.length > 0" class="progress-list">
        <mat-card *ngFor="let p of progress" class="progress-item">
          <mat-card-title>{{ p.course_title }} • {{ p.module_title }}</mat-card-title>
          <mat-card-subtitle>{{ p.lesson_title }}</mat-card-subtitle>
          <mat-card-content>
            <div class="details">
              <span class="badge" [class.done]="p.completed">
                <mat-icon>{{ p.completed ? 'check_circle' : 'radio_button_unchecked' }}</mat-icon>
                {{ p.completed ? 'Concluída' : 'Pendente' }}
              </span>
              <span class="info"><mat-icon>schedule</mat-icon> {{ p.time_spent }}s</span>
              <span class="info" *ngIf="p.score !== undefined"><mat-icon>grade</mat-icon> {{ p.score }}</span>
            </div>
          </mat-card-content>
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
    .progress-list { display: flex; flex-direction: column; gap: 12px; }
    .details { display: flex; gap: 12px; align-items: center; color: #666; }
    .badge { display: inline-flex; align-items: center; gap: 4px; }
    .badge.done { color: #4caf50; }
    .info mat-icon, .badge mat-icon { font-size: 16px; width: 16px; height: 16px; }
  `]
})
export class ProgressComponent implements OnInit {
  progress: Progress[] = [];
  isLoading = false;

  constructor(private learningApi: LearningApiService) {}

  ngOnInit(): void {
    this.loadProgress();
  }

  loadProgress(): void {
    this.isLoading = true;
    this.learningApi.getMyProgress().subscribe({
      next: (res) => {
        this.progress = res || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar progresso', err);
        this.progress = [];
        this.isLoading = false;
      }
    });
  }
}
