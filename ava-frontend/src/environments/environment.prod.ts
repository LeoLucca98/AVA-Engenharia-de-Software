export const environment = {
  production: true,
  // Em produção (Docker Compose local), o API Gateway publica em http://localhost:8080.
  // Ajuste este valor para o domínio público do gateway no seu ambiente real,
  // ex.: 'https://api.seudominio.com'.
  apiBaseUrl: 'http://localhost:8080',
  apiEndpoints: {
    auth: {
      login: '/auth/login/',
      register: '/auth/register/',
      refresh: '/auth/token/refresh/',
      user: '/auth/user/'
    },
    learning: {
      courses: '/learning/courses/',
      myCourses: '/learning/enrollments/my_courses/',
      enroll: '/learning/enrollments/enroll/',
      unenroll: '/learning/enrollments/unenroll/',
      progress: '/learning/progress/',
      markComplete: '/learning/progress/mark_complete/',
      interactions: '/learning/interactions/'
    },
    recommendations: {
      recommendations: '/rec/recommendations/',
      userRecommendations: '/rec/recommendations/user'
    }
  },
  appConfig: {
    appName: 'AVA - Adaptive Virtual Assistant',
    version: '1.0.0',
    defaultPageSize: 20,
    tokenRefreshInterval: 300000, // 5 minutos
    sessionTimeout: 3600000 // 1 hora
  }
};
