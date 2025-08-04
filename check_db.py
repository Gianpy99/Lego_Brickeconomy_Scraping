import sqlite3

conn = sqlite3.connect('lego_database/LegoDatabase.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", [t[0] for t in tables])

# Get column info for each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\nTable {table_name} columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
