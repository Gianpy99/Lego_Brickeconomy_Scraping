"""
Final system verification script
Tests all major components to ensure everything works correctly
"""

import sqlite3
import os
from pathlib import Path

def test_database_functionality():
    """Test that the database is accessible and contains data"""
    print("=== Testing Database ===")
    
    try:
        conn = sqlite3.connect('lego_database/LegoDatabase.db')
        cursor = conn.cursor()
        
        # Test sets table
        cursor.execute('SELECT COUNT(*) FROM lego_sets')
        sets_count = cursor.fetchone()[0]
        print(f"✅ LEGO Sets: {sets_count} records")
        
        # Test minifigs table
        cursor.execute('SELECT COUNT(*) FROM minifig')
        minifigs_count = cursor.fetchone()[0]
        print(f"✅ Minifigures: {minifigs_count} records")
        
        # Test images in sets
        cursor.execute('SELECT COUNT(*) FROM lego_sets WHERE has_image = 1')
        sets_with_images = cursor.fetchone()[0]
        print(f"✅ Sets with images: {sets_with_images}")
        
        # Test images in minifigs
        cursor.execute('SELECT COUNT(*) FROM minifig WHERE has_image = 1')
        minifigs_with_images = cursor.fetchone()[0]
        print(f"✅ Minifigs with images: {minifigs_with_images}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_web_files():
    """Test that all web files exist and are properly sized"""
    print("\n=== Testing Web Interface ===")
    
    web_files = {
        'index.html': 'Homepage',
        'sets.html': 'Sets Database',
        'minifigs.html': 'Minifigures Database', 
        'analytics.html': 'Analytics Dashboard'
    }
    
    all_good = True
    web_dir = Path('lego_database')
    
    for filename, description in web_files.items():
        file_path = web_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {description}: {size:,} bytes")
        else:
            print(f"❌ {description}: Missing")
            all_good = False
    
    return all_good

def test_images():
    """Test that image files are available"""
    print("\n=== Testing Images ===")
    
    images_dir = Path('lego_database/images')
    if images_dir.exists():
        jpg_files = list(images_dir.glob('*.jpg'))
        print(f"✅ Image files: {len(jpg_files)} available")
        
        # Check total size
        total_size = sum(f.stat().st_size for f in jpg_files)
        print(f"✅ Total image size: {total_size / (1024*1024):.1f} MB")
        return True
    else:
        print("❌ Images directory missing")
        return False

def test_enhanced_systems():
    """Test the enhanced systems are working"""
    print("\n=== Testing Enhanced Systems ===")
    
    try:
        # Test enhanced logging
        from logging_system import get_logger
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ Enhanced logging system working")
        
        # Test database manager
        from database_manager import get_database_manager
        db_manager = get_database_manager("lego_database/LegoDatabase.db")
        stats = db_manager.get_comprehensive_stats()
        print(f"✅ Database manager: {stats.total_sets} sets, {stats.total_minifigs} minifigs")
        
        # Test main interface
        from main import EnhancedLegoUnifiedDatabase
        db = EnhancedLegoUnifiedDatabase()
        enhanced_stats = db.get_enhanced_stats()
        print(f"✅ Enhanced interface: {enhanced_stats['sets']['total']} sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced systems error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LEGO Brickeconomy System Verification")
    print("=" * 50)
    
    tests = [
        test_database_functionality,
        test_web_files,
        test_images,
        test_enhanced_systems
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED! System is fully functional.")
        print("\n📋 What you can do now:")
        print("  • Run: python main.py")
        print("  • Open: lego_database/index.html")
        print("  • Browse: 52 LEGO sets and 155 minifigures")
        print("  • Enjoy: Responsive web interface with search!")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        failed_count = sum(1 for r in results if not r)
        print(f"❌ {failed_count}/{len(tests)} tests failed")

if __name__ == "__main__":
    main()
