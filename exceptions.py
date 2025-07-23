"""
Custom exceptions for the LEGO BrickEconomy Scraper
"""

class BrickEconomyScraperError(Exception):
    """Base exception for scraper-related errors"""
    pass

class LoginError(BrickEconomyScraperError):
    """Raised when login fails"""
    pass

class ScrapingError(BrickEconomyScraperError):
    """Raised when scraping fails"""
    pass

class ElementNotFoundError(BrickEconomyScraperError):
    """Raised when expected web elements are not found"""
    pass

class DataValidationError(BrickEconomyScraperError):
    """Raised when scraped data fails validation"""
    pass
