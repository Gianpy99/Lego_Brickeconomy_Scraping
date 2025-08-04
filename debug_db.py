import sqlite3

# Check database content
conn = sqlite3.connect('lego_database/LegoDatabase.db')
cursor = conn.cursor()

# Check sets table
print("=== SETS TABLE ===")
cursor.execute('SELECT COUNT(*) FROM lego_sets')
sets_count = cursor.fetchone()[0]
print(f'Total sets: {sets_count}')

if sets_count > 0:
    cursor.execute('SELECT lego_code, official_name, image_path, has_image FROM lego_sets LIMIT 5')
    print('Sample sets data:')
    for row in cursor.fetchall():
        print(f'  Code: {row[0]}, Name: {row[1]}, Image: {row[2]}, Has_Image: {row[3]}')

# Check minifigs table
print("\n=== MINIFIGS TABLE ===")
cursor.execute('SELECT COUNT(*) FROM minifig')
minifigs_count = cursor.fetchone()[0]
print(f'Total minifigs: {minifigs_count}')

if minifigs_count > 0:
    cursor.execute('SELECT minifig_code, official_name, image_path, has_image FROM minifig LIMIT 5')
    print('Sample minifigs data:')
    for row in cursor.fetchall():
        print(f'  Code: {row[0]}, Name: {row[1]}, Image: {row[2]}, Has_Image: {row[3]}')

conn.close()
