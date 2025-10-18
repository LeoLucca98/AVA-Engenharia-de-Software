/**
 * API Gateway Server with JWT Validation
 * Routes requests to microservices and validates JWT tokens
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const { jwtValidationMiddleware, optionalJwtValidation } = require('./jwt-validator');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 80;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for API gateway
  crossOriginEmbedderPolicy: false
}));

// CORS configuration
const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ['http://localhost:4200'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-Id', 'X-User-Id', 'X-User-Email', 'X-User-Username', 'X-User-Roles']
};

app.use(cors(corsOptions));

// Compression
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too Many Requests',
    message: 'Rate limit exceeded. Please try again later.',
    code: 'RATE_LIMIT_EXCEEDED'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  req.headers['x-request-id'] = requestId;
  
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url} - ${req.ip} - ${requestId}`);
  next();
});

// Welcome endpoint
app.get('/', (req, res) => {
  res.status(200).json({
    service: 'AVA API Gateway',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      health: '/healthz',
      auth: {
        base: '/auth',
        login: '/auth/login/',
        register: '/auth/register/',
        refresh: '/auth/refresh/',
        logout: '/auth/logout/',
        profile: '/auth/profile/'
      },
      learning: {
        base: '/learning',
        courses: '/learning/courses/',
        enrollments: '/learning/enrollments/',
        progress: '/learning/progress/',
        resources: '/learning/resources/'
      },
      recommendations: {
        base: '/rec',
        recommendations: '/rec/recommendations/',
        interactions: '/rec/interactions/'
      }
    },
    message: 'Bem-vindo ao AVA - Adaptive Virtual Assistant API'
  });
});

// Health check endpoint
app.get('/healthz', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'api-gateway',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Service URLs
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://auth_service:8000';
const LEARNING_SERVICE_URL = process.env.LEARNING_SERVICE_URL || 'http://learning_service:8000';
const RECOMMENDATION_SERVICE_URL = process.env.RECOMMENDATION_SERVICE_URL || 'http://recommendation_service:8000';

// Proxy configuration
const proxyOptions = {
  target: '',
  changeOrigin: true,
  timeout: 30000,
  proxyTimeout: 30000,
  onError: (err, req, res) => {
    console.error('Proxy error:', err.message);
    res.status(503).json({
      error: 'Service Unavailable',
      message: 'The requested service is temporarily unavailable',
      code: 'SERVICE_UNAVAILABLE'
    });
  },
  onProxyReq: (proxyReq, req, res) => {
    // Pass through headers
    const headersToPass = ['x-request-id', 'x-user-id', 'x-user-email', 'x-user-username', 'x-user-roles'];
    headersToPass.forEach(header => {
      if (req.headers[header]) {
        proxyReq.setHeader(header, req.headers[header]);
      }
    });
  }
};

// Auth service routes (no JWT validation needed for login/register)
app.use('/auth', createProxyMiddleware({
  ...proxyOptions,
  target: AUTH_SERVICE_URL,
  pathRewrite: {
    '^/auth': '/api'
  }
}));

// Learning service routes (JWT validation required)
app.use('/learning', jwtValidationMiddleware, createProxyMiddleware({
  ...proxyOptions,
  target: LEARNING_SERVICE_URL,
  pathRewrite: {
    '^/learning': '/learning'
  }
}));

// Recommendation service routes (JWT validation required)
app.use('/rec', jwtValidationMiddleware, createProxyMiddleware({
  ...proxyOptions,
  target: RECOMMENDATION_SERVICE_URL,
  pathRewrite: {
    '^/rec': ''
  }
}));

// Public endpoints (optional JWT validation)
app.use('/public', optionalJwtValidation, createProxyMiddleware({
  ...proxyOptions,
  target: LEARNING_SERVICE_URL,
  pathRewrite: {
    '^/public': '/learning'
  }
}));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred',
    code: 'INTERNAL_ERROR',
    requestId: req.headers['x-request-id']
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'The requested endpoint does not exist',
    code: 'ENDPOINT_NOT_FOUND',
    path: req.originalUrl,
    requestId: req.headers['x-request-id']
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`Auth Service: ${AUTH_SERVICE_URL}`);
  console.log(`Learning Service: ${LEARNING_SERVICE_URL}`);
  console.log(`Recommendation Service: ${RECOMMENDATION_SERVICE_URL}`);
  console.log(`JWKS URL: ${process.env.AUTH_SERVICE_JWKS_URL || 'http://auth_service:8000/api/.well-known/jwks.json'}`);
});

module.exports = app;
