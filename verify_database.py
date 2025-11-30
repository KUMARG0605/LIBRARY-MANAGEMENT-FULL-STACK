"""
Quick script to verify database contents
"""
from app_new import create_app
from models import db, Book, Category, Department

app = create_app()

with app.app_context():
    print("📊 Database Statistics:")
    print(f"Total Books: {Book.query.count()}")
    print(f"Available Books: {Book.query.filter(Book.available_copies > 0).count()}")
    print(f"Categories: {Category.query.count()}")
    print(f"Departments: {Department.query.count()}")
    
    print("\n📚 Sample Books by Department:")
    departments = Department.query.all()
    for dept in departments[:5]:
        count = Book.query.filter_by(department=dept.code).count()
        print(f"  {dept.name} ({dept.code}): {count} books")
    
    print("\n📖 Recently Added Books:")
    for book in Book.query.order_by(Book.added_date.desc()).limit(10).all():
        status = f"✅ {book.available_copies} available" if book.available_copies > 0 else "❌ Not available"
        print(f"  - {book.title[:50]}... by {book.author[:30]} ({status})")
