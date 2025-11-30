"""
Test Email Configuration
Sends a test email to verify Gmail SMTP setup
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

# Create test Flask app
app = Flask(__name__)

# Configure email
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@library.com')

# Initialize mail
mail = Mail(app)

def test_email():
    """Send a test email"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    
    print(f"\nMail Server: {app.config['MAIL_SERVER']}")
    print(f"Mail Port: {app.config['MAIL_PORT']}")
    print(f"Use TLS: {app.config['MAIL_USE_TLS']}")
    print(f"Username: {app.config['MAIL_USERNAME']}")
    print(f"Password: {'*' * len(str(app.config['MAIL_PASSWORD'])) if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
    print(f"Default Sender: {app.config['MAIL_DEFAULT_SENDER']}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n❌ ERROR: Email credentials not configured!")
        print("Please set MAIL_USERNAME and MAIL_PASSWORD in .env file")
        return False
    
    print("\n📧 Sending test email...")
    
    try:
        with app.app_context():
            msg = Message(
                subject="Test Email - Library Management System",
                recipients=[app.config['MAIL_USERNAME']],  # Send to yourself
                body="""
Hello!

This is a test email from your Library Management System.

If you received this email, your email configuration is working correctly! ✅

Email Details:
- Server: smtp.gmail.com
- Port: 587
- TLS: Enabled
- From: bothackerr03@gmail.com

You can now send:
✓ Welcome emails to new users
✓ Book borrowing confirmations
✓ Due date reminders
✓ Overdue notices
✓ Password reset emails
✓ Announcements

Best regards,
Digital Learning Library Team
                """,
                html=f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #141438; border-bottom: 3px solid #007bff; padding-bottom: 10px;">
                            📧 Test Email - Library Management System
                        </h2>
                        
                        <p style="color: #333; font-size: 16px; line-height: 1.6;">Hello!</p>
                        
                        <p style="color: #333; font-size: 16px; line-height: 1.6;">
                            This is a test email from your <strong>Library Management System</strong>.
                        </p>
                        
                        <div style="background: #e8f5e9; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 5px;">
                            <p style="color: #28a745; font-weight: bold; margin: 0;">
                                ✅ Email Configuration Working!
                            </p>
                            <p style="color: #333; margin: 10px 0 0 0;">
                                If you received this email, your email setup is correct.
                            </p>
                        </div>
                        
                        <h3 style="color: #141438; margin-top: 30px;">📋 Email Details:</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li><strong>Server:</strong> smtp.gmail.com</li>
                            <li><strong>Port:</strong> 587</li>
                            <li><strong>TLS:</strong> Enabled</li>
                            <li><strong>From:</strong> {app.config['MAIL_USERNAME']}</li>
                        </ul>
                        
                        <h3 style="color: #141438; margin-top: 30px;">✨ What You Can Send:</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>✓ Welcome emails to new users</li>
                            <li>✓ Book borrowing confirmations</li>
                            <li>✓ Due date reminders</li>
                            <li>✓ Overdue notices</li>
                            <li>✓ Password reset emails</li>
                            <li>✓ Announcements</li>
                        </ul>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 14px; text-align: center; margin: 0;">
                            Digital Learning Library<br>
                            3-4, Police Station Road<br>
                            +91 9392513416
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            
            mail.send(msg)
            print("✅ Email sent successfully!")
            print(f"✉️ Check your inbox at: {app.config['MAIL_USERNAME']}")
            print("\n" + "="*60)
            return True
            
    except Exception as e:
        print(f"\n❌ Failed to send email: {str(e)}")
        print("\nCommon issues:")
        print("1. App Password incorrect - Generate new one from Google Account")
        print("2. 2-Factor Authentication not enabled on Gmail")
        print("3. 'Less secure app access' needs to be enabled (for older accounts)")
        print("4. Check if Gmail is blocking the login attempt")
        print("\n" + "="*60)
        return False

if __name__ == '__main__':
    test_email()
