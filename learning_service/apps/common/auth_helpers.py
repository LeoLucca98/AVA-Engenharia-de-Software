"""
Authentication helpers for learning service.
Supports both JWT validation and trusted X-User-Id headers from API Gateway.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from jose import jwt, JWTError
import requests
from functools import wraps

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass


def get_jwks_from_auth_service() -> Dict[str, Any]:
    """
    Fetch JWKS from auth service.
    """
    auth_service_url = getattr(settings, 'AUTH_SERVICE_URL', 'http://auth_service:8000')
    jwks_url = f"{auth_service_url}/api/.well-known/jwks.json"
    
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
            # Convert JWK to PEM format (simplified)
            # In production, use a proper JWK to PEM converter
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


def extract_user_from_request(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """
    Extract user information from request.
    Supports both JWT tokens and trusted X-User-Id headers.
    """
    # Check for trusted header from API Gateway (internal calls)
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        # This is a trusted internal call from API Gateway
        return {
            'user_id': int(user_id),
            'email': request.META.get('HTTP_X_USER_EMAIL', ''),
            'username': request.META.get('HTTP_X_USER_USERNAME', ''),
            'roles': request.META.get('HTTP_X_USER_ROLES', '["student"]'),
            'source': 'gateway_header'
        }
    
    # Check for JWT token in Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        try:
            payload = validate_jwt_token(token)
            return {
                'user_id': int(payload.get('sub')),
                'email': payload.get('email', ''),
                'username': payload.get('username', ''),
                'roles': payload.get('roles', ['student']),
                'source': 'jwt_token'
            }
        except AuthenticationError:
            # JWT validation failed, but don't raise here
            # Let the permission classes handle it
            pass
    
    return None


def get_current_user(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """
    Get current user from request.
    Returns None if no valid authentication found.
    """
    return extract_user_from_request(request)


def require_authentication(view_func):
    """
    Decorator to require authentication for a view.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'Valid JWT token or trusted header required',
                'code': 'AUTHENTICATION_REQUIRED'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Add user to request
        request.current_user = user
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_role(required_roles: List[str]):
    """
    Decorator to require specific roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'Valid JWT token or trusted header required',
                    'code': 'AUTHENTICATION_REQUIRED'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            user_roles = user.get('roles', [])
            if isinstance(user_roles, str):
                import json
                try:
                    user_roles = json.loads(user_roles)
                except json.JSONDecodeError:
                    user_roles = ['student']
            
            if not any(role in user_roles for role in required_roles):
                return JsonResponse({
                    'error': 'Insufficient permissions',
                    'message': f'Required roles: {required_roles}',
                    'code': 'INSUFFICIENT_PERMISSIONS'
                }, status=status.HTTP_403_FORBIDDEN)
            
            request.current_user = user
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class IsAuthenticatedOrTrustedHeader(BasePermission):
    """
    Custom permission class that allows access if:
    1. User has valid JWT token, OR
    2. Request has trusted X-User-Id header from API Gateway
    """
    
    def has_permission(self, request, view):
        user = get_current_user(request)
        if user:
            request.current_user = user
            return True
        return False


class IsOwnerOrInstructor(BasePermission):
    """
    Permission class for course ownership or instructor role.
    """
    
    def has_permission(self, request, view):
        user = get_current_user(request)
        if not user:
            return False
        
        request.current_user = user
        return True
    
    def has_object_permission(self, request, view, obj):
        user = request.current_user
        user_roles = user.get('roles', [])
        
        if isinstance(user_roles, str):
            import json
            try:
                user_roles = json.loads(user_roles)
            except json.JSONDecodeError:
                user_roles = ['student']
        
        # Check if user is owner or instructor
        if hasattr(obj, 'owner_id') and obj.owner_id == user['user_id']:
            return True
        
        if 'instructor' in user_roles or 'owner' in user_roles:
            return True
        
        return False


class IsStudentOrInstructor(BasePermission):
    """
    Permission class for student or instructor access.
    """
    
    def has_permission(self, request, view):
        user = get_current_user(request)
        if not user:
            return False
        
        request.current_user = user
        return True
    
    def has_object_permission(self, request, view, obj):
        user = request.current_user
        user_roles = user.get('roles', [])
        
        if isinstance(user_roles, str):
            import json
            try:
                user_roles = json.loads(user_roles)
            except json.JSONDecodeError:
                user_roles = ['student']
        
        # Students and instructors can access
        if 'student' in user_roles or 'instructor' in user_roles or 'owner' in user_roles:
            return True
        
        return False


def get_user_id_from_request(request: HttpRequest) -> Optional[int]:
    """
    Extract user ID from request.
    Returns None if no valid authentication found.
    """
    user = get_current_user(request)
    return user['user_id'] if user else None


def is_internal_request(request: HttpRequest) -> bool:
    """
    Check if request is from internal service (has trusted headers).
    """
    return bool(request.META.get('HTTP_X_USER_ID'))


def log_auth_info(request: HttpRequest, action: str = ""):
    """
    Log authentication information for debugging.
    """
    user = get_current_user(request)
    if user:
        logger.info(f"Auth info - User: {user['user_id']}, Source: {user['source']}, Action: {action}")
    else:
        logger.warning(f"No authentication found - Action: {action}")
