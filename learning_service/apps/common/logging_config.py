"""
Structured logging configuration for Learning Service.
"""
import json
import logging
import uuid
from datetime import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': 'learning-service',
            'correlation_id': getattr(record, 'correlation_id', None),
            'user_id': getattr(record, 'user_id', None),
            'request_id': getattr(record, 'request_id', None),
            'method': getattr(record, 'method', None),
            'path': getattr(record, 'path', None),
            'status_code': getattr(record, 'status_code', None),
            'response_time': getattr(record, 'response_time', None),
            'course_id': getattr(record, 'course_id', None),
            'lesson_id': getattr(record, 'lesson_id', None),
            'enrollment_id': getattr(record, 'enrollment_id', None),
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


class CorrelationIDMiddleware(MiddlewareMixin):
    """Middleware to add correlation ID to requests."""
    
    def process_request(self, request):
        # Get correlation ID from header or generate new one
        correlation_id = request.META.get('HTTP_X_REQUEST_ID') or str(uuid.uuid4())
        request.correlation_id = correlation_id
        
        # Add to request META for logging
        request.META['CORRELATION_ID'] = correlation_id


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log HTTP requests and responses."""
    
    def process_request(self, request):
        request.start_time = datetime.utcnow()
        
        # Log request
        logger = logging.getLogger('learning_service.requests')
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'correlation_id': getattr(request, 'correlation_id', None),
                'method': request.method,
                'path': request.path,
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'remote_addr': request.META.get('REMOTE_ADDR'),
                'content_type': request.META.get('CONTENT_TYPE'),
                'content_length': request.META.get('CONTENT_LENGTH'),
                'user_id': request.META.get('HTTP_X_USER_ID'),
            }
        )
    
    def process_response(self, request, response):
        # Calculate response time
        if hasattr(request, 'start_time'):
            response_time = (datetime.utcnow() - request.start_time).total_seconds()
        else:
            response_time = None
        
        # Log response
        logger = logging.getLogger('learning_service.requests')
        logger.info(
            f"Request completed: {request.method} {request.path} - {response.status_code}",
            extra={
                'correlation_id': getattr(request, 'correlation_id', None),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content) if hasattr(response, 'content') else None,
                'user_id': request.META.get('HTTP_X_USER_ID'),
            }
        )
        
        # Add correlation ID to response headers
        if hasattr(request, 'correlation_id'):
            response['X-Request-ID'] = request.correlation_id
        
        return response


def get_logger(name):
    """Get a logger with structured formatting."""
    logger = logging.getLogger(name)
    
    # Add correlation ID to all log records
    class CorrelationIDFilter(logging.Filter):
        def filter(self, record):
            # Try to get correlation ID from current request context
            try:
                from django.utils.deprecation import get_current_request
                request = get_current_request()
                if request and hasattr(request, 'correlation_id'):
                    record.correlation_id = request.correlation_id
            except:
                pass
            return True
    
    # Add filter to logger
    if not any(isinstance(f, CorrelationIDFilter) for f in logger.filters):
        logger.addFilter(CorrelationIDFilter())
    
    return logger


def log_learning_event(event_type, user_id=None, course_id=None, lesson_id=None, 
                      enrollment_id=None, details=None, correlation_id=None):
    """Log learning-related events."""
    logger = get_logger('learning_service.learning')
    logger.info(
        f"Learning event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'enrollment_id': enrollment_id,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


def log_progress_event(event_type, user_id=None, lesson_id=None, course_id=None, 
                      progress_data=None, details=None, correlation_id=None):
    """Log progress-related events."""
    logger = get_logger('learning_service.progress')
    logger.info(
        f"Progress event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'lesson_id': lesson_id,
            'course_id': course_id,
            'progress_data': progress_data,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


def log_enrollment_event(event_type, user_id=None, course_id=None, enrollment_id=None, 
                        role=None, details=None, correlation_id=None):
    """Log enrollment-related events."""
    logger = get_logger('learning_service.enrollment')
    logger.info(
        f"Enrollment event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'course_id': course_id,
            'enrollment_id': enrollment_id,
            'role': role,
            'details': details,
            'correlation_id': correlation_id,
        }
    )


def log_interaction_event(event_type, user_id=None, lesson_id=None, course_id=None, 
                         interaction_type=None, details=None, correlation_id=None):
    """Log interaction events."""
    logger = get_logger('learning_service.interaction')
    logger.info(
        f"Interaction event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': user_id,
            'lesson_id': lesson_id,
            'course_id': course_id,
            'interaction_type': interaction_type,
            'details': details,
            'correlation_id': correlation_id,
        }
    )
