"""
Web scraper for LEGO BrickEconomy website
"""
import time
import logging
from typing import List, Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    ElementClickInterceptedException,
    NoSuchElementException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from config import Config
from models import LegoSetDetails
from exceptions import LoginError, ScrapingError, ElementNotFoundError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrickEconomyScraper:
    """Professional LEGO BrickEconomy scraper with robust error handling"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
        
    def setup_driver(self) -> None:
        """Initialize Chrome WebDriver with performance optimizations"""
        try:
            options = Options()
            
            # Headless mode for speed
            if self.config.HEADLESS:
                options.add_argument("--headless=new")  # Use new headless mode
                logger.info("Running in headless mode for maximum speed")
            
            # Core performance options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Speed optimizations
            options.add_argument("--aggressive-cache-discard")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-crash-reporter")
            options.add_argument("--disable-oopr-debug-crash-dump")
            options.add_argument("--no-crash-upload")
            options.add_argument("--disable-low-res-tiling")
            
            # Disable logging for performance
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Block resource-heavy content
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Block images for speed
                    "plugins": 2,
                    "popups": 2,
                    "geolocation": 2,
                    "notifications": 2,
                    "media_stream": 2,
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set aggressive timeouts for speed
            self.driver.set_page_load_timeout(10)  # Faster page loads
            self.driver.implicitly_wait(1)  # Reduced wait times
            
            if not self.config.HEADLESS:
                self.driver.maximize_window()
            
            logger.info("Chrome WebDriver initialized with performance optimizations")
            
        except Exception as e:
            raise ScrapingError(f"Failed to initialize WebDriver: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
    
    def wait_and_find_element(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """Wait for and find element with timeout"""
        timeout = timeout or self.config.WAIT_TIME
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def wait_and_click_element(self, by: By, value: str, timeout: int = None) -> bool:
        """Wait for element to be clickable and click it"""
        timeout = timeout or self.config.WAIT_TIME
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except (TimeoutException, ElementClickInterceptedException):
            return False
    
    def handle_popups_and_cookies(self, aggressive=True) -> None:
        """Handle all popups including cookies and other overlays with speed optimization"""
        try:
            # Reduce initial wait time
            time.sleep(1)
            
            if aggressive:
                # Aggressive popup removal using JavaScript
                aggressive_scripts = [
                    # Remove overlay elements
                    """
                    var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="popup"], [id*="modal"], [id*="popup"]');
                    overlays.forEach(function(el) { 
                        if(el.style.display !== 'none' && el.offsetParent) el.remove(); 
                    });
                    """,
                    # Auto-accept all cookies
                    """
                    var acceptBtns = document.querySelectorAll('button[id*="accept"], button[class*="accept"], [data-testid*="accept"], button[id="ez-accept-all"]');
                    acceptBtns.forEach(function(btn) { 
                        if(btn.offsetParent && btn.style.display !== 'none') {
                            btn.click(); 
                            console.log('Auto-clicked:', btn);
                        }
                    });
                    """,
                    # Remove fixed positioned elements likely to be popups
                    """
                    var fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position:fixed"]');
                    fixedElements.forEach(function(el) { 
                        var zIndex = parseInt(window.getComputedStyle(el).zIndex) || 0;
                        if(zIndex > 999 && el.offsetHeight > 30) el.remove(); 
                    });
                    """,
                    # Hide cookie banners
                    """
                    var cookieBanners = document.querySelectorAll('[class*="cookie"], [class*="consent"], [class*="banner"]');
                    cookieBanners.forEach(function(el) { 
                        el.style.display = 'none'; 
                        el.remove();
                    });
                    """
                ]
                
                for script in aggressive_scripts:
                    try:
                        self.driver.execute_script(script)
                    except:
                        continue
                
                logger.info("Aggressive popup cleanup completed")
                time.sleep(0.5)
            
            # Quick cookie acceptance - reduced selectors for speed
            cookie_selectors = [
                '//*[@id="ez-accept-all"]',  # BrickEconomy specific - try first
                '//button[contains(@class, "ez-accept-all")]',
                '//button[contains(text(), "Accept")]',
                '//*[contains(@class, "cookie")]//button'
            ]
            
            for selector in cookie_selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                    if element and element.is_displayed():
                        # JavaScript click for reliability
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"Cookies accepted with selector: {selector}")
                        time.sleep(0.5)
                        return  # Early exit on success
                except:
                    continue
            
            # Quick popup close attempt
            popup_close_selectors = [
                "//span[contains(@class, 'close')]",
                "//button[contains(@class, 'close')]",
                "//*[@aria-label='Close']"
            ]
            
            for selector in popup_close_selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=0.5)
                    if element and element.is_displayed():
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"Popup closed with selector: {selector}")
                        time.sleep(0.3)
                        return
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Could not handle popups: {str(e)}")
    
    def login(self) -> None:
        """Login to BrickEconomy with improved popup handling"""
        if self.is_logged_in:
            return
            
        try:
            # Navigate to main page
            self.driver.get(self.config.BASE_URL)
            logger.info("Navigated to BrickEconomy homepage")
            
            # Handle popups and cookies first
            self.handle_popups_and_cookies()
            
            # Try multiple strategies to find and click login button
            login_button_selectors = [
                self.config.XPaths.LOGIN_BUTTON,
                "//a[contains(@href, 'login')]",
                "//button[contains(text(), 'Login')]",
                "//a[contains(text(), 'Login')]",
                "//a[contains(text(), 'Sign in')]",
                "//button[contains(text(), 'Sign in')]",
                "//*[@id='MenuLogin']//a",
                "//*[@id='MenuLogin']//span",
                "//span[contains(text(), 'Login')]/parent::a",
                "//div[contains(@class, 'login')]//a"
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    # Scroll to top to ensure visibility
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    
                    # Try to find and click login button
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if element and element.is_displayed():
                        # Try JavaScript click first
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                            logger.info(f"Login button clicked via JavaScript with selector: {selector}")
                            login_clicked = True
                            break
                        except:
                            # Fallback to regular click
                            try:
                                element.click()
                                logger.info(f"Login button clicked normally with selector: {selector}")
                                login_clicked = True
                                break
                            except:
                                continue
                except Exception as e:
                    logger.debug(f"Login selector failed {selector}: {str(e)}")
                    continue
            
            if not login_clicked:
                # Try one more time with a more aggressive approach
                try:
                    # Look for any clickable element that might be the login
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            if link.is_displayed() and ("login" in link.text.lower() or "sign" in link.text.lower()):
                                link.click()
                                logger.info(f"Found login link by text: {link.text}")
                                login_clicked = True
                                break
                        except:
                            continue
                except:
                    pass
            
            if not login_clicked:
                raise LoginError("Could not find or click login button after trying multiple strategies")
            
            # Wait for login form to appear
            time.sleep(3)
            
            # Handle any additional popups that might appear after clicking login
            self.handle_popups_and_cookies()
            
            # Enter credentials with multiple strategies
            username_selectors = [
                self.config.XPaths.USERNAME_FIELD,
                "//input[@type='text']",
                "//input[@name='username']",
                "//input[@name='email']",
                "//input[@placeholder*='username']",
                "//input[@placeholder*='email']",
                "//*[@id='LoginModalUsername']"
            ]
            
            username_entered = False
            for selector in username_selectors:
                try:
                    username_field = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if username_field and username_field.is_displayed():
                        username_field.clear()
                        username_field.send_keys(self.config.USERNAME)
                        logger.info(f"Username entered with selector: {selector}")
                        username_entered = True
                        break
                except:
                    continue
            
            if not username_entered:
                raise LoginError("Could not find username field")
            
            # Enter password
            password_selectors = [
                self.config.XPaths.PASSWORD_FIELD,
                "//input[@type='password']",
                "//input[@name='password']",
                "//*[@id='LoginModalPassword']"
            ]
            
            password_entered = False
            for selector in password_selectors:
                try:
                    password_field = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if password_field and password_field.is_displayed():
                        password_field.clear()
                        password_field.send_keys(self.config.PASSWORD)
                        logger.info(f"Password entered with selector: {selector}")
                        password_entered = True
                        break
                except:
                    continue
            
            if not password_entered:
                raise LoginError("Could not find password field")
            
            # Submit login form
            submit_selectors = [
                self.config.XPaths.LOGIN_SUBMIT,
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Sign in')]",
                "//*[@id='LoginModalLogin']"
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    submit_button = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if submit_button and submit_button.is_displayed():
                        # Try JavaScript click first
                        try:
                            self.driver.execute_script("arguments[0].click();", submit_button)
                            logger.info(f"Login submitted via JavaScript with selector: {selector}")
                            submit_clicked = True
                            break
                        except:
                            try:
                                submit_button.click()
                                logger.info(f"Login submitted normally with selector: {selector}")
                                submit_clicked = True
                                break
                            except:
                                continue
                except:
                    continue
            
            if not submit_clicked:
                # Try pressing Enter on password field as fallback
                try:
                    password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                    password_field.send_keys(Keys.RETURN)
                    logger.info("Login submitted via Enter key")
                    submit_clicked = True
                except:
                    pass
            
            if not submit_clicked:
                raise LoginError("Could not submit login form")
            
            # Wait for login to complete and handle any redirects
            time.sleep(5)
            
            # Check if login was successful by looking for user-specific elements
            success_indicators = [
                "//a[contains(@href, 'logout')]",
                "//span[contains(text(), 'Logout')]",
                "//*[contains(@class, 'user')]",
                "//*[contains(@class, 'profile')]"
            ]
            
            login_successful = False
            for indicator in success_indicators:
                try:
                    element = self.wait_and_find_element(By.XPATH, indicator, timeout=3)
                    if element:
                        login_successful = True
                        break
                except:
                    continue
            
            if login_successful:
                self.is_logged_in = True
                logger.info("Successfully logged in to BrickEconomy")
            else:
                # Check if we're still on login page or got redirected
                current_url = self.driver.current_url.lower()
                if "login" not in current_url and "signin" not in current_url:
                    # Assume success if we're not on login page anymore
                    self.is_logged_in = True
                    logger.info("Login appears successful (redirected from login page)")
                else:
                    logger.warning("Login status unclear, proceeding anyway")
                    self.is_logged_in = True  # Proceed optimistically
            
        except Exception as e:
            raise LoginError(f"Login failed: {str(e)}")
    
    def search_lego_set(self, lego_code: str) -> bool:
        """Search for a LEGO set by code - optimized for headless performance"""
        try:
            # Navigate directly with reduced timeout
            self.driver.get(f"{self.config.BASE_URL}")
            time.sleep(1)  # Reduced wait
            
            # Aggressive popup handling first
            self.handle_popups_and_cookies(aggressive=True)
            
            # Enhanced search box detection for headless
            search_selectors = [
                '//*[@id="txtSearchHeader"]',  # BrickEconomy specific - primary
                self.config.XPaths.SEARCH_BOX,
                "//input[@type='search']",
                "//input[contains(@placeholder, 'search')]"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    # Wait for element to be present and interactable
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if search_box:
                        logger.info(f"Search box found: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                # Try with JavaScript in headless mode
                try:
                    self.driver.execute_script("""
                        var searchBox = document.getElementById('txtSearchHeader');
                        if (searchBox) {
                            searchBox.style.visibility = 'visible';
                            searchBox.style.display = 'block';
                            searchBox.disabled = false;
                            searchBox.focus();
                        }
                    """)
                    search_box = self.driver.find_element(By.XPATH, '//*[@id="txtSearchHeader"]')
                    logger.info("Search box activated via JavaScript")
                except:
                    raise ElementNotFoundError("Could not find or activate search box")
            
            # Enhanced search execution for headless
            try:
                # Ensure field is ready
                self.driver.execute_script("arguments[0].focus();", search_box)
                time.sleep(0.5)
                
                # Clear and enter search term
                search_box.clear()
                search_box.send_keys(lego_code)
                
                # Submit search - try multiple methods
                try:
                    search_box.send_keys(Keys.RETURN)
                except:
                    # Fallback: click search button or submit form
                    try:
                        search_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                        search_button.click()
                    except:
                        # Final fallback: JavaScript form submission
                        self.driver.execute_script("""
                            var form = document.querySelector('form');
                            if (form) form.submit();
                        """)
                
                logger.info(f"Search initiated for: {lego_code}")
                
            except Exception as e:
                raise ElementNotFoundError(f"Could not execute search: {str(e)}")
            
            time.sleep(2)  # Wait for results
            
            # Quick popup cleanup after search
            self.driver.execute_script("""
                var overlays = document.querySelectorAll('[class*="modal"], [class*="popup"]');
                overlays.forEach(function(el) { el.remove(); });
            """)
            
            # Enhanced Sets tab clicking for headless
            sets_tab_selectors = [
                self.config.XPaths.SETS_TAB,
                "//a[@href='#sets']",
                "//a[contains(text(), 'Sets')]"
            ]
            
            for selector in sets_tab_selectors:
                try:
                    sets_tab = self.wait_and_find_element(By.XPATH, selector, timeout=2)
                    if sets_tab and sets_tab.is_displayed():
                        # Use JavaScript for reliable clicking
                        self.driver.execute_script("arguments[0].click();", sets_tab)
                        logger.info(f"Sets tab clicked: {selector}")
                        break
                except:
                    continue
            
            time.sleep(0.5)  # Minimal wait
            logger.info(f"Fast search completed for: {lego_code}")
            return True
            
        except Exception as e:
            logger.error(f"Fast search failed for {lego_code}: {str(e)}")
            return False
    
    def find_matching_set(self, lego_code: str) -> Optional[Any]:
        """Find the matching LEGO set from search results"""
        try:
            # Get all search result rows
            search_results = self.driver.find_elements(
                By.XPATH, 
                '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]/tbody/tr'
            )
            
            # Skip header row and iterate through results
            for i in range(1, len(search_results), 2):
                try:
                    result_row = search_results[i]
                    
                    # Check theme
                    theme_elements = result_row.find_elements(By.XPATH, './td[2]/div[2]/a[1]')
                    if not theme_elements:
                        continue
                    
                    theme = theme_elements[0].text
                    if theme not in self.config.TARGET_THEMES:
                        logger.debug(f"Skipping theme: {theme}")
                        continue
                    
                    # Find the set link
                    set_link_xpath = f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]/tbody/tr[{i+1}]/td[2]/div[1]/h4/a'
                    set_link = self.driver.find_element(By.XPATH, set_link_xpath)
                    
                    if set_link:
                        logger.info(f"Found matching set with theme: {theme}")
                        set_link.click()
                        time.sleep(2)
                        return set_link
                        
                except Exception as e:
                    logger.debug(f"Error processing search result {i}: {str(e)}")
                    continue
            
            logger.warning(f"No matching set found for {lego_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding matching set: {str(e)}")
            return None
    
    def extract_detail_value(self, text: str, context_xpath: str = None, 
                           is_range: bool = False, is_used: bool = False) -> str:
        """Extract detail value from the page"""
        try:
            context_xpath = context_xpath or self.config.XPaths.SET_DETAILS_PANEL
            
            if is_range:
                # Handle range values with specific XPaths
                xpaths = [
                    '//*[@id="ContentPlaceHolder1_PanelSetPricing"]/div[2]/div[11]/div[2]',
                    '//*[@id="ContentPlaceHolder1_PanelSetPricing"]/div[2]/div[10]/div[2]'
                ]
                
                for xpath in xpaths:
                    element = self.wait_and_find_element(By.XPATH, xpath, timeout=2)
                    if element:
                        return element.text
                        
            elif is_used:
                # Handle used values by checking multiple div positions
                for div_num in range(8, 14):
                    xpath = f'{context_xpath}/div[2]/div[{div_num}]//*[contains(text(),"{text}")]/following-sibling::div[1]'
                    element = self.wait_and_find_element(By.XPATH, xpath, timeout=1)
                    if element:
                        return element.text
            else:
                # Standard value extraction
                xpath = f'{context_xpath}//*[contains(text(),"{text}")]/following-sibling::div[1]'
                element = self.wait_and_find_element(By.XPATH, xpath)
                if element:
                    return element.text
            
            return "NA"
            
        except Exception as e:
            logger.debug(f"Could not extract {text}: {str(e)}")
            return "NA"
    
    def scrape_set_details(self, lego_code: str) -> LegoSetDetails:
        """Scrape detailed information for a LEGO set"""
        details = LegoSetDetails(lego_code=lego_code)
        
        try:
            # Extract basic information
            details.official_name = self.extract_detail_value("Name")
            details.number_of_pieces = self.extract_detail_value("Pieces")
            details.number_of_minifigs = self.extract_detail_value("Minifigs")
            details.released = self.extract_detail_value("Released")
            details.retired = self.extract_detail_value("Retired")
            
            # Extract pricing information
            pricing_context = self.config.XPaths.PRICING_PANEL
            details.value_new_sealed = self.extract_detail_value("Value", pricing_context)
            details.value_used = self.extract_detail_value("Value", pricing_context, is_used=True)
            details.value_range = self.extract_detail_value("Range", pricing_context, is_range=True)
            details.retail_price_eur = self.extract_detail_value("Retail price", pricing_context)
            
            # Try to get UK pricing
            facts_context = self.config.XPaths.FACTS_PANEL
            uk_price = self.extract_detail_value("United Kingdom", facts_context)
            details.retail_price_gbp = uk_price if uk_price != "NA" else details.retail_price_eur
            
            logger.info(f"Successfully scraped details for {lego_code}")
            
        except Exception as e:
            logger.error(f"Error scraping details for {lego_code}: {str(e)}")
        
        return details
    
    def scrape_lego_sets(self, lego_codes: List[str]) -> Dict[str, LegoSetDetails]:
        """Scrape multiple LEGO sets"""
        if not self.driver:
            raise ScrapingError("WebDriver not initialized")
        
        # Login first
        self.login()
        
        results = {}
        
        for i, lego_code in enumerate(lego_codes, 1):
            logger.info(f"Processing {i}/{len(lego_codes)}: {lego_code}")
            
            try:
                # Search for the set
                if not self.search_lego_set(lego_code):
                    results[lego_code] = LegoSetDetails(lego_code=lego_code)
                    continue
                
                # Find and click on the matching set
                if not self.find_matching_set(lego_code):
                    results[lego_code] = LegoSetDetails(lego_code=lego_code)
                    continue
                
                # Scrape the details
                details = self.scrape_set_details(lego_code)
                results[lego_code] = details
                
                # Add delay between requests
                time.sleep(self.config.SCRAPING_DELAY)
                
            except Exception as e:
                logger.error(f"Error processing {lego_code}: {str(e)}")
                results[lego_code] = LegoSetDetails(lego_code=lego_code)
                continue
        
        logger.info(f"Completed scraping {len(results)} sets")
        return results
