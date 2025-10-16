"""
Utilitários comuns para o learning_service
"""
import json
import logging
from typing import Any, Dict, List, Optional
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Carrega JSON de forma segura, retornando default em caso de erro
    """
    try:
        return json.loads(json_string) if json_string else default
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Serializa dados para JSON de forma segura
    """
    try:
        return json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize JSON: {e}")
        return default


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 20) -> Dict:
    """
    Pagina um queryset manualmente
    """
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    items = list(queryset[start:end])
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
        'has_next': end < total,
        'has_previous': page > 1
    }


def validate_tags(tags: List[str]) -> List[str]:
    """
    Valida e limpa tags
    """
    if not tags:
        return []
    
    # Remove tags vazias e duplicadas
    cleaned_tags = list(set([tag.strip().lower() for tag in tags if tag.strip()]))
    
    # Limita o número de tags
    return cleaned_tags[:10]


def validate_metadata(metadata: Dict) -> Dict:
    """
    Valida e limpa metadata
    """
    if not isinstance(metadata, dict):
        return {}
    
    # Remove chaves com valores None ou vazios
    cleaned_metadata = {
        k: v for k, v in metadata.items() 
        if v is not None and v != ''
    }
    
    return cleaned_metadata


def calculate_progress_percentage(completed_lessons: int, total_lessons: int) -> float:
    """
    Calcula a porcentagem de progresso
    """
    if total_lessons == 0:
        return 0.0
    
    return round((completed_lessons / total_lessons) * 100, 2)


def get_user_role_in_course(user_id: int, course_id: int) -> Optional[str]:
    """
    Obtém o papel do usuário em um curso
    """
    from apps.enrollments.models import Enrollment
    
    enrollment = Enrollment.objects.filter(
        course_id=course_id,
        user_id=user_id,
        status='active'
    ).first()
    
    return enrollment.role if enrollment else None


def is_user_enrolled_in_course(user_id: int, course_id: int) -> bool:
    """
    Verifica se o usuário está matriculado no curso
    """
    from apps.enrollments.models import Enrollment
    
    return Enrollment.objects.filter(
        course_id=course_id,
        user_id=user_id,
        status='active'
    ).exists()


def can_user_access_course(user_id: int, course_id: int) -> bool:
    """
    Verifica se o usuário pode acessar o curso (enrolled ou public)
    """
    from apps.courses.models import Course
    
    # Verifica se o curso é público
    course = Course.objects.filter(id=course_id, is_published=True).first()
    if not course:
        return False
    
    # Se o usuário é o owner, pode acessar
    if course.owner_id == user_id:
        return True
    
    # Se o usuário está matriculado, pode acessar
    return is_user_enrolled_in_course(user_id, course_id)


def send_interaction_event(user_id: int, lesson_id: int, interaction_type: str, payload: Dict):
    """
    Envia evento de interação para o recommendation service
    """
    try:
        import requests
        
        event_data = {
            'user_id': user_id,
            'lesson_id': lesson_id,
            'interaction_type': interaction_type,
            'payload': payload,
            'timestamp': None  # Será preenchido pelo recommendation service
        }
        
        # URL do recommendation service (configurável)
        recommendation_url = getattr(settings, 'RECOMMENDATION_SERVICE_URL', 'http://recommendation_service:8000')
        events_url = f"{recommendation_url}/events/interaction"
        
        response = requests.post(
            events_url,
            json=event_data,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code not in [200, 201]:
            logger.warning(f"Failed to send interaction event: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending interaction event: {e}")


def format_lesson_content(content: str, content_type: str = 'markdown') -> str:
    """
    Formata o conteúdo da lição baseado no tipo
    """
    if not content:
        return ""
    
    if content_type == 'html':
        return content
    
    # Para markdown, poderia usar uma biblioteca como markdown
    # Por enquanto, retorna como está
    return content


def extract_user_id(request) -> Optional[int]:
    """
    Extrai o ID do usuário do token JWT na requisição
    """
    try:
        # Verifica se há um header de autorização
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        # Remove o prefixo "Bearer "
        token = auth_header[7:]
        
        # Decodifica o token JWT (sem verificação de assinatura para simplicidade)
        import base64
        import json
        
        # Divide o token em partes
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decodifica o payload (parte do meio)
        payload = parts[1]
        # Adiciona padding se necessário
        payload += '=' * (4 - len(payload) % 4)
        
        decoded_payload = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded_payload)
        
        # Retorna o user_id do payload
        return payload_data.get('user_id')
        
    except Exception as e:
        logger.warning(f"Error extracting user ID from token: {e}")
        return None