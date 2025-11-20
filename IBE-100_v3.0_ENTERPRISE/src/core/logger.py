"""
Enterprise Logging System
Provides structured logging with rotation, multiple handlers, and audit trails
"""

import logging
import logging.handlers
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class EnterpriseLogger:
    """Enterprise-grade logging system with multiple handlers"""
    
    def __init__(self, name: str, log_dir: Path = None):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup multiple log handlers"""
        
        # 1. Console Handler (colored output)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. File Handler (all logs)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 3. Error Handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. Structured JSON Handler (for analytics)
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'structured.json',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(json_handler)
        
        # 5. Audit Handler (audit trail)
        audit_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'audit.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        audit_handler.setFormatter(audit_formatter)
        self.logger.addHandler(audit_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra={'extra_data': kwargs} if kwargs else None)
    
    def critical(self, message: str, exc_info=None, **kwargs):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra={'extra_data': kwargs} if kwargs else None)
    
    def audit(self, action: str, details: dict = None):
        """Log audit event"""
        audit_msg = f"AUDIT: {action}"
        if details:
            audit_msg += f" | {json.dumps(details, ensure_ascii=False)}"
        self.logger.info(audit_msg)


# Global logger instance
_loggers = {}


def get_logger(name: str = "IBE100", log_dir: Path = None) -> EnterpriseLogger:
    """Get or create a logger instance"""
    if name not in _loggers:
        _loggers[name] = EnterpriseLogger(name, log_dir)
    return _loggers[name]

