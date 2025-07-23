"""
Quick test script for optimized scraping without login
"""

from scraper import BrickEconomyScraper
from config import Config
import time

def test_search_optimization():
    """Test the search functionality without login"""
    config = Config()
    config.HEADLESS = True  # Force headless
    
    print("🚀 Testing optimized search without login...")
    
    with BrickEconomyScraper(config) as scraper:
        start_time = time.time()
        
        # Test search for public data
        code = "3920"
        print(f"⚡ Searching for {code}...")
        
        if scraper.search_lego_set(code):
            print(f"✅ Search successful for {code}")
            
            # Try to extract some basic info that doesn't require login
            try:
                # Navigate to first result if available  
                from selenium.webdriver.common.by import By
                results = scraper.driver.find_elements(By.XPATH, "//a[contains(@href, 'set')]")
                if results:
                    print(f"📦 Found {len(results)} potential results")
                else:
                    print("❌ No results found")
            except Exception as e:
                print(f"⚠️ Could not extract results: {e}")
        else:
            print(f"❌ Search failed for {code}")
        
        elapsed = time.time() - start_time
        print(f"⏱️ Completed in {elapsed:.1f} seconds")

if __name__ == "__main__":
    test_search_optimization()
