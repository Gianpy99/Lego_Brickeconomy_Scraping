"""
Enhanced Logging System for LEGO BrickEconomy Scraper
Provides comprehensive logging with multiple outputs and structured formats
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
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
        
        # Add extra fields if present
        if hasattr(record, 'lego_code'):
            log_data['lego_code'] = record.lego_code
        if hasattr(record, 'url'):
            log_data['url'] = record.url
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors for console"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Format message with color
        formatted = f"{color}[{timestamp}] {record.levelname:8} {reset}"
        formatted += f"{record.name:20} | {record.getMessage()}"
        
        # Add location info for warnings and errors
        if record.levelno >= logging.WARNING:
            formatted += f" ({record.module}:{record.lineno})"
        
        return formatted


class LegoLogger:
    """Enhanced logging system for LEGO scraper"""
    
    def __init__(self, name: str = "LegoScraper", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        self._setup_error_handler()
    
    def _setup_console_handler(self):
        """Setup colored console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        # General log file (INFO and above)
        general_file = self.log_dir / "scraper.log"
        general_handler = logging.handlers.RotatingFileHandler(
            general_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')
        )
        self.logger.addHandler(general_handler)
        
        # Debug log file (all levels)
        debug_file = self.log_dir / "debug.log"
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_file, maxBytes=50*1024*1024, backupCount=3, encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(debug_handler)
    
    def _setup_error_handler(self):
        """Setup error-only handler with JSON format"""
        error_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=10*1024*1024, backupCount=10, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(error_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger"""
        return self.logger
    
    def log_scraping_start(self, operation: str, lego_code: str = None, url: str = None):
        """Log the start of a scraping operation"""
        extra = {'operation': operation}
        if lego_code:
            extra['lego_code'] = lego_code
        if url:
            extra['url'] = url
        
        self.logger.info(f"Starting {operation}", extra=extra)
    
    def log_scraping_success(self, operation: str, lego_code: str = None, 
                           duration: float = None, data_extracted: Dict[str, Any] = None):
        """Log successful scraping operation"""
        extra = {'operation': operation}
        if lego_code:
            extra['lego_code'] = lego_code
        if duration:
            extra['duration'] = duration
        
        message = f"Successfully completed {operation}"
        if duration:
            message += f" in {duration:.2f}s"
        if data_extracted:
            message += f" - extracted {len(data_extracted)} fields"
        
        self.logger.info(message, extra=extra)
    
    def log_scraping_error(self, operation: str, error: Exception, 
                          lego_code: str = None, url: str = None):
        """Log scraping error with context"""
        extra = {'operation': operation}
        if lego_code:
            extra['lego_code'] = lego_code
        if url:
            extra['url'] = url
        
        # Import here to avoid circular imports
        from exceptions import BrickEconomyScraperError
        
        if isinstance(error, BrickEconomyScraperError):
            # Log structured error info
            error_data = error.to_dict()
            self.logger.error(f"Scraping failed: {error.message}", extra={**extra, **error_data})
        else:
            # Log generic error
            self.logger.error(f"Scraping failed: {str(error)}", extra=extra, exc_info=True)
    
    def log_database_operation(self, operation: str, table: str = None, 
                             record_count: int = None, duration: float = None):
        """Log database operations"""
        extra = {'operation': f"db_{operation}"}
        if table:
            extra['table'] = table
        if duration:
            extra['duration'] = duration
        
        message = f"Database {operation}"
        if table:
            message += f" on {table}"
        if record_count:
            message += f" - {record_count} records"
        if duration:
            message += f" ({duration:.3f}s)"
        
        self.logger.info(message, extra=extra)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics"""
        extra = {'metric': metric_name, 'value': value, 'unit': unit}
        self.logger.info(f"Performance: {metric_name} = {value}{unit}", extra=extra)
    
    def create_session_summary(self, stats: Dict[str, Any]):
        """Create a summary log for the session"""
        summary_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'session_stats': stats,
            'log_files': {
                'general': str(self.log_dir / "scraper.log"),
                'debug': str(self.log_dir / "debug.log"),
                'errors': str(self.log_dir / "errors.log")
            }
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Session summary saved to {summary_file}")


# Global logger instance
_global_logger = None

def get_logger(name: str = "LegoScraper") -> logging.Logger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = LegoLogger(name)
    return _global_logger.get_logger()


def setup_logging(name: str = "LegoScraper", log_dir: str = "logs") -> LegoLogger:
    """Setup and return the logging system"""
    global _global_logger
    _global_logger = LegoLogger(name, log_dir)
    return _global_logger


# Convenience functions
def log_info(message: str, **kwargs):
    """Quick info logging"""
    get_logger().info(message, extra=kwargs)

def log_error(message: str, error: Exception = None, **kwargs):
    """Quick error logging"""
    if error:
        get_logger().error(message, exc_info=error, extra=kwargs)
    else:
        get_logger().error(message, extra=kwargs)

def log_debug(message: str, **kwargs):
    """Quick debug logging"""
    get_logger().debug(message, extra=kwargs)
