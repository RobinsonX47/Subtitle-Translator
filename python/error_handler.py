#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive error handling and recovery system for subtitle translation
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorType(Enum):
    """Categories of errors"""
    API_ERROR = "api_error"
    FILE_READ_ERROR = "file_read_error"
    FILE_WRITE_ERROR = "file_write_error"
    PARSING_ERROR = "parsing_error"
    TRANSLATION_ERROR = "translation_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorRecord:
    """Represents a single error event"""
    error_type: str
    severity: str
    filename: str
    language: Optional[str]
    message: str
    details: Optional[Dict] = None
    timestamp: Optional[str] = None
    recoverable: bool = False
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)
    
    def is_retryable(self) -> bool:
        """Check if this error can be retried"""
        return self.recoverable and self.retry_count < self.max_retries
    
    def increment_retry(self) -> 'ErrorRecord':
        """Increment retry count"""
        self.retry_count += 1
        return self

class ErrorLogger:
    """Centralized error logging and tracking"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.errors: List[ErrorRecord] = []
        self.log_file = log_file or "translation_errors.log"
        self.failed_files: Dict[str, List[ErrorRecord]] = {}
    
    def log_error(
        self,
        error_type: str,
        severity: str,
        filename: str,
        language: Optional[str] = None,
        message: str = "",
        details: Optional[Dict] = None,
        recoverable: bool = False
    ) -> ErrorRecord:
        """Log an error and return the error record"""
        error = ErrorRecord(
            error_type=error_type,
            severity=severity,
            filename=filename,
            language=language,
            message=message,
            details=details,
            recoverable=recoverable
        )
        
        self.errors.append(error)
        
        # Track failed files
        key = f"{filename}_{language}" if language else filename
        if key not in self.failed_files:
            self.failed_files[key] = []
        self.failed_files[key].append(error)
        
        # Write to file
        self._write_to_log_file(error)
        
        return error
    
    def _write_to_log_file(self, error: ErrorRecord):
        """Write error to log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error.to_dict()) + '\n')
        except Exception as e:
            print(f"Failed to write error log: {e}")
    
    def get_failed_files(self) -> List[Tuple[str, str, int]]:
        """Get list of failed files with language and error count"""
        failed = []
        for key, errors in self.failed_files.items():
            parts = key.split('_')
            filename = parts[0]
            lang = '_'.join(parts[1:]) if len(parts) > 1 else None
            failed.append((filename, lang, len(errors)))
        return failed
    
    def get_retryable_failures(self) -> List[Dict]:
        """Get list of failures that can be retried"""
        retryable = []
        for key, errors in self.failed_files.items():
            for error in errors:
                if error.is_retryable():
                    retryable.append({
                        'filename': error.filename,
                        'language': error.language,
                        'error_type': error.error_type,
                        'message': error.message
                    })
        return retryable
    
    def get_summary(self) -> Dict:
        """Get error summary statistics"""
        return {
            'total_errors': len(self.errors),
            'by_type': self._count_by_type(),
            'by_severity': self._count_by_severity(),
            'failed_files_count': len(self.failed_files),
            'retryable_count': len(self.get_retryable_failures())
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count errors by type"""
        counts = {}
        for error in self.errors:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count errors by severity"""
        counts = {}
        for error in self.errors:
            counts[error.severity] = counts.get(error.severity, 0) + 1
        return counts
    
    def clear_log(self):
        """Clear error log file"""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
        except Exception as e:
            print(f"Failed to clear log: {e}")
    
    def export_errors(self, filepath: str):
        """Export errors to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([e.to_dict() for e in self.errors], f, indent=2)
        except Exception as e:
            print(f"Failed to export errors: {e}")

class ErrorRecovery:
    """Error recovery and retry strategies"""
    
    @staticmethod
    def should_retry_api_error(error: Exception) -> bool:
        """Determine if API error is retryable"""
        error_str = str(error).lower()
        
        # Retryable: rate limits, timeouts, temporary failures
        retryable_keywords = [
            'rate limit', 'timeout', 'temporarily', 'connection',
            'overloaded', '429', '503', '502', 'unavailable'
        ]
        
        return any(keyword in error_str for keyword in retryable_keywords)
    
    @staticmethod
    def get_retry_delay(retry_count: int) -> float:
        """Get exponential backoff delay in seconds"""
        # 1s, 2s, 4s, 8s, max 60s
        delay = min(2 ** retry_count, 60)
        return float(delay)
    
    @staticmethod
    def get_error_message_for_ui(error: ErrorRecord) -> str:
        """Format error message for UI display"""
        messages = {
            ErrorType.API_ERROR.value: f"API error: {error.message}",
            ErrorType.FILE_READ_ERROR.value: f"Cannot read file: {error.message}",
            ErrorType.FILE_WRITE_ERROR.value: f"Cannot write file: {error.message}",
            ErrorType.PARSING_ERROR.value: f"Format error: {error.message}",
            ErrorType.TRANSLATION_ERROR.value: f"Translation failed: {error.message}",
            ErrorType.TIMEOUT_ERROR.value: "Request timed out - will retry",
            ErrorType.RATE_LIMIT_ERROR.value: "Rate limited - waiting before retry",
            ErrorType.AUTHENTICATION_ERROR.value: "Authentication failed - check API key",
            ErrorType.VALIDATION_ERROR.value: f"Validation error: {error.message}",
            ErrorType.UNKNOWN_ERROR.value: f"Unknown error: {error.message}"
        }
        return messages.get(error.error_type, f"Error: {error.message}")
