import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", [t[0] for t in tables])

# Try to add address column if users table exists
try:
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns in users table:", columns)
    
    if 'address' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
        conn.commit()
        print("✅ Added address column")
    else:
        print("ℹ️  Address column already exists")
except Exception as e:
    print(f"Error: {e}")

conn.close()
