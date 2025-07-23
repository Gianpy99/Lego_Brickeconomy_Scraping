#!/usr/bin/env python3
"""
Quick Test Script for LEGO BrickEconomy Scraper
==============================================

A simple test script to verify that all modules can be imported
and basic functionality works without needing full credentials.

Usage: python test_imports.py
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from config import Config
        print("✅ config.py imported successfully")
        
        from models import LegoSetDetails
        print("✅ models.py imported successfully")
        
        from exceptions import BrickEconomyScraperError
        print("✅ exceptions.py imported successfully")
        
        from data_loader import DataLoader
        print("✅ data_loader.py imported successfully")
        
        from data_export import DataExporter
        print("✅ data_export.py imported successfully")
        
        # Test scraper import (might fail if selenium not installed)
        try:
            from scraper import BrickEconomyScraper
            print("✅ scraper.py imported successfully")
        except ImportError as e:
            print(f"⚠️  scraper.py import warning: {e}")
            print("   This is normal if selenium is not installed yet")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_models():
    """Test data models"""
    print("\n🧪 Testing data models...")
    
    try:
        from models import LegoSetDetails
        
        # Create a test instance
        test_set = LegoSetDetails(
            lego_code="12345",
            official_name="Test Set",
            retail_price_eur="€29.99"
        )
        
        print("✅ LegoSetDetails created successfully")
        
        # Test price cleaning
        clean_prices = test_set.get_clean_prices()
        print(f"✅ Price cleaning works: {clean_prices}")
        
        # Test to_dict
        data_dict = test_set.to_dict()
        print("✅ to_dict() method works")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test error: {e}")
        return False

def test_data_loader():
    """Test data loader with sample data"""
    print("\n🧪 Testing data loader...")
    
    try:
        from data_loader import DataLoader
        
        # Test string loading
        codes = DataLoader.load_from_list("1234,5678,9012")
        print(f"✅ String loading: {codes}")
        
        # Test list loading
        codes = DataLoader.load_from_list(['1234', '5678', '9012'])
        print(f"✅ List loading: {codes}")
        
        # Test validation
        valid_codes = DataLoader.validate_codes(['1234', 'ABC123', '!!!'])
        print(f"✅ Validation works: {valid_codes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loader test error: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        
        # Test basic configuration
        config = Config()
        print(f"✅ Config created: {config.BASE_URL}")
        print(f"✅ Target themes: {len(config.TARGET_THEMES)} themes")
        print(f"✅ Wait time: {config.WAIT_TIME}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LEGO BrickEconomy Scraper - Module Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_models,
        test_data_loader,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scraper modules are working correctly.")
        print("\nNext steps:")
        print("1. Run: python setup.py (to install dependencies)")
        print("2. Configure your .env file with credentials")
        print("3. Run: python demo.py (for interactive demonstration)")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("Make sure you have installed the requirements: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
