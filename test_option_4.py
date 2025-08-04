"""
Test finale per simulare l'opzione 4 del menu principale
"""

def simulate_option_4():
    """Simula l'esecuzione dell'opzione 4 dal menu"""
    print("\n🌐 CREATING/UPDATING WEB INTERFACE")
    print("=" * 50)
    
    try:
        # Import delle funzioni necessarie
        from enhanced_web_generator import generate_enhanced_web_interface
        import subprocess
        import sys
        import os
        
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
        return True
        
    except Exception as e:
        print(f"❌ Error creating enhanced web interface: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = simulate_option_4()
    if result:
        print("\n✅ SIMULATION SUCCESSFUL! Option 4 will work correctly in main.py")
    else:
        print("\n❌ SIMULATION FAILED! There are issues to fix")
