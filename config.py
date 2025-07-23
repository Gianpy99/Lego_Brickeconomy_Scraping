"""
Configuration settings for the LEGO BrickEconomy Scraper
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the scraper"""
    
    # BrickEconomy website settings
    BASE_URL = "https://www.brickeconomy.com/"
    LOGIN_URL = "https://www.brickeconomy.com/"
    
    # User credentials (loaded from environment)
    USERNAME = os.getenv("BRICKECONOMY_USERNAME", "")
    PASSWORD = os.getenv("BRICKECONOMY_PASSWORD", "")
    
    # Selenium settings
    HEADLESS = os.getenv("CHROME_HEADLESS", "false").lower() == "true"
    WAIT_TIME = 10
    SCRAPING_DELAY = int(os.getenv("SCRAPING_DELAY", "2"))
    
    # Output settings
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "xlsx")
    OUTPUT_DIRECTORY = "output"
    
    # Target themes to filter results
    TARGET_THEMES: List[str] = [
        "The Lord of the Rings",
        "Harry Potter", 
        "Icons",
        "Games",
        "BrickHeadz",
        "Dimensions",
        "The Hobbit"
    ]
    
    # XPath selectors
    class XPaths:
        SEARCH_BOX = '//*[@id="txtSearchHeader"]'
        SETS_TAB = '//a[@href="#sets"]'
        COOKIE_ACCEPT = '//*[@id="ez-accept-all"]'
        LOGIN_BUTTON = '//*[@id="MenuLogin"]/a/span'
        USERNAME_FIELD = '//*[@id="LoginModalUsername"]'
        PASSWORD_FIELD = '//*[@id="LoginModalPassword"]'
        LOGIN_SUBMIT = '//*[@id="LoginModalLogin"]'
        
        # Set details page
        SET_DETAILS_PANEL = '//*[@id="ContentPlaceHolder1_SetDetails"]'
        PRICING_PANEL = '//*[@id="ContentPlaceHolder1_PanelSetPricing"]'
        FACTS_PANEL = '//*[@id="ContentPlaceHolder1_PanelSetFacts"]'
        
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        errors = []
        
        if not cls.USERNAME:
            errors.append("BRICKECONOMY_USERNAME not set")
        if not cls.PASSWORD:
            errors.append("BRICKECONOMY_PASSWORD not set")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
