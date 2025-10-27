"""
Authentication helpers for recommendation service.
Supports both JWT validation and trusted X-User-Id headers from API Gateway.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
import json

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass


def get_jwks_from_auth_service() -> Dict[str, Any]:
    """
    Fetch JWKS from auth service. Prefer the API Gateway as proxy to avoid invalid Host issues.
    """
    jwks_url = os.getenv('AUTH_SERVICE_JWKS_URL', 'http://api-gateway/auth/.well-known/jwks.json')
    
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS from {jwks_url}: {e}")
        raise AuthenticationError("Unable to verify token")


def get_signing_key_from_jwks(jwks: Dict[str, Any], kid: str) -> str:
    """
    Extract signing key from JWKS.
    """
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return key
    raise AuthenticationError("Signing key not found")


def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Validate JWT token using JWKS from auth service.
    """
    try:
        # Decode header to get key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        if not kid:
            raise AuthenticationError("Token missing key ID")
        
        # Get JWKS and signing key
        jwks = get_jwks_from_auth_service()
        signing_key = get_signing_key_from_jwks(jwks, kid)
        
        # Validate token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=['RS256'],
            audience='ava-microservices',
            issuer='ava-auth-service',
            options={'verify_exp': True, 'verify_aud': True, 'verify_iss': True}
        )
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise AuthenticationError("Token validation failed")


def extract_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract user information from request.
    Supports both JWT tokens and trusted X-User-Id headers.
    """
    # Check for trusted header from API Gateway (internal calls)
    user_id = request.headers.get('x-user-id')
    if user_id:
        # This is a trusted internal call from API Gateway
        return {
            'user_id': int(user_id),
            'email': request.headers.get('x-user-email', ''),
            'username': request.headers.get('x-user-username', ''),
            'roles': request.headers.get('x-user-roles', '["student"]'),
            'source': 'gateway_header'
        }
    
    return None


def extract_user_from_token(credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[Dict[str, Any]]:
    """
    Extract user information from JWT token.
    """
    if not credentials:
        return None
    
    try:
        payload = validate_jwt_token(credentials.credentials)
        return {
            'user_id': int(payload.get('sub')),
            'email': payload.get('email', ''),
            'username': payload.get('username', ''),
            'roles': payload.get('roles', ['student']),
            'source': 'jwt_token'
        }
    except AuthenticationError:
        return None


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user from request.
    Tries trusted headers first, then JWT token.
    """
    # Try trusted headers first (from API Gateway)
    user = extract_user_from_request(request)
    if user:
        return user
    
    # Try JWT token
    user = extract_user_from_token(credentials)
    if user:
        return user
    
    return None


def require_authentication(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency that requires authentication.
    Raises HTTPException if no valid authentication found.
    """
    user = get_current_user(request, credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                'error': 'Authentication required',
                'message': 'Valid JWT token or trusted header required',
                'code': 'AUTHENTICATION_REQUIRED'
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    log_auth_info(user, "authenticated_request")
    return user


def require_role(required_roles: List[str]):
    """
    Dependency factory for role-based access control.
    """
    def role_checker(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Dict[str, Any]:
        user = get_current_user(request, credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Authentication required',
                    'message': 'Valid JWT token or trusted header required',
                    'code': 'AUTHENTICATION_REQUIRED'
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_roles = user.get('roles', [])
        if isinstance(user_roles, str):
            try:
                user_roles = json.loads(user_roles)
            except json.JSONDecodeError:
                user_roles = ['student']
        
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    'error': 'Insufficient permissions',
                    'message': f'Required roles: {required_roles}',
                    'code': 'INSUFFICIENT_PERMISSIONS'
                }
            )
        
        log_auth_info(user, f"role_check_{required_roles}")
        return user
    
    return role_checker


def get_user_id_from_request(request: Request) -> Optional[int]:
    """
    Extract user ID from request.
    Returns None if no valid authentication found.
    """
    user = get_current_user(request)
    return user['user_id'] if user else None


def is_internal_request(request: Request) -> bool:
    """
    Check if request is from internal service (has trusted headers).
    """
    return bool(request.headers.get('x-user-id'))


def log_auth_info(user: Dict[str, Any], action: str = ""):
    """
    Log authentication information for debugging.
    """
    logger.info(f"Auth info - User: {user['user_id']}, Source: {user['source']}, Action: {action}")


# Common dependencies
CurrentUser = Depends(require_authentication)
CurrentUserOptional = Depends(get_current_user)
StudentOrInstructor = Depends(require_role(['student', 'instructor', 'owner']))
InstructorOnly = Depends(require_role(['instructor', 'owner']))
