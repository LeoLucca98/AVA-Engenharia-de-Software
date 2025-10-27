export const environment = {
  production: false,
  // Em desenvolvimento usamos o proxy do Angular (proxy.conf.json),
  // então a base deve ser vazia para que as chamadas sejam relativas
  // e evitarem CORS (ex.: "/auth/login/" será proxyado para 8080).
  apiBaseUrl: '',
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
