import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { 
  Course, 
  Module, 
  Lesson, 
  Enrollment, 
  MyCourse, 
  EnrollmentRequest, 
  UnenrollRequest 
} from '../../shared/models/course.model';
import { 
  Progress, 
  MarkCompleteRequest, 
  Interaction, 
  InteractionRequest 
} from '../../shared/models/progress.model';
import { PaginatedResponse } from '../../shared/models/api-response.model';

@Injectable({
  providedIn: 'root'
})
export class LearningApiService {
  private readonly API_URL = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  // Courses
  getCourses(page: number = 1, pageSize: number = 20, search?: string): Observable<PaginatedResponse<Course>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());

    if (search) {
      params = params.set('search', search);
    }

    // Adapta a resposta do DRF (count/results) para nosso formato (items/total/...)
    return this.http.get<any>(
      `${this.API_URL}${environment.apiEndpoints.learning.courses}`,
      { params }
    ).pipe(
      map((res: any) => {
        // Se já vier no nosso formato esperado, só retorna
        if (res && 'items' in res) {
          return res as PaginatedResponse<Course>;
        }

        // DRF PageNumberPagination: { count, next, previous, results }
        const total = Number(res?.count ?? 0);
        const items: Course[] = Array.isArray(res?.results) ? res.results : (Array.isArray(res) ? res : []);
        const totalPages = pageSize > 0 ? Math.ceil(total / pageSize) : 1;
        const hasNext = Boolean(res?.next);
        const hasPrevious = Boolean(res?.previous);

        const adapted: PaginatedResponse<Course> = {
          items,
          total,
          page,
          page_size: pageSize,
          total_pages: totalPages,
          has_next: hasNext,
          has_previous: hasPrevious
        };
        return adapted;
      })
    );
  }

  getCourse(id: number): Observable<Course> {
    return this.http.get<Course>(
      `${this.API_URL}${environment.apiEndpoints.learning.courses}${id}/`
    );
  }

  createCourse(course: Partial<Course>): Observable<Course> {
    return this.http.post<Course>(
      `${this.API_URL}${environment.apiEndpoints.learning.courses}`,
      course
    );
  }

  updateCourse(id: number, course: Partial<Course>): Observable<Course> {
    return this.http.put<Course>(
      `${this.API_URL}${environment.apiEndpoints.learning.courses}${id}/`,
      course
    );
  }

  deleteCourse(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}${environment.apiEndpoints.learning.courses}${id}/`
    );
  }

  // Modules
  getModules(courseId?: number): Observable<Module[]> {
    let params = new HttpParams();
    if (courseId) {
      params = params.set('course', courseId.toString());
    }

    return this.http.get<Module[]>(
      `${this.API_URL}/learning/modules/`,
      { params }
    );
  }

  getModule(id: number): Observable<Module> {
    return this.http.get<Module>(
      `${this.API_URL}/learning/modules/${id}/`
    );
  }

  createModule(module: Partial<Module>): Observable<Module> {
    return this.http.post<Module>(
      `${this.API_URL}/learning/modules/`,
      module
    );
  }

  updateModule(id: number, module: Partial<Module>): Observable<Module> {
    return this.http.put<Module>(
      `${this.API_URL}/learning/modules/${id}/`,
      module
    );
  }

  deleteModule(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/learning/modules/${id}/`
    );
  }

  // Lessons
  getLessons(moduleId?: number, courseId?: number): Observable<Lesson[]> {
    let params = new HttpParams();
    if (moduleId) {
      params = params.set('module', moduleId.toString());
    }
    if (courseId) {
      params = params.set('module__course', courseId.toString());
    }

    return this.http.get<Lesson[]>(
      `${this.API_URL}/learning/lessons/`,
      { params }
    );
  }

  getLesson(id: number): Observable<Lesson> {
    return this.http.get<Lesson>(
      `${this.API_URL}/learning/lessons/${id}/`
    );
  }

  createLesson(lesson: Partial<Lesson>): Observable<Lesson> {
    return this.http.post<Lesson>(
      `${this.API_URL}/learning/lessons/`,
      lesson
    );
  }

  updateLesson(id: number, lesson: Partial<Lesson>): Observable<Lesson> {
    return this.http.put<Lesson>(
      `${this.API_URL}/learning/lessons/${id}/`,
      lesson
    );
  }

  deleteLesson(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/learning/lessons/${id}/`
    );
  }

  // Enrollments
  getMyCourses(): Observable<MyCourse[]> {
    return this.http.get<MyCourse[]>(
      `${this.API_URL}${environment.apiEndpoints.learning.myCourses}`
    );
  }

  enrollInCourse(enrollment: EnrollmentRequest): Observable<Enrollment> {
    return this.http.post<Enrollment>(
      `${this.API_URL}${environment.apiEndpoints.learning.enroll}`,
      enrollment
    );
  }

  unenrollFromCourse(request: UnenrollRequest): Observable<void> {
    return this.http.post<void>(
      `${this.API_URL}${environment.apiEndpoints.learning.unenroll}`,
      request
    );
  }

  // Progress
  getMyProgress(): Observable<Progress[]> {
    return this.http.get<Progress[]>(
      `${this.API_URL}${environment.apiEndpoints.learning.progress}`
    );
  }

  getLessonProgress(lessonId: number): Observable<Progress> {
    return this.http.get<Progress>(
      `${this.API_URL}${environment.apiEndpoints.learning.progress}lesson_progress/?lesson_id=${lessonId}`
    );
  }

  getCourseProgress(courseId: number): Observable<Progress[]> {
    return this.http.get<Progress[]>(
      `${this.API_URL}${environment.apiEndpoints.learning.progress}course_progress/?course_id=${courseId}`
    );
  }

  markLessonComplete(request: MarkCompleteRequest): Observable<Progress> {
    return this.http.post<Progress>(
      `${this.API_URL}${environment.apiEndpoints.learning.markComplete}`,
      request
    );
  }

  // Interactions
  getMyInteractions(): Observable<Interaction[]> {
    return this.http.get<Interaction[]>(
      `${this.API_URL}${environment.apiEndpoints.learning.interactions}`
    );
  }

  createInteraction(interaction: InteractionRequest): Observable<Interaction> {
    return this.http.post<Interaction>(
      `${this.API_URL}${environment.apiEndpoints.learning.interactions}`,
      interaction
    );
  }

  getInteractionsByType(type: string): Observable<Interaction[]> {
    return this.http.get<Interaction[]>(
      `${this.API_URL}${environment.apiEndpoints.learning.interactions}by_type/?type=${type}`
    );
  }
}
