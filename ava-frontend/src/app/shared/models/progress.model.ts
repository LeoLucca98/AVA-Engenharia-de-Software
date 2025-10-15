export interface Progress {
  id: number;
  user_id: number;
  lesson: number;
  lesson_title: string;
  course_title: string;
  module_title: string;
  completed: boolean;
  score?: number;
  time_spent: number;
  last_accessed: string;
  created_at: string;
  updated_at: string;
}

export interface MarkCompleteRequest {
  lesson_id: number;
  score?: number;
  time_spent?: number;
}

export interface Interaction {
  id: number;
  user_id: number;
  lesson?: number;
  lesson_title?: string;
  resource?: number;
  resource_title?: string;
  target_title?: string;
  interaction_type: 'view' | 'like' | 'note' | 'answer' | 'download' | 'share' | 'bookmark';
  payload: Record<string, any>;
  created_at: string;
}

export interface InteractionRequest {
  lesson?: number;
  resource?: number;
  interaction_type: 'view' | 'like' | 'note' | 'answer' | 'download' | 'share' | 'bookmark';
  payload: Record<string, any>;
}
