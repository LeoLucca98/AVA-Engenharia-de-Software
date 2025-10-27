import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LearningApiService } from '../core/services/learning-api.service';
import { MyCourse } from '../shared/models/course.model';

@Component({
  selector: 'app-my-courses',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title"><mat-icon>book</mat-icon> Meus Cursos</h1>

      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div *ngIf="!isLoading && myCourses.length === 0" class="empty-state">
        <mat-icon>school</mat-icon>
        <p>Você ainda não está matriculado em nenhum curso.</p>
        <a mat-raised-button color="primary" routerLink="/courses">Explorar cursos</a>
      </div>

      <div *ngIf="!isLoading && myCourses.length > 0" class="courses-grid">
        <mat-card *ngFor="let mc of myCourses" class="course-card" (click)="goToCourse(mc.course)">
          <mat-card-header>
            <mat-card-title>{{ mc.course_title }}</mat-card-title>
            <mat-card-subtitle>{{ mc.course_description }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="course-stats">
              <span class="stat"><mat-icon>menu_book</mat-icon>{{ mc.total_lessons }} lições</span>
              <span class="stat"><mat-icon>folder</mat-icon>{{ mc.total_modules }} módulos</span>
            </div>
            <div class="course-tags">
              <mat-chip *ngFor="let tag of mc.course_tags" class="tag-chip">{{ tag }}</mat-chip>
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
    </div>
  `,
  styles: [`
    .page-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
    .page-title { display: flex; align-items: center; gap: 8px; font-weight: 400; }
    .loading-container { display: flex; justify-content: center; align-items: center; height: 200px; }
    .empty-state { text-align: center; padding: 40px 20px; color: #666; }
    .empty-state mat-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 16px; color: #ccc; }
    .courses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
    .course-card { cursor: pointer; }
    .course-stats { display: flex; gap: 16px; margin-bottom: 12px; color: #666; }
    .course-stats mat-icon { font-size: 16px; width: 16px; height: 16px; margin-right: 4px; }
    .course-tags { display: flex; flex-wrap: wrap; gap: 4px; }
  `]
})
export class MyCoursesComponent implements OnInit {
  myCourses: MyCourse[] = [];
  isLoading = false;

  constructor(private learningApi: LearningApiService, private router: Router) {}

  ngOnInit(): void {
    this.loadMyCourses();
  }

  loadMyCourses(): void {
    this.isLoading = true;
    this.learningApi.getMyCourses().subscribe({
      next: (res) => {
        this.myCourses = res || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar meus cursos', err);
        this.myCourses = [];
        this.isLoading = false;
      }
    });
  }

  goToCourse(courseId: number): void {
    this.router.navigate(['/courses', courseId]);
  }
}
