"""
Admin Routes - Dashboard, User Management, Book Management, Reports
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import csv
import io

from models import db, User, Book, Borrowing, Reservation, Review, Category, Department, Notification, ActivityLog, Setting
from email_service import send_email

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
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    # Get statistics
    stats = {
        'total_books': Book.query.count(),
        'total_users': User.query.count(),
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'overdue_books': Borrowing.query.filter(
            Borrowing.status == 'borrowed',
            Borrowing.due_date < datetime.utcnow()
        ).count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'total_fines': db.session.query(func.sum(Borrowing.fine_amount)).scalar() or 0,
    }
    
    # Recent activities
    recent_borrowings = Borrowing.query.order_by(Borrowing.borrow_date.desc()).limit(10).all()
    
    # Top borrowed books
    top_books = db.session.query(
        Book, func.count(Borrowing.id).label('borrow_count')
    ).join(Borrowing).group_by(Book.id)\
        .order_by(desc('borrow_count')).limit(5).all()
    
    # Recent user registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          stats=stats,
                          recent_borrowings=recent_borrowings,
                          top_books=top_books,
                          recent_users=recent_users,
                          datetime=datetime)


# ==================== BOOK MANAGEMENT ====================

@admin_bp.route('/books')
@admin_required
def books():
    """Manage books"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Book.query
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term)
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    books = query.order_by(Book.title).paginate(page=page, per_page=20)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('admin/books/index.html',
                          books=books,
                          categories=categories,
                          search=search,
                          current_category=category)


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    """Add a new book"""
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', type=int)
        category = request.form.get('category', '')
        department = request.form.get('department', '')
        total_copies = request.form.get('total_copies', 1, type=int)
        shelf_location = request.form.get('shelf_location', '').strip()
        description = request.form.get('description', '').strip()
        language = request.form.get('language', 'English')
        pages = request.form.get('pages', type=int)
        
        # Check if ISBN exists
        if Book.query.filter_by(isbn=isbn).first():
            flash('A book with this ISBN already exists.', 'danger')
            return render_template('admin/books/add.html')
        
        book = Book(
            isbn=isbn,
            title=title,
            author=author,
            publisher=publisher,
            publication_year=publication_year,
            category=category,
            department=department,
            total_copies=total_copies,
            available_copies=total_copies,
            shelf_location=shelf_location,
            description=description,
            language=language,
            pages=pages
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    categories = Category.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('admin/books/add.html',
                          categories=categories,
                          departments=departments)


@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    """Edit a book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.publisher = request.form.get('publisher', '').strip()
        book.publication_year = request.form.get('publication_year', type=int)
        book.category = request.form.get('category', '')
        book.department = request.form.get('department', '')
        
        new_total = request.form.get('total_copies', 1, type=int)
        diff = new_total - book.total_copies
        book.total_copies = new_total
        book.available_copies = max(0, book.available_copies + diff)
        
        book.shelf_location = request.form.get('shelf_location', '').strip()
        book.description = request.form.get('description', '').strip()
        book.language = request.form.get('language', 'English')
        book.pages = request.form.get('pages', type=int)
        book.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    categories = Category.query.filter_by(is_active=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('admin/books/edit.html',
                          book=book,
                          categories=categories,
                          departments=departments)


@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get_or_404(book_id)
    
    # Check for active borrowings
    active = Borrowing.query.filter_by(book_id=book_id, status='borrowed').first()
    if active:
        flash('Cannot delete book with active borrowings.', 'danger')
        return redirect(url_for('admin.books'))
    
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully.', 'success')
    return redirect(url_for('admin.books'))


# ==================== USER MANAGEMENT ====================

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    query = User.query
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                User.user_id.ilike(search_term),
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    if role:
        query = query.filter_by(role=role)
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/users/index.html',
                          users=users,
                          search=search,
                          current_role=role)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    
    borrowings = Borrowing.query.filter_by(user_id=user.id)\
        .order_by(Borrowing.borrow_date.desc()).limit(10).all()
    
    # Calculate user statistics
    user_stats = {
        'total_borrowed': Borrowing.query.filter_by(user_id=user.id).count(),
        'active_borrowed': Borrowing.query.filter_by(user_id=user.id, status='borrowed').count(),
        'active_reservations': Reservation.query.filter_by(user_id=user.id, status='pending').count(),
        'total_fines': db.session.query(func.sum(Borrowing.fine_amount)).filter_by(user_id=user.id).scalar() or 0,
        'reviews_count': Review.query.filter_by(user_id=user.id).count(),
    }
    
    return render_template('admin/users/detail.html',
                          user=user,
                          borrowings=borrowings,
                          user_stats=user_stats)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activate/deactivate user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.user_id} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    """Change user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'student')
    
    if user.id == current_user.id:
        flash('Cannot change your own role.', 'danger')
        return redirect(url_for('admin.users'))
    
    if new_role in ['student', 'faculty', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'User role changed to {new_role}.', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user account"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete your own account.'}), 400
    
    if user.role == 'admin':
        return jsonify({'success': False, 'message': 'Cannot delete admin accounts.'}), 400
    
    # Check for active borrowings
    active_borrowings = Borrowing.query.filter_by(
        user_id=user.id,
        status='borrowed'
    ).count()
    
    if active_borrowings > 0:
        return jsonify({
            'success': False, 
            'message': f'User has {active_borrowings} active borrowing(s). Please return books first.'
        }), 400
    
    try:
        # Delete related records
        Notification.query.filter_by(user_id=user.id).delete()
        ActivityLog.query.filter_by(user_id=user.id).delete()
        Review.query.filter_by(user_id=user.id).delete()
        Reservation.query.filter_by(user_id=user.id).delete()
        Borrowing.query.filter_by(user_id=user.id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User {user.user_id} deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(user_id):
    """Suspend user account"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot suspend your own account.'}), 400
    
    if user.role == 'admin':
        return jsonify({'success': False, 'message': 'Cannot suspend admin accounts.'}), 400
    
    user.is_active = False
    db.session.commit()
    
    # Send email notification to user
    try:
        subject = "Account Suspended - Digital Learning Library"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc3545;">Account Suspended</h2>
            <p>Dear {user.full_name},</p>
            <p>Your account at Digital Learning Library has been suspended by the administration.</p>
            <div style="background: #fff3cd; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 5px 0;"><strong>User ID:</strong> {user.user_id}</p>
                <p style="margin: 5px 0;"><strong>Email:</strong> {user.email}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #dc3545;">Suspended</span></p>
            </div>
            <p><strong>What this means:</strong></p>
            <ul>
                <li>You cannot log in to your account</li>
                <li>You cannot borrow or reserve books</li>
                <li>All active borrowings remain valid until their due date</li>
            </ul>
            <p>If you believe this is an error or have questions, please contact the library administration immediately.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">Digital Learning Library<br>3-4, Police Station Road<br>+91 9392513416</p>
        </body>
        </html>
        """
        text_body = f"Account Suspended\n\nYour account has been suspended. Please contact library administration.\nDigital Learning Library\n3-4, Police Station Road\n+91 9392513416"
        send_email(subject, user.email, text_body, html_body)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return jsonify({'success': True, 'message': f'User {user.user_id} suspended successfully.'})


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate user account"""
    user = User.query.get_or_404(user_id)
    
    user.is_active = True
    db.session.commit()
    
    # Send email notification to user
    try:
        subject = "Account Activated - Welcome Back!"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #28a745;">Account Activated!</h2>
            <p>Dear {user.full_name},</p>
            <p>Great news! Your account at Digital Learning Library has been activated.</p>
            <div style="background: #d4edda; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #28a745;">
                <p style="margin: 5px 0;"><strong>User ID:</strong> {user.user_id}</p>
                <p style="margin: 5px 0;"><strong>Email:</strong> {user.email}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #28a745;">Active</span></p>
            </div>
            <p><strong>You can now:</strong></p>
            <ul>
                <li>Log in to your account</li>
                <li>Browse and borrow books</li>
                <li>Make reservations</li>
                <li>Access all library services</li>
            </ul>
            <p>Welcome back to Digital Learning Library! We're happy to have you.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">Digital Learning Library<br>3-4, Police Station Road<br>+91 9392513416</p>
        </body>
        </html>
        """
        text_body = f"Account Activated!\n\nYour account has been activated. You can now log in and access all library services.\nDigital Learning Library\n3-4, Police Station Road\n+91 9392513416"
        send_email(subject, user.email, text_body, html_body)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return jsonify({'success': True, 'message': f'User {user.user_id} activated successfully.'})


# ==================== BORROWINGS MANAGEMENT ====================

@admin_bp.route('/borrowings')
@admin_required
def borrowings():
    """Manage borrowings"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    overdue = request.args.get('overdue', '')
    
    query = Borrowing.query
    
    if status:
        query = query.filter_by(status=status)
    
    if overdue == 'yes':
        query = query.filter(
            Borrowing.status == 'borrowed',
            Borrowing.due_date < datetime.utcnow()
        )
    
    borrowings = query.order_by(Borrowing.borrow_date.desc())\
        .paginate(page=page, per_page=20)
    
    # Calculate statistics for the borrowings page
    stats = {
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'due_today': Borrowing.query.filter(
            Borrowing.status == 'borrowed',
            func.date(Borrowing.due_date) == datetime.utcnow().date()
        ).count(),
        'overdue': Borrowing.query.filter(
            Borrowing.status == 'borrowed',
            Borrowing.due_date < datetime.utcnow()
        ).count(),
        'returned_today': Borrowing.query.filter(
            Borrowing.status == 'returned',
            func.date(Borrowing.return_date) == datetime.utcnow().date()
        ).count(),
    }
    
    return render_template('admin/borrowings/index.html',
                          borrowings=borrowings,
                          stats=stats,
                          current_status=status,
                          overdue=overdue)


@admin_bp.route('/borrowings/<int:borrowing_id>/mark-returned', methods=['POST'])
@admin_required
def mark_returned(borrowing_id):
    """Mark a book as returned"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    if borrowing.status != 'borrowed':
        return jsonify({'success': False, 'message': 'This borrowing is not active.'}), 400
    
    # Calculate fine
    fine = borrowing.calculate_fine()
    
    borrowing.return_date = datetime.utcnow()
    borrowing.fine_amount = fine
    borrowing.status = 'returned'
    
    # Update book availability
    borrowing.book.available_copies += 1
    
    db.session.commit()
    
    # Create notification with action URL for the user
    notification = Notification(
        user_id=borrowing.user_id,
        title=f'Book Returned: {borrowing.book.title}',
        message=f'Your book "{borrowing.book.title}" has been returned. Fine: ₹{fine}' if fine > 0 else f'Your book "{borrowing.book.title}" has been returned successfully.',
        notification_type='return',
        related_id=borrowing.id,
        action_url=url_for('user.dashboard')
    )
    db.session.add(notification)
    db.session.commit()
    
    # Generate verification code
    from email_service import create_transaction_verification
    verification_code = create_transaction_verification(borrowing.user_id, borrowing.id, 'return')
    
    # Send email notification to user
    try:
        subject = f"Book Returned: {borrowing.book.title}"
        fine_color = '#dc3545' if fine > 0 else '#28a745'
        fine_msg = f'<p style="color: #dc3545;"><strong>Note:</strong> Please pay the fine amount of ₹{fine} at the library.</p>' if fine > 0 else '<p style="color: #28a745;">No fine applicable. Thank you for returning on time!</p>'
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">Book Returned Successfully!</h2>
            <p>Dear {borrowing.user.full_name},</p>
            <p>Your book has been returned:</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">{borrowing.book.title}</h3>
                <p style="margin: 5px 0;"><strong>Author:</strong> {borrowing.book.author}</p>
                <p style="margin: 5px 0;"><strong>Borrowed Date:</strong> {borrowing.borrow_date.strftime('%B %d, %Y')}</p>
                <p style="margin: 5px 0;"><strong>Return Date:</strong> {borrowing.return_date.strftime('%B %d, %Y')}</p>
                <p style="margin: 5px 0;"><strong>Fine Amount:</strong> <span style="color: {fine_color}; font-weight: bold;">₹{fine}</span></p>
            </div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <p style="color: white; margin: 5px 0; font-size: 14px;">Transaction Verification Code</p>
                <h1 style="color: white; margin: 10px 0; letter-spacing: 5px; font-size: 32px;">{verification_code}</h1>
                <p style="color: white; margin: 5px 0; font-size: 12px;">Valid for 24 hours</p>
            </div>
            {fine_msg}
            <p>Keep this verification code for your records.</p>
            <p>Thank you for using Digital Learning Library!</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">Digital Learning Library<br>3-4, Police Station Road<br>+91 9392513416</p>
        </body>
        </html>
        """
        text_body = f"Book Returned: {borrowing.book.title}\n\nFine: ₹{fine}\n\nVerification Code: {verification_code}\n\nThank you!"
        send_email(subject, borrowing.user.email, text_body, html_body)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return jsonify({'success': True, 'message': f'Book returned. Fine: ₹{fine}'})


@admin_bp.route('/borrowings/<int:borrowing_id>/return', methods=['POST'])
@admin_required
def return_borrowing(borrowing_id):
    """Alternative route for marking returned"""
    return mark_returned(borrowing_id)


@admin_bp.route('/borrowings/<int:borrowing_id>/renew', methods=['POST'])
@admin_required
def renew_borrowing(borrowing_id):
    """Renew a borrowing for additional days"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    if borrowing.status != 'borrowed':
        return jsonify({'success': False, 'message': 'This borrowing is not active.'}), 400
    
    # Check if overdue
    if borrowing.is_overdue():
        return jsonify({'success': False, 'message': 'Cannot renew overdue borrowings. Please return and clear fines first.'}), 400
    
    # Extend due date by 14 days
    borrowing.due_date = borrowing.due_date + timedelta(days=14)
    db.session.commit()
    
    # Generate verification code
    from email_service import create_transaction_verification
    verification_code = create_transaction_verification(borrowing.user_id, borrowing.id, 'renew')
    
    # Send email notification to user
    try:
        subject = f"Book Renewed by Admin: {borrowing.book.title}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">Book Renewed by Library Admin!</h2>
            <p>Dear {borrowing.user.full_name},</p>
            <p>Your borrowing has been renewed by the library administrator:</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">{borrowing.book.title}</h3>
                <p style="margin: 5px 0;"><strong>Author:</strong> {borrowing.book.author}</p>
                <p style="margin: 5px 0;"><strong>New Due Date:</strong> <span style="color: #28a745; font-weight: bold;">{borrowing.due_date.strftime('%B %d, %Y')}</span></p>
            </div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <p style="color: white; margin: 5px 0; font-size: 14px;">Transaction Verification Code</p>
                <h1 style="color: white; margin: 10px 0; letter-spacing: 5px; font-size: 32px;">{verification_code}</h1>
                <p style="color: white; margin: 5px 0; font-size: 12px;">Valid for 24 hours</p>
            </div>
            <p>Please return the book by the new due date to avoid late fees.</p>
            <p>Keep this verification code for your records.</p>
            <p>Thank you for using Digital Learning Library!</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">Digital Learning Library<br>3-4, Police Station Road<br>+91 9392513416</p>
        </body>
        </html>
        """
        text_body = f"Book Renewed: {borrowing.book.title}\n\nNew Due Date: {borrowing.due_date.strftime('%B %d, %Y')}\n\nVerification Code: {verification_code}"
        send_email(subject, borrowing.user.email, text_body, html_body)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return jsonify({'success': True, 'message': f'Borrowing renewed until {borrowing.due_date.strftime("%Y-%m-%d")}'})


@admin_bp.route('/borrowings/<int:borrowing_id>/cancel', methods=['POST'])
@admin_required
def cancel_borrowing(borrowing_id):
    """Cancel a borrowing"""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    
    if borrowing.status == 'returned':
        return jsonify({'success': False, 'message': 'This borrowing is already returned.'}), 400
    
    borrowing.status = 'cancelled'
    borrowing.book.available_copies += 1
    
    db.session.commit()
    
    # Send email notification to user
    try:
        subject = f"Borrowing Cancelled: {borrowing.book.title}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc3545;">Borrowing Cancelled</h2>
            <p>Dear {borrowing.user.full_name},</p>
            <p>Your borrowing has been cancelled by the library administrator:</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">{borrowing.book.title}</h3>
                <p style="margin: 5px 0;"><strong>Author:</strong> {borrowing.book.author}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #dc3545;">Cancelled</span></p>
            </div>
            <p>If you have any questions, please contact the library administration.</p>
            <p>Thank you for using Digital Learning Library!</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">Digital Learning Library<br>3-4, Police Station Road<br>+91 9392513416</p>
        </body>
        </html>
        """
        text_body = f"Borrowing Cancelled: {borrowing.book.title}\n\nPlease contact library for details."
        send_email(subject, borrowing.user.email, text_body, html_body)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return jsonify({'success': True, 'message': 'Borrowing cancelled successfully.'})


# ==================== CATEGORIES & DEPARTMENTS ====================

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    """Manage categories"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '').strip()
        
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'warning')
        else:
            category = Category(name=name, description=description, icon=icon)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/departments', methods=['GET', 'POST'])
@admin_required
def departments():
    """Manage departments"""
    if request.method == 'POST':
        code = request.form.get('code', '').upper().strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if Department.query.filter_by(code=code).first():
            flash('Department code already exists.', 'warning')
        else:
            dept = Department(code=code, name=name, description=description)
            db.session.add(dept)
            db.session.commit()
            flash('Department added successfully!', 'success')
    
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)


# ==================== SETTINGS ====================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """System settings"""
    if request.method == 'POST':
        for key in request.form:
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                Setting.set(setting_key, request.form.get(key))
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    # Convert settings list to dictionary for template
    settings_list = Setting.query.all()
    settings_dict = {}
    for setting in settings_list:
        settings_dict[setting.key] = setting.value
    
    return render_template('admin/settings.html', settings=settings_dict)


# ==================== REPORTS ====================

@admin_bp.route('/reports')
@admin_required
def reports():
    """Generate reports"""
    return render_template('admin/reports.html')


@admin_bp.route('/reports/export/<report_type>')
@admin_required
def export_report(report_type):
    """Export report as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'books':
        writer.writerow(['ISBN', 'Title', 'Author', 'Category', 'Total', 'Available'])
        books = Book.query.all()
        for book in books:
            writer.writerow([book.isbn, book.title, book.author,
                           book.category, book.total_copies, book.available_copies])
    
    elif report_type == 'borrowings':
        writer.writerow(['User', 'Book', 'Borrow Date', 'Due Date', 'Status', 'Fine'])
        borrowings = Borrowing.query.all()
        for b in borrowings:
            writer.writerow([b.user.user_id, b.book.title,
                           b.borrow_date.strftime('%Y-%m-%d'),
                           b.due_date.strftime('%Y-%m-%d'),
                           b.status, b.fine_amount])
    
    elif report_type == 'users':
        writer.writerow(['User ID', 'Name', 'Email', 'Role', 'Department', 'Status'])
        users = User.query.all()
        for user in users:
            writer.writerow([user.user_id, user.full_name, user.email,
                           user.role, user.department, 'Active' if user.is_active else 'Inactive'])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={report_type}_report.csv'
    }


# ==================== ACTIVITY LOG ====================

@admin_bp.route('/activity-log')
@admin_required
def activity_log():
    """View activity log"""
    page = request.args.get('page', 1, type=int)
    
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc())\
        .paginate(page=page, per_page=50)
    
    return render_template('admin/activity_log.html', logs=logs)


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Advanced analytics dashboard"""
    from datetime import date
    
    # Calculate statistics
    stats = {
        'total_books': Book.query.count(),
        'total_users': User.query.filter(User.role != 'admin').count(),
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'total_revenue': db.session.query(func.sum(Borrowing.fine_amount)).scalar() or 0,
        'books_added_this_month': Book.query.filter(
            func.extract('month', Book.created_at) == datetime.utcnow().month
        ).count(),
        'new_users_this_week': User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count(),
        'due_this_week': Borrowing.query.filter(
            Borrowing.status == 'borrowed',
            Borrowing.due_date <= datetime.utcnow() + timedelta(days=7)
        ).count(),
        'revenue_this_month': db.session.query(func.sum(Borrowing.fine_amount)).filter(
            func.extract('month', Borrowing.updated_at) == datetime.utcnow().month
        ).scalar() or 0,
    }
    
    # Borrowing data for last 30 days
    borrowing_labels = []
    borrowing_data = []
    return_data = []
    
    for i in range(30):
        date = (datetime.utcnow() - timedelta(days=29-i)).date()
        borrowing_labels.append(date.strftime('%b %d'))
        
        borrows = Borrowing.query.filter(
            func.date(Borrowing.borrow_date) == date
        ).count()
        borrowing_data.append(borrows)
        
        returns = Borrowing.query.filter(
            func.date(Borrowing.return_date) == date,
            Borrowing.status == 'returned'
        ).count()
        return_data.append(returns)
    
    # Category distribution
    category_labels = []
    category_data = []
    
    # Since category is a string field, we'll group by the string value
    category_stats = db.session.query(
        Book.category, func.count(Book.id).label('count')
    ).filter(Book.is_active == True).group_by(Book.category).all()
    
    for cat_name, count in category_stats:
        if cat_name:  # Only include non-null categories
            category_labels.append(cat_name)
            category_data.append(count)
    
    # Registration trends
    registration_labels = []
    registration_data = []
    
    for i in range(12):
        month_date = datetime.utcnow() - timedelta(days=i*30)
        registration_labels.insert(0, month_date.strftime('%b'))
        
        count = User.query.filter(
            func.extract('month', User.created_at) == month_date.month,
            func.extract('year', User.created_at) == month_date.year
        ).count()
        registration_data.insert(0, count)
    
    # Department stats
    department_labels = []
    department_users = []
    department_borrowings = []
    
    departments = Department.query.filter_by(is_active=True).all()
    for dept in departments:
        department_labels.append(dept.name)
        
        user_count = User.query.filter_by(department_id=dept.id).count()
        department_users.append(user_count)
        
        borrow_count = db.session.query(func.count(Borrowing.id)).join(User).filter(
            User.department_id == dept.id
        ).scalar() or 0
        department_borrowings.append(borrow_count)
    
    # Popular books
    popular_books = db.session.query(
        Book, func.count(Borrowing.id).label('borrow_count')
    ).join(Borrowing).group_by(Book.id)\
        .order_by(desc('borrow_count')).limit(10).all()
    
    # Add average rating to popular books
    for book, count in popular_books:
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(book_id=book.id).scalar() or 0
        book.avg_rating = round(avg_rating, 1)
        book.borrow_count = count
    
    # Recent activities
    recent_activities = []
    recent_borrows = Borrowing.query.order_by(Borrowing.borrow_date.desc()).limit(15).all()
    
    for borrowing in recent_borrows:
        activity = {
            'action': f"{borrowing.user.full_name} borrowed a book",
            'details': f"{borrowing.book.title} - Due: {borrowing.due_date.strftime('%b %d, %Y')}",
            'timestamp': borrowing.borrow_date.strftime('%b %d, %I:%M %p')
        }
        recent_activities.append(activity)
    
    # Subscription stats
    from models import Subscription
    subscription_stats = {
        'basic': Subscription.query.filter_by(plan_id=1, is_active=True).count(),
        'premium': Subscription.query.filter_by(plan_id=2, is_active=True).count(),
        'vip': Subscription.query.filter_by(plan_id=3, is_active=True).count(),
        'monthly_revenue': db.session.query(func.sum(Subscription.amount)).filter(
            Subscription.is_active == True
        ).scalar() or 0
    }
    
    import json
    return render_template('admin/analytics.html',
                          stats=stats,
                          borrowing_labels=json.dumps(borrowing_labels),
                          borrowing_data=json.dumps(borrowing_data),
                          return_data=json.dumps(return_data),
                          category_labels=json.dumps(category_labels),
                          category_data=json.dumps(category_data),
                          registration_labels=json.dumps(registration_labels),
                          registration_data=json.dumps(registration_data),
                          department_labels=json.dumps(department_labels),
                          department_users=json.dumps(department_users),
                          department_borrowings=json.dumps(department_borrowings),
                          popular_books=[(b, c) for b, c in popular_books],
                          recent_activities=recent_activities,
                          subscription_stats=subscription_stats,
                          datetime=datetime)

