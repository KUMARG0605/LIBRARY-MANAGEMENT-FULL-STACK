"""
Quick Database Statistics Check
Verifies the actual counts in the database
"""

from app_new import create_app
from models import db, Book, User, Borrowing, Reservation
from sqlalchemy import func

# Create app and get context
app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("📊 LIBRARY MANAGEMENT SYSTEM - DATABASE STATISTICS")
    print("="*60)
    
    # Books statistics
    total_books = Book.query.count()
    available_books = Book.query.filter(Book.available_copies > 0).count()
    
    print(f"\n📚 BOOKS:")
    print(f"   Total Books in Database: {total_books}")
    print(f"   Available Books: {available_books}")
    
    # Sample book titles
    if total_books > 0:
        sample_books = Book.query.limit(5).all()
        print(f"\n   Sample Books:")
        for book in sample_books:
            print(f"   - {book.title} by {book.author}")
    
    # Users statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    print(f"\n👥 USERS:")
    print(f"   Total Users: {total_users}")
    print(f"   Students: {total_students}")
    print(f"   Faculty: {total_faculty}")
    print(f"   Admins: {total_admins}")
    
    # Borrowings statistics
    total_borrowings = Borrowing.query.count()
    active_borrowings = Borrowing.query.filter_by(status='borrowed').count()
    returned = Borrowing.query.filter_by(status='returned').count()
    
    print(f"\n📖 BORROWINGS:")
    print(f"   Total Borrowings: {total_borrowings}")
    print(f"   Active: {active_borrowings}")
    print(f"   Returned: {returned}")
    
    # Fines
    total_fines = db.session.query(func.sum(Borrowing.fine_amount)).scalar() or 0
    
    print(f"\n💰 FINES:")
    print(f"   Total Fines: ₹{total_fines:.2f}")
    
    # Reservations
    total_reservations = Reservation.query.count()
    pending_reservations = Reservation.query.filter_by(status='pending').count()
    
    print(f"\n🔖 RESERVATIONS:")
    print(f"   Total: {total_reservations}")
    print(f"   Pending: {pending_reservations}")
    
    print("\n" + "="*60)
    print("✅ Statistics check complete!")
    print("="*60 + "\n")
