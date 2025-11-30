"""
Database Models for Library Management System
Using SQLAlchemy ORM with relationships
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for students, faculty, and administrators"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default='student')  # student, faculty, admin
    department = db.Column(db.String(50))
    profile_image = db.Column(db.String(255), default='default_avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='user', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    reading_progress = db.relationship('ReadingProgress', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_active_borrowings(self):
        return self.borrowings.filter_by(status='borrowed').all()
    
    def get_total_fine(self):
        total = 0
        for borrowing in self.get_active_borrowings():
            if borrowing.is_overdue():
                total += borrowing.calculate_fine()
        return total
    
    def can_borrow(self):
        return len(self.get_active_borrowings()) < 5 and self.get_total_fine() == 0
    
    def __repr__(self):
        return f'<User {self.user_id}>'


class Book(db.Model):
    """Book model with comprehensive details"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    edition = db.Column(db.String(20))
    category = db.Column(db.String(50), index=True)
    department = db.Column(db.String(50), index=True)
    language = db.Column(db.String(30), default='English')
    pages = db.Column(db.Integer)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    shelf_location = db.Column(db.String(20))
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255), default='default_book.png')
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='book', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='book', lazy='dynamic')
    reviews = db.relationship('Review', backref='book', lazy='dynamic')
    
    def is_available(self):
        return self.available_copies > 0
    
    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    def get_pending_reservations(self):
        return self.reservations.filter_by(status='pending').order_by(Reservation.created_at).all()
    
    def __repr__(self):
        return f'<Book {self.title}>'


class Borrowing(db.Model):
    """Borrowing records with fine calculation"""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    renewed_count = db.Column(db.Integer, default=0)
    fine_amount = db.Column(db.Float, default=0)
    fine_paid = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, lost
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_overdue(self):
        if self.status == 'borrowed':
            return datetime.utcnow() > self.due_date
        return False
    
    def days_overdue(self):
        if self.is_overdue():
            return (datetime.utcnow() - self.due_date).days
        return 0
    
    def calculate_fine(self, fine_per_day=5):
        return self.days_overdue() * fine_per_day
    
    def can_renew(self):
        return self.status == 'borrowed' and self.renewed_count < 2 and not self.is_overdue()
    
    def renew(self, days=14):
        if self.can_renew():
            self.due_date = datetime.utcnow() + timedelta(days=days)
            self.renewed_count += 1
            return True
        return False
    
    def __repr__(self):
        return f'<Borrowing {self.id}>'


class Reservation(db.Model):
    """Book reservation queue"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, fulfilled, cancelled, expired
    notified = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
    
    def __repr__(self):
        return f'<Reservation {self.id}>'


class Review(db.Model):
    """Book reviews and ratings"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'


class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30))  # due_reminder, reservation, fine, general
    related_id = db.Column(db.Integer)  # ID of related book, borrowing, etc.
    action_url = db.Column(db.String(255))  # URL for action button
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'


class Category(db.Model):
    """Book categories"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Department(db.Model):
    """Academic departments"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Department {self.code}>'


class ActivityLog(db.Model):
    """System activity logging"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(30))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityLog {self.id}>'


class Setting(db.Model):
    """System settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get(key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value, description=None):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return f'<Setting {self.key}>'


class SubscriptionPlan(db.Model):
    """Subscription plans for users"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Basic, Premium, VIP
    description = db.Column(db.Text)
    price_monthly = db.Column(db.Float, nullable=False)
    price_yearly = db.Column(db.Float, nullable=False)
    max_books = db.Column(db.Integer, default=5)
    digital_access = db.Column(db.String(50), default='Limited')  # Limited, Full, Unlimited
    max_renewals = db.Column(db.Integer, default=2)
    priority_reservation = db.Column(db.Boolean, default=False)
    no_late_fees = db.Column(db.Boolean, default=False)
    features = db.Column(db.Text)  # JSON string of features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subscriptions = db.relationship('Subscription', backref='plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'


class Subscription(db.Model):
    """User subscriptions"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    auto_renew = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_active(self):
        return self.status == 'active' and datetime.utcnow() <= self.end_date
    
    def days_remaining(self):
        if self.is_active():
            return (self.end_date - datetime.utcnow()).days
        return 0
    
    def __repr__(self):
        return f'<Subscription {self.id}>'


class DigitalBook(db.Model):
    """Digital books with file storage"""
    __tablename__ = 'digital_books'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10))  # PDF, EPUB
    file_size = db.Column(db.Integer)  # in bytes
    total_pages = db.Column(db.Integer)
    access_level = db.Column(db.String(20), default='premium')  # free, premium, vip
    download_allowed = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    book = db.relationship('Book', backref='digital_version')
    reading_progress = db.relationship('ReadingProgress', backref='digital_book', lazy='dynamic')
    
    def __repr__(self):
        return f'<DigitalBook {self.id}>'


class ReadingProgress(db.Model):
    """Track user's reading progress in digital books"""
    __tablename__ = 'reading_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    digital_book_id = db.Column(db.Integer, db.ForeignKey('digital_books.id'), nullable=False)
    current_page = db.Column(db.Integer, default=1)
    total_pages = db.Column(db.Integer)
    percentage = db.Column(db.Float, default=0)
    last_read = db.Column(db.DateTime, default=datetime.utcnow)
    bookmarks = db.Column(db.Text)  # JSON array of page numbers
    highlights = db.Column(db.Text)  # JSON array of highlights
    notes = db.Column(db.Text)  # JSON array of notes
    
    def update_progress(self, page):
        self.current_page = page
        if self.total_pages:
            self.percentage = (page / self.total_pages) * 100
        self.last_read = datetime.utcnow()
    
    def __repr__(self):
        return f'<ReadingProgress {self.id}>'


class Payment(db.Model):
    """Payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    payment_method = db.Column(db.String(50))  # razorpay, phonepe, gpay, upi
    payment_gateway = db.Column(db.String(50))
    purpose = db.Column(db.String(100))  # subscription, fine, others
    reference_id = db.Column(db.String(100))  # subscription_id, borrowing_id, etc.
    status = db.Column(db.String(20), default='pending')  # pending, success, failed, refunded
    gateway_response = db.Column(db.Text)  # JSON response from payment gateway
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'


class EmailLog(db.Model):
    """Log all sent emails"""
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    email_type = db.Column(db.String(50))  # verification, welcome, notification, etc.
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailLog {self.id}>'


class Announcement(db.Model):
    """Admin announcements"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(30))  # general, urgent, maintenance, event
    target_audience = db.Column(db.String(50))  # all, students, faculty, department_specific
    target_department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    is_email_sent = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Announcement {self.title}>'


class TransactionVerification(db.Model):
    """Verification codes for book transactions"""
    __tablename__ = 'transaction_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.id'))
    transaction_type = db.Column(db.String(20), nullable=False)  # borrow, renew, return
    verification_code = db.Column(db.String(10), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='transaction_verifications')
    borrowing = db.relationship('Borrowing', backref='verifications')
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<TransactionVerification {self.verification_code}>'
