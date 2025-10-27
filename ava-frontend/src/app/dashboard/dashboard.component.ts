import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { Router, RouterModule } from '@angular/router';

import { LearningApiService } from '../core/services/learning-api.service';
import { RecApiService } from '../core/services/rec-api.service';
import { AuthService } from '../core/services/auth.service';
import { Course, MyCourse } from '../shared/models/course.model';
import { RecommendationResponse } from '../shared/models/recommendation.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatGridListModule,
    RouterModule
  ],
  template: `
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1>Dashboard</h1>
        <p>Bem-vindo de volta! Continue seu aprendizado.</p>
      </div>

      <div class="dashboard-content">
        <!-- Meus Cursos -->
        <mat-card class="dashboard-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>book</mat-icon>
              Meus Cursos
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngIf="isLoadingMyCourses" class="loading-container">
              <mat-spinner diameter="40"></mat-spinner>
            </div>
            
            <div *ngIf="!isLoadingMyCourses && myCourses.length === 0" class="empty-state">
              <mat-icon>school</mat-icon>
              <p>Você ainda não está matriculado em nenhum curso.</p>
              <button mat-raised-button color="primary" routerLink="/courses">
                Explorar Cursos
              </button>
            </div>
            
            <div *ngIf="!isLoadingMyCourses && myCourses.length > 0" class="courses-grid">
              <mat-card *ngFor="let course of myCourses" 
                        class="course-card"
                        (click)="goToCourse(course.course)">
                <mat-card-header>
                  <mat-card-title>{{ course.course_title }}</mat-card-title>
                  <mat-card-subtitle>{{ course.course_description }}</mat-card-subtitle>
                </mat-card-header>
                <mat-card-content>
                  <div class="course-stats">
                    <span class="stat">
                      <mat-icon>menu_book</mat-icon>
                      {{ course.total_lessons }} lições
                    </span>
                    <span class="stat">
                      <mat-icon>folder</mat-icon>
                      {{ course.total_modules }} módulos
                    </span>
                    <span class="stat" *ngIf="progressPercent[course.course] !== undefined">
                      <mat-icon>trending_up</mat-icon>
                      {{ progressPercent[course.course] }}%
                    </span>
                  </div>
                  <div class="course-tags">
                    <mat-chip *ngFor="let tag of course.course_tags" class="tag-chip">
                      {{ tag }}
                    </mat-chip>
                  </div>
                </mat-card-content>
                <mat-card-actions>
                  <button mat-button color="primary">
                    <mat-icon>play_arrow</mat-icon>
                    Continuar
                  </button>
                </mat-card-actions>
              </mat-card>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Recomendações -->
        <mat-card class="dashboard-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>recommend</mat-icon>
              Recomendações para Você
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngIf="isLoadingRecommendations" class="loading-container">
              <mat-spinner diameter="40"></mat-spinner>
            </div>
            
            <div *ngIf="!isLoadingRecommendations && recommendations.length === 0" class="empty-state">
              <mat-icon>psychology</mat-icon>
              <p>Não há recomendações disponíveis no momento.</p>
            </div>
            
            <div *ngIf="!isLoadingRecommendations && recommendations.length > 0" class="recommendations-list">
              <div *ngFor="let rec of recommendations" class="recommendation-item">
                <div class="recommendation-content">
                  <h3>{{ rec.title }}</h3>
                  <p>{{ rec.reason }}</p>
                  <div class="recommendation-score">
                    <mat-icon>star</mat-icon>
                    <span>{{ (rec.score * 100).toFixed(0) }}% de compatibilidade</span>
                  </div>
                </div>
                <div class="recommendation-actions">
                  <button mat-raised-button color="primary" (click)="viewRecommendation(rec.course_id)">
                    Ver Curso
                  </button>
                </div>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Cursos Populares -->
        <mat-card class="dashboard-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>trending_up</mat-icon>
              Cursos Populares
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngIf="isLoadingPopularCourses" class="loading-container">
              <mat-spinner diameter="40"></mat-spinner>
            </div>
            
            <div *ngIf="!isLoadingPopularCourses && popularCourses.length === 0" class="empty-state">
              <mat-icon>school</mat-icon>
              <p>Não há cursos populares disponíveis.</p>
            </div>
            
            <div *ngIf="!isLoadingPopularCourses && popularCourses.length > 0" class="courses-grid">
              <mat-card *ngFor="let course of popularCourses" 
                        class="course-card"
                        (click)="goToCourse(course.id)">
                <mat-card-header>
                  <mat-card-title>{{ course.title }}</mat-card-title>
                  <mat-card-subtitle>{{ course.description }}</mat-card-subtitle>
                </mat-card-header>
                <mat-card-content>
                  <div class="course-stats">
                    <span class="stat">
                      <mat-icon>menu_book</mat-icon>
                      {{ course.total_lessons }} lições
                    </span>
                    <span class="stat">
                      <mat-icon>folder</mat-icon>
                      {{ course.total_modules }} módulos
                    </span>
                  </div>
                  <div class="course-tags">
                    <mat-chip *ngFor="let tag of course.tags" class="tag-chip">
                      {{ tag }}
                    </mat-chip>
                  </div>
                </mat-card-content>
                <mat-card-actions>
                  <button mat-button color="primary">
                    <mat-icon>visibility</mat-icon>
                    Ver Detalhes
                  </button>
                </mat-card-actions>
              </mat-card>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .dashboard-header {
      text-align: center;
      margin-bottom: 32px;
    }
    
    .dashboard-header h1 {
      font-size: 2.5rem;
      font-weight: 300;
      margin-bottom: 8px;
    }
    
    .dashboard-header p {
      color: #666;
      font-size: 1.1rem;
    }
    
    .dashboard-content {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    .dashboard-card {
      margin-bottom: 24px;
    }
    
    .dashboard-card mat-card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 1.5rem;
    }
    
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
    }
    
    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: #666;
    }
    
    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 16px;
      color: #ccc;
    }
    
    .courses-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }
    
    .course-card {
      cursor: pointer;
      transition: transform 0.2s ease-in-out;
    }
    
    .course-card:hover {
      transform: translateY(-4px);
    }
    
    .course-stats {
      display: flex;
      gap: 16px;
      margin-bottom: 12px;
    }
    
    .stat {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 0.9rem;
      color: #666;
    }
    
    .stat mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }
    
    .course-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }
    
    .tag-chip {
      font-size: 0.8rem;
    }
    
    .recommendations-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .recommendation-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
    }
    
    .recommendation-content h3 {
      margin: 0 0 8px 0;
      font-size: 1.1rem;
    }
    
    .recommendation-content p {
      margin: 0 0 8px 0;
      color: #666;
      font-size: 0.9rem;
    }
    
    .recommendation-score {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 0.8rem;
      color: #4caf50;
    }
    
    .recommendation-score mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }
    
    @media (max-width: 768px) {
      .dashboard-container {
        padding: 16px;
      }
      
      .dashboard-header h1 {
        font-size: 2rem;
      }
      
      .courses-grid {
        grid-template-columns: 1fr;
      }
      
      .recommendation-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  myCourses: MyCourse[] = [];
  popularCourses: Course[] = [];
  recommendations: any[] = [];
  progressPercent: Record<number, number> = {};
  
  isLoadingMyCourses = false;
  isLoadingPopularCourses = false;
  isLoadingRecommendations = false;

  constructor(
    private learningApiService: LearningApiService,
    private recApiService: RecApiService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadMyCourses();
    this.loadPopularCourses();
    this.loadRecommendations();
  }

  loadMyCourses(): void {
    this.isLoadingMyCourses = true;
    this.learningApiService.getMyCourses().subscribe({
      next: (courses) => {
        // Garante arrays definidos para evitar erros em templates
        this.myCourses = (courses || []).map(c => ({
          ...c,
          course_tags: c.course_tags || [],
        }));
        this.isLoadingMyCourses = false;

        // Carrega progresso por curso
        for (const c of this.myCourses) {
          this.learningApiService.getCourseProgress(c.course).subscribe({
            next: (ps) => {
              const done = (ps || []).filter(p => p.completed).length;
              const total = c.total_lessons || 0;
              this.progressPercent[c.course] = total > 0 ? Math.round((done / total) * 100) : 0;
            },
            error: () => {
              this.progressPercent[c.course] = 0;
            }
          });
        }
      },
      error: (error) => {
        console.error('Error loading my courses:', error);
        this.isLoadingMyCourses = false;
      }
    });
  }

  loadPopularCourses(): void {
    this.isLoadingPopularCourses = true;
    this.learningApiService.getCourses(1, 6).subscribe({
      next: (response) => {
        this.popularCourses = (response?.items || []).map(c => ({
          ...c,
          tags: c.tags || [],
        }));
        this.isLoadingPopularCourses = false;
      },
      error: (error) => {
        console.error('Error loading popular courses:', error);
        this.isLoadingPopularCourses = false;
      }
    });
  }

  loadRecommendations(): void {
    this.isLoadingRecommendations = true;
    const user = this.authService.getCurrentUser();
    
    if (user && user.id) {
      this.recApiService.getUserRecommendations(user.id, 5).subscribe({
        next: (response) => {
          this.recommendations = response?.recommendations || [];
          this.isLoadingRecommendations = false;
        },
        error: (error) => {
          console.error('Error loading recommendations:', error);
          this.isLoadingRecommendations = false;
        }
      });
    } else {
      this.isLoadingRecommendations = false;
    }
  }

  goToCourse(courseId: number): void {
    this.router.navigate(['/courses', courseId]);
  }

  viewRecommendation(courseId: number): void {
    this.router.navigate(['/courses', courseId]);
  }
}
