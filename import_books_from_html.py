"""
Script to import books from HTML files into the database
"""
import re
from bs4 import BeautifulSoup
from app_new import create_app
from models import db, Book, Category, Department
import os

# Department and category mapping
DEPARTMENT_MAPPING = {
    'cs_book details.html': {'dept': 'CSE', 'dept_name': 'Computer Science Engineering', 'category': 'Computer Science'},
    'ece_book details.html': {'dept': 'ECE', 'dept_name': 'Electronics and Communication Engineering', 'category': 'Engineering'},
    'eee_book details.html': {'dept': 'EEE', 'dept_name': 'Electrical and Electronics Engineering', 'category': 'Engineering'},
    'mech_book details.html': {'dept': 'MECH', 'dept_name': 'Mechanical Engineering', 'category': 'Engineering'},
    'ce_books details.html': {'dept': 'CE', 'dept_name': 'Civil Engineering', 'category': 'Engineering'},
    'chem_books details.html': {'dept': 'CHEM', 'dept_name': 'Chemical Engineering', 'category': 'Engineering'},
    'mme_books details.html': {'dept': 'MME', 'dept_name': 'Metallurgical and Materials Engineering', 'category': 'Engineering'},
    'fiction_books details.html': {'dept': None, 'dept_name': None, 'category': 'Fiction'},
    'non-fiction_books details.html': {'dept': None, 'dept_name': None, 'category': 'Non-Fiction'},
    'horror_books details.html': {'dept': None, 'dept_name': None, 'category': 'Horror'},
    'comic_books details.html': {'dept': None, 'dept_name': None, 'category': 'Comics'},
}

def extract_books_from_html(file_path, dept_code, category_name):
    """Extract book data from HTML file"""
    books = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Find all book rows in the table
        table = soup.find('table', class_='book-table')
        if not table:
            print(f"No book table found in {file_path}")
            return books
            
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                title = cols[0].get_text(strip=True)
                author = cols[1].get_text(strip=True)
                
                # Generate ISBN (simple unique identifier)
                isbn = f"978-0-{hash(title) % 10000:04d}-{hash(author) % 10000:04d}-{len(books)}"
                
                books.append({
                    'title': title,
                    'author': author,
                    'isbn': isbn,
                    'department': dept_code,
                    'category': category_name,
                    'total_copies': 3,
                    'available_copies': 3,
                    'publisher': 'Various',
                    'description': f'A comprehensive book on {title}',
                    'is_active': True
                })
                
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        
    return books

def main():
    """Main function to import all books"""
    app = create_app('development')
    
    with app.app_context():
        print("Starting book import...")
        
        # Process each HTML file
        base_path = os.path.dirname(os.path.abspath(__file__))
        total_imported = 0
        
        for filename, mapping in DEPARTMENT_MAPPING.items():
            file_path = os.path.join(base_path, filename)
            
            if not os.path.exists(file_path):
                print(f"File not found: {filename}")
                continue
                
            print(f"\nProcessing {filename}...")
            
            # Extract books from HTML
            books = extract_books_from_html(
                file_path,
                mapping['dept'],
                mapping['category']
            )
            
            # Ensure category exists
            category = Category.query.filter_by(name=mapping['category']).first()
            if not category:
                category = Category(
                    name=mapping['category'],
                    description=f'{mapping["category"]} books',
                    is_active=True
                )
                db.session.add(category)
                db.session.commit()
                print(f"Created category: {mapping['category']}")
            
            # Ensure department exists (if applicable)
            if mapping['dept']:
                dept = Department.query.filter_by(code=mapping['dept']).first()
                if not dept:
                    dept = Department(
                        code=mapping['dept'],
                        name=mapping['dept_name'],
                        is_active=True
                    )
                    db.session.add(dept)
                    db.session.commit()
                    print(f"Created department: {mapping['dept_name']}")
            
            # Import books
            for book_data in books:
                # Check if book already exists
                existing = Book.query.filter_by(isbn=book_data['isbn']).first()
                if existing:
                    print(f"  Skipping duplicate: {book_data['title']}")
                    continue
                    
                book = Book(**book_data)
                db.session.add(book)
                total_imported += 1
                print(f"  Added: {book_data['title']} by {book_data['author']}")
            
            db.session.commit()
            print(f"Imported {len(books)} books from {filename}")
        
        print(f"\n✅ Total books imported: {total_imported}")
        print(f"📚 Total books in database: {Book.query.count()}")
        print(f"📁 Total categories: {Category.query.count()}")
        print(f"🏢 Total departments: {Department.query.count()}")

if __name__ == '__main__':
    main()
