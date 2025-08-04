"""
Debug per capire perché la pagina sets.html è vuota
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path

def debug_sets_page_generation():
    """Debug della generazione della pagina sets"""
    try:
        print("🔍 DEBUG: Generazione pagina sets.html")
        
        # 1. Verifica connessione database
        db_path = "lego_database/LegoDatabase.db"
        print(f"Database path: {db_path}")
        print(f"Database exists: {Path(db_path).exists()}")
        
        # 2. Test query SQL
        with sqlite3.connect(db_path) as conn:
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets ORDER BY lego_code", conn)
            print(f"Query result: {len(sets_df)} sets found")
            
        # 3. Test generazione dati JSON
        sets_data = []
        for _, row in sets_df.iterrows():
            image_path = row['image_path'] if pd.notna(row['image_path']) else ''
            if image_path:
                image_path = image_path.replace('\\', '/')
            
            sets_data.append({
                'code': row['lego_code'],
                'name': row['official_name'],
                'pieces': row['number_of_pieces'],
                'minifigs': row['number_of_minifigs'],
                'released': row['released'],
                'theme': row['theme'],
                'price_eur': row['retail_price_eur'],
                'price_gbp': row['retail_price_gbp'],
                'image_path': image_path,
                'has_image': bool(row['has_image'])
            })
        
        print(f"Generated data: {len(sets_data)} sets")
        
        # 4. Test JSON serialization
        json_data = json.dumps(sets_data, ensure_ascii=False)
        print(f"JSON length: {len(json_data)} characters")
        
        # 5. Test dell'enhanced web generator
        print("\n🧪 Testing enhanced web generator...")
        from enhanced_web_generator import ResponsiveWebGenerator
        
        generator = ResponsiveWebGenerator()
        sets_page = generator.generate_sets_page_with_search()
        print(f"Enhanced generator result: {sets_page}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_sets_page_generation()
