export interface Course {
  id: number;
  title: string;
  description: string;
  owner_id: number;
  tags: string[];
  is_published: boolean;
  created_at: string;
  updated_at: string;
  total_lessons: number;
  total_modules: number;
}

export interface Module {
  id: number;
  course: number;
  course_title: string;
  title: string;
  order: number;
  created_at: string;
  updated_at: string;
  total_lessons: number;
}

export interface Lesson {
  id: number;
  module: number;
  course_title: string;
  module_title: string;
  title: string;
  content: string;
  content_type: 'markdown' | 'html';
  order: number;
  resource_links: ResourceLink[];
  created_at: string;
  updated_at: string;
}

export interface ResourceLink {
  title: string;
  url: string;
}

export interface Enrollment {
  id: number;
  course: number;
  course_title: string;
  course_description: string;
  user_id: number;
  role: 'student' | 'instructor' | 'owner';
  status: 'active' | 'completed' | 'suspended' | 'cancelled';
  enrolled_at: string;
  updated_at: string;
}

export interface MyCourse extends Enrollment {
  course_tags: string[];
  course_is_published: boolean;
  course_created_at: string;
  total_lessons: number;
  total_modules: number;
}

export interface EnrollmentRequest {
  course: number;
  role: 'student' | 'instructor';
}

export interface UnenrollRequest {
  course_id: number;
}
