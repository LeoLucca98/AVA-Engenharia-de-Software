import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  TokenRefreshRequest, 
  TokenRefreshResponse 
} from '../../shared/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = environment.apiBaseUrl;
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'current_user';

  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private refreshTokenInterval: any;

  constructor(private http: HttpClient) {
    this.initializeAuth();
  }

  private initializeAuth(): void {
    const token = this.getAccessToken();
    const user = this.getStoredUser();
    
    if (token && user) {
      // Atualizar roles do token se necessário
      const roles = this.extractRolesFromToken(token);
      if (roles && (!user.roles || user.roles.length === 0)) {
        user.roles = roles;
        this.setCurrentUser(user); // Atualiza storage
      }
      this.currentUserSubject.next(user);
      this.startTokenRefresh();
    }
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(
      `${this.API_URL}${environment.apiEndpoints.auth.login}`,
      credentials
    ).pipe(
      tap(response => {
        this.setTokens(response.access, response.refresh);
        // Extrair roles do token JWT e adicionar ao user
        const roles = this.extractRolesFromToken(response.access);
        if (roles) {
          response.user.roles = roles;
        }
        this.setCurrentUser(response.user);
        this.startTokenRefresh();
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  register(userData: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(
      `${this.API_URL}${environment.apiEndpoints.auth.register}`,
      userData
    ).pipe(
      catchError(error => {
        console.error('Register error:', error);
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    this.clearTokens();
    this.currentUserSubject.next(null);
    this.stopTokenRefresh();
  }

  refreshToken(): Observable<TokenRefreshResponse> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      this.logout();
      return throwError(() => new Error('No refresh token available'));
    }

    const request: TokenRefreshRequest = { refresh: refreshToken };

    return this.http.post<TokenRefreshResponse>(
      `${this.API_URL}${environment.apiEndpoints.auth.refresh}`,
      request
    ).pipe(
      tap(response => {
        this.setAccessToken(response.access);
      }),
      catchError(error => {
        console.error('Token refresh error:', error);
        this.logout();
        return throwError(() => error);
      })
    );
  }

  getCurrentUserFromAPI(): Observable<User> {
    return this.http.get<User>(
      `${this.API_URL}${environment.apiEndpoints.auth.user}`
    ).pipe(
      tap(user => {
        // Se o user não tem roles, tenta extrair do token
        if (!user.roles || user.roles.length === 0) {
          const roles = this.extractRolesFromToken(this.getAccessToken());
          if (roles) {
            user.roles = roles;
          }
        }
        this.setCurrentUser(user);
      }),
      catchError(error => {
        console.error('Get current user error:', error);
        return throwError(() => error);
      })
    );
  }

  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return !!token && !this.isTokenExpired(token);
  }

  getAccessToken(): string | null {
    return sessionStorage.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return sessionStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getUserRole(): string | null {
    const user = this.getCurrentUser();
    if (!user) return null;
    
    // Retorna o primeiro role (prioridade: admin > instructor > student)
    const roles = user.roles || this.extractRolesFromToken(this.getAccessToken());
    if (roles && roles.length > 0) {
      if (roles.includes('admin')) return 'admin';
      if (roles.includes('instructor')) return 'instructor';
      return roles[0];
    }
    
    return 'student'; // Default
  }

  getUserRoles(): string[] {
    const user = this.getCurrentUser();
    if (!user) return [];
    
    return user.roles || this.extractRolesFromToken(this.getAccessToken()) || ['student'];
  }

  hasRole(role: string): boolean {
    return this.getUserRoles().includes(role);
  }

  isAdmin(): boolean {
    return this.hasRole('admin');
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    sessionStorage.setItem(this.TOKEN_KEY, accessToken);
    sessionStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  private setAccessToken(accessToken: string): void {
    sessionStorage.setItem(this.TOKEN_KEY, accessToken);
  }

  private setCurrentUser(user: User): void {
    this.currentUserSubject.next(user);
    sessionStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private getStoredUser(): User | null {
    const userStr = sessionStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  private clearTokens(): void {
    sessionStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(this.USER_KEY);
  }

  private startTokenRefresh(): void {
    this.stopTokenRefresh();
    
    this.refreshTokenInterval = setInterval(() => {
      this.refreshToken().subscribe({
        next: () => console.log('Token refreshed successfully'),
        error: (error) => console.error('Token refresh failed:', error)
      });
    }, environment.appConfig.tokenRefreshInterval);
  }

  private stopTokenRefresh(): void {
    if (this.refreshTokenInterval) {
      clearInterval(this.refreshTokenInterval);
      this.refreshTokenInterval = null;
    }
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (error) {
      return true;
    }
  }

  private extractRolesFromToken(token: string | null): string[] | null {
    if (!token) return null;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.roles || null;
    } catch (error) {
      console.error('Error extracting roles from token:', error);
      return null;
    }
  }
}
