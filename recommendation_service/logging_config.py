"""
Structured logging configuration for Recommendation Service.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import uvicorn


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': 'recommendation-service',
            'correlation_id': getattr(record, 'correlation_id', None),
            'user_id': getattr(record, 'user_id', None),
            'request_id': getattr(record, 'request_id', None),
            'method': getattr(record, 'method', None),
            'path': getattr(record, 'path', None),
            'status_code': getattr(record, 'status_code', None),
            'response_time': getattr(record, 'response_time', None),
            'recommendation_id': getattr(record, 'recommendation_id', None),
            'algorithm': getattr(record, 'algorithm', None),
            'interaction_id': getattr(record, 'interaction_id', None),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class CorrelationIDFilter(logging.Filter):
    """Filter to add correlation ID to log records."""
    
    def filter(self, record):
        # Try to get correlation ID from context
        try:
            from contextvars import copy_context
            context = copy_context()
            correlation_id = context.get('correlation_id')
            if correlation_id:
                record.correlation_id = correlation_id
        except:
            pass
        return True


def setup_logging():
    """Setup structured logging for the recommendation service."""
    
    # Create formatter
    json_formatter = JSONFormatter()
    
    # Create handlers
    file_handler = logging.FileHandler('logs/recommendation_service.json.log')
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure loggers
    loggers = [
        'recommendation_service',
        'recommendation_service.requests',
        'recommendation_service.recommendations',
        'recommendation_service.interactions',
        'recommendation_service.algorithms',
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addFilter(CorrelationIDFilter())
        logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured formatting."""
    return logging.getLogger(name)


def log_request(method: str, path: str, status_code: int, response_time: float, 
                user_id: Optional[str] = None, correlation_id: Optional[str] = None):
    """Log HTTP request/response."""
    logger = get_logger('recommendation_service.requests')
    logger.info(
        f"Request: {method} {path} - {status_code}",
        extra={
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time': response_time,
            'user_id': user_id,
            'correlation_id': correlation_id,
        }
    )


def log_recommendation_event(event_type: str, user_id: Optional[str] = None, 
                           recommendation_id: Optional[str] = None, 
                           algorithm: Optional[str] = None, 
                           details: Optional[Dict[str, Any]] = None, 
                           correlation_id: Optional[str] = None):
    """Log recommendation-related events."""
    logger = get_logger('recommendation_service.recommendations')
    logger.info(
        f"Recommendation event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'algorithm': algorithm,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


def log_interaction_event(event_type: str, user_id: Optional[str] = None, 
                         interaction_id: Optional[str] = None, 
                         interaction_type: Optional[str] = None, 
                         details: Optional[Dict[str, Any]] = None, 
                         correlation_id: Optional[str] = None):
    """Log interaction events."""
    logger = get_logger('recommendation_service.interactions')
    logger.info(
        f"Interaction event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'interaction_id': interaction_id,
            'interaction_type': interaction_type,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


def log_algorithm_event(event_type: str, algorithm: str, 
                       performance_data: Optional[Dict[str, Any]] = None, 
                       details: Optional[Dict[str, Any]] = None, 
                       correlation_id: Optional[str] = None):
    """Log algorithm-related events."""
    logger = get_logger('recommendation_service.algorithms')
    logger.info(
        f"Algorithm event: {event_type}",
        extra={
            'event_type': event_type,
            'algorithm': algorithm,
            'performance_data': performance_data,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


# Setup logging when module is imported
setup_logging()
