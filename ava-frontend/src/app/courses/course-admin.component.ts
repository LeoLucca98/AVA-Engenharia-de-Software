import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTableModule } from '@angular/material/table';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';

import { LearningApiService } from '../core/services/learning-api.service';
import { Course } from '../shared/models/course.model';

@Component({
  selector: 'app-course-admin',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatChipsModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatTableModule,
    MatMenuModule,
    MatTooltipModule
  ],
  template: `
    <div class="page-container">
      <div class="header">
        <h1 class="page-title">
          <mat-icon>admin_panel_settings</mat-icon>
          Gerenciar Cursos
        </h1>
        <button mat-raised-button color="primary" (click)="openCreateForm()">
          <mat-icon>add</mat-icon>
          Novo Curso
        </button>
      </div>

      <div *ngIf="isLoading" class="loading-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <div *ngIf="!isLoading && courses.length === 0" class="empty-state">
        <mat-icon>inbox</mat-icon>
        <p>Nenhum curso cadastrado.</p>
        <button mat-button color="primary" (click)="openCreateForm()">
          Criar primeiro curso
        </button>
      </div>

      <div *ngIf="!isLoading && courses.length > 0" class="courses-table-container">
        <table mat-table [dataSource]="courses" class="courses-table">
          <ng-container matColumnDef="title">
            <th mat-header-cell *matHeaderCellDef> Título </th>
            <td mat-cell *matCellDef="let course"> {{ course.title }} </td>
          </ng-container>

          <ng-container matColumnDef="description">
            <th mat-header-cell *matHeaderCellDef> Descrição </th>
            <td mat-cell *matCellDef="let course"> 
              {{ course.description.length > 100 ? (course.description.substring(0, 100) + '...') : course.description }}
            </td>
          </ng-container>

          <ng-container matColumnDef="tags">
            <th mat-header-cell *matHeaderCellDef> Tags </th>
            <td mat-cell *matCellDef="let course">
              <mat-chip *ngFor="let tag of course.tags" class="tag-chip">{{ tag }}</mat-chip>
            </td>
          </ng-container>

          <ng-container matColumnDef="is_published">
            <th mat-header-cell *matHeaderCellDef> Publicado </th>
            <td mat-cell *matCellDef="let course">
              <mat-icon [class.published]="course.is_published" [class.unpublished]="!course.is_published">
                {{ course.is_published ? 'check_circle' : 'cancel' }}
              </mat-icon>
            </td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef> Ações </th>
            <td mat-cell *matCellDef="let course">
              <button mat-icon-button [matMenuTriggerFor]="menu">
                <mat-icon>more_vert</mat-icon>
              </button>
              <mat-menu #menu="matMenu">
                <button mat-menu-item (click)="editCourse(course)">
                  <mat-icon>edit</mat-icon>
                  <span>Editar</span>
                </button>
                <button mat-menu-item (click)="deleteCourse(course)" class="delete-action">
                  <mat-icon>delete</mat-icon>
                  <span>Excluir</span>
                </button>
              </mat-menu>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
        </table>
      </div>
    </div>

    <!-- Dialog de Criar/Editar -->
    <div class="form-dialog" *ngIf="showForm">
      <div class="dialog-overlay" (click)="closeForm()"></div>
      <div class="dialog-content">
        <div class="dialog-header">
          <h2>{{ editingCourse ? 'Editar Curso' : 'Novo Curso' }}</h2>
          <button mat-icon-button (click)="closeForm()">
            <mat-icon>close</mat-icon>
          </button>
        </div>
        
        <form [formGroup]="courseForm" (ngSubmit)="saveCourse()">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Título</mat-label>
            <input matInput formControlName="title" placeholder="Ex: Python para Iniciantes">
            <mat-error *ngIf="courseForm.get('title')?.hasError('required')">
              Título é obrigatório
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Descrição</mat-label>
            <textarea matInput formControlName="description" rows="4" 
              placeholder="Descreva o curso..."></textarea>
            <mat-error *ngIf="courseForm.get('description')?.hasError('required')">
              Descrição é obrigatória
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Tags (separadas por vírgula)</mat-label>
            <input matInput formControlName="tagsInput" 
              placeholder="Ex: python, programação, iniciantes">
            <mat-hint>Separe as tags por vírgula</mat-hint>
          </mat-form-field>

          <div class="form-row">
            <mat-checkbox formControlName="is_published">
              Publicar curso
            </mat-checkbox>
          </div>

          <div class="form-actions">
            <button mat-button type="button" (click)="closeForm()">Cancelar</button>
            <button mat-raised-button color="primary" type="submit" 
              [disabled]="courseForm.invalid || isSaving">
              <mat-spinner *ngIf="isSaving" diameter="20" class="button-spinner"></mat-spinner>
              <span *ngIf="!isSaving">{{ editingCourse ? 'Salvar' : 'Criar' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .page-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    
    .page-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 400;
      margin: 0;
    }
    
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
    }
    
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }
    
    .empty-state mat-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      margin-bottom: 16px;
      color: #ccc;
    }
    
    .courses-table-container {
      background: white;
      border-radius: 4px;
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .courses-table {
      width: 100%;
    }
    
    .tag-chip {
      margin: 2px;
      font-size: 12px;
    }
    
    .published { color: #4caf50; }
    .unpublished { color: #f44336; }
    
    .delete-action { color: #f44336; }
    
    .form-dialog {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
    }
    
    .dialog-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
    }
    
    .dialog-content {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      border-radius: 8px;
      padding: 24px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid #e0e0e0;
    }
    
    .dialog-header h2 {
      margin: 0;
      font-weight: 400;
    }
    
    .full-width {
      width: 100%;
      margin-bottom: 16px;
    }
    
    .form-row {
      margin-bottom: 16px;
    }
    
    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid #e0e0e0;
    }
    
    .button-spinner {
      display: inline-block;
      margin-right: 8px;
    }
  `]
})
export class CourseAdminComponent implements OnInit {
  courses: Course[] = [];
  isLoading = false;
  isSaving = false;
  showForm = false;
  editingCourse: Course | null = null;
  
  displayedColumns: string[] = ['title', 'description', 'tags', 'is_published', 'actions'];
  
  courseForm: FormGroup;

  constructor(
    private learningApi: LearningApiService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {
    this.courseForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      tagsInput: [''],
      is_published: [false]
    });
  }

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    this.isLoading = true;
    this.learningApi.getCourses(1, 100).subscribe({
      next: (res) => {
        this.courses = res.items || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar cursos', err);
        this.snackBar.open('Erro ao carregar cursos', 'Fechar', { duration: 3000 });
        this.courses = [];
        this.isLoading = false;
      }
    });
  }

  openCreateForm(): void {
    this.editingCourse = null;
    this.courseForm.reset({
      title: '',
      description: '',
      tagsInput: '',
      is_published: false
    });
    this.showForm = true;
  }

  editCourse(course: Course): void {
    this.editingCourse = course;
    this.courseForm.patchValue({
      title: course.title,
      description: course.description,
      tagsInput: course.tags.join(', '),
      is_published: course.is_published
    });
    this.showForm = true;
  }

  closeForm(): void {
    this.showForm = false;
    this.editingCourse = null;
    this.courseForm.reset();
  }

  saveCourse(): void {
    if (this.courseForm.invalid) {
      return;
    }

    this.isSaving = true;
    const formValue = this.courseForm.value;
    
    // Processar tags
    const tags = formValue.tagsInput
      ? formValue.tagsInput.split(',').map((t: string) => t.trim()).filter((t: string) => t.length > 0)
      : [];

    const courseData: Partial<Course> = {
      title: formValue.title,
      description: formValue.description,
      tags: tags,
      is_published: formValue.is_published
    };

    const action = this.editingCourse
      ? this.learningApi.updateCourse(this.editingCourse.id, courseData)
      : this.learningApi.createCourse(courseData);

    action.subscribe({
      next: () => {
        this.snackBar.open(
          `Curso ${this.editingCourse ? 'atualizado' : 'criado'} com sucesso!`,
          'Fechar',
          { duration: 3000 }
        );
        this.closeForm();
        this.loadCourses();
        this.isSaving = false;
      },
      error: (err) => {
        console.error('Erro ao salvar curso', err);
        this.snackBar.open(
          `Erro ao ${this.editingCourse ? 'atualizar' : 'criar'} curso`,
          'Fechar',
          { duration: 3000 }
        );
        this.isSaving = false;
      }
    });
  }

  deleteCourse(course: Course): void {
    if (!confirm(`Tem certeza que deseja excluir o curso "${course.title}"?`)) {
      return;
    }

    this.learningApi.deleteCourse(course.id).subscribe({
      next: () => {
        this.snackBar.open('Curso excluído com sucesso!', 'Fechar', { duration: 3000 });
        this.loadCourses();
      },
      error: (err) => {
        console.error('Erro ao excluir curso', err);
        this.snackBar.open('Erro ao excluir curso', 'Fechar', { duration: 3000 });
      }
    });
  }
}
