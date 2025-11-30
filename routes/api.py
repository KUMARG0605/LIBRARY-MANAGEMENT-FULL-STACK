"""
API Routes - RESTful API endpoints for the library system
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import or_

from models import db, Book, Borrowing, Reservation, User, Notification

api_bp = Blueprint('api', __name__)


# ==================== BOOK APIs ====================

@api_bp.route('/books')
def get_books():
    """Get all books with filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    department = request.args.get('department', '')
    search = request.args.get('search', '')
    
    query = Book.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if department:
        query = query.filter_by(department=department)
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term)
            )
        )
    
    books = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'books': [{
            'id': book.id,
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'department': book.department,
            'available': book.available_copies > 0,
            'available_copies': book.available_copies,
            'cover_image': book.cover_image,
            'rating': book.get_average_rating()
        } for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': page
    })


@api_bp.route('/books/<int:book_id>')
def get_book(book_id):
    """Get a single book by ID"""
    book = Book.query.get_or_404(book_id)
    
    return jsonify({
        'id': book.id,
        'isbn': book.isbn,
        'title': book.title,
        'author': book.author,
        'publisher': book.publisher,
        'publication_year': book.publication_year,
        'category': book.category,
        'department': book.department,
        'language': book.language,
        'pages': book.pages,
        'total_copies': book.total_copies,
        'available_copies': book.available_copies,
        'shelf_location': book.shelf_location,
        'description': book.description,
        'cover_image': book.cover_image,
        'rating': book.get_average_rating()
    })


@api_bp.route('/search')
def search():
    """Quick search API for real-time autocomplete"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'books': [], 'authors': [], 'categories': []})
    
    search_term = f'%{query}%'
    
    # Search books
    books = Book.query.filter(
        Book.is_active == True,
        or_(
            Book.title.ilike(search_term),
            Book.author.ilike(search_term),
            Book.isbn.ilike(search_term)
        )
    ).limit(limit).all()
    
    # Get unique authors matching search
    from sqlalchemy import func, distinct
    authors_query = db.session.query(
        Book.author,
        func.count(Book.id).label('book_count')
    ).filter(
        Book.is_active == True,
        Book.author.ilike(search_term)
    ).group_by(Book.author).limit(5).all()
    
    # Get matching categories
    from models import Category
    categories = Category.query.filter(
        Category.is_active == True,
        Category.name.ilike(search_term)
    ).limit(5).all()
    
    return jsonify({
        'books': [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category.name if book.category else 'General',
            'isbn': book.isbn,
            'available_copies': book.available_copies,
            'cover_image': book.cover_image or 'default_book.png'
        } for book in books],
        'authors': [{
            'name': author,
            'book_count': count
        } for author, count in authors_query],
        'categories': [{
            'id': cat.id,
            'name': cat.name,
            'book_count': Book.query.filter_by(category_id=cat.id, is_active=True).count()
        } for cat in categories]
    })


# ==================== USER APIs ====================

@api_bp.route('/user/borrowings')
@login_required
def get_user_borrowings():
    """Get current user's borrowings"""
    status = request.args.get('status', 'borrowed')
    
    borrowings = Borrowing.query.filter_by(
        user_id=current_user.id,
        status=status
    ).all()
    
    return jsonify([{
        'id': b.id,
        'book': {
            'id': b.book.id,
            'title': b.book.title,
            'author': b.book.author
        },
        'borrow_date': b.borrow_date.isoformat(),
        'due_date': b.due_date.isoformat(),
        'is_overdue': b.is_overdue(),
        'days_overdue': b.days_overdue(),
        'fine': b.calculate_fine(),
        'can_renew': b.can_renew()
    } for b in borrowings])


@api_bp.route('/user/reservations')
@login_required
def get_user_reservations():
    """Get current user's reservations"""
    reservations = Reservation.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).all()
    
    return jsonify([{
        'id': r.id,
        'book': {
            'id': r.book.id,
            'title': r.book.title,
            'author': r.book.author
        },
        'created_at': r.created_at.isoformat(),
        'expiry_date': r.expiry_date.isoformat() if r.expiry_date else None
    } for r in reservations])


@api_bp.route('/user/notifications')
@login_required
def get_user_notifications():
    """Get current user's notifications"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications])


@api_bp.route('/user/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@api_bp.route('/user/stats')
@login_required
def get_user_stats():
    """Get current user's statistics"""
    total_borrowed = Borrowing.query.filter_by(user_id=current_user.id).count()
    currently_borrowed = Borrowing.query.filter_by(
        user_id=current_user.id,
        status='borrowed'
    ).count()
    overdue = Borrowing.query.filter(
        Borrowing.user_id == current_user.id,
        Borrowing.status == 'borrowed',
        Borrowing.due_date < datetime.utcnow()
    ).count()
    
    return jsonify({
        'total_borrowed': total_borrowed,
        'currently_borrowed': currently_borrowed,
        'overdue': overdue,
        'total_fine': current_user.get_total_fine(),
        'can_borrow': current_user.can_borrow()
    })


# ==================== ADMIN APIs ====================

@api_bp.route('/admin/stats')
@login_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_books = Book.query.count()
    total_users = User.query.count()
    active_borrowings = Borrowing.query.filter_by(status='borrowed').count()
    overdue = Borrowing.query.filter(
        Borrowing.status == 'borrowed',
        Borrowing.due_date < datetime.utcnow()
    ).count()
    
    return jsonify({
        'total_books': total_books,
        'total_users': total_users,
        'active_borrowings': active_borrowings,
        'overdue': overdue
    })


@api_bp.route('/admin/borrowing-trends')
@login_required
def get_borrowing_trends():
    """Get borrowing trends for charts"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    from datetime import timedelta
    from sqlalchemy import func
    
    trends = []
    for i in range(30):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = Borrowing.query.filter(
            func.date(Borrowing.borrow_date) == date
        ).count()
        trends.append({
            'date': date.isoformat(),
            'count': count
        })
    
    trends.reverse()
    return jsonify(trends)


# ==================== HEALTH CHECK ====================

@api_bp.route('/health')
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })
