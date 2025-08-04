"""
Script per analizzare i collegamenti tra minifigure e set LEGO
"""
import sqlite3
import json

def analyze_connections():
    """Analizza i collegamenti tra minifigure e set basati sui dati"""
    conn = sqlite3.connect('lego_database/LegoDatabase.db')
    cursor = conn.cursor()
    
    # Get all sets with themes
    cursor.execute('SELECT lego_code, official_name, theme FROM lego_sets ORDER BY lego_code')
    sets = cursor.fetchall()
    
    # Get all minifigs with sets info
    cursor.execute('SELECT minifig_code, official_name, sets FROM minifig ORDER BY minifig_code')
    minifigs = cursor.fetchall()
    
    print(f"=== ANALYSIS RESULTS ===")
    print(f"Total sets: {len(sets)}")
    print(f"Total minifigs: {len(minifigs)}")
    
    # Sample minifig sets data
    print(f"\n=== SAMPLE MINIFIG-SET CONNECTIONS ===")
    for i, (code, name, sets_info) in enumerate(minifigs[:10]):
        print(f"- {code} ({name}): sets = {sets_info}")
    
    # Create matrix data
    matrix_data = {
        'sets': [],
        'minifigs': [],
        'connections': []
    }
    
    # Add sets data
    for set_code, set_name, set_theme in sets:
        matrix_data['sets'].append({
            'code': set_code,
            'name': set_name,
            'theme': set_theme or 'Unknown'
        })
    
    # Add minifigs data and create connections
    for minifig_code, minifig_name, minifig_sets in minifigs:
        matrix_data['minifigs'].append({
            'code': minifig_code,
            'name': minifig_name,
            'sets': minifig_sets or ''
        })
        
        # Parse the sets field to create connections
        if minifig_sets:
            # Try to extract set codes from the sets field
            # This might be comma-separated or other format
            set_codes = []
            if ',' in minifig_sets:
                set_codes = [s.strip() for s in minifig_sets.split(',')]
            else:
                # Try to match against known set codes
                for set_code, _, _ in sets:
                    if set_code in minifig_sets:
                        set_codes.append(set_code)
            
            # Create connections
            for set_code in set_codes:
                # Verify the set exists
                if any(s[0] == set_code for s in sets):
                    matrix_data['connections'].append({
                        'minifig_code': minifig_code,
                        'set_code': set_code
                    })
    
    print(f"\n=== MATRIX SUMMARY ===")
    print(f"Total connections: {len(matrix_data['connections'])}")
    
    # Group by theme
    themes = {}
    for set_item in matrix_data['sets']:
        theme = set_item['theme']
        if theme not in themes:
            themes[theme] = {'sets': [], 'minifigs': set()}
        themes[theme]['sets'].append(set_item['code'])
        
        # Add minifigs for this theme
        for conn in matrix_data['connections']:
            if conn['set_code'] == set_item['code']:
                themes[theme]['minifigs'].add(conn['minifig_code'])
    
    print(f"\n=== CONNECTIONS BY THEME ===")
    for theme, data in themes.items():
        print(f"- {theme}: {len(data['sets'])} sets, {len(data['minifigs'])} minifigs")
    
    # Save matrix data for the web page
    with open('lego_database/matrix_data.json', 'w', encoding='utf-8') as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)
    
    print("Matrix data saved to: lego_database/matrix_data.json")
    
    conn.close()
    return matrix_data

if __name__ == "__main__":
    analyze_connections()
