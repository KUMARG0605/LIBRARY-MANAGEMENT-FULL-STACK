from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyodbc
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database Connection
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-LK3TR\\SQLEXPRESS;'
    'DATABASE=LibraryDB;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# ==================== DATABASE SETUP ====================
def setup_database():
    tables = [
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            role VARCHAR(20) DEFAULT 'student',
            department VARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            is_active BIT DEFAULT 1
        )''',
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'books')
        CREATE TABLE books (
            id INT IDENTITY(1,1) PRIMARY KEY,
            isbn VARCHAR(20) UNIQUE NOT NULL,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(100) NOT NULL,
            publisher VARCHAR(100),
            category VARCHAR(50),
            department VARCHAR(50),
            total_copies INT DEFAULT 1,
            available_copies INT DEFAULT 1,
            shelf_location VARCHAR(20),
            description TEXT,
            cover_image VARCHAR(255),
            added_date DATETIME DEFAULT GETDATE()
        )''',
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'borrowings')
        CREATE TABLE borrowings (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            book_id INT NOT NULL,
            borrow_date DATETIME DEFAULT GETDATE(),
            due_date DATETIME,
            return_date DATETIME NULL,
            fine_amount DECIMAL(10,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'borrowed',
            FOREIGN KEY (book_id) REFERENCES books(id)
        )''',
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'reservations')
        CREATE TABLE reservations (
            id INT IDENTITY(1,1) PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            book_id INT NOT NULL,
            reservation_date DATETIME DEFAULT GETDATE(),
            status VARCHAR(20) DEFAULT 'pending',
            FOREIGN KEY (book_id) REFERENCES books(id)
        )'''
    ]
    for table in tables:
        cursor.execute(table)
    conn.commit()

setup_database()

# ==================== DECORATORS ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================
@app.route('/')
def home():
    # Get featured books
    cursor.execute('SELECT TOP 8 * FROM books WHERE available_copies > 0 ORDER BY added_date DESC')
    featured_books = cursor.fetchall()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM borrowings WHERE status = ?', ('borrowed',))
    active_borrowings = cursor.fetchone()[0]
    
    return render_template('home.html', 
                          featured_books=featured_books,
                          total_books=total_books,
                          total_users=total_users,
                          active_borrowings=active_borrowings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id'].upper()
        full_name = request.form['full_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        phone = request.form.get('phone', '')
        department = request.form.get('department', '')
        role = request.form.get('role', 'student')
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE user_id = ? OR email = ?', (user_id, email))
        if cursor.fetchone():
            flash('User ID or Email already exists!', 'danger')
            return render_template('register.html')
        
        # Insert new user
        cursor.execute('''INSERT INTO users (user_id, full_name, email, password, phone, department, role)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, full_name, email, password, phone, department, role))
        conn.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id'].upper()
        password = request.form['password']
        
        cursor.execute('SELECT * FROM users WHERE user_id = ? AND is_active = 1', (user_id,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['full_name'] = user.full_name
            session['role'] = user.role
            session['email'] = user.email
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # Get user's borrowed books
    cursor.execute('''SELECT b.*, bk.title, bk.author, bk.isbn 
                     FROM borrowings b 
                     JOIN books bk ON b.book_id = bk.id 
                     WHERE b.user_id = ? AND b.status = ?''', (user_id, 'borrowed'))
    borrowed_books = cursor.fetchall()
    
    # Get user's reservations
    cursor.execute('''SELECT r.*, bk.title, bk.author 
                     FROM reservations r 
                     JOIN books bk ON r.book_id = bk.id 
                     WHERE r.user_id = ? AND r.status = ?''', (user_id, 'pending'))
    reservations = cursor.fetchall()
    
    # Calculate fines
    total_fine = 0
    for book in borrowed_books:
        if book.due_date < datetime.now():
            days_overdue = (datetime.now() - book.due_date).days
            total_fine += days_overdue * 5  # Rs 5 per day
    
    return render_template('dashboard.html', 
                          borrowed_books=borrowed_books,
                          reservations=reservations,
                          total_fine=total_fine)

@app.route('/books')
def books():
    category = request.args.get('category', '')
    department = request.args.get('department', '')
    search = request.args.get('search', '')
    
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    if department:
        query += ' AND department = ?'
        params.append(department)
    if search:
        query += ' AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY title'
    cursor.execute(query, params)
    books = cursor.fetchall()
    
    # Get categories and departments for filters
    cursor.execute('SELECT DISTINCT category FROM books WHERE category IS NOT NULL')
    categories = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT DISTINCT department FROM books WHERE department IS NOT NULL')
    departments = [row[0] for row in cursor.fetchall()]
    
    return render_template('books.html', books=books, categories=categories, 
                          departments=departments, current_category=category,
                          current_department=department, search=search)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    if not book:
        flash('Book not found!', 'danger')
        return redirect(url_for('books'))
    return render_template('book_detail.html', book=book)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    user_id = session['user_id']
    
    # Check book availability
    cursor.execute('SELECT available_copies FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    
    if not book or book.available_copies <= 0:
        flash('Book not available!', 'danger')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Check if user already has this book
    cursor.execute('SELECT * FROM borrowings WHERE user_id = ? AND book_id = ? AND status = ?',
                  (user_id, book_id, 'borrowed'))
    if cursor.fetchone():
        flash('You already have this book!', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Check borrowing limit (max 5 books)
    cursor.execute('SELECT COUNT(*) FROM borrowings WHERE user_id = ? AND status = ?',
                  (user_id, 'borrowed'))
    if cursor.fetchone()[0] >= 5:
        flash('Borrowing limit reached! Return some books first.', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Create borrowing record
    due_date = datetime.now() + timedelta(days=14)  # 2 weeks
    cursor.execute('''INSERT INTO borrowings (user_id, book_id, due_date) VALUES (?, ?, ?)''',
                  (user_id, book_id, due_date))
    
    # Update book availability
    cursor.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = ?', (book_id,))
    conn.commit()
    
    flash('Book borrowed successfully! Due date: ' + due_date.strftime('%Y-%m-%d'), 'success')
    return redirect(url_for('dashboard'))

@app.route('/return/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    cursor.execute('SELECT * FROM borrowings WHERE id = ? AND user_id = ?',
                  (borrowing_id, session['user_id']))
    borrowing = cursor.fetchone()
    
    if not borrowing:
        flash('Invalid request!', 'danger')
        return redirect(url_for('dashboard'))
    
    # Calculate fine if overdue
    fine = 0
    if borrowing.due_date < datetime.now():
        days_overdue = (datetime.now() - borrowing.due_date).days
        fine = days_overdue * 5
    
    # Update borrowing record
    cursor.execute('''UPDATE borrowings SET return_date = GETDATE(), status = ?, fine_amount = ? 
                     WHERE id = ?''', ('returned', fine, borrowing_id))
    
    # Update book availability
    cursor.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
                  (borrowing.book_id,))
    conn.commit()
    
    if fine > 0:
        flash(f'Book returned! Fine amount: Rs {fine}', 'warning')
    else:
        flash('Book returned successfully!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book(book_id):
    user_id = session['user_id']
    
    # Check if already reserved
    cursor.execute('SELECT * FROM reservations WHERE user_id = ? AND book_id = ? AND status = ?',
                  (user_id, book_id, 'pending'))
    if cursor.fetchone():
        flash('Already reserved!', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))
    
    cursor.execute('INSERT INTO reservations (user_id, book_id) VALUES (?, ?)', (user_id, book_id))
    conn.commit()
    flash('Book reserved! You will be notified when available.', 'success')
    return redirect(url_for('dashboard'))

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
@admin_required
def admin_dashboard():
    cursor.execute('SELECT COUNT(*) FROM books')
    total_books = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM borrowings WHERE status = ?', ('borrowed',))
    active_borrowings = cursor.fetchone()[0]
    cursor.execute('SELECT SUM(fine_amount) FROM borrowings WHERE fine_amount > 0')
    total_fines = cursor.fetchone()[0] or 0
    
    # Recent activities
    cursor.execute('''SELECT TOP 10 b.*, u.full_name, bk.title 
                     FROM borrowings b 
                     JOIN users u ON b.user_id = u.user_id 
                     JOIN books bk ON b.book_id = bk.id 
                     ORDER BY b.borrow_date DESC''')
    recent_activities = cursor.fetchall()
    
    return render_template('admin/dashboard.html',
                          total_books=total_books,
                          total_users=total_users,
                          active_borrowings=active_borrowings,
                          total_fines=total_fines,
                          recent_activities=recent_activities)

@app.route('/admin/books', methods=['GET', 'POST'])
@admin_required
def admin_books():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        publisher = request.form.get('publisher', '')
        category = request.form.get('category', '')
        department = request.form.get('department', '')
        total_copies = int(request.form.get('total_copies', 1))
        shelf_location = request.form.get('shelf_location', '')
        description = request.form.get('description', '')
        
        cursor.execute('''INSERT INTO books (isbn, title, author, publisher, category, department,
                         total_copies, available_copies, shelf_location, description)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (isbn, title, author, publisher, category, department,
                       total_copies, total_copies, shelf_location, description))
        conn.commit()
        flash('Book added successfully!', 'success')
    
    cursor.execute('SELECT * FROM books ORDER BY title')
    books = cursor.fetchall()
    return render_template('admin/books.html', books=books)

@app.route('/admin/users')
@admin_required
def admin_users():
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    return render_template('admin/users.html', users=users)

@app.route('/admin/borrowings')
@admin_required
def admin_borrowings():
    cursor.execute('''SELECT b.*, u.full_name, bk.title, bk.isbn 
                     FROM borrowings b 
                     JOIN users u ON b.user_id = u.user_id 
                     JOIN books bk ON b.book_id = bk.id 
                     ORDER BY b.borrow_date DESC''')
    borrowings = cursor.fetchall()
    return render_template('admin/borrowings.html', borrowings=borrowings)

# ==================== API ROUTES ====================
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    cursor.execute('''SELECT id, title, author, isbn FROM books 
                     WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?''',
                  (f'%{query}%', f'%{query}%', f'%{query}%'))
    results = [{'id': row[0], 'title': row[1], 'author': row[2], 'isbn': row[3]} 
               for row in cursor.fetchall()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
