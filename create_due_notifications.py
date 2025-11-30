"""
Create notifications for due date reminders and overdue books
Run this script daily via cron job or scheduler
"""

from app_new import app, db
from models import Borrowing, Notification
from datetime import datetime, timedelta
from flask import url_for

def create_due_date_notifications():
    """Create notifications for books due in 3 days and overdue books"""
    with app.app_context():
        today = datetime.utcnow().date()
        three_days_later = today + timedelta(days=3)
        
        # Get active borrowings
        active_borrowings = Borrowing.query.filter_by(status='borrowed').all()
        
        due_soon_count = 0
        overdue_count = 0
        
        for borrowing in active_borrowings:
            due_date = borrowing.due_date.date()
            
            # Check if book is due in 3 days
            if due_date == three_days_later:
                # Check if notification already exists for today
                existing = Notification.query.filter_by(
                    user_id=borrowing.user_id,
                    notification_type='due_reminder',
                    related_id=borrowing.id
                ).filter(
                    Notification.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).first()
                
                if not existing:
                    notification = Notification(
                        user_id=borrowing.user_id,
                        title=f'Book Due Soon: {borrowing.book.title}',
                        message=f'Your book "{borrowing.book.title}" is due in 3 days ({due_date.strftime("%B %d, %Y")}). Please return or renew it on time.',
                        notification_type='due_reminder',
                        related_id=borrowing.id,
                        action_url=f'/user/dashboard'
                    )
                    db.session.add(notification)
                    due_soon_count += 1
            
            # Check if book is overdue
            elif due_date < today:
                # Check if notification already exists for today
                existing = Notification.query.filter_by(
                    user_id=borrowing.user_id,
                    notification_type='overdue',
                    related_id=borrowing.id
                ).filter(
                    Notification.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).first()
                
                if not existing:
                    days_overdue = (today - due_date).days
                    fine = borrowing.calculate_fine()
                    notification = Notification(
                        user_id=borrowing.user_id,
                        title=f'Overdue: {borrowing.book.title}',
                        message=f'Your book "{borrowing.book.title}" is {days_overdue} day(s) overdue. Current fine: ₹{fine}. Please return it immediately.',
                        notification_type='overdue',
                        related_id=borrowing.id,
                        action_url=f'/user/dashboard'
                    )
                    db.session.add(notification)
                    overdue_count += 1
        
        db.session.commit()
        
        print(f"✅ Notifications created:")
        print(f"   - Due soon reminders: {due_soon_count}")
        print(f"   - Overdue notices: {overdue_count}")
        print(f"   - Total: {due_soon_count + overdue_count}")

if __name__ == '__main__':
    create_due_date_notifications()
