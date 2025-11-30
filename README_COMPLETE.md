# 📚 Digital Learning Library - Complete Full Stack System

A comprehensive, production-ready Library Management System with modern features including email notifications, subscription plans, digital book reading, and integrated payment gateways.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

## 🌟 Key Features

### 📧 Comprehensive Email System
- **Verification Emails**: Secure email verification for new users
- **Welcome Emails**: Personalized welcome messages with account details
- **Login Alerts**: Security notifications for new logins with IP/device info
- **Due Date Reminders**: Automated reminders for book due dates
- **Overdue Notices**: Fine calculations and overdue notifications
- **Reservation Alerts**: Notifications when reserved books become available
- **Announcements**: Admin broadcast system to all users or specific groups
- **Payment Receipts**: Automated receipt generation for all transactions
- **Subscription Confirmations**: Detailed subscription activation emails

### 💳 Multiple Payment Gateways
- **Razorpay Integration**: Complete payment processing
- **PhonePe**: Direct UPI payments via PhonePe
- **Google Pay**: GPay integration for quick payments
- **UPI Links**: Generate universal UPI payment links
- **QR Codes**: Payment QR code generation
- **Automatic Receipts**: Email receipts for all transactions
- **Refund Support**: Automated refund processing

### 📱 Subscription Plans
1. **Basic Plan** (Free)
   - Borrow up to 3 books
   - Limited digital access
   - Standard support

2. **Premium Plan** (₹299/month, ₹2999/year)
   - Borrow up to 5 books
   - Full digital library access
   - Priority reservations
   - 3 renewals allowed
   - Email notifications

3. **VIP Plan** (₹599/month, ₹5999/year)
   - Borrow up to 10 books
   - Unlimited digital access
   - Download books (selected titles)
   - Priority support
   - No late fees
   - Exclusive early access to new books

### 📖 Digital Book Reader
- **Multi-Format Support**: PDF and EPUB readers
- **Reading Progress**: Auto-save reading position
- **Bookmarks**: Save important pages
- **Highlights**: Highlight text passages
- **Notes**: Add personal notes
- **Customization**: 
  - Font size adjustment
  - Line height control
  - Reading modes (Light, Sepia, Dark)
  - Zoom controls
- **Keyboard Shortcuts**: Navigate with arrow keys
- **Responsive Design**: Works on all devices

### 👥 User Management
- Student, Faculty, and Admin roles
- Email verification system
- Password reset functionality
- Profile management with avatars
- Activity tracking

### 📚 Book Management
- Comprehensive book cataloging
- ISBN-based identification
- Multiple categories and departments
- Cover image uploads
- Digital and physical book tracking
- Advanced search and filters

### 🔔 Smart Notifications
- In-app notification system
- Email notifications
- Due date reminders
- Fine alerts
- Reservation updates
- New book announcements

### 📊 Admin Dashboard
- User analytics
- Book statistics
- Fine collection tracking
- Activity logs
- Announcement system
- Email broadcast to users
- Subscription management

### 🔒 Security Features
- Password hashing with bcrypt
- CSRF protection
- Session management
- Login activity tracking
- IP address logging
- Secure token generation

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.9+
pip (Python package manager)
Git
```

### 1. Clone the Repository
```bash
git clone https://github.com/KUMARG0605/LIbrary-management.git
cd LIbrary-management
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_APP=app_new.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///library.db

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=bothackerr03@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=bothackerr03@gmail.com

# Application URL
BASE_URL=http://localhost:5000

# Payment Gateways
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### 5. Gmail App Password Setup
1. Go to Google Account Settings
2. Security → 2-Step Verification (enable it)
3. App passwords → Generate new app password
4. Copy the 16-character password
5. Use this in `MAIL_PASSWORD` field

### 6. Razorpay Setup (for payments)
1. Sign up at https://razorpay.com
2. Get API Keys from Dashboard
3. Add keys to `.env` file

### 7. Initialize Database
```bash
python
>>> from app_new import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 8. Run the Application
```bash
python app_new.py
```

Access the application at `http://localhost:5000`

### 9. Default Admin Login
```
User ID: ADMIN001
Password: admin123
```

**⚠️ Change the default admin password immediately!**

## 📁 Project Structure

```
Library-Management/
├── app_new.py              # Main application factory
├── config.py               # Configuration settings
├── models.py               # Database models (with subscriptions, payments, digital books)
├── email_service.py        # Comprehensive email handling
├── payment_service.py      # Payment gateway integration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── routes/                # Route blueprints
│   ├── __init__.py
│   ├── main.py           # Home, search
│   ├── auth.py           # Login, register, verification
│   ├── books.py          # Book browsing, reader
│   ├── user.py           # Dashboard, profile, subscription
│   ├── admin.py          # Admin panel, announcements
│   └── api.py            # API endpoints
├── templates/            # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── books/
│   ├── user/
│   ├── admin/
│   ├── reader.html       # Digital book reader
│   └── emails/           # Email templates
│       ├── verification.html
│       ├── welcome.html
│       ├── login_alert.html
│       ├── announcement.html
│       ├── payment_receipt.html
│       └── subscription_confirmation.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   ├── images/
│   └── uploads/          # Uploaded files (book covers, digital books)
├── migrations/           # Database migrations
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker image
└── README.md           # Documentation
```

## 🎯 Core Functionalities

### For Students/Faculty
1. **Browse Books**: Search by title, author, ISBN, category
2. **Borrow Books**: Borrow up to 5 books (or more with subscription)
3. **Reserve Books**: Queue for unavailable books
4. **Digital Reading**: Read books online with progress tracking
5. **Manage Profile**: Update information and view history
6. **Pay Fines**: Online payment for overdue books
7. **Subscribe**: Choose subscription plans for extra benefits
8. **Receive Notifications**: Email and in-app alerts

### For Admins
1. **Manage Books**: Add, edit, delete books
2. **Manage Users**: View, activate/deactivate users
3. **Track Borrowings**: Monitor all borrowing activities
4. **Send Announcements**: Email broadcasts to users
5. **View Analytics**: Dashboard with statistics
6. **Manage Subscriptions**: Track subscription plans
7. **Process Payments**: Monitor all transactions
8. **Upload Digital Books**: Add PDF/EPUB files

## 🛠️ API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/verify/<token>` - Email verification
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password/<token>` - Reset password

### Books
- `GET /books` - List all books
- `GET /books/<id>` - Book details
- `POST /books/borrow/<id>` - Borrow book
- `POST /books/return/<id>` - Return book
- `POST /books/reserve/<id>` - Reserve book
- `GET /books/read/<id>` - Digital reader

### User
- `GET /user/dashboard` - User dashboard
- `GET /user/profile` - View profile
- `POST /user/profile` - Update profile
- `GET /user/borrowings` - Borrowing history
- `POST /user/subscribe` - Purchase subscription

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/books` - Add book
- `PUT /admin/books/<id>` - Update book
- `DELETE /admin/books/<id>` - Delete book
- `POST /admin/announcement` - Send announcement
- `GET /admin/users` - List all users

### Payments
- `POST /api/payment/create` - Create payment order
- `POST /api/payment/verify` - Verify payment
- `GET /api/payment/receipt/<id>` - Get receipt

## 💻 Technology Stack

### Backend
- **Flask 3.0**: Web framework
- **SQLAlchemy**: ORM with relationship management
- **Flask-Login**: Authentication
- **Flask-Mail**: Email handling
- **Flask-WTF**: Form handling & CSRF
- **Flask-Migrate**: Database migrations
- **Razorpay SDK**: Payment processing

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Bootstrap 5**: Responsive design
- **JavaScript**: Interactive features
- **jQuery**: DOM manipulation
- **Font Awesome**: Icons

### Database
- **SQLite**: Development
- **PostgreSQL**: Production (recommended)

### Payment Gateways
- **Razorpay**: Primary payment processor
- **UPI**: PhonePe, GPay integration

### Email
- **Gmail SMTP**: Email delivery via bothackerr03@gmail.com

## 🐳 Docker Deployment

### Build and Run
```bash
docker-compose up -d
```

### Services
- **web**: Flask application (port 5000)
- **db**: PostgreSQL database (port 5432)
- **nginx**: Reverse proxy (port 80)

## 🌐 Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app_new:create_app()"
```

### Environment Variables for Production
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/library_prod
SECRET_KEY=generate-strong-secret-key
SESSION_COOKIE_SECURE=True
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/library/static;
    }
}
```

## 📧 Email Configuration Details

All emails are sent from: **bothackerr03@gmail.com**

### Email Types Configured:
1. **Verification Email**: Sent upon registration
2. **Welcome Email**: Sent after email verification
3. **Login Alert**: Sent on new device login
4. **Password Reset**: Sent on forgot password request
5. **Due Reminders**: 3 days before due date
6. **Overdue Notices**: Daily for overdue books
7. **Reservation Available**: When reserved book is available
8. **New Book Alerts**: Optional notifications for new books
9. **Announcements**: Admin broadcasts
10. **Payment Receipts**: For all transactions
11. **Subscription Confirmations**: Upon subscription purchase

## 💡 Usage Examples

### Send Announcement (Admin)
```python
from email_service import send_admin_announcement

recipients = ['user1@example.com', 'user2@example.com']
send_admin_announcement(
    recipients,
    'Library Closed Tomorrow',
    'The library will be closed on Dec 25 for maintenance.'
)
```

### Process Payment
```python
from payment_service import process_subscription_payment

order = process_subscription_payment(
    user_id=1,
    plan_id=2,  # Premium plan
    duration_months=12
)
```

### Save Reading Progress
```python
from models import ReadingProgress

progress = ReadingProgress.query.filter_by(
    user_id=current_user.id,
    digital_book_id=book_id
).first()

if progress:
    progress.update_progress(page=50)
else:
    progress = ReadingProgress(
        user_id=current_user.id,
        digital_book_id=book_id,
        current_page=50,
        total_pages=200
    )
    db.session.add(progress)
db.session.commit()
```

## 🔐 Security Best Practices

1. **Change Default Credentials**: Update admin password immediately
2. **Use Strong Secrets**: Generate secure SECRET_KEY
3. **Enable HTTPS**: Use SSL certificates in production
4. **Update Dependencies**: Keep all packages updated
5. **Backup Database**: Regular automated backups
6. **Monitor Logs**: Check for suspicious activities
7. **Email Security**: Use app-specific passwords
8. **Payment Security**: Never expose API keys

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Kumar G**
- GitHub: [@KUMARG0605](https://github.com/KUMARG0605)
- Email: bothackerr03@gmail.com

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Bootstrap for responsive design framework
- Razorpay for payment gateway integration
- All contributors and users

## 📞 Support

For support, email bothackerr03@gmail.com or create an issue in the repository.

---

**⭐ If you find this project useful, please star it on GitHub!**
