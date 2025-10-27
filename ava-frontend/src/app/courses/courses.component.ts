import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LearningApiService } from '../core/services/learning-api.service';
import { Course } from '../shared/models/course.model';

@Component({
  selector: 'app-courses',
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
      <h1 class="page-title"><mat-icon>school</mat-icon> Cursos</h1>

      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div *ngIf="!isLoading && courses.length === 0" class="empty-state">
        <mat-icon>inbox</mat-icon>
        <p>Nenhum curso disponível.</p>
      </div>

      <div *ngIf="!isLoading && courses.length > 0" class="courses-grid">
        <mat-card *ngFor="let course of courses" class="course-card">
          <mat-card-header>
            <mat-card-title>{{ course.title }}</mat-card-title>
            <mat-card-subtitle>{{ course.description }}</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="course-stats">
              <span class="stat"><mat-icon>menu_book</mat-icon>{{ course.total_lessons }} lições</span>
              <span class="stat"><mat-icon>folder</mat-icon>{{ course.total_modules }} módulos</span>
            </div>
            <div class="course-tags">
              <mat-chip *ngFor="let tag of course.tags" class="tag-chip">{{ tag }}</mat-chip>
            </div>
          </mat-card-content>
          <mat-card-actions>
            <a mat-button color="primary" [routerLink]="['/courses', course.id]">
              <mat-icon>visibility</mat-icon>
              Ver detalhes
            </a>
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
    .course-card { height: 100%; }
    .course-stats { display: flex; gap: 16px; margin-bottom: 12px; color: #666; }
    .course-stats mat-icon { font-size: 16px; width: 16px; height: 16px; margin-right: 4px; }
    .course-tags { display: flex; flex-wrap: wrap; gap: 4px; }
  `]
})
export class CoursesComponent implements OnInit {
  courses: Course[] = [];
  isLoading = false;

  constructor(private learningApi: LearningApiService) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    this.isLoading = true;
    this.learningApi.getCourses(1, 20).subscribe({
      next: (res) => {
        this.courses = res.items || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar cursos', err);
        this.courses = [];
        this.isLoading = false;
      }
    });
  }
}
