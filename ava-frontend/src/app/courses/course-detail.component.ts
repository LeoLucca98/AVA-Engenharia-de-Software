import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { LearningApiService } from '../core/services/learning-api.service';
import { Course } from '../shared/models/course.model';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatChipsModule, MatProgressSpinnerModule, MatButtonModule, MatListModule],
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

            <!-- Ações de inscrição -->
            <div class="actions">
              <button *ngIf="!isEnrolled" mat-raised-button color="primary" (click)="enroll()">
                <mat-icon>how_to_reg</mat-icon>
                Inscrever-se
              </button>
              <button *ngIf="isEnrolled" mat-stroked-button color="warn" (click)="unenroll()">
                <mat-icon>logout</mat-icon>
                Desistir do curso
              </button>
              <span *ngIf="isEnrolled" class="progress-pill">
                <mat-icon>trending_up</mat-icon>
                {{ completionPercent }}% concluído
              </span>
            </div>

            <!-- Conteúdo do curso (apenas matriculado) -->
            <div *ngIf="isEnrolled" class="content-grid">
              <div class="lessons-list">
                <h3><mat-icon>menu_book</mat-icon> Lições</h3>
                <mat-nav-list>
                  <a mat-list-item *ngFor="let l of lessons" (click)="selectLesson(l.id)" [class.completed]="completedLessonIds.has(l.id)">
                    <mat-icon matListItemIcon>{{ completedLessonIds.has(l.id) ? 'check_circle' : 'radio_button_unchecked' }}</mat-icon>
                    <div matListItemTitle>{{ l.title }}</div>
                    <div matListItemLine>{{ l.module_title }}</div>
                  </a>
                </mat-nav-list>
              </div>
              <div class="lesson-viewer" *ngIf="selectedLesson">
                <h3>{{ selectedLesson.title }}</h3>
                <div class="lesson-content" [innerHTML]="selectedLesson.content"></div>
                <div class="viewer-actions">
                  <button mat-raised-button color="primary" (click)="markComplete(selectedLesson.id)">
                    <mat-icon>done_all</mat-icon>
                    Marcar como concluída
                  </button>
                </div>
              </div>
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
    .actions { display: flex; align-items: center; gap: 12px; margin-top: 12px; margin-bottom: 8px; }
    .progress-pill { display: inline-flex; align-items: center; gap: 6px; color: #4caf50; font-weight: 500; }
    .content-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-top: 16px; }
    .lessons-list h3, .lesson-viewer h3 { display: flex; align-items: center; gap: 8px; margin: 0 0 8px 0; }
    .lesson-content { background: #fafafa; padding: 12px; border: 1px solid #eee; border-radius: 6px; }
    a.mat-mdc-list-item.completed { color: #4caf50; }
    .viewer-actions { margin-top: 12px; }
    @media (max-width: 768px) { .content-grid { grid-template-columns: 1fr; } }
  `]
})
export class CourseDetailComponent implements OnInit {
  course: Course | null = null;
  isLoading = false;
  isEnrolled = false;
  completionPercent = 0;
  lessons: any[] = [];
  completedLessonIds = new Set<number>();
  selectedLesson: any | null = null;

  constructor(private route: ActivatedRoute, private learningApi: LearningApiService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!isNaN(id)) {
      this.fetchCourse(id);
      this.checkEnrollment(id);
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

  private checkEnrollment(courseId: number): void {
    this.learningApi.getMyCourses().subscribe({
      next: (my) => {
        const found = (my || []).find(m => m.course === courseId && m.status === 'active');
        this.isEnrolled = !!found;
        if (this.isEnrolled) {
          this.loadLessons(courseId);
          this.loadCourseProgress(courseId);
        }
      },
      error: () => {
        this.isEnrolled = false;
      }
    });
  }

  enroll(): void {
    if (!this.course) return;
    this.learningApi.enrollInCourse({ course: this.course.id, role: 'student' }).subscribe({
      next: () => {
        this.isEnrolled = true;
        this.loadLessons(this.course!.id);
        this.loadCourseProgress(this.course!.id);
      },
      error: (err) => console.error('Erro ao se inscrever', err)
    });
  }

  unenroll(): void {
    if (!this.course) return;
    this.learningApi.unenrollFromCourse({ course_id: this.course.id }).subscribe({
      next: () => {
        this.isEnrolled = false;
        this.lessons = [];
        this.completedLessonIds.clear();
        this.completionPercent = 0;
        this.selectedLesson = null;
      },
      error: (err) => console.error('Erro ao desistir do curso', err)
    });
  }

  private loadLessons(courseId: number): void {
    this.learningApi.getLessons(undefined, courseId).subscribe({
      next: (ls) => this.lessons = ls || [],
      error: (err) => console.error('Erro ao carregar lições', err)
    });
  }

  private loadCourseProgress(courseId: number): void {
    this.learningApi.getCourseProgress(courseId).subscribe({
      next: (ps) => {
        this.completedLessonIds = new Set((ps || []).filter(p => p.completed).map(p => p.lesson));
        const total = this.course?.total_lessons || 0;
        const done = this.completedLessonIds.size;
        this.completionPercent = total > 0 ? Math.round((done / total) * 100) : 0;
      },
      error: (err) => console.error('Erro ao carregar progresso do curso', err)
    });
  }

  selectLesson(lessonId: number): void {
    this.learningApi.getLesson(lessonId).subscribe({
      next: (l) => this.selectedLesson = l,
      error: (err) => console.error('Erro ao abrir lição', err)
    });
  }

  markComplete(lessonId: number): void {
    this.learningApi.markLessonComplete({ lesson_id: lessonId }).subscribe({
      next: () => {
        this.completedLessonIds.add(lessonId);
        const total = this.course?.total_lessons || 0;
        const done = this.completedLessonIds.size;
        this.completionPercent = total > 0 ? Math.round((done / total) * 100) : 0;
      },
      error: (err) => console.error('Erro ao marcar lição como concluída', err)
    });
  }
}
