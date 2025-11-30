"""
Initialize Database with Default Data
Run this script to create all tables and add sample data
"""

from app_new import create_app
from models import db, User, Book, Category, Department
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app('development')

with app.app_context():
    print("🗄️  Creating database tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Check if admin user exists
    admin = User.query.filter_by(user_id='ADMIN001').first()
    if not admin:
        print("\n👤 Creating default admin user...")
        admin = User(
            user_id='ADMIN001',
            full_name='System Administrator',
            email='admin@library.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        print("✅ Admin user created (ID: ADMIN001, Password: admin123)")
    
    # Add departments if they don't exist
    departments = [
        {'code': 'CSE', 'name': 'Computer Science Engineering'},
        {'code': 'ECE', 'name': 'Electronics and Communication Engineering'},
        {'code': 'EEE', 'name': 'Electrical and Electronics Engineering'},
        {'code': 'MECH', 'name': 'Mechanical Engineering'},
        {'code': 'CIVIL', 'name': 'Civil Engineering'},
        {'code': 'MME', 'name': 'Metallurgical Engineering'},
        {'code': 'CHEM', 'name': 'Chemical Engineering'},
    ]
    
    print("\n🏢 Adding departments...")
    for dept_data in departments:
        dept = Department.query.filter_by(code=dept_data['code']).first()
        if not dept:
            dept = Department(**dept_data, is_active=True)
            db.session.add(dept)
            print(f"   Added: {dept_data['name']}")
    
    # Add categories if they don't exist
    categories = [
        {'name': 'Fiction', 'description': 'Fiction books and novels'},
        {'name': 'Non-Fiction', 'description': 'Non-fiction and educational books'},
        {'name': 'Science', 'description': 'Science and technology books'},
        {'name': 'Engineering', 'description': 'Engineering textbooks'},
        {'name': 'Comics', 'description': 'Comic books and graphic novels'},
        {'name': 'Horror', 'description': 'Horror and thriller books'},
    ]
    
    print("\n📚 Adding categories...")
    for cat_data in categories:
        cat = Category.query.filter_by(name=cat_data['name']).first()
        if not cat:
            cat = Category(**cat_data, is_active=True)
            db.session.add(cat)
            print(f"   Added: {cat_data['name']}")
    
    # Add sample books
    print("\n📖 Adding sample books...")
    sample_books = [
        {
            'isbn': '978-0-13-468599-1',
            'title': 'Introduction to Algorithms',
            'author': 'Thomas H. Cormen',
            'category': 'Engineering',
            'department': 'CSE',
            'publisher': 'MIT Press',
            'publication_year': 2009,
            'total_copies': 5,
            'available_copies': 5,
            'description': 'Comprehensive textbook on algorithms'
        },
        {
            'isbn': '978-0-262-03384-8',
            'title': 'Artificial Intelligence: A Modern Approach',
            'author': 'Stuart Russell, Peter Norvig',
            'category': 'Engineering',
            'department': 'CSE',
            'publisher': 'Pearson',
            'publication_year': 2020,
            'total_copies': 3,
            'available_copies': 3,
            'description': 'Leading textbook in Artificial Intelligence'
        },
        {
            'isbn': '978-0-7432-7356-5',
            'title': '1984',
            'author': 'George Orwell',
            'category': 'Fiction',
            'publisher': 'Signet Classic',
            'publication_year': 1961,
            'total_copies': 10,
            'available_copies': 10,
            'description': 'Classic dystopian novel'
        },
    ]
    
    for book_data in sample_books:
        book = Book.query.filter_by(isbn=book_data['isbn']).first()
        if not book:
            book = Book(**book_data, is_active=True, added_date=datetime.utcnow())
            db.session.add(book)
            print(f"   Added: {book_data['title']}")
    
    # Commit all changes
    db.session.commit()
    
    print("\n" + "="*60)
    print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
    print("="*60)
    print("\n🔐 Default Login Credentials:")
    print("   User ID: ADMIN001")
    print("   Password: admin123")
    print("\n🌐 Start the application:")
    print("   python app_new.py")
    print("\n🔗 Access at: http://localhost:5000")
    print("="*60)
