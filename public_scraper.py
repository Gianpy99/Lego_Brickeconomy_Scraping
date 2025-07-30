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
        """Extract all available public data for a LEGO set with improved name extraction"""
        
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
            
            # Try to click on EXACT match first, then fallback to first result
            exact_match_selectors = [
                f'//a[contains(@href, "/{lego_code}-") or contains(@href, "/{lego_code}/") or @href[substring-after(., "/set/") = "{lego_code}"]]',
                f'//a[contains(@href, "set/{lego_code}")]',
                f'//tr[contains(., "{lego_code}")]//a[contains(@href, "set")]'
            ]

            # Fallback selectors (solo se non trova match esatto)
            fallback_selectors = [
                f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[2]//a[contains(@href, "set")]',
                f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//a[contains(@href, "set")]'
            ]
            
            result_clicked = False

            # Prima prova i match esatti
            print(f"🎯 Looking for EXACT match for {lego_code}")
            for selector in exact_match_selectors:
                try:
                    element = self.wait_and_find_element(By.XPATH, selector, timeout=3)
                    if element:
                        href = element.get_attribute('href')
                        print(f"✅ Found exact match: {href}")
                        
                        # Verify this is really our set
                        if lego_code.lower() in href.lower():
                            # Extract set name from parent row
                            self._extract_name_from_search_results(element, details, lego_code)
                            
                            # Click the exact match
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", element)
                            result_clicked = True
                            print(f"🎯 Clicked exact match for {lego_code}")
                            break
                except Exception as e:
                    continue

            # Se non trova match esatto, usa i fallback
            if not result_clicked:
                print(f"⚠️ No exact match found, trying fallback selectors...")
                for selector in fallback_selectors:
                    try:
                        element = self.wait_and_find_element(By.XPATH, selector, timeout=5)
                        if element:
                            # Extract set name from href or text
                            href = element.get_attribute('href')
                            if href and lego_code.lower() in href.lower():
                                self._extract_name_from_search_results(element, details, lego_code)
                            else:
                                details.official_name = f"LEGO Set {lego_code}"
                            
                            # Scroll to element and click
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", element)
                            result_clicked = True
                            print(f"📋 Used fallback selector for {lego_code}")
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {str(e)}")
                        continue
            
            if not result_clicked:
                return details
                
            # Wait for page load and handle popups
            time.sleep(2)
            self.handle_popups_and_cookies(aggressive=True)
            
            # NOW EXTRACT THE OFFICIAL NAME FROM THE SET PAGE
            self._extract_official_name_from_page(details, lego_code)
            
            # Extract other data using multiple strategies
            self._extract_pieces(details)
            self._extract_minifigs(details)
            self._extract_dates(details)
            self._extract_prices(details)
            
            return details
                
        except Exception as e:
            logger.warning(f"Error extracting data for {lego_code}: {str(e)}")
        
        return details
    
    def _extract_name_from_search_results(self, element, details: LegoSetDetails, lego_code: str):
        """Extract name from search results table"""
        try:
            # Try to extract name from the link text first
            link_text = element.text.strip()
            if link_text and len(link_text) > len(lego_code) and lego_code not in link_text:
                details.official_name = link_text
                return
            
            # Extract from table row
            try:
                row = element.find_element(By.XPATH, './ancestor::tr')
                cells = row.find_elements(By.TAG_NAME, 'td')
                for cell in cells:
                    cell_text = cell.text.strip()
                    # Look for the name cell (usually contains set name, not just code)
                    if (cell_text and 
                        len(cell_text) > len(lego_code) + 3 and  # Must be longer than just the code
                        not cell_text.replace(',', '').replace(' ', '').isdigit() and  # Not just numbers
                        lego_code.lower() in cell_text.lower()):  # Contains the code
                        # Clean up the name
                        name = cell_text.replace(lego_code, '').strip()
                        name = name.lstrip(':').lstrip('-').strip()  # Remove prefixes
                        if name and len(name) > 3:
                            details.official_name = f"{lego_code}: {name}"
                            return
            except:
                pass
            
            # Fallback
            details.official_name = f"LEGO Set {lego_code}"
        except:
            details.official_name = f"LEGO Set {lego_code}"
    
    def _extract_official_name_from_page(self, details: LegoSetDetails, lego_code: str):
        """Extract official set name from the individual set page"""
        
        # Selectors for set name on the individual set page
        name_selectors = [
            # Page title or main heading
            '//h1',
            '//title',
            '//*[@id="ContentPlaceHolder1_SetDetails"]//h1',
            '//*[@id="ContentPlaceHolder1_SetDetails"]//h2',
            # Look for set name in breadcrumbs or page header
            '//div[contains(@class, "breadcrumb")]//text()[last()]',
            # Look for the set name in the main content area
            '//*[@id="ContentPlaceHolder1_PanelSetDetails"]//h1',
            '//*[@id="ContentPlaceHolder1_PanelSetDetails"]//h2',
            # Generic selectors for headings containing the LEGO code
            f'//h1[contains(text(), "{lego_code}")]',
            f'//h2[contains(text(), "{lego_code}")]',
            f'//*[contains(@class, "title") or contains(@class, "heading")]//*[contains(text(), "{lego_code}")]',
        ]
        
        for selector in name_selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element:
                    text = element.text.strip()
                    if self._is_valid_set_name(text, lego_code):
                        details.official_name = self._clean_set_name(text, lego_code)
                        print(f"🏷️ Found official name from page: {details.official_name}")
                        return
            except:
                continue
        
        # If still not found, try to get from page title
        try:
            page_title = self.driver.title
            if page_title and self._is_valid_set_name(page_title, lego_code):
                details.official_name = self._clean_set_name(page_title, lego_code)
                print(f"🏷️ Found name from page title: {details.official_name}")
                return
        except:
            pass
        
        # Try meta tags
        meta_selectors = [
            '//meta[@property="og:title"]',
            '//meta[@name="title"]',
        ]
        
        for selector in meta_selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element:
                    content = element.get_attribute('content')
                    if content and self._is_valid_set_name(content, lego_code):
                        details.official_name = self._clean_set_name(content, lego_code)
                        print(f"🏷️ Found name from meta tag: {details.official_name}")
                        return
            except:
                continue
        
        # Last resort: try to find any text containing the LEGO code
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{lego_code}')]")
            for element in elements[:5]:  # Check first 5 matches
                try:
                    text = element.text.strip()
                    if self._is_valid_set_name(text, lego_code):
                        details.official_name = self._clean_set_name(text, lego_code)
                        print(f"🏷️ Found name from last resort: {details.official_name}")
                        return
                except:
                    continue
        except:
            pass

    def _is_valid_set_name(self, text: str, lego_code: str) -> bool:
        """Check if the extracted text looks like a valid LEGO set name"""
        if not text or len(text) < len(lego_code) + 3:
            return False
        
        # Must contain the LEGO code
        if lego_code.lower() not in text.lower():
            return False
        
        # Should not be just numbers or very short
        if len(text.strip()) < 10:
            return False
        
        # Exclude navigation elements and common page elements
        exclude_terms = [
            'brickeconomy', 'login', 'register', 'menu', 'navigation', 
            'cookie', 'privacy', 'terms', 'contact', 'search', 'browse',
            'sign in', 'sign up', 'cart', 'wishlist'
        ]
        
        if any(term in text.lower() for term in exclude_terms):
            return False
        
        return True

    def _clean_set_name(self, text: str, lego_code: str) -> str:
        """Clean and format the extracted set name"""
        # Remove common prefixes/suffixes
        text = text.replace('BrickEconomy', '').replace('LEGO', '').strip()
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # If the name doesn't start with the LEGO code, prepend it
        if not text.startswith(lego_code):
            # Try to find where the code appears and restructure
            if lego_code in text:
                parts = text.split(lego_code, 1)
                if len(parts) == 2:
                    name_part = parts[1].strip().lstrip(':').lstrip('-').strip()
                    if name_part:
                        text = f"{lego_code}: {name_part}"
                    else:
                        text = f"{lego_code}: {parts[0].strip()}"
            else:
                text = f"{lego_code}: {text}"
        
        # Clean up formatting
        text = text.replace('  ', ' ').strip()
        
        # Remove trailing punctuation that doesn't belong
        while text.endswith(('|', '-', ':', ';')) and len(text) > len(lego_code) + 2:
            text = text[:-1].strip()
        
        return text
    
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