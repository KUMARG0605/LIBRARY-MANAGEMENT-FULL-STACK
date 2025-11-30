# 📚 Digital Learning Library Management System

A comprehensive, production-ready Library Management System built with Flask, PostgreSQL, and modern web technologies. Features include book management, user authentication, borrowing system, reservations, reviews, and admin dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### User Features
- 🔐 **Secure Authentication**: Login, registration, password reset, email verification
- 📖 **Book Browsing**: Search, filter by category/department, sort options
- 📚 **Borrowing System**: Borrow books, track due dates, auto-calculate fines
- 🔖 **Reservations**: Reserve unavailable books, get notified when available
- ⭐ **Reviews & Ratings**: Rate and review books
- 📊 **User Dashboard**: Track borrowings, reservations, fines, notifications
- 👤 **Profile Management**: Update profile, change password, view history

### Admin Features
- 📈 **Admin Dashboard**: Analytics, statistics, charts
- 👥 **User Management**: View, activate/deactivate users
- 📕 **Book Management**: Add, edit, delete books with cover images
- 📋 **Borrowing Management**: Track all borrowings, process returns
- 🏷️ **Category/Department Management**: Organize library structure
- ⚙️ **Settings**: Configure system parameters
- 📊 **Reports**: Generate borrowing statistics and reports

### Technical Features
- 🚀 **RESTful API**: Complete API for mobile/external apps
- 🐳 **Docker Ready**: Full Docker and docker-compose configuration
- 🔄 **Database Migrations**: Flask-Migrate for schema management
- 📧 **Email Integration**: Flask-Mail for notifications
- 🎨 **Modern UI**: Bootstrap 5, Font Awesome, custom CSS
- 📱 **Responsive Design**: Mobile-first approach
- 🔒 **Security**: CSRF protection, password hashing, session management
- ⚡ **Performance**: Redis caching, optimized queries
- 🌐 **Production Ready**: Gunicorn, Nginx, PostgreSQL

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/KUMARG0605/LIbrary-management.git
cd LIbrary-management
```

2. **Create virtual environment**
```powershell
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure environment**
```powershell
Copy-Item .env.example .env
# Edit .env with your settings
```

5. **Initialize database**
```powershell
python -c "from app_new import app, db; app.app_context().push(); db.create_all()"
```

6. **Run the application**
```powershell
python app_new.py
```

Visit: `http://localhost:5000`

**Default Admin Login:**
- Username: ADMIN001
- Password: admin123

### Option 2: Docker Deployment

1. **Start all services**
```powershell
docker-compose up -d --build
```

2. **Check status**
```powershell
docker-compose ps
```

3. **View logs**
```powershell
docker-compose logs -f web
```

Visit: `http://localhost`

## 📝 Configuration

Edit `.env` file with your settings:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///library_dev.db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🔐 Default Admin Access

- **Username**: ADMIN001
- **Email**: admin@library.com
- **Password**: admin123

⚠️ **Change this immediately in production!**

## 📚 API Endpoints

### Books API
```
GET  /api/search?q=term         # Search books
GET  /api/books/{id}            # Get book details
GET  /api/categories            # List categories
GET  /api/departments           # List departments
```

### User API (Authentication Required)
```
GET  /api/user/borrowings       # Get user's borrowings
GET  /api/user/reservations     # Get user's reservations
```

### Public Stats
```
GET  /api/stats                 # Library statistics
```

## 🛠️ Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- SQLAlchemy - ORM
- Flask-Login - Authentication
- Flask-Mail - Email notifications
- Flask-WTF - Form handling
- Flask-Migrate - Database migrations

**Frontend:**
- Bootstrap 5 - UI framework
- Font Awesome 6 - Icons
- jQuery 3.7 - JavaScript library
- Custom CSS/JS

**Database:**
- PostgreSQL (Production)
- SQLite (Development)

**Deployment:**
- Docker & Docker Compose
- Gunicorn - WSGI server
- Nginx - Reverse proxy
- Redis - Caching

## 📦 Project Structure

```
library-management/
├── app_new.py              # Main application
├── config.py               # Configuration
├── models.py               # Database models
├── forms.py                # WTForms
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker config
├── docker-compose.yml      # Multi-container setup
├── routes/                 # Application routes
│   ├── main.py            # Main routes
│   ├── auth.py            # Authentication
│   ├── books.py           # Book management
│   ├── user.py            # User dashboard
│   ├── admin.py           # Admin panel
│   └── api.py             # API endpoints
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── main/
│   ├── auth/
│   ├── books/
│   ├── user/
│   ├── admin/
│   └── errors/
├── static/                 # Static files
│   ├── css/
│   ├── js/
│   └── images/
└── nginx/                  # Nginx config
```

## 🧪 Testing

```powershell
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📊 Database Models

- **User**: Users (students, faculty, admin)
- **Book**: Book catalog with details
- **Borrowing**: Borrowing records with fines
- **Reservation**: Book reservations
- **Review**: Book reviews and ratings
- **Notification**: User notifications
- **Category**: Book categories
- **Department**: Academic departments
- **ActivityLog**: System activity logging
- **Setting**: System configuration

## 🚢 Deployment

### Production Checklist

- [ ] Change SECRET_KEY
- [ ] Change admin password
- [ ] Use PostgreSQL database
- [ ] Configure Redis cache
- [ ] Set up email server
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Enable monitoring

### Docker Commands

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Execute commands
docker-compose exec web flask db upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 👥 Author

**Kumar G** - [@KUMARG0605](https://github.com/KUMARG0605)

## 📞 Support

- Email: info@library.com
- GitHub Issues: [Create Issue](https://github.com/KUMARG0605/LIbrary-management/issues)

---

Made with ❤️ by Kumar G | © 2025 Digital Learning Library