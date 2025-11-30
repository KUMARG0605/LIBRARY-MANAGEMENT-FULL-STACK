# 🚀 DIGITAL LEARNING - Library Management System
## Production-Grade Full-Stack Application

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, production-ready library management system with modern features including email notifications, payment integration, digital book reading, and subscription plans.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Features
- 📚 **Complete Book Management** - Add, edit, search, and categorize books
- 👥 **User Management** - Student, faculty, and admin roles with permissions
- 📖 **Borrowing System** - Issue, return, renew books with due date tracking
- 🔍 **Advanced Search** - Filter by category, department, availability
- 📊 **Analytics Dashboard** - Real-time statistics and reports

### Advanced Features
- ✉️ **11 Email Notification Types**
  - Account verification & welcome emails
  - Login alerts with IP tracking
  - Book due reminders (3 days advance)
  - Overdue notices with fine calculation
  - Reservation availability alerts
  - New book announcements
  - Admin broadcasts
  - Payment receipts
  - Subscription confirmations

- 💳 **Payment Integration**
  - Razorpay gateway (cards, UPI, net banking)
  - PhonePe & Google Pay links
  - UPI payment QR codes
  - Automatic receipt generation

- 📱 **Subscription Plans**
  - **Basic**: Free - 5 books, standard features
  - **Premium**: ₹299/month - 10 books, priority reservations
  - **VIP**: ₹599/month - Unlimited books, digital library access

- 📖 **Digital Book Reader**
  - PDF & EPUB support
  - Reading progress tracking
  - Bookmarks & highlights
  - Notes functionality
  - 3 reading modes (day/night/sepia)
  - Adjustable font size & line height

### UI/UX Features
- 🎨 Dark Blue Theme (#141438) - Professional, modern design
- 📱 Fully Responsive - Works on all devices
- ⚡ Real-time Updates - Instant notifications
- 🔒 Secure Authentication - Password hashing, session management
- ♿ Accessible - WCAG 2.1 compliant

---

## 🛠 Tech Stack

### Frontend
- **HTML5/CSS3** - Semantic markup, modern styling
- **Bootstrap 5.3** - Responsive framework
- **JavaScript (ES6+)** - Interactive features
- **Font Awesome 6.5** - Icons
- **jQuery 3.7** - DOM manipulation

### Backend
- **Python 3.11** - Core language
- **Flask 3.0** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-Mail** - Email service integration
- **Flask-Migrate** - Database migrations
- **Flask-WTF** - Form handling & CSRF protection
- **Razorpay SDK** - Payment processing

### Database
- **SQLite** - Development database
- **PostgreSQL 15** - Production database (recommended)
- **Redis** - Caching & session storage

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy & load balancer
- **Gunicorn** - WSGI HTTP server
- **Let's Encrypt** - SSL certificates

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
pip (Python package manager)
Git
```

### 1-Minute Setup
```powershell
# Clone repository
git clone https://github.com/KUMARG0605/LIbrary-management.git
cd LIbrary-management

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run application
python app_new.py
```

**Access**: http://localhost:5000

**Default Admin**:
- User ID: `ADMIN001`
- Password: `admin123`

---

## 📦 Installation

### Development Setup

1. **Create Virtual Environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

3. **Configure Environment**
```powershell
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
notepad .env
```

4. **Initialize Database**
```powershell
python init_db.py
```

5. **Run Development Server**
```powershell
python app_new.py
```

### Email Setup (Gmail)

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Visit https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Update .env**
```env
MAIL_USERNAME=bothackerr03@gmail.com
MAIL_PASSWORD=your-app-password-here
```

### Payment Setup (Razorpay)

1. **Create Account**: https://dashboard.razorpay.com/signup
2. **Get API Keys**: Settings → API Keys
3. **Update .env**:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret_key
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Flask Configuration
FLASK_APP=app_new.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this

# Database
DATABASE_URL=sqlite:///library.db
# Production: postgresql://user:pass@localhost/library_db

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=bothackerr03@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=bothackerr03@gmail.com

# Payment (Razorpay)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret_key

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Application
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/uploads
```

### Database Schema

The system uses 17 interconnected tables:

**Core Tables:**
- `users` - User accounts (admin, faculty, student)
- `books` - Book inventory
- `categories` - Book categories
- `departments` - Academic departments
- `borrowings` - Book loans
- `reservations` - Book reservations
- `reviews` - Book reviews

**Advanced Tables:**
- `subscriptions` - User subscription plans
- `subscription_plans` - Plan definitions
- `digital_books` - Digital library content
- `reading_progress` - User reading history
- `payments` - Transaction records
- `email_logs` - Email audit trail
- `announcements` - Admin broadcasts
- `notifications` - In-app alerts
- `activity_logs` - System audit logs
- `fines` - Overdue fines

---

## 🐳 Deployment

### Docker Deployment

1. **Build & Run**
```powershell
docker-compose up -d
```

2. **Initialize Database (First Time)**
```powershell
docker-compose exec web python init_db.py
```

3. **Access Application**
- HTTP: http://localhost
- HTTPS: https://localhost (after SSL setup)

### Manual Production Deployment

#### 1. Server Setup (Ubuntu 22.04)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib nginx redis-server

# Create application user
sudo useradd -m -s /bin/bash library
sudo su - library
```

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/KUMARG0605/LIbrary-management.git
cd LIbrary-management

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Initialize database
python init_db.py
```

#### 3. PostgreSQL Setup
```bash
sudo -u postgres psql

CREATE DATABASE library_management;
CREATE USER library_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE library_management TO library_user;
\q
```

Update `.env`:
```env
DATABASE_URL=postgresql://library_user:secure_password@localhost/library_management
```

#### 4. Gunicorn Service
Create `/etc/systemd/system/library.service`:
```ini
[Unit]
Description=Digital Learning Library Management System
After=network.target postgresql.service redis.service

[Service]
User=library
Group=www-data
WorkingDirectory=/home/library/LIbrary-management
Environment="PATH=/home/library/LIbrary-management/venv/bin"
ExecStart=/home/library/LIbrary-management/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/home/library/LIbrary-management/library.sock \
    --timeout 120 \
    --access-logfile /home/library/logs/access.log \
    --error-logfile /home/library/logs/error.log \
    "app_new:create_app()"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start library
sudo systemctl enable library
```

#### 5. Nginx Configuration
Create `/etc/nginx/sites-available/library`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://unix:/home/library/LIbrary-management/library.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/library/LIbrary-management/static/;
        expires 30d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/library /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Setup (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

---

## 📡 API Documentation

### Authentication Endpoints

**POST /auth/login**
```json
{
  "user_id": "ADMIN001",
  "password": "admin123",
  "remember": false
}
```

**POST /auth/register**
```json
{
  "user_id": "STU001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "1234567890",
  "role": "student",
  "department": "CSE"
}
```

### Book Endpoints

**GET /books/**
- Query params: `page`, `category`, `department`, `search`, `sort`, `availability`
- Returns: Paginated book list

**GET /books/<int:book_id>**
- Returns: Book details, reviews, similar books

**POST /books/<int:book_id>/borrow**
- Auth required
- Action: Borrow book

**POST /books/<int:book_id>/reserve**
- Auth required
- Action: Reserve unavailable book

### User Endpoints

**GET /user/dashboard**
- Auth required
- Returns: User dashboard data

**GET /user/borrowings**
- Auth required
- Returns: User's borrowed books

**POST /user/renew/<int:borrowing_id>**
- Auth required
- Action: Renew book

### Admin Endpoints

**GET /admin/dashboard**
- Admin only
- Returns: System statistics

**POST /admin/books/add**
- Admin only
- Action: Add new book

**POST /admin/announcement**
- Admin only
- Action: Send announcement email

### Payment Endpoints

**POST /api/payment/create**
```json
{
  "amount": 299,
  "type": "subscription",
  "plan_id": 2
}
```

**POST /api/payment/verify**
```json
{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "signature_xxx"
}
```

---

## 🧪 Testing

### Run Tests
```powershell
# Unit tests
python -m pytest tests/

# With coverage
python -m pytest --cov=. tests/

# Specific test file
python -m pytest tests/test_auth.py
```

### Test Admin Login
```powershell
# Default credentials
User ID: ADMIN001
Password: admin123
```

### Test Email Service
```powershell
python -c "
from app_new import create_app
from email_service import send_verification_email

app = create_app()
with app.app_context():
    send_verification_email('test@example.com', 'TEST001', 'ABC123')
    print('✅ Email sent!')
"
```

---

## 📚 Documentation

- **User Guide**: `docs/USER_GUIDE.md`
- **Admin Manual**: `docs/ADMIN_GUIDE.md`
- **API Reference**: `docs/API_DOCS.md`
- **Setup Guide**: `SETUP_GUIDE.md`
- **Features List**: `FEATURES.md`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**KUMAR G**
- GitHub: [@KUMARG0605](https://github.com/KUMARG0605)
- Email: bothackerr03@gmail.com

---

## 🙏 Acknowledgments

- Flask framework and its extensive ecosystem
- Bootstrap team for the responsive framework
- Font Awesome for the icon library
- All contributors and testers

---

## 📞 Support

For support, email bothackerr03@gmail.com or open an issue on GitHub.

---

**⭐ If you find this project helpful, please give it a star!**

**🔗 Live Demo**: https://your-domain.com (coming soon)

---

*Last Updated: November 29, 2025*
