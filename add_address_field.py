"""
Migration script to add address field to users table
Run this once to update the database schema
"""

import sqlite3

def add_address_field():
    """Add address column to users table"""
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'address' not in columns:
            # Add the address column
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
            conn.commit()
            print("✅ Successfully added 'address' column to users table")
        else:
            print("ℹ️  'address' column already exists in users table")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Adding address field to users table...")
    add_address_field()
    print("Migration complete!")
