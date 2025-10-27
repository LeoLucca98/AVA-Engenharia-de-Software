import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LearningApiService } from '../core/services/learning-api.service';
import { Course } from '../shared/models/course.model';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatChipsModule, MatProgressSpinnerModule],
  template: `
    <div class="page-container">
      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <ng-container *ngIf="!isLoading">
        <mat-card *ngIf="course; else notFound">
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
              <mat-chip *ngFor="let tag of (course.tags || [])">{{ tag }}</mat-chip>
            </div>
          </mat-card-content>
        </mat-card>

        <ng-template #notFound>
          <p>Curso não encontrado.</p>
        </ng-template>
      </ng-container>
    </div>
  `,
  styles: [`
    .page-container { max-width: 900px; margin: 0 auto; padding: 20px; }
    .loading-container { display: flex; justify-content: center; align-items: center; height: 200px; }
    .course-stats { display: flex; gap: 16px; margin-bottom: 12px; color: #666; }
    .course-stats mat-icon { font-size: 16px; width: 16px; height: 16px; margin-right: 4px; }
    .course-tags { display: flex; flex-wrap: wrap; gap: 4px; }
  `]
})
export class CourseDetailComponent implements OnInit {
  course: Course | null = null;
  isLoading = false;

  constructor(private route: ActivatedRoute, private learningApi: LearningApiService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!isNaN(id)) {
      this.fetchCourse(id);
    }
  }

  private fetchCourse(id: number): void {
    this.isLoading = true;
    this.learningApi.getCourse(id).subscribe({
      next: (res) => {
        this.course = { ...res, tags: (res as any).tags || [] } as Course;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar curso', err);
        this.course = null;
        this.isLoading = false;
      }
    });
  }
}
