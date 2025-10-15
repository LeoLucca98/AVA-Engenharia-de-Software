from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import time
import uuid
from auth_helpers import (
    require_authentication, get_current_user, get_user_id_from_request,
    CurrentUser, CurrentUserOptional, log_auth_info
)
from logging_config import (
    get_logger, log_request, log_recommendation_event, 
    log_interaction_event, log_algorithm_event
)

app = FastAPI(
    title="AVA Recommendation Service",
    description="Serviço de recomendações inteligentes para o AVA - Adaptive Virtual Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=[
        {"url": "http://localhost:8003", "description": "Development server"},
        {"url": "http://recommendation_service:8000", "description": "Internal service"},
    ],
    contact={
        "name": "AVA Development Team",
        "email": "dev@ava.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "recommendations",
            "description": "Operações de recomendação de conteúdo",
        },
        {
            "name": "interactions",
            "description": "Processamento de eventos de interação",
        },
        {
            "name": "health",
            "description": "Verificação de saúde do serviço",
        },
    ],
)

# Add correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # Add to request state
    request.state.correlation_id = correlation_id
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request
    log_request(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        response_time=process_time,
        user_id=request.headers.get("X-User-Id"),
        correlation_id=correlation_id
    )
    
    # Add correlation ID to response headers
    response.headers["X-Request-ID"] = correlation_id
    
    return response

class InteractionEvent(BaseModel):
    user_id: int
    lesson_id: int
    interaction_type: str
    payload: dict
    timestamp: Optional[str] = None

class RecommendationRequest(BaseModel):
    user_id: int
    course_id: Optional[int] = None
    limit: int = 10

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[dict]
    metadata: dict

@app.get("/", tags=["health"])
async def root():
    """Root endpoint - verifica se o serviço está rodando."""
    return {"message": "Recommendation Service is running"}

@app.get("/health/", tags=["health"])
async def health_check():
    """Health check endpoint - verifica a saúde do serviço."""
    return {"status": "healthy", "service": "recommendation"}

@app.get("/healthz/", tags=["health"])
async def health_check_z():
    """Health check endpoint - verifica a saúde do serviço (formato /healthz)."""
    return {"status": "healthy", "service": "recommendation"}

@app.post("/events/interaction", tags=["interactions"])
async def receive_interaction_event(
    event: InteractionEvent,
    request: Request,
    current_user: Dict[str, Any] = CurrentUser
):
    """
    Recebe eventos de interação do learning_service.
    
    Este endpoint processa eventos de interação do usuário com o conteúdo,
    como visualizações, cliques, conclusões de lições, etc.
    """
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    log_auth_info(current_user, "interaction_event")
    log_interaction_event(
        event_type="interaction_received",
        user_id=str(current_user['user_id']),
        interaction_id=f"{event.user_id}_{event.lesson_id}_{event.interaction_type}",
        interaction_type=event.interaction_type,
        details={
            "lesson_id": event.lesson_id,
            "payload": event.payload
        },
        correlation_id=correlation_id
    )
    
    return {
        "message": "Interaction event received",
        "event_id": f"{event.user_id}_{event.lesson_id}_{event.interaction_type}",
        "processed_by": current_user['user_id']
    }

@app.post("/recommendations/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: Dict[str, Any] = CurrentUser
):
    """
    Gera recomendações para um usuário
    """
    log_auth_info(current_user, "get_recommendations")
    # Implementação básica - retorna recomendações mockadas
    mock_recommendations = [
        {
            "course_id": 1,
            "title": "Python para Iniciantes",
            "score": 0.95,
            "reason": "Baseado no seu interesse em programação"
        },
        {
            "course_id": 2,
            "title": "Django Web Development",
            "score": 0.87,
            "reason": "Recomendado para quem gosta de Python"
        }
    ]
    
    return RecommendationResponse(
        user_id=request.user_id,
        recommendations=mock_recommendations[:request.limit],
        metadata={
            "total_recommendations": len(mock_recommendations),
            "algorithm": "collaborative_filtering",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    )

@app.get("/recommendations/user/{user_id}")
async def get_user_recommendations(
    user_id: int, 
    limit: int = 10,
    current_user: Optional[Dict[str, Any]] = CurrentUserOptional
):
    """
    Obtém recomendações para um usuário específico
    """
    if current_user:
        log_auth_info(current_user, f"get_user_recommendations_for_{user_id}")
    
    request = RecommendationRequest(user_id=user_id, limit=limit)
    return await get_recommendations(request, current_user or {})

@app.get("/recommendations/me")
async def get_my_recommendations(
    limit: int = 10,
    current_user: Dict[str, Any] = CurrentUser
):
    """
    Obtém recomendações para o usuário atual
    """
    log_auth_info(current_user, "get_my_recommendations")
    
    request = RecommendationRequest(user_id=current_user['user_id'], limit=limit)
    return await get_recommendations(request, current_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
