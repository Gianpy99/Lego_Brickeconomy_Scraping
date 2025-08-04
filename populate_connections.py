#!/usr/bin/env python3
"""
Script to populate set_minifig_relations table
Extracts set codes from minifig.sets column and creates connections
"""

import sqlite3
import re
from logging_system import setup_logging, get_logger

# Setup logging
logger_system = setup_logging("ConnectionsPopulator")
logger = get_logger(__name__)

def extract_set_codes_from_names(sets_text, available_sets):
    """Extract set codes from set names text"""
    if not sets_text:
        return []
    
    # Dictionary to map set names to codes
    name_to_code = {}
    for code, name in available_sets:
        # Create multiple variations for matching
        variations = [
            name,
            name.replace(" ", ""),
            re.sub(r'^\d+\s+', '', name),  # Remove leading number
            code  # Also try the code itself
        ]
        for variation in variations:
            name_to_code[variation.lower()] = code
    
    found_codes = []
    set_names = [s.strip() for s in sets_text.split(',')]
    
    for set_name in set_names:
        set_name_clean = set_name.strip()
        
        # Try exact match first
        if set_name_clean.lower() in name_to_code:
            found_codes.append(name_to_code[set_name_clean.lower()])
            continue
        
        # Try to extract set code from the beginning
        code_match = re.match(r'^(\d+)', set_name_clean)
        if code_match:
            potential_code = code_match.group(1)
            if potential_code in [code for code, _ in available_sets]:
                found_codes.append(potential_code)
                continue
        
        # Try fuzzy matching
        for name_key, code in name_to_code.items():
            if set_name_clean.lower() in name_key or name_key in set_name_clean.lower():
                found_codes.append(code)
                break
    
    return list(set(found_codes))  # Remove duplicates

def populate_connections():
    """Populate the set_minifig_relations table"""
    db_path = "lego_database/LegoDatabase.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all available sets
        cursor.execute("SELECT lego_code, official_name FROM lego_sets WHERE lego_code IS NOT NULL")
        available_sets = cursor.fetchall()
        logger.info(f"Found {len(available_sets)} available sets")
        
        # Get all minifigs with set information
        cursor.execute("SELECT minifig_code, sets FROM minifig WHERE sets IS NOT NULL AND sets != ''")
        minifigs_with_sets = cursor.fetchall()
        logger.info(f"Found {len(minifigs_with_sets)} minifigs with set information")
        
        connections_created = 0
        connections_data = []
        
        for minifig_code, sets_text in minifigs_with_sets:
            set_codes = extract_set_codes_from_names(sets_text, available_sets)
            
            for set_code in set_codes:
                connections_data.append((set_code, minifig_code))
                connections_created += 1
            
            if set_codes:
                logger.debug(f"Minifig {minifig_code}: {sets_text} -> {set_codes}")
        
        # Insert connections
        if connections_data:
            cursor.executemany(
                "INSERT OR IGNORE INTO set_minifig_relations (set_code, minifig_code) VALUES (?, ?)",
                connections_data
            )
            conn.commit()
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM set_minifig_relations")
        final_count = cursor.fetchone()[0]
        
        logger.info(f"Successfully created {connections_created} connections")
        logger.info(f"Total connections in database: {final_count}")
        
        # Show some statistics
        cursor.execute("""
            SELECT s.theme, COUNT(*) as connections
            FROM set_minifig_relations r
            JOIN lego_sets s ON r.set_code = s.lego_code
            GROUP BY s.theme
            ORDER BY connections DESC
        """)
        
        theme_stats = cursor.fetchall()
        logger.info("Connections by theme:")
        for theme, count in theme_stats:
            logger.info(f"  {theme}: {count} connections")
        
        conn.close()
        return final_count
        
    except Exception as e:
        logger.error(f"Error populating connections: {e}")
        return 0

if __name__ == "__main__":
    print("🔗 Populating set-minifig connections...")
    count = populate_connections()
    print(f"✅ Created {count} connections!")
