"""
Add related_id and action_url columns to notifications table
"""

import sqlite3

# Connect to database
conn = sqlite3.connect('instance/library_dev.db')
cursor = conn.cursor()

try:
    # Add related_id column
    cursor.execute("ALTER TABLE notifications ADD COLUMN related_id INTEGER")
    print("✅ Added 'related_id' column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'related_id' already exists")
    else:
        print(f"❌ Error adding 'related_id': {e}")

try:
    # Add action_url column
    cursor.execute("ALTER TABLE notifications ADD COLUMN action_url VARCHAR(255)")
    print("✅ Added 'action_url' column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'action_url' already exists")
    else:
        print(f"❌ Error adding 'action_url': {e}")

# Commit changes
conn.commit()
conn.close()

print("\n✅ Database migration completed successfully!")
print("\nNotifications now support:")
print("  - Action URLs for direct navigation")
print("  - Related entity IDs (book_id, borrowing_id)")
print("  - Enhanced notification features")
