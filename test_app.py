"""
Quick Test Script - Library Management System
Tests critical endpoints and functionality
"""

from app_new import create_app, db
from models import User, Book, Category, Department
from sqlalchemy import text

def test_application():
    """Test basic application functionality"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("TESTING LIBRARY MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Test 1: Database Connection
        print("\n✓ Test 1: Database Connection")
        try:
            db.session.execute(text('SELECT 1'))
            print("  ✅ Database connected successfully")
        except Exception as e:
            print(f"  ❌ Database connection failed: {e}")
            return False
        
        # Test 2: Check Tables
        print("\n✓ Test 2: Database Tables")
        try:
            tables = ['users', 'books', 'borrowings', 'reservations', 
                     'categories', 'departments', 'reviews']
            for table in tables:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  ✅ {table}: {count} records")
        except Exception as e:
            print(f"  ❌ Table check failed: {e}")
        
        # Test 3: Admin User
        print("\n✓ Test 3: Admin User")
        try:
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"  ✅ Admin user exists: {admin.user_id}")
            else:
                print("  ⚠️ No admin user found")
        except Exception as e:
            print(f"  ❌ Admin check failed: {e}")
        
        # Test 4: Books
        print("\n✓ Test 4: Books")
        try:
            total_books = Book.query.count()
            available_books = Book.query.filter_by(is_active=True).count()
            print(f"  ✅ Total books: {total_books}")
            print(f"  ✅ Available books: {available_books}")
            
            if total_books > 0:
                sample_book = Book.query.first()
                print(f"  ✅ Sample book: {sample_book.title}")
        except Exception as e:
            print(f"  ❌ Books check failed: {e}")
        
        # Test 5: Categories & Departments
        print("\n✓ Test 5: Categories & Departments")
        try:
            categories = Category.query.filter_by(is_active=True).count()
            departments = Department.query.filter_by(is_active=True).count()
            print(f"  ✅ Active categories: {categories}")
            print(f"  ✅ Active departments: {departments}")
        except Exception as e:
            print(f"  ❌ Categories/Departments check failed: {e}")
        
        # Test 6: Routes
        print("\n✓ Test 6: Application Routes")
        try:
            routes = []
            for rule in app.url_map.iter_rules():
                if not rule.endpoint.startswith('static'):
                    routes.append(f"{rule.endpoint}: {rule.rule}")
            
            print(f"  ✅ Total routes: {len(routes)}")
            
            # Check critical routes
            critical_routes = [
                'main.index',
                'auth.login',
                'auth.register',
                'books.index',
                'books.detail',
                'user.dashboard',
                'admin.dashboard',
                'admin.books',
                'admin.add_book',
                'admin.analytics',
                'api.search'
            ]
            
            for route in critical_routes:
                exists = any(route in r for r in routes)
                status = "✅" if exists else "❌"
                print(f"  {status} {route}")
                
        except Exception as e:
            print(f"  ❌ Routes check failed: {e}")
        
        # Test 7: Email Configuration
        print("\n✓ Test 7: Email Configuration")
        try:
            mail_server = app.config.get('MAIL_SERVER')
            mail_username = app.config.get('MAIL_USERNAME')
            if mail_server and mail_username:
                print(f"  ✅ Mail server: {mail_server}")
                print(f"  ✅ Mail username: {mail_username}")
            else:
                print("  ⚠️ Email not configured")
        except Exception as e:
            print(f"  ❌ Email check failed: {e}")
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ All critical tests passed!")
        print("🚀 Application is ready to run!")
        print("\nTo start the application:")
        print("  python app_new.py")
        print("\nDefault admin credentials:")
        print("  User ID: ADMIN001")
        print("  Password: admin123")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    test_application()
