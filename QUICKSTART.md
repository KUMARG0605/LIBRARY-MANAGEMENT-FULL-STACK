# Quick Start Guide

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional)

## 🚀 Quick Setup (5 minutes)

### Step 1: Setup Environment

Open PowerShell in the project directory and run:

```powershell
.\setup.ps1
```

This script will:
- Create virtual environment
- Install dependencies
- Create .env file
- Initialize database
- Create necessary folders

### Step 2: Configure Settings (Optional)

Edit `.env` file if needed:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///library_dev.db
```

### Step 3: Run Application

```powershell
.\run.ps1
```

Or manually:
```powershell
venv\Scripts\activate
python app_new.py
```

### Step 4: Access Application

Open browser and visit:
```
http://localhost:5000
```

## 🔑 Default Login

**Admin Account:**
- Username: `ADMIN001`
- Email: `admin@library.com`
- Password: `admin123`

⚠️ **Change this password immediately!**

## 📖 User Guide

### For Students/Faculty:

1. **Register Account**
   - Click "Register" in navbar
   - Fill in details (User ID, Email, Name, etc.)
   - Choose role (Student/Faculty)
   - Submit registration

2. **Browse Books**
   - Click "Books" in navbar
   - Use search or filters
   - Click on book for details

3. **Borrow a Book**
   - Open book detail page
   - Click "Borrow Book"
   - Book appears in your dashboard
   - Due date is 14 days from borrow date

4. **Return a Book**
   - Go to Dashboard
   - Find borrowed book
   - Click "Return" button
   - Fine calculated if overdue

5. **Reserve a Book**
   - If book unavailable
   - Click "Reserve Book"
   - Get notified when available

### For Admins:

1. **Access Admin Panel**
   - Login as admin
   - Click dropdown → "Admin Panel"

2. **Add Books**
   - Admin Panel → Books → Add Book
   - Fill in book details
   - Upload cover image (optional)
   - Submit

3. **Manage Users**
   - Admin Panel → Users
   - View, activate/deactivate users
   - View user borrowing history

4. **Track Borrowings**
   - Admin Panel → Borrowings
   - See all active/returned borrowings
   - Process returns manually

5. **View Reports**
   - Admin Panel → Reports
   - Select date range
   - View statistics

## 🐳 Docker Deployment

### Using Docker Compose:

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Web: http://localhost
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Environment Variables:

Edit `.env` for Docker:
```env
FLASK_ENV=production
DATABASE_URL=postgresql://library_user:library_password@db:5432/library_db
REDIS_URL=redis://redis:6379/0
```

## 🔧 Common Issues

### Issue: Module not found
**Solution:**
```powershell
pip install -r requirements.txt
```

### Issue: Database error
**Solution:**
```powershell
python -c "from app_new import app, db; app.app_context().push(); db.drop_all(); db.create_all()"
```

### Issue: Port already in use
**Solution:** Change port in `app_new.py`:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

## 📚 API Usage

### Search Books:
```bash
curl http://localhost:5000/api/search?q=python
```

### Get Book Details:
```bash
curl http://localhost:5000/api/books/1
```

### Get Statistics:
```bash
curl http://localhost:5000/api/stats
```

## 🎨 Customization

### Change Library Name:
Edit `templates/base.html`:
```html
<a class="navbar-brand" href="/">Your Library Name</a>
```

### Change Colors:
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #your-color;
}
```

### Add Categories:
1. Login as admin
2. Admin Panel → Categories
3. Add new category

## 📱 Mobile App (API)

Use the RESTful API for mobile apps:
- Base URL: `http://your-domain.com/api`
- Authentication: Session-based
- Format: JSON

## 🆘 Support

- GitHub Issues: [Report Bug](https://github.com/KUMARG0605/LIbrary-management/issues)
- Email: info@library.com

## 📄 License

MIT License - Free to use and modify

---

**Happy Learning! 📚**
