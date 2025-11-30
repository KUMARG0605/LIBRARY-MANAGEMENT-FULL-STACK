from app_new import create_app
from models import Book
import os

app = create_app()

with app.app_context():
    # Get all books ordered by ID (newest first)
    all_books = Book.query.order_by(Book.id.desc()).limit(10).all()
    
    print("=" * 80)
    print("RECENTLY ADDED BOOKS (Last 10)")
    print("=" * 80)
    
    for book in all_books:
        print(f"\nID: {book.id}")
        print(f"Title: {book.title}")
        print(f"ISBN: {book.isbn}")
        print(f"Author: {book.author}")
        print(f"Category: {book.category}")
        print("-" * 80)
    
    print(f"\n\nTotal books in database: {Book.query.count()}")
