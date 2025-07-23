"""
Fast LEGO BrickEconomy Scraper
Optimized version for maximum speed with automatic popup handling
"""

import time
import logging
from typing import List, Dict, Any
from scraper import BrickEconomyScraper
from config import Config
from data_loader import DataLoader
from data_export import DataExporter
from models import LegoSetDetails

# Configure logging for speed
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

class FastLegoScraper:
    """Ultra-fast LEGO scraper with aggressive optimizations"""
    
    def __init__(self, headless: bool = True):
        """Initialize fast scraper"""
        self.config = Config()
        self.config.HEADLESS = headless  # Force headless for speed
        self.config.WAIT_TIME = 2  # Reduced wait time
        self.scraped_data = []
        
    def scrape_codes_fast(self, lego_codes: List[str], max_concurrent: int = 3) -> List[LegoSetDetails]:
        """Scrape multiple LEGO codes with speed optimizations"""
        start_time = time.time()
        results = []
        
        print(f"🚀 FAST MODE: Starting to scrape {len(lego_codes)} sets...")
        
        # Use context manager for automatic cleanup
        with BrickEconomyScraper(self.config) as scraper:
            # Single login for all searches
            scraper.login()
            print("✅ Logged in successfully")
            
            for i, code in enumerate(lego_codes, 1):
                print(f"⚡ Processing {i}/{len(lego_codes)}: {code}")
                
                try:
                    # Fast search
                    if scraper.search_lego_set(code):
                        # Fast data extraction
                        lego_set = scraper.scrape_set_details(code)
                        if lego_set.name != "Not found":
                            results.append(lego_set)
                            print(f"  ✅ Found: {lego_set.name}")
                        else:
                            print(f"  ❌ Not found: {code}")
                    else:
                        print(f"  ❌ Search failed: {code}")
                        
                except Exception as e:
                    print(f"  ❌ Error: {code} - {str(e)}")
                    logger.warning(f"Failed to scrape {code}: {str(e)}")
                
                # Minimal delay between searches
                if i < len(lego_codes):  # Don't wait after last item
                    time.sleep(0.5)
        
        elapsed = time.time() - start_time
        print(f"\n🎯 COMPLETED in {elapsed:.1f} seconds")
        print(f"📊 Success rate: {len(results)}/{len(lego_codes)} ({100*len(results)/len(lego_codes):.1f}%)")
        
        return results
    
    def quick_demo(self):
        """Quick demonstration with a few sets"""
        demo_codes = ["3920", "9469", "10333"]
        print("🚀 FAST SCRAPER DEMO")
        print("=" * 50)
        
        results = self.scrape_codes_fast(demo_codes)
        
        if results:
            print("\n📋 RESULTS:")
            for lego_set in results:
                print(f"  📦 {lego_set.code}: {lego_set.name}")
                print(f"     💰 Current: {lego_set.current_value} | Used: {lego_set.used_value}")
        
        return results

def main():
    """Main function for fast scraping"""
    import sys
    
    if len(sys.argv) > 1:
        # Command line usage
        codes = sys.argv[1].split(',')
        headless = '--headless' in sys.argv or len(sys.argv) > 2
    else:
        # Interactive mode
        codes_input = input("Enter LEGO codes (comma-separated): ").strip()
        if not codes_input:
            codes = ["3920", "9469"]  # Default demo codes
        else:
            codes = [c.strip() for c in codes_input.split(',')]
        
        headless_input = input("Use headless mode for maximum speed? (y/n) [y]: ").strip().lower()
        headless = headless_input != 'n'
    
    print(f"\n🚀 FAST MODE: {'Headless' if headless else 'Visible'}")
    
    # Create and run fast scraper
    fast_scraper = FastLegoScraper(headless=headless)
    results = fast_scraper.scrape_codes_fast(codes)
    
    # Quick export
    if results:
        exporter = DataExporter()
        filename = f"fast_scrape_{int(time.time())}"
        
        # Export to Excel
        excel_file = exporter.export_to_excel(results, filename)
        print(f"\n💾 Results saved to: {excel_file}")
        
        # Show summary
        exporter.print_summary(results)

if __name__ == "__main__":
    main()
