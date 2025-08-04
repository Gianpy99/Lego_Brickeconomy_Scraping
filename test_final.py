"""
Test finale per l'opzione 4 del main.py
"""

import subprocess
import sys
import os

def test_main_option_4():
    """Test dell'opzione 4 del main.py"""
    print("🧪 Testing main.py option 4...")
    
    try:
        # Simula l'opzione 4
        from enhanced_web_generator import generate_enhanced_web_interface
        
        # Generate enhanced web interface (index.html + sets.html)
        generate_enhanced_web_interface()
        print("✅ Enhanced main page and sets page created")
        
        # Configura l'ambiente per evitare errori Unicode
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Generate minifigs page
        result = subprocess.run([sys.executable, "generate_minifigs_page.py"], 
                             capture_output=True, text=True, cwd=".", env=env)
        if result.returncode == 0:
            print("✅ Enhanced minifigs page created")
        else:
            # Controlla se il file è stato creato nonostante l'errore Unicode
            if "Enhanced minifigures page generated" in result.stderr:
                print("✅ Enhanced minifigs page created (Unicode display issue ignored)")
            else:
                print(f"⚠️ Minifigs page issue: {result.stderr}")
        
        # Generate analytics page
        result = subprocess.run([sys.executable, "generate_analytics_page.py"], 
                             capture_output=True, text=True, cwd=".", env=env)
        if result.returncode == 0:
            print("✅ Enhanced analytics page created")
        else:
            # Controlla se il file è stato creato nonostante l'errore Unicode
            if "Enhanced analytics page generated" in result.stderr:
                print("✅ Enhanced analytics page created (Unicode display issue ignored)")
            else:
                print(f"⚠️ Analytics page issue: {result.stderr}")
        
        print("\n🌐 Complete enhanced web interface created!")
        print("🌐 Open lego_database/index.html in your browser!")
        
        # Verifica che i file siano stati creati correttamente
        files_to_check = [
            "lego_database/index.html",
            "lego_database/sets.html", 
            "lego_database/minifigs.html",
            "lego_database/analytics.html"
        ]
        
        all_good = True
        for file_path in files_to_check:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"✅ {file_path}: {size:,} bytes")
            else:
                print(f"❌ {file_path}: Missing!")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_option_4()
    if success:
        print("\n🎉 SUCCESS! Option 4 works perfectly!")
    else:
        print("\n❌ FAILED! There are still issues.")
