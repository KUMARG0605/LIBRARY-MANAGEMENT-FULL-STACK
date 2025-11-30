from app_new import create_app
from models import Book

app = create_app()

with app.app_context():
    isbn = '978-3-16-148410-1000'
    book = Book.query.filter_by(isbn=isbn).first()
    
    if book:
        print(f"✓ Book found: {book.title}")
        print(f"  ID: {book.id}")
        print(f"  ISBN: {book.isbn}")
        print(f"  Author: {book.author}")
    else:
        print(f"✗ No book found with ISBN: {isbn}")
        print("\nSearching similar ISBNs...")
        similar = Book.query.filter(Book.isbn.like('%978-3-16-148410%')).all()
        if similar:
            for b in similar:
                print(f"  - {b.isbn}: {b.title} (ID: {b.id})")
        else:
            print("  No similar ISBNs found")
