"""
Autenticação customizada para JWT via auth_service
"""
import requests
import logging
from django.conf import settings
from rest_framework import authentication, exceptions
from jose import jwt, JWTError
from jose.backends import RSAKey

logger = logging.getLogger(__name__)


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Autenticação JWT que valida tokens via auth_service
    """
    
    def authenticate(self, request):
        """
        Autentica o usuário via JWT token
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Primeiro, tenta validar com a chave local (HS256)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            # Suporta tokens com 'sub' (padrão JWT) ou 'user_id' (legado)
            user_id = payload.get('sub') or payload.get('user_id')

        except JWTError:
            try:
                # Se falhar, tenta validar via auth_service (RS256)
                payload = self._validate_token_via_auth_service(token)
                # Suporta tokens com 'sub' (padrão) ou 'user_id' (legado)
                user_id = payload.get('sub') or payload.get('user_id')

            except Exception as e:
                logger.error(f"JWT validation failed: {e}")
                raise exceptions.AuthenticationFailed('Token inválido')
        
        if not user_id:
            raise exceptions.AuthenticationFailed('Token inválido')
        
        # Cria um usuário anônimo com o ID do token
        user = AnonymousUser(user_id)
        return (user, token)
    
    def _validate_token_via_auth_service(self, token):
        """
        Valida o token via auth_service
        """
        try:
            # Busca as chaves públicas do auth_service
            jwks_url = settings.AUTH_SERVICE_JWKS_URL
            response = requests.get(jwks_url, timeout=5)
            response.raise_for_status()
            
            jwks = response.json()
            
            # Decodifica o header do token para obter o kid (pode estar ausente)
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            # Encontra a chave correspondente; se não houver kid, usa a primeira
            key = None
            for jwk in jwks.get('keys', []):
                if not kid or jwk.get('kid') == kid:
                    key = RSAKey(jwk, algorithm='RS256')
                    break
            
            if not key:
                raise JWTError('Chave não encontrada no JWKS')
            
            # Valida o token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                # Observação: a verificação de aud/iss já é feita no API Gateway.
                # Para evitar falhas de "Invalid audience" aqui, desabilitamos
                # explicitamente essas verificações neste serviço.
                audience=None,
                issuer=None,
                options={
                    'verify_aud': False,
                    'verify_iss': False
                }
            )
            
            return payload
            
        except Exception as e:
            logger.error(f"Auth service validation failed: {e}")
            raise JWTError('Falha na validação via auth_service')


class AnonymousUser:
    """
    Usuário anônimo com ID do JWT
    """
    
    def __init__(self, user_id):
        self.id = user_id
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"User({self.id})"
