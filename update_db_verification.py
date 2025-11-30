"""
Update database schema to add TransactionVerification table
"""

from app_new import app, db
from models import TransactionVerification

with app.app_context():
    # Create the new table
    db.create_all()
    print("✅ Database updated successfully!")
    print("✅ TransactionVerification table created")
    print("\nVerification codes will now be sent for:")
    print("  - Book borrowing")
    print("  - Book renewal (user and admin)")
    print("  - Book return")
