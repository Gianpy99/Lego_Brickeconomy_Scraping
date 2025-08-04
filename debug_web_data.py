import sqlite3
import pandas as pd
import json

# Test database connectivity and data
try:
    conn = sqlite3.connect('lego_database/LegoDatabase.db')
    
    # Check sets
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lego_sets')
    sets_count = cursor.fetchone()[0]
    print(f"Sets in database: {sets_count}")
    
    # Get sample data
    cursor.execute('SELECT lego_code, official_name FROM lego_sets LIMIT 5')
    sets_sample = cursor.fetchall()
    print("\nFirst 5 sets:")
    for row in sets_sample:
        print(f"  {row[0]}: {row[1]}")
    
    # Test the actual query used by the generator
    sets_df = pd.read_sql_query("SELECT * FROM lego_sets ORDER BY lego_code", conn)
    print(f"\nDataFrame shape: {sets_df.shape}")
    print(f"Columns: {list(sets_df.columns)}")
    
    # Generate sample data like the web generator does
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
    
    print(f"\nGenerated {len(sets_data)} sets for web page")
    if sets_data:
        print(f"First set: {sets_data[0]['code']} - {sets_data[0]['name']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
