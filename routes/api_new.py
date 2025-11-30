"""
API Routes
RESTful API endpoints for mobile/external apps
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from models import db, Book, User, Borrowing, Reservation, Category, Department

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
def api_search():
    """Search books API"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) |
        (Book.author.ilike(f'%{query}%')) |
        (Book.isbn.ilike(f'%{query}%'))
    ).filter_by(is_active=True).limit(limit).all()
    
    results = [{
        'id': book.id,
        'isbn': book.isbn,
        'title': book.title,
        'author': book.author,
        'category': book.category,
        'available': book.is_available(),
        'cover_image': book.cover_image
    } for book in books]
    
    return jsonify({'results': results, 'count': len(results)})


@api_bp.route('/books/<int:book_id>')
def api_book_detail(book_id):
    """Get book details"""
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
        'description': book.description,
        'total_copies': book.total_copies,
        'available_copies': book.available_copies,
        'average_rating': book.get_average_rating(),
        'cover_image': book.cover_image
    })


@api_bp.route('/categories')
def api_categories():
    """Get all categories"""
    categories = Category.query.filter_by(is_active=True).all()
    
    return jsonify({
        'categories': [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'icon': cat.icon
        } for cat in categories]
    })


@api_bp.route('/departments')
def api_departments():
    """Get all departments"""
    departments = Department.query.filter_by(is_active=True).all()
    
    return jsonify({
        'departments': [{
            'id': dept.id,
            'code': dept.code,
            'name': dept.name,
            'description': dept.description
        } for dept in departments]
    })


@api_bp.route('/user/borrowings')
@login_required
def api_user_borrowings():
    """Get user's borrowings"""
    borrowings = Borrowing.query.filter_by(
        user_id=current_user.id
    ).order_by(Borrowing.borrow_date.desc()).all()
    
    return jsonify({
        'borrowings': [{
            'id': b.id,
            'book_title': b.book.title,
            'book_author': b.book.author,
            'borrow_date': b.borrow_date.isoformat(),
            'due_date': b.due_date.isoformat(),
            'return_date': b.return_date.isoformat() if b.return_date else None,
            'status': b.status,
            'is_overdue': b.is_overdue(),
            'fine_amount': float(b.fine_amount)
        } for b in borrowings]
    })


@api_bp.route('/user/reservations')
@login_required
def api_user_reservations():
    """Get user's reservations"""
    reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(Reservation.created_at.desc()).all()
    
    return jsonify({
        'reservations': [{
            'id': r.id,
            'book_title': r.book.title,
            'book_author': r.book.author,
            'created_at': r.created_at.isoformat(),
            'status': r.status
        } for r in reservations]
    })


@api_bp.route('/stats')
def api_stats():
    """Get library statistics"""
    stats = {
        'total_books': Book.query.filter_by(is_active=True).count(),
        'available_books': Book.query.filter(
            Book.is_active == True,
            Book.available_copies > 0
        ).count(),
        'total_users': User.query.filter_by(is_active=True).count(),
        'active_borrowings': Borrowing.query.filter_by(status='borrowed').count(),
        'categories': Category.query.filter_by(is_active=True).count(),
        'departments': Department.query.filter_by(is_active=True).count()
    }
    
    return jsonify(stats)


@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Not found'}), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
