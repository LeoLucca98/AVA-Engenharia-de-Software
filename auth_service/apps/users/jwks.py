"""
JWKS (JSON Web Key Set) utilities for JWT token validation.
"""
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
import os


def generate_key_pair():
    """
    Generate RSA key pair for JWT signing.
    Returns (private_key, public_key) as PEM strings.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem


def get_or_create_jwt_keys():
    """
    Get or create JWT key pair, storing them in environment variables or files.
    """
    private_key = getattr(settings, 'JWT_PRIVATE_KEY', None)
    public_key = getattr(settings, 'JWT_PUBLIC_KEY', None)
    
    if not private_key or not public_key:
        # Generate new key pair
        private_key, public_key = generate_key_pair()
        
        # Store in environment variables (in production, use secure key management)
        os.environ['JWT_PRIVATE_KEY'] = private_key
        os.environ['JWT_PUBLIC_KEY'] = public_key
        
        # Also store in settings for this session
        settings.JWT_PRIVATE_KEY = private_key
        settings.JWT_PUBLIC_KEY = public_key
    
    return private_key, public_key


def get_jwks():
    """
    Generate JWKS (JSON Web Key Set) from public key.
    """
    _, public_key_pem = get_or_create_jwt_keys()
    
    # Parse public key
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8')
    )
    
    # Get key components
    public_numbers = public_key.public_numbers()
    
    # Convert to JWK format
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "key_ops": ["verify"],
        "alg": "RS256",
        "kid": "ava-auth-key-1",  # Key ID
        "n": public_numbers.n.to_bytes(
            (public_numbers.n.bit_length() + 7) // 8, 
            byteorder='big'
        ).hex(),
        "e": public_numbers.e.to_bytes(
            (public_numbers.e.bit_length() + 7) // 7, 
            byteorder='big'
        ).hex()
    }
    
    return {
        "keys": [jwk]
    }


@require_http_methods(["GET"])
@cache_page(60 * 60)  # Cache for 1 hour
def jwks_endpoint(request):
    """
    JWKS endpoint for JWT token validation.
    Returns the public key in JWKS format.
    """
    try:
        jwks = get_jwks()
        return JsonResponse(jwks)
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to generate JWKS"}, 
            status=500
        )
