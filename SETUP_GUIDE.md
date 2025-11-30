# Library Management System - Setup & Installation Guide

## 🚀 Quick Setup Instructions

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Configure Gmail for Email Service

1. **Enable 2-Step Verification**:
   - Go to https://myaccount.google.com/security
   - Find "2-Step Verification" and turn it ON
   - Follow the setup process

2. **Generate App Password**:
   - After enabling 2-Step Verification
   - Go to https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Windows Computer" or "Other"
   - Click "Generate"
   - **Copy the 16-character password** (it looks like: xxxx xxxx xxxx xxxx)

3. **Update .env file**:
   ```env
   MAIL_USERNAME=bothackerr03@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Paste the app password here
   ```

### Step 3: Setup Razorpay (Optional - for payments)

1. **Create Account**:
   - Visit https://razorpay.com
   - Sign up for free
   - Complete KYC (for production)

2. **Get API Keys**:
   - Go to Settings → API Keys
   - Generate Test Keys (for development)
   - Generate Live Keys (for production)
   - Copy Key ID and Key Secret

3. **Update .env file**:
   ```env
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
   ```

### Step 4: Initialize Database

Run this in PowerShell:
```powershell
python -c "from app_new import app, db; app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### Step 5: Run the Application

```powershell
python app_new.py
```

Access at: http://localhost:5000

## 📧 Email Features Included

All emails are sent from: **bothackerr03@gmail.com**

### Automated Emails:
1. ✅ **Welcome Email** - When user registers
2. ✅ **Email Verification** - To verify new accounts
3. ✅ **Login Alerts** - Security notifications for new logins
4. ✅ **Password Reset** - Secure password reset links
5. ✅ **Due Date Reminders** - 3 days before due date
6. ✅ **Overdue Notices** - Daily for overdue books with fines
7. ✅ **Reservation Alerts** - When reserved books become available
8. ✅ **Payment Receipts** - For all transactions
9. ✅ **Subscription Confirmations** - Plan activation emails
10. ✅ **Admin Announcements** - Broadcast messages to users

## 💳 Payment Methods Integrated

### Razorpay
- Credit/Debit Cards
- Net Banking
- UPI
- Wallets

### Direct UPI
- PhonePe
- Google Pay
- Paytm
- BHIM

### Features:
- ✅ Secure payment processing
- ✅ Automatic payment verification
- ✅ Email receipts
- ✅ Refund support
- ✅ Transaction history

## 📱 Subscription Plans

### 1. Basic Plan (FREE)
- Borrow 3 books
- 14 days borrowing period
- Limited digital access
- Standard support

### 2. Premium Plan (₹299/month or ₹2999/year)
- Borrow 5 books
- Full digital library access
- Priority reservations
- 3 renewals allowed
- Email notifications
- Save 17% with yearly plan

### 3. VIP Plan (₹599/month or ₹5999/year)
- Borrow 10 books
- Unlimited digital access
- Download books offline
- Priority support
- No late fees
- Early access to new books
- Save 17% with yearly plan

## 📖 Digital Book Reader Features

### Supported Formats:
- PDF files
- EPUB files

### Reader Features:
- ✅ Reading progress auto-save
- ✅ Bookmarks on any page
- ✅ Text highlighting
- ✅ Personal notes
- ✅ Font size control (12px - 24px)
- ✅ Line height adjustment
- ✅ 3 Reading modes: Light, Sepia, Dark
- ✅ Zoom controls (50% - 200%)
- ✅ Keyboard shortcuts
- ✅ Fullscreen mode
- ✅ Table of contents
- ✅ Page navigation
- ✅ Progress bar

### Keyboard Shortcuts:
- `Arrow Right` - Next page
- `Arrow Left` - Previous page
- `F` - Toggle fullscreen

## 🎯 Default Admin Account

```
User ID: ADMIN001
Email: admin@library.com
Password: admin123
```

⚠️ **IMPORTANT**: Change this password immediately after first login!

## 📊 Admin Capabilities

### User Management:
- View all users
- Activate/deactivate accounts
- View user activity
- Send email announcements

### Book Management:
- Add new books (physical + digital)
- Upload book covers
- Upload PDF/EPUB files
- Set book categories
- Manage inventory

### Borrowing Management:
- Track all borrowings
- Process returns
- Calculate fines
- View overdue books
- Generate reports

### Communication:
- Send announcements to all users
- Send to specific departments
- Send to students/faculty separately
- Email templates included

### Analytics:
- Total books count
- Active borrowings
- Total users
- Fine collection
- Popular books
- User activity logs

## 🔧 Configuration Options

Edit `config.py` to customize:

```python
MAX_BORROW_DAYS = 14          # Days a book can be borrowed
MAX_BOOKS_PER_USER = 5        # Maximum books per user
FINE_PER_DAY = 5              # Fine per day (₹)
RESERVATION_EXPIRY_DAYS = 3   # Days to collect reserved book
MAX_RENEWALS = 2              # Maximum renewals allowed
```

## 🐛 Troubleshooting

### Email not sending?
1. Verify 2-Step Verification is enabled
2. Check app password is correct (16 characters)
3. Make sure MAIL_USE_TLS=True
4. Check firewall/antivirus settings

### Database errors?
```powershell
# Reset database
Remove-Item library.db
python -c "from app_new import app, db; app.app_context().push(); db.create_all()"
```

### Port 5000 already in use?
```powershell
# Change port in app_new.py
app.run(debug=True, port=5001)  # Use 5001 instead
```

### Payment gateway not working?
1. Check Razorpay credentials in .env
2. Verify test mode is enabled
3. Check internet connection
4. Review Razorpay dashboard for errors

## 📱 Mobile Responsiveness

The system is fully responsive and works on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1440px+)

## 🔐 Security Features

- ✅ Password hashing with bcrypt
- ✅ CSRF protection on all forms
- ✅ Session security
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure token generation
- ✅ Login activity tracking
- ✅ IP address logging
- ✅ Email verification
- ✅ Password reset with expiry

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Lazy loading of relationships
- Pagination on large datasets
- Static file caching
- Minified CSS/JS in production
- Gzip compression

## 🎨 Customization

### Change Theme Colors:
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #4CAF50;    /* Main green color */
    --secondary-color: #2196F3;  /* Blue accent */
    --danger-color: #f44336;     /* Red for errors */
}
```

### Change Logo/Branding:
Replace files in `static/images/`:
- `logo.png` - Main logo
- `favicon.ico` - Browser icon

### Customize Email Templates:
Edit files in `templates/emails/`:
- Change colors, fonts, layout
- Add your logo
- Modify text content

## 📞 Support & Contact

- **Email**: bothackerr03@gmail.com
- **GitHub**: https://github.com/KUMARG0605/LIbrary-management
- **Issues**: Create issue on GitHub repository

## 🚀 Deployment to Production

### Heroku:
```powershell
heroku create your-library-app
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set FLASK_ENV=production
git push heroku main
```

### Railway:
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Docker:
```powershell
docker-compose up -d --build
```

## ✅ Checklist Before Going Live

- [ ] Changed admin password
- [ ] Set strong SECRET_KEY
- [ ] Configured production database (PostgreSQL)
- [ ] Set up Gmail app password
- [ ] Configured Razorpay with live keys
- [ ] Enabled HTTPS/SSL
- [ ] Set up domain name
- [ ] Configured backups
- [ ] Tested all email features
- [ ] Tested payment gateway
- [ ] Tested book reader
- [ ] Set up monitoring
- [ ] Created user documentation

## 🎓 Learning Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Bootstrap: https://getbootstrap.com/
- Razorpay Docs: https://razorpay.com/docs/

---

**Happy Coding! 🚀**

For any questions or issues, contact: bothackerr03@gmail.com
