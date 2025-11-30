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
