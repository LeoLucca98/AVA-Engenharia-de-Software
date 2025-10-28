import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';

import { AuthService } from './core/services/auth.service';
import { User } from './shared/models/user.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule,
    MatMenuModule,
    MatBadgeModule,
    MatDividerModule
  ],
  template: `
    <div class="app-container">
      <mat-toolbar color="primary" class="app-toolbar">
        <button mat-icon-button (click)="sidenav.toggle()" class="menu-button">
          <mat-icon>menu</mat-icon>
        </button>
        
        <span class="app-title">AVA</span>
        
        <span class="spacer"></span>
        
        <div *ngIf="currentUser; else loginButtons" class="user-menu">
          <button mat-button [matMenuTriggerFor]="userMenu" class="user-button">
            <mat-icon>account_circle</mat-icon>
            {{ currentUser.first_name }}
            <mat-icon>arrow_drop_down</mat-icon>
          </button>
          
          <mat-menu #userMenu="matMenu">
            <button mat-menu-item (click)="goToProfile()">
              <mat-icon>person</mat-icon>
              Perfil
            </button>
            <button mat-menu-item (click)="goToSettings()">
              <mat-icon>settings</mat-icon>
              Configurações
            </button>
            <mat-divider></mat-divider>
            <button mat-menu-item (click)="logout()">
              <mat-icon>logout</mat-icon>
              Sair
            </button>
          </mat-menu>
        </div>
        
        <ng-template #loginButtons>
          <button mat-button routerLink="/auth/login">Entrar</button>
          <button mat-button routerLink="/auth/register" color="accent">Cadastrar</button>
        </ng-template>
      </mat-toolbar>

      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav #sidenav mode="side" opened class="sidenav">
          <mat-nav-list>
            <a mat-list-item routerLink="/dashboard" routerLinkActive="active">
              <mat-icon matListItemIcon>dashboard</mat-icon>
              <span matListItemTitle>Dashboard</span>
            </a>
            
            <a mat-list-item routerLink="/courses" routerLinkActive="active">
              <mat-icon matListItemIcon>school</mat-icon>
              <span matListItemTitle>Cursos</span>
            </a>
            
            <a mat-list-item routerLink="/my-courses" routerLinkActive="active">
              <mat-icon matListItemIcon>book</mat-icon>
              <span matListItemTitle>Meus Cursos</span>
            </a>
            
            <a mat-list-item routerLink="/recommendations" routerLinkActive="active">
              <mat-icon matListItemIcon>recommend</mat-icon>
              <span matListItemTitle>Recomendações</span>
            </a>
            
            <mat-divider></mat-divider>
            
            <a mat-list-item routerLink="/progress" routerLinkActive="active">
              <mat-icon matListItemIcon>trending_up</mat-icon>
              <span matListItemTitle>Progresso</span>
            </a>
            
            <mat-divider *ngIf="isAdmin()"></mat-divider>
            
            <a mat-list-item routerLink="/admin/courses" routerLinkActive="active" *ngIf="isAdmin()">
              <mat-icon matListItemIcon>admin_panel_settings</mat-icon>
              <span matListItemTitle>Gerenciar Cursos</span>
            </a>
          </mat-nav-list>
        </mat-sidenav>

        <mat-sidenav-content class="main-content">
          <router-outlet></router-outlet>
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>
  `,
  styles: [`
    .app-container {
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    
    .app-toolbar {
      position: sticky;
      top: 0;
      z-index: 1000;
    }
    
    .menu-button {
      margin-right: 16px;
    }
    
    .app-title {
      font-size: 1.5rem;
      font-weight: 500;
    }
    
    .spacer {
      flex: 1 1 auto;
    }
    
    .user-button {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .sidenav-container {
      flex: 1;
    }
    
    .sidenav {
      width: 250px;
    }
    
    .main-content {
      padding: 20px;
      overflow-y: auto;
    }
    
    .active {
      background-color: rgba(0, 0, 0, 0.04);
    }
    
    @media (max-width: 768px) {
      .sidenav {
        width: 200px;
      }
      
      .main-content {
        padding: 16px;
      }
    }
  `]
})
export class AppComponent implements OnInit {
  currentUser: User | null = null;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  goToProfile(): void {
    // Implementar navegação para perfil
  }

  goToSettings(): void {
    // Implementar navegação para configurações
  }

  logout(): void {
    this.authService.logout();
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }
}
