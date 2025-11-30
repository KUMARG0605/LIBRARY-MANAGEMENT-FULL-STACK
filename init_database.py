"""
Initialize database with proper schema
"""
from app_new import db
from models import User, Book, Category, Department
from werkzeug.security import generate_password_hash

# Create application context
from app_new import app

with app.app_context():
    # Drop all tables and recreate (fresh start with address field)
    print("Creating database tables...")
    db.drop_all()
    db.create_all()
    print("✅ Tables created successfully")
    
    # Create admin user
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            user_id='ADMIN001',
            email='admin@library.com',
            full_name='Admin User',
            role='admin',
            phone='1234567890',
            address='Library Headquarters'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Admin user created: ADMIN001 / admin123")
    
    # Create some sample categories
    categories_data = [
        ('Fiction', 'Fiction books and novels'),
        ('Non-Fiction', 'Non-fiction and educational books'),
        ('Science', 'Scientific literature'),
        ('Technology', 'Technology and programming books'),
        ('History', 'Historical books'),
        ('Biography', 'Biographies and memoirs'),
        ('Self-Help', 'Self-improvement books'),
        ('Comics', 'Comic books and graphic novels'),
        ('Horror', 'Horror and thriller books'),
        ('Romance', 'Romance novels'),
        ('Mystery', 'Mystery and detective novels')
    ]
    
    for name, desc in categories_data:
        if not Category.query.filter_by(name=name).first():
            cat = Category(name=name, description=desc, is_active=True)
            db.session.add(cat)
    
    print("✅ Categories created")
    
    # Create some sample departments
    departments_data = [
        ('Computer Science', 'CSE'),
        ('Mechanical Engineering', 'MECH'),
        ('Electrical Engineering', 'EEE'),
        ('Civil Engineering', 'CIVIL'),
        ('Electronics Engineering', 'ECE'),
        ('Chemical Engineering', 'CHEM'),
        ('Mathematics', 'MATH'),
        ('Physics', 'PHY'),
        ('Chemistry', 'CHE'),
        ('General', 'GEN')
    ]
    
    for name, code in departments_data:
        if not Department.query.filter_by(code=code).first():
            dept = Department(name=name, code=code, is_active=True)
            db.session.add(dept)
    
    print("✅ Departments created")
    
    # Create sample books
    books_data = [
        {
            'isbn': '9780262033848',
            'title': 'Introduction to Algorithms',
            'author': 'Thomas H. Cormen',
            'publisher': 'MIT Press',
            'category': 'Technology',
            'department': 'Computer Science',
            'language': 'English',
            'publication_year': 2009,
            'total_copies': 5,
            'price': 3500.00,
            'description': 'Comprehensive introduction to algorithms and data structures'
        },
        {
            'isbn': '9780132350884',
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'publisher': 'Prentice Hall',
            'category': 'Technology',
            'department': 'Computer Science',
            'language': 'English',
            'publication_year': 2008,
            'total_copies': 3,
            'price': 2500.00,
            'description': 'A Handbook of Agile Software Craftsmanship'
        },
        {
            'isbn': '9780134685991',
            'title': 'Effective Java',
            'author': 'Joshua Bloch',
            'publisher': 'Addison-Wesley',
            'category': 'Technology',
            'department': 'Computer Science',
            'language': 'English',
            'publication_year': 2018,
            'total_copies': 4,
            'price': 3000.00,
            'description': 'Best practices for the Java platform'
        }
    ]
    
    for book_data in books_data:
        if not Book.query.filter_by(isbn=book_data['isbn']).first():
            book = Book(**book_data)
            db.session.add(book)
    
    print("✅ Sample books created")
    
    db.session.commit()
    print("\n" + "="*60)
    print("DATABASE INITIALIZATION COMPLETE")
    print("="*60)
    print("Admin Credentials:")
    print("  User ID: ADMIN001")
    print("  Password: admin123")
    print("="*60)
