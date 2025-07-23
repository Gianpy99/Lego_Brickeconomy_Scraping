"""
Professional LEGO BrickEconomy Scraper - No Login Version
Ultra-fast scraper that extracts public data without authentication
"""

import time
import logging
from typing import List, Dict, Any
from scraper import BrickEconomyScraper
from config import Config
from data_loader import DataLoader
from data_export import DataExporter
from models import LegoSetDetails
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Minimal logging for speed
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class PublicLegoScraper(BrickEconomyScraper):
    """High-speed scraper for public LEGO data"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.skip_login = True
    
    def extract_public_set_data(self, lego_code: str) -> LegoSetDetails:
        """Extract all available public data for a LEGO set"""
        
        # Initialize with defaults
        details = LegoSetDetails(
            lego_code=lego_code,
            official_name="Not found",
            number_of_pieces=None,
            number_of_minifigs=None,
            released=None,
            retired=None,
            retail_price_eur=None,
            retail_price_gbp=None,
            value_new_sealed=None,
            value_used=None
        )
        
        try:
            # Search for the set
            if not self.search_lego_set(lego_code):
                return details
            
            # Try to click on first result and extract name
            first_result_selectors = [
                f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[2]//a[contains(@href, "set")]',
                f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//a[contains(@href, "set")]',
                f'//a[contains(@href, "set") and contains(@href, "{lego_code}")]'
            ]
            
            result_clicked = False
            for selector in first_result_selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=5)
                    if element:
                        # Extract set name from href or text
                        try:
                            href = element.get_attribute('href')
                            if href and lego_code.lower() in href.lower():
                                # Get set name from parent elements
                                parent_text = element.find_element(By.XPATH, './ancestor::tr').text
                                for line in parent_text.split('\n'):
                                    if lego_code in line and len(line.strip()) > len(lego_code):
                                        details.official_name = line.strip()
                                        break
                                
                                if details.official_name == "Not found":
                                    details.official_name = f"LEGO Set {lego_code}"
                        except:
                            details.official_name = f"LEGO Set {lego_code}"
                        
                        # Scroll to element and click
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", element)
                        result_clicked = True
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if not result_clicked:
                return details
                
            # Wait for page load and handle popups
            time.sleep(2)
            self.handle_popups_and_cookies(aggressive=True)
            
            # Extract data using multiple strategies
            self._extract_pieces(details)
            self._extract_minifigs(details)
            self._extract_dates(details)
            self._extract_prices(details)
            
            return details
            
        except Exception as e:
            logger.warning(f"Error extracting data for {lego_code}: {str(e)}")
            return details
    
    def _extract_pieces(self, details: LegoSetDetails):
        """Extract piece count with improved selectors"""
        selectors = [
            # More specific selectors for BrickEconomy
            '//*[@id="ContentPlaceHolder1_SetDetails"]//*[contains(text(), "Pieces")]/following-sibling::*[1]',
            '//*[@id="ContentPlaceHolder1_PanelSetFacts"]//*[contains(text(), "Pieces")]/following-sibling::*[1]',
            '//*[contains(text(), "Pieces")]/following-sibling::*[1]',
            '//*[contains(text(), "Parts")]/following-sibling::*[1]',
            # Alternative pattern - look for numbers near "pieces" text
            '//div[contains(text(), "Pieces")]/..//*[contains(text(), "pieces")]',
        ]
        
        for selector in selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element:
                    text = element.text.strip()
                    if text and any(c.isdigit() for c in text):
                        # Extract number from text like "394 (PPP £0.06)" or "5197 pieces"
                        import re
                        numbers = re.findall(r'[\d,]+', text)
                        if numbers:
                            pieces_str = numbers[0].replace(',', '')
                            if pieces_str.isdigit() and int(pieces_str) > 0:
                                details.number_of_pieces = pieces_str
                                return
            except:
                continue
    
    def _extract_minifigs(self, details: LegoSetDetails):
        """Extract minifigure count with improved selectors"""
        selectors = [
            # More specific selectors for BrickEconomy
            '//*[@id="ContentPlaceHolder1_SetDetails"]//*[contains(text(), "Minifigs")]/following-sibling::*[1]',
            '//*[@id="ContentPlaceHolder1_PanelSetFacts"]//*[contains(text(), "Minifigs")]/following-sibling::*[1]',
            '//*[contains(text(), "Minifigs")]/following-sibling::*[1]',
            '//*[contains(text(), "Minifigures")]/following-sibling::*[1]',
            # Alternative - look in the set details area
            '//div[contains(text(), "Minifigs")]/..//*[text()]',
        ]
        
        for selector in selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element:
                    text = element.text.strip()
                    if text and (text.isdigit() or any(c.isdigit() for c in text)):
                        # Extract just the number
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            minifig_count = numbers[0]
                            if minifig_count.isdigit() and int(minifig_count) >= 0:
                                details.number_of_minifigs = minifig_count
                                return
            except:
                continue
    
    def _extract_dates(self, details: LegoSetDetails):
        """Extract release and retirement dates"""
        date_fields = {
            'released': ['//*[contains(text(), "Released")]/following-sibling::*[1]'],
            'retired': ['//*[contains(text(), "Retired")]/following-sibling::*[1]']
        }
        
        for field, selectors in date_fields.items():
            for selector in selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                    if element:
                        text = element.text.strip()
                        if text and text.lower() not in ['', 'n/a', 'unknown', '-']:
                            setattr(details, field, text)
                            break
                except:
                    continue
    
    def _extract_prices(self, details: LegoSetDetails):
        """Extract price information"""
        # Look for retail price
        retail_selectors = [
            '//*[contains(text(), "Retail price")]/following-sibling::*[1]',
            '//*[contains(text(), "RRP")]/following-sibling::*[1]',
        ]
        
        for selector in retail_selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element:
                    text = element.text.strip()
                    if text:
                        if '£' in text:
                            details.retail_price_gbp = text
                        elif '€' in text:
                            details.retail_price_eur = text
                        else:
                            details.retail_price_eur = text
                        break
            except:
                continue
        
        # Look for current values in visible prices
        try:
            price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '£') or contains(text(), '€')]")
            prices = []
            for elem in price_elements[:10]:  # Limit search
                try:
                    text = elem.text.strip()
                    if text and ('£' in text or '€' in text) and any(c.isdigit() for c in text):
                        prices.append(text)
                except:
                    continue
            
            # Try to identify current value (often the higher prices)
            if prices:
                # Filter out very low prices (likely not current values)
                significant_prices = [p for p in prices if any(c.isdigit() for c in p) and 
                                    int(''.join(filter(str.isdigit, p.split()[0]))) > 5]
                
                if significant_prices:
                    details.value_new_sealed = significant_prices[0]  # Take first significant price
                    
        except Exception:
            pass

def scrape_lego_codes_fast(lego_codes: List[str], headless: bool = True) -> List[LegoSetDetails]:
    """Fast scraping of multiple LEGO codes without login"""
    
    config = Config()
    config.HEADLESS = headless
    config.WAIT_TIME = 1  # Fast mode
    
    print(f"🚀 FAST PUBLIC SCRAPING: {len(lego_codes)} sets")
    print(f"⚡ Mode: {'Headless' if headless else 'Visible'}")
    print("=" * 60)
    
    results = []
    start_time = time.time()
    
    with PublicLegoScraper(config) as scraper:
        for i, code in enumerate(lego_codes, 1):
            print(f"📦 Processing {i}/{len(lego_codes)}: {code}")
            
            try:
                details = scraper.extract_public_set_data(code)
                results.append(details)
                
                # Show quick summary
                if details.official_name != "Not found":
                    print(f"  ✅ {details.official_name}")
                    if details.number_of_pieces:
                        print(f"     🧩 {details.number_of_pieces} pieces")
                    if details.retail_price_eur or details.retail_price_gbp:
                        price = details.retail_price_gbp or details.retail_price_eur
                        print(f"     💰 {price}")
                else:
                    print(f"  ❌ Not found")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                # Still add empty result to maintain order
                results.append(LegoSetDetails(lego_code=code, official_name="Error"))
            
            # Navigate back for next search (except last item)
            if i < len(lego_codes):
                scraper.driver.get("https://www.brickeconomy.com/")
                time.sleep(0.5)  # Minimal delay
    
    elapsed = time.time() - start_time
    success_count = len([r for r in results if r.official_name not in ["Not found", "Error"]])
    
    print("\n" + "=" * 60)
    print(f"🎯 COMPLETED in {elapsed:.1f} seconds")
    print(f"📊 Success: {success_count}/{len(lego_codes)} ({100*success_count/len(lego_codes):.1f}%)")
    print(f"⚡ Speed: {len(lego_codes)/elapsed*60:.1f} sets/minute")
    
    return results

def main():
    """Main function"""
    import sys
    
    # Simple command line interface
    if len(sys.argv) > 1:
        codes_input = sys.argv[1]
        codes = [c.strip() for c in codes_input.split(',')]
        headless = True  # Default to headless for command line
    else:
        # Interactive mode
        print("🚀 FAST PUBLIC LEGO SCRAPER")
        print("No login required - extracts public data only")
        print("=" * 50)
        
        codes_input = input("Enter LEGO codes (comma-separated) [3920,9469,10333]: ").strip()
        if not codes_input:
            codes = ["3920", "9469", "10333"]  # Default demo
        else:
            codes = [c.strip() for c in codes_input.split(',')]
        
        headless_input = input("Use headless mode for speed? (y/n) [y]: ").strip().lower()
        headless = headless_input != 'n'
    
    # Run scraper
    results = scrape_lego_codes_fast(codes, headless)
    
    # Export results
    if results and any(r.official_name not in ["Not found", "Error"] for r in results):
        print("\n💾 Exporting results...")
        
        exporter = DataExporter()
        timestamp = int(time.time())
        
        # Export to Excel
        excel_file = exporter.export_to_excel(results, f"public_scrape_{timestamp}")
        print(f"📊 Excel: {excel_file}")
        
        # Show summary
        print("\n📋 SUMMARY:")
        for result in results[:5]:  # Show first 5
            if result.official_name not in ["Not found", "Error"]:
                print(f"  📦 {result.lego_code}: {result.official_name}")

if __name__ == "__main__":
    main()
