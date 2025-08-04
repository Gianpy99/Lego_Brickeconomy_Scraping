"""
Enhanced Custom Exceptions for the LEGO BrickEconomy Scraper
Provides comprehensive error handling with detailed context and recovery suggestions
"""

from typing import Optional, Dict, Any
import traceback
from datetime import datetime


class BrickEconomyScraperError(Exception):
    """
    Base exception for scraper-related errors with enhanced context
    
    Attributes:
        message: Human-readable error message
        error_code: Unique error identifier
        context: Additional context information
        timestamp: When the error occurred
        suggestions: Recovery suggestions for the user
    """
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None, suggestions: list = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now()
        self.suggestions = suggestions or []
        self.traceback_info = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'suggestions': self.suggestions,
            'traceback': self.traceback_info
        }
    
    def __str__(self) -> str:
        """Enhanced string representation with context"""
        base = f"{self.error_code}: {self.message}"
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            base += f" [Context: {context_str}]"
        if self.suggestions:
            base += f" [Suggestions: {'; '.join(self.suggestions)}]"
        return base


class LoginError(BrickEconomyScraperError):
    """Raised when login fails"""
    
    def __init__(self, message: str = "Login failed", username: str = None, **kwargs):
        suggestions = [
            "Check your username and password",
            "Verify internet connection",
            "Check if BrickEconomy website is accessible",
            "Try again after a few minutes"
        ]
        context = {"username": username} if username else {}
        super().__init__(message, "LOGIN_FAILED", context, suggestions, **kwargs)


class ScrapingError(BrickEconomyScraperError):
    """Raised when scraping fails"""
    
    def __init__(self, message: str = "Scraping operation failed", url: str = None, 
                 lego_code: str = None, retry_count: int = 0, **kwargs):
        suggestions = [
            "Check internet connection",
            "Verify the LEGO code is correct",
            "Try again later - the website might be temporarily unavailable",
            "Check if BrickEconomy has changed their page structure"
        ]
        context = {
            "url": url,
            "lego_code": lego_code,
            "retry_count": retry_count
        }
        super().__init__(message, "SCRAPING_FAILED", context, suggestions, **kwargs)


class ElementNotFoundError(BrickEconomyScraperError):
    """Raised when expected web elements are not found"""
    
    def __init__(self, message: str = "Required web element not found", 
                 selector: str = None, element_type: str = None, page_url: str = None, **kwargs):
        suggestions = [
            "BrickEconomy may have updated their website structure",
            "Check if the page loaded correctly",
            "Verify the LEGO code exists",
            "Try refreshing the page"
        ]
        context = {
            "selector": selector,
            "element_type": element_type,
            "page_url": page_url
        }
        super().__init__(message, "ELEMENT_NOT_FOUND", context, suggestions, **kwargs)


class DataValidationError(BrickEconomyScraperError):
    """Raised when scraped data fails validation"""
    
    def __init__(self, message: str = "Data validation failed", 
                 field_name: str = None, field_value: Any = None, 
                 expected_type: str = None, **kwargs):
        suggestions = [
            "Check data extraction logic",
            "Verify website structure hasn't changed",
            "Review validation rules",
            "Check for data format changes on BrickEconomy"
        ]
        context = {
            "field_name": field_name,
            "field_value": str(field_value) if field_value is not None else None,
            "expected_type": expected_type
        }
        super().__init__(message, "DATA_VALIDATION_FAILED", context, suggestions, **kwargs)


class DatabaseError(BrickEconomyScraperError):
    """Raised when database operations fail"""
    
    def __init__(self, message: str = "Database operation failed", 
                 operation: str = None, table: str = None, **kwargs):
        suggestions = [
            "Check database file permissions",
            "Verify disk space is available",
            "Check if database file is corrupted",
            "Try restarting the application"
        ]
        context = {
            "operation": operation,
            "table": table
        }
        super().__init__(message, "DATABASE_ERROR", context, suggestions, **kwargs)


class NetworkError(BrickEconomyScraperError):
    """Raised when network-related errors occur"""
    
    def __init__(self, message: str = "Network error occurred", 
                 url: str = None, status_code: int = None, timeout: bool = False, **kwargs):
        suggestions = [
            "Check your internet connection",
            "Verify BrickEconomy website is accessible",
            "Try again after a few minutes",
            "Check firewall settings"
        ]
        context = {
            "url": url,
            "status_code": status_code,
            "timeout": timeout
        }
        super().__init__(message, "NETWORK_ERROR", context, suggestions, **kwargs)


class ImageDownloadError(BrickEconomyScraperError):
    """Raised when image download fails"""
    
    def __init__(self, message: str = "Image download failed", 
                 image_url: str = None, lego_code: str = None, **kwargs):
        suggestions = [
            "Check internet connection",
            "Verify image URL is accessible",
            "Check disk space for image storage",
            "Try downloading the image manually"
        ]
        context = {
            "image_url": image_url,
            "lego_code": lego_code
        }
        super().__init__(message, "IMAGE_DOWNLOAD_FAILED", context, suggestions, **kwargs)


class ConfigurationError(BrickEconomyScraperError):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str = "Configuration error", 
                 config_key: str = None, config_value: Any = None, **kwargs):
        suggestions = [
            "Check your configuration file",
            "Verify all required settings are present",
            "Review the configuration documentation",
            "Reset to default configuration if needed"
        ]
        context = {
            "config_key": config_key,
            "config_value": str(config_value) if config_value is not None else None
        }
        super().__init__(message, "CONFIGURATION_ERROR", context, suggestions, **kwargs)


# Utility functions for error handling
def handle_exception(exc: Exception, logger=None) -> BrickEconomyScraperError:
    """
    Convert any exception to a BrickEconomyScraperError with context
    
    Args:
        exc: The original exception
        logger: Optional logger to record the error
    
    Returns:
        BrickEconomyScraperError with enhanced context
    """
    if isinstance(exc, BrickEconomyScraperError):
        return exc
    
    # Map common exceptions to specific error types
    if isinstance(exc, ConnectionError):
        error = NetworkError(f"Connection error: {str(exc)}")
    elif isinstance(exc, TimeoutError):
        error = NetworkError(f"Timeout error: {str(exc)}", timeout=True)
    elif isinstance(exc, ValueError):
        error = DataValidationError(f"Value error: {str(exc)}")
    elif isinstance(exc, FileNotFoundError):
        error = ConfigurationError(f"File not found: {str(exc)}")
    else:
        error = BrickEconomyScraperError(
            f"Unexpected error: {str(exc)}",
            error_code="UNEXPECTED_ERROR",
            context={"original_exception": type(exc).__name__}
        )
    
    if logger:
        logger.error(f"Exception handled: {error}")
    
    return error


def retry_on_error(max_retries: int = 3, delay: float = 1.0, 
                  exceptions: tuple = (ScrapingError, NetworkError)):
    """
    Decorator for retrying operations that might fail
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        if hasattr(e, 'context'):
                            e.context['retry_attempt'] = attempt + 1
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        break
                except Exception as e:
                    # Don't retry on unexpected exceptions
                    raise handle_exception(e)
            
            # If we get here, all retries failed
            if isinstance(last_exception, BrickEconomyScraperError):
                last_exception.context['max_retries_exceeded'] = True
                raise last_exception
            else:
                raise ScrapingError(
                    f"Operation failed after {max_retries} retries: {str(last_exception)}",
                    retry_count=max_retries
                )
        
        return wrapper
    return decorator
