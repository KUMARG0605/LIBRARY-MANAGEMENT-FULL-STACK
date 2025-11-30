"""
Admin Routes
Dashboard, User Management, Book Management, Analytics
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func

from models import db, User, Book, Borrowing, Reservation, Review, Category, Department, Setting

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    # Statistics
    stats = {
        'total_books': Book.query.filter_by(is_active=True).count(),
        'total_users': User.query.filter_by(is_active=True).count(),
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'total_fines': db.session.query(func.sum(Borrowing.fine_amount)).filter(
            Borrowing.fine_paid == False
        ).scalar() or 0
    }
    
    # Recent activities
    recent_borrowings = Borrowing.query.order_by(
        Borrowing.borrow_date.desc()
    ).limit(10).all()
    
    # Overdue books
    overdue_books = Borrowing.query.filter(
        Borrowing.status == 'borrowed',
        Borrowing.due_date < datetime.utcnow()
    ).order_by(Borrowing.due_date).limit(10).all()
    
    # Popular books
    popular_books = db.session.query(
        Book.id, Book.title, Book.author, func.count(Borrowing.id).label('borrow_count')
    ).join(Borrowing).group_by(Book.id, Book.title, Book.author).order_by(
        func.count(Borrowing.id).desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          stats=stats,
                          recent_borrowings=recent_borrowings,
                          overdue_books=overdue_books,
                          popular_books=popular_books)


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    per_page = 20
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.user_id.ilike(f'%{search}%')) |
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    if role:
        query = query.filter_by(role=role)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html',
                          users=pagination.items,
                          pagination=pagination,
                          search=search,
                          role=role)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """User detail view"""
    user = User.query.get_or_404(user_id)
    
    borrowings = Borrowing.query.filter_by(user_id=user.id).order_by(
        Borrowing.borrow_date.desc()
    ).limit(10).all()
    
    return render_template('admin/user_detail.html',
                          user=user,
                          borrowings=borrowings)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    """Activate/deactivate user"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/books')
@admin_required
def books():
    """Manage books"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    per_page = 20
    
    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) |
            (Book.author.ilike(f'%{search}%')) |
            (Book.isbn.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Book.added_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/books.html',
                          books=pagination.items,
                          pagination=pagination,
                          search=search,
                          category=category)


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    """Add new book"""
    if request.method == 'POST':
        book = Book(
            isbn=request.form['isbn'],
            title=request.form['title'],
            author=request.form['author'],
            publisher=request.form.get('publisher'),
            publication_year=request.form.get('publication_year', type=int),
            edition=request.form.get('edition'),
            category=request.form.get('category'),
            department=request.form.get('department'),
            language=request.form.get('language', 'English'),
            pages=request.form.get('pages', type=int),
            total_copies=request.form.get('total_copies', 1, type=int),
            available_copies=request.form.get('total_copies', 1, type=int),
            shelf_location=request.form.get('shelf_location'),
            description=request.form.get('description')
        )
        
        # Handle cover image upload
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                # TODO: Save file and update book.cover_image
                pass
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/add_book.html')


@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    """Edit book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.isbn = request.form['isbn']
        book.title = request.form['title']
        book.author = request.form['author']
        book.publisher = request.form.get('publisher')
        book.publication_year = request.form.get('publication_year', type=int)
        book.edition = request.form.get('edition')
        book.category = request.form.get('category')
        book.department = request.form.get('department')
        book.language = request.form.get('language', 'English')
        book.pages = request.form.get('pages', type=int)
        book.total_copies = request.form.get('total_copies', type=int)
        book.shelf_location = request.form.get('shelf_location')
        book.description = request.form.get('description')
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/edit_book.html', book=book)


@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete_book(book_id):
    """Delete/deactivate book"""
    book = Book.query.get_or_404(book_id)
    book.is_active = False
    db.session.commit()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin.books'))


@admin_bp.route('/borrowings')
@admin_required
def borrowings():
    """Manage borrowings"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    per_page = 20
    
    query = Borrowing.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Borrowing.borrow_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/borrowings.html',
                          borrowings=pagination.items,
                          pagination=pagination,
                          status=status)


@admin_bp.route('/borrowings/<int:borrowing_id>/return', methods=['POST'])
@admin_required
def process_return(borrowing_id):
    """Process book return"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    borrowing.return_date = datetime.utcnow()
    borrowing.status = 'returned'
    
    if borrowing.is_overdue():
        borrowing.fine_amount = borrowing.calculate_fine()
    
    borrowing.book.available_copies += 1
    
    db.session.commit()
    
    flash('Return processed successfully!', 'success')
    return redirect(url_for('admin.borrowings'))


@admin_bp.route('/reservations')
@admin_required
def reservations():
    """Manage reservations"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = Reservation.query.order_by(Reservation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/reservations.html',
                          reservations=pagination.items,
                          pagination=pagination)


@admin_bp.route('/categories')
@admin_required
def categories():
    """Manage categories"""
    all_categories = Category.query.all()
    return render_template('admin/categories.html', categories=all_categories)


@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    """Add category"""
    name = request.form['name']
    description = request.form.get('description')
    icon = request.form.get('icon')
    
    category = Category(name=name, description=description, icon=icon)
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully!', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/departments')
@admin_required
def departments():
    """Manage departments"""
    all_departments = Department.query.all()
    return render_template('admin/departments.html', departments=all_departments)


@admin_bp.route('/settings')
@admin_required
def settings():
    """System settings"""
    all_settings = Setting.query.all()
    return render_template('admin/settings.html', settings=all_settings)


@admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_setting():
    """Update setting"""
    key = request.form['key']
    value = request.form['value']
    
    Setting.set(key, value)
    
    flash('Setting updated successfully!', 'success')
    return redirect(url_for('admin.settings'))


@admin_bp.route('/reports')
@admin_required
def reports():
    """Generate reports"""
    # Date range
    start_date = request.args.get('start_date', (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    # Borrowing statistics
    borrowing_stats = db.session.query(
        func.date(Borrowing.borrow_date).label('date'),
        func.count(Borrowing.id).label('count')
    ).filter(
        Borrowing.borrow_date.between(start_date, end_date)
    ).group_by(func.date(Borrowing.borrow_date)).all()
    
    return render_template('admin/reports.html',
                          borrowing_stats=borrowing_stats,
                          start_date=start_date,
                          end_date=end_date)
