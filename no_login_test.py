"""
No-Login LEGO BrickEconomy Scraper
Test if we can extract data without authentication
"""

from scraper import BrickEconomyScraper
from config import Config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class NoLoginScraper(BrickEconomyScraper):
    """Scraper that attempts to extract data without login"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.skip_login = True
    
    def extract_public_data(self, lego_code: str) -> dict:
        """Try to extract data that might be public"""
        data = {
            'lego_code': lego_code,
            'name': 'Not found',
            'pieces': 'Not found',
            'minifigs': 'Not found',
            'released': 'Not found',
            'retired': 'Not found',
            'retail_price_eur': 'Not found',
            'retail_price_gbp': 'Not found',
            'current_value': 'Not found',
            'used_value': 'Not found'
        }
        
        try:
            # Search for the set
            if not self.search_lego_set(lego_code):
                return data
            
            print(f"  🔍 Searching results for {lego_code}...")
            
            # Try to click on first result
            first_result_selectors = [
                '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[2]//a[contains(@href, "set")]',
                '//a[contains(@href, "set") and contains(@href, "' + lego_code + '")]',
                '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//h4//a'
            ]
            
            result_clicked = False
            for selector in first_result_selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if element and element.is_displayed():
                        # Get the set name before clicking
                        try:
                            data['name'] = element.text.strip()
                            print(f"    📦 Found set: {data['name']}")
                        except:
                            pass
                        
                        # Click to go to details page
                        self.driver.execute_script("arguments[0].click();", element)
                        result_clicked = True
                        break
                except Exception as e:
                    continue
            
            if not result_clicked:
                print(f"    ❌ Could not click on any result for {lego_code}")
                return data
                
            # Wait for details page to load
            time.sleep(3)
            
            # Handle any popups on details page
            self.handle_popups_and_cookies(aggressive=True)
            
            print(f"  📊 Extracting data from details page...")
            
            # Try to extract basic information that might be public
            info_selectors = {
                'pieces': [
                    '//*[contains(text(), "Pieces")]/following-sibling::*[1]',
                    '//*[contains(text(), "Parts")]/following-sibling::*[1]',
                    '//div[contains(@class, "pieces")]',
                ],
                'minifigs': [
                    '//*[contains(text(), "Minifigs")]/following-sibling::*[1]',
                    '//*[contains(text(), "Minifigures")]/following-sibling::*[1]',
                ],
                'released': [
                    '//*[contains(text(), "Released")]/following-sibling::*[1]',
                    '//*[contains(text(), "Release")]/following-sibling::*[1]',
                ],
                'retired': [
                    '//*[contains(text(), "Retired")]/following-sibling::*[1]',
                    '//*[contains(text(), "Retirement")]/following-sibling::*[1]',
                ],
                'retail_price_eur': [
                    '//*[contains(text(), "Retail price")]/following-sibling::*[1]',
                    '//*[contains(text(), "RRP")]/following-sibling::*[1]',
                ],
                'current_value': [
                    '//*[contains(text(), "Current value")]/following-sibling::*[1]',
                    '//*[contains(text(), "Value")]/following-sibling::*[1]',
                    '//div[contains(@class, "value")]//span',
                ]
            }
            
            # Try to extract each piece of information
            for field, selectors in info_selectors.items():
                for selector in selectors:
                    try:
                        element = self.wait_and_find_element(By.XPATH, selector, timeout=2)
                        if element and element.text.strip():
                            value = element.text.strip()
                            if value and value.lower() not in ['', 'n/a', 'unknown', '-']:
                                data[field] = value
                                print(f"    ✅ {field}: {value}")
                                break
                    except:
                        continue
            
            # Try to get any visible price information
            price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€') or contains(text(), '£') or contains(text(), '$')]")
            prices_found = []
            for elem in price_elements[:5]:  # Limit to first 5 to avoid too much noise
                try:
                    text = elem.text.strip()
                    if text and ('€' in text or '£' in text or '$' in text):
                        prices_found.append(text)
                except:
                    continue
            
            if prices_found:
                print(f"    💰 Prices found: {', '.join(prices_found)}")
                # Try to assign the first reasonable price
                for price in prices_found:
                    if '€' in price and data['retail_price_eur'] == 'Not found':
                        data['retail_price_eur'] = price
                    elif '£' in price and data['retail_price_gbp'] == 'Not found':
                        data['retail_price_gbp'] = price
            
            return data
            
        except Exception as e:
            print(f"    ❌ Error extracting data: {str(e)}")
            return data

def test_public_scraping():
    """Test scraping without login"""
    print("🚀 Testing LEGO scraping WITHOUT login")
    print("=" * 60)
    
    config = Config()
    config.HEADLESS = True  # Faster
    config.WAIT_TIME = 2    # Faster
    
    test_codes = ["3920", "9469", "10333"]
    
    with NoLoginScraper(config) as scraper:
        results = []
        
        for i, code in enumerate(test_codes, 1):
            print(f"\n⚡ Testing {i}/{len(test_codes)}: {code}")
            
            data = scraper.extract_public_data(code)
            results.append(data)
            
            # Navigate back for next search
            if i < len(test_codes):
                scraper.driver.get("https://www.brickeconomy.com/")
                time.sleep(1)
        
        print("\n" + "=" * 60)
        print("📋 RESULTS SUMMARY:")
        print("=" * 60)
        
        for data in results:
            print(f"\n📦 {data['lego_code']}: {data['name']}")
            for key, value in data.items():
                if key not in ['lego_code', 'name'] and value != 'Not found':
                    print(f"   {key}: {value}")
        
        # Count success rate
        successful_extractions = 0
        total_fields = 0
        
        for data in results:
            for key, value in data.items():
                if key != 'lego_code':
                    total_fields += 1
                    if value != 'Not found':
                        successful_extractions += 1
        
        success_rate = (successful_extractions / total_fields) * 100 if total_fields > 0 else 0
        print(f"\n📊 Success rate: {successful_extractions}/{total_fields} fields ({success_rate:.1f}%)")
        
        return results

if __name__ == "__main__":
    test_public_scraping()
