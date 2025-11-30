from app_new import create_app
from models import Book
import os

app = create_app()

def create_pdf_content(book):
    """Generate simple PDF content for a book"""
    return f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 300
>>
stream
BT
/F1 28 Tf
50 750 Td
({book.title[:50]}) Tj
0 -60 Td
/F1 16 Tf
(Author: {book.author}) Tj
0 -40 Td
(ISBN: {book.isbn}) Tj
0 -40 Td
(Category: {book.category or 'N/A'}) Tj
0 -40 Td
(Department: {book.department or 'N/A'}) Tj
0 -80 Td
/F1 12 Tf
(This is a sample PDF file for the Library Management System.) Tj
0 -30 Td
(Replace this with actual book content.) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
0000000623 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
682
%%EOF
"""

with app.app_context():
    # Get all books
    all_books = Book.query.all()
    pdf_dir = 'static/books/pdfs'
    
    print("=" * 80)
    print("CREATING PDF FILES FOR ALL BOOKS")
    print("=" * 80)
    
    created_count = 0
    skipped_count = 0
    
    for book in all_books:
        # Use ISBN as filename (sanitize it)
        filename = f"{book.isbn.replace('/', '-').replace(' ', '_')}.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        # Also create with book ID for backward compatibility
        id_filename = f"{book.id}.pdf"
        id_filepath = os.path.join(pdf_dir, id_filename)
        
        # Check if files already exist
        if os.path.exists(filepath) and os.path.exists(id_filepath):
            print(f"✓ Skipped (exists): {book.title[:40]} - {filename}")
            skipped_count += 1
            continue
        
        # Create PDF content
        pdf_content = create_pdf_content(book)
        
        # Write both ISBN and ID versions
        with open(filepath, 'w', encoding='latin-1') as f:
            f.write(pdf_content)
        
        with open(id_filepath, 'w', encoding='latin-1') as f:
            f.write(pdf_content)
        
        print(f"✓ Created: {book.title[:40]} - {filename}")
        created_count += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Total books: {len(all_books)}")
    print(f"PDFs created: {created_count}")
    print(f"PDFs skipped: {skipped_count}")
    print(f"\nPDFs location: {pdf_dir}")
    print("=" * 80)
    
    # List newest book
    newest = Book.query.order_by(Book.id.desc()).first()
    print(f"\nNewest book:")
    print(f"  ID: {newest.id}")
    print(f"  Title: {newest.title}")
    print(f"  ISBN: {newest.isbn}")
    print(f"  PDF files: {newest.id}.pdf and {newest.isbn}.pdf")
