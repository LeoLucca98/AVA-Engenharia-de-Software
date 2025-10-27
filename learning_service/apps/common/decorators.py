"""
Decoradores utilitários para autenticação e autorização
"""
import functools
import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


def extract_user_id(request):
    """
    Extrai o user_id do JWT ou do header X-User-Id
    """
    # Primeiro, tenta extrair do header X-User-Id (se o gateway validar)
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        return int(user_id)
    
    # Se não encontrar, tenta extrair do usuário autenticado
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.id
    
    return None


def require_authentication(view_func):
    """
    Decorador que requer autenticação
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = extract_user_id(request)
        if not user_id:
            return JsonResponse(
                {'error': 'Autenticação necessária'}, 
                status=401
            )
        
        # Adiciona o user_id ao request para uso posterior
        request.user_id = user_id
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_owner_or_instructor(view_func):
    """
    Decorador que requer que o usuário seja owner ou instructor do curso
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = extract_user_id(request)
        if not user_id:
            return JsonResponse(
                {'error': 'Autenticação necessária'}, 
                status=401
            )
        
        # Verifica se o usuário é owner ou instructor
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        if course_id:
            from apps.enrollments.models import Enrollment
            
            enrollment = Enrollment.objects.filter(
                course_id=course_id,
                user_id=user_id,
                role__in=['instructor', 'owner'],
                status='active'
            ).first()
            
            if not enrollment:
                return JsonResponse(
                    {'error': 'Permissão negada. Apenas owners/instructors podem acessar este recurso'}, 
                    status=403
                )
        
        request.user_id = user_id
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_student_or_instructor(view_func):
    """
    Decorador que requer que o usuário seja student ou instructor do curso
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = extract_user_id(request)
        if not user_id:
            return JsonResponse(
                {'error': 'Autenticação necessária'}, 
                status=401
            )
        
        # Verifica se o usuário está matriculado no curso
        course_id = kwargs.get('course_id') or kwargs.get('pk')
        if course_id:
            from apps.enrollments.models import Enrollment
            
            enrollment = Enrollment.objects.filter(
                course_id=course_id,
                user_id=user_id,
                status='active'
            ).first()
            
            if not enrollment:
                return JsonResponse(
                    {'error': 'Permissão negada. Você não está matriculado neste curso'}, 
                    status=403
                )
        
        request.user_id = user_id
        return view_func(request, *args, **kwargs)
    
    return wrapper


def log_interaction(view_func):
    """
    Decorador que registra interações do usuário
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = extract_user_id(request)
        
        # Executa a view
        response = view_func(request, *args, **kwargs)
        
        # Registra a interação se for bem-sucedida
        if response.status_code in [200, 201, 204] and user_id:
            try:
                # App progress está na raiz (progress.models)
                from progress.models import Interaction
                
                # Determina o tipo de interação baseado no método HTTP
                interaction_type = 'view'
                if request.method == 'POST':
                    interaction_type = 'create'
                elif request.method == 'PUT' or request.method == 'PATCH':
                    interaction_type = 'update'
                elif request.method == 'DELETE':
                    interaction_type = 'delete'
                
                # Cria a interação
                Interaction.objects.create(
                    user_id=user_id,
                    interaction_type=interaction_type,
                    payload={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to log interaction: {e}")
        
        return response
    
    return wrapper
