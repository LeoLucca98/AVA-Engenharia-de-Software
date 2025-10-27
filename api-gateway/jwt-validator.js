/**
 * JWT Validator for API Gateway
 * Validates RS256 JWT tokens and extracts user information
 */

const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');
const http = require('http');

// JWKS client configuration
// Importante: requisições diretas ao Django com host contendo underscore (ex: auth_service)
// causam 400 Bad Request. Para evitar isso, por padrão usamos o próprio gateway
// como proxy para o endpoint JWKS, que não exige autenticação.
// Isso funciona tanto em desenvolvimento quanto em produção dentro do container.
// Use 127.0.0.1 para garantir IPv4 dentro do container (evita ::1 quando o servidor escuta em 0.0.0.0)
const DEFAULT_JWKS_URL = 'http://127.0.0.1/auth/.well-known/jwks.json';

const client = jwksClient({
  jwksUri: process.env.AUTH_SERVICE_JWKS_URL || DEFAULT_JWKS_URL,
  cache: true,
  cacheMaxAge: 600000, // 10 minutes
  rateLimit: true,
  jwksRequestsPerMinute: 5
});

/**
 * Get signing key from JWKS
 */
function getKey(header, callback) {
  // Alguns emissores não incluem 'kid' no header do token.
  // Usamos um fallback para a nossa chave padrão.
  const kid = header.kid || 'ava-auth-key-1';

  client.getSigningKey(kid, (err, key) => {
    if (err) {
      console.error('Error getting signing key:', err);
      return callback(err);
    }
    
    const signingKey = key.publicKey || key.rsaPublicKey;
    callback(null, signingKey);
  });
}

/**
 * Validate JWT token and extract user information
 */
function validateToken(token) {
  return new Promise((resolve, reject) => {
    if (!token) {
      return reject(new Error('No token provided'));
    }

    // Remove 'Bearer ' prefix if present
    const cleanToken = token.replace(/^Bearer\s+/i, '');

    jwt.verify(cleanToken, getKey, {
      algorithms: ['RS256'],
      audience: 'ava-microservices',
      issuer: 'ava-auth-service',
      clockTolerance: 30 // 30 seconds tolerance
    }, (err, decoded) => {
      if (err) {
        console.error('JWT validation error:', err.message);
        return reject(err);
      }

      resolve({
        userId: decoded.sub,
        email: decoded.email,
        username: decoded.username,
        roles: decoded.roles || ['student'],
        exp: decoded.exp,
        iat: decoded.iat
      });
    });
  });
}

/**
 * Middleware to validate JWT and inject X-User-Id header
 */
function jwtValidationMiddleware(req, res, next) {
  // Skip validation for certain paths
  const skipPaths = ['/healthz', '/health', '/.well-known'];
  if (skipPaths.some(path => req.url.startsWith(path))) {
    return next();
  }

  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Authorization header is required',
      code: 'MISSING_AUTH_HEADER'
    });
  }

  validateToken(authHeader)
    .then(userInfo => {
      // Inject user information into headers for downstream services
      req.headers['x-user-id'] = userInfo.userId;
      req.headers['x-user-email'] = userInfo.email;
      req.headers['x-user-username'] = userInfo.username;
      req.headers['x-user-roles'] = JSON.stringify(userInfo.roles);
      
      // Store user info in request for logging
      req.user = userInfo;
      
      next();
    })
    .catch(err => {
      console.error('JWT validation failed:', err.message);
      
      let statusCode = 401;
      let errorCode = 'INVALID_TOKEN';
      
      if (err.name === 'TokenExpiredError') {
        errorCode = 'TOKEN_EXPIRED';
      } else if (err.name === 'JsonWebTokenError') {
        errorCode = 'MALFORMED_TOKEN';
      } else if (err.name === 'NotBeforeError') {
        errorCode = 'TOKEN_NOT_ACTIVE';
      }
      
      res.status(statusCode).json({
        error: 'Unauthorized',
        message: 'Invalid or expired token',
        code: errorCode,
        details: process.env.NODE_ENV === 'development' ? err.message : undefined
      });
    });
}

/**
 * Optional JWT validation (for public endpoints that can work with or without auth)
 */
function optionalJwtValidation(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return next(); // Continue without authentication
  }

  validateToken(authHeader)
    .then(userInfo => {
      // Inject user information if token is valid
      req.headers['x-user-id'] = userInfo.userId;
      req.headers['x-user-email'] = userInfo.email;
      req.headers['x-user-username'] = userInfo.username;
      req.headers['x-user-roles'] = JSON.stringify(userInfo.roles);
      req.user = userInfo;
      next();
    })
    .catch(err => {
      // Log error but continue without authentication
      console.warn('Optional JWT validation failed:', err.message);
      next();
    });
}

module.exports = {
  validateToken,
  jwtValidationMiddleware,
  optionalJwtValidation,
  getKey
};
