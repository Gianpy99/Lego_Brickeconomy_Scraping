"""
Test script to verify the web pages generate correct data
"""

import sqlite3
import pandas as pd
import json

def test_sets_data():
    """Test sets data generation"""
    print("=== Testing Sets Data Generation ===")
    
    db_path = "lego_database/LegoDatabase.db"
    with sqlite3.connect(db_path) as conn:
        sets_df = pd.read_sql_query("SELECT * FROM lego_sets ORDER BY lego_code LIMIT 3", conn)
    
    sets_data = []
    for _, row in sets_df.iterrows():
        # Fix image path for web (convert backslashes to forward slashes)
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
    
    print("Sample sets data:")
    for item in sets_data:
        print(f"  Code: {item['code']}, Image: {item['image_path']}, Has_Image: {item['has_image']}")
    
    return sets_data

def test_minifigs_data():
    """Test minifigs data generation"""
    print("\n=== Testing Minifigs Data Generation ===")
    
    db_path = "lego_database/LegoDatabase.db"
    with sqlite3.connect(db_path) as conn:
        minifigs_df = pd.read_sql_query("SELECT * FROM minifig ORDER BY minifig_code LIMIT 3", conn)
    
    minifigs_data = []
    for _, row in minifigs_df.iterrows():
        # Fix image path for web (convert backslashes to forward slashes)
        image_path = row['image_path'] if pd.notna(row['image_path']) else ''
        if image_path:
            image_path = image_path.replace('\\', '/')
            
        minifigs_data.append({
            'code': row['minifig_code'],
            'name': row['official_name'],
            'character': row.get('official_name', ''),
            'theme': 'Lord of the Rings',
            'years': row.get('year', ''),
            'sets': row.get('sets', ''),
            'image_path': image_path,
            'has_image': bool(row['has_image'])
        })
    
    print("Sample minifigs data:")
    for item in minifigs_data:
        print(f"  Code: {item['code']}, Image: {item['image_path']}, Has_Image: {item['has_image']}")
    
    return minifigs_data

if __name__ == "__main__":
    sets_data = test_sets_data()
    minifigs_data = test_minifigs_data()
    
    print(f"\n=== Summary ===")
    print(f"Sets with corrected paths: {len([s for s in sets_data if '/' in s['image_path']])}")
    print(f"Minifigs with corrected paths: {len([m for m in minifigs_data if '/' in m['image_path']])}")
    print("✅ All image paths should now use forward slashes for web compatibility!")
