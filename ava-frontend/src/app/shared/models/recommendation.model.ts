export interface Recommendation {
  course_id: number;
  title: string;
  score: number;
  reason: string;
}

export interface RecommendationRequest {
  user_id: number;
  course_id?: number;
  limit?: number;
}

export interface RecommendationResponse {
  user_id: number;
  recommendations: Recommendation[];
  metadata: {
    total_recommendations: number;
    algorithm: string;
    timestamp: string;
  };
}
