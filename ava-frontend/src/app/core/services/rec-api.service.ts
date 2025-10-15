import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { 
  RecommendationRequest, 
  RecommendationResponse 
} from '../../shared/models/recommendation.model';

@Injectable({
  providedIn: 'root'
})
export class RecApiService {
  private readonly API_URL = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  getRecommendations(request: RecommendationRequest): Observable<RecommendationResponse> {
    return this.http.post<RecommendationResponse>(
      `${this.API_URL}${environment.apiEndpoints.recommendations.recommendations}`,
      request
    );
  }

  getUserRecommendations(userId: number, limit: number = 10): Observable<RecommendationResponse> {
    const params = new HttpParams()
      .set('limit', limit.toString());

    return this.http.get<RecommendationResponse>(
      `${this.API_URL}${environment.apiEndpoints.recommendations.userRecommendations}/${userId}`,
      { params }
    );
  }

  getCourseRecommendations(courseId: number, limit: number = 10): Observable<RecommendationResponse> {
    const request: RecommendationRequest = {
      user_id: 0, // Será preenchido pelo backend baseado no token
      course_id: courseId,
      limit
    };

    return this.getRecommendations(request);
  }
}
