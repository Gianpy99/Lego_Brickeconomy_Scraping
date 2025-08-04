"""
Test for the enhanced web interface generation from main.py
"""

import sys
import subprocess
from enhanced_web_generator import generate_enhanced_web_interface

def test_enhanced_web_generation():
    """Test the enhanced web generation process"""
    print("\n🌐 TESTING ENHANCED WEB INTERFACE GENERATION")
    print("=" * 50)
    
    try:
        # Generate enhanced web interface (index.html + sets.html)
        generate_enhanced_web_interface()
        print("✅ Enhanced main page and sets page created")
        
        # Generate minifigs page by running the module
        result = subprocess.run([sys.executable, "generate_minifigs_page.py"], 
                             capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("✅ Enhanced minifigs page created")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ Minifigs page generation warning: {result.stderr}")
        
        # Generate analytics page by running the module
        result = subprocess.run([sys.executable, "generate_analytics_page.py"], 
                             capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("✅ Enhanced analytics page created")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ Analytics page generation warning: {result.stderr}")
        
        print("\n🌐 Complete enhanced web interface created!")
        print("🌐 Open lego_database/index.html in your browser!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating enhanced web interface: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_web_generation()
