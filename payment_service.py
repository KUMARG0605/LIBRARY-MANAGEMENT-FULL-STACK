"""
Payment Gateway Integration
Supports Razorpay, PhonePe, Google Pay, UPI
"""

import razorpay
import hashlib
import json
import uuid
from flask import current_app, url_for
from models import db, Payment
from datetime import datetime


class PaymentGateway:
    """Base payment gateway class"""
    
    def __init__(self):
        self.razorpay_client = None
        self.initialize_razorpay()
    
    def initialize_razorpay(self):
        """Initialize Razorpay client"""
        try:
            key_id = current_app.config.get('RAZORPAY_KEY_ID')
            key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
            if key_id and key_secret:
                self.razorpay_client = razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            print(f"Razorpay initialization error: {str(e)}")
    
    def create_order(self, amount, currency='INR', purpose='subscription', user_id=None, reference_id=None):
        """
        Create a payment order
        
        Args:
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            purpose: Payment purpose
            user_id: User ID
            reference_id: Reference ID (subscription_id, borrowing_id, etc.)
        
        Returns:
            dict: Order details
        """
        try:
            # Convert amount to paise (smallest currency unit)
            amount_paise = int(amount * 100)
            
            # Create Razorpay order
            order_data = {
                'amount': amount_paise,
                'currency': currency,
                'payment_capture': 1,  # Auto capture
                'notes': {
                    'purpose': purpose,
                    'user_id': str(user_id) if user_id else '',
                    'reference_id': str(reference_id) if reference_id else ''
                }
            }
            
            razorpay_order = self.razorpay_client.order.create(data=order_data)
            
            # Create payment record in database
            transaction_id = str(uuid.uuid4())
            payment = Payment(
                user_id=user_id,
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                payment_method='razorpay',
                payment_gateway='razorpay',
                purpose=purpose,
                reference_id=reference_id,
                status='pending',
                gateway_response=json.dumps(razorpay_order)
            )
            db.session.add(payment)
            db.session.commit()
            
            return {
                'success': True,
                'order_id': razorpay_order['id'],
                'transaction_id': transaction_id,
                'amount': amount,
                'currency': currency,
                'key_id': current_app.config.get('RAZORPAY_KEY_ID')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify Razorpay payment signature
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay
        
        Returns:
            bool: True if signature is valid
        """
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.razorpay_client.utility.verify_payment_signature(params_dict)
            return True
        
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def update_payment_status(self, transaction_id, status, gateway_response=None):
        """Update payment status in database"""
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if payment:
            payment.status = status
            if gateway_response:
                payment.gateway_response = json.dumps(gateway_response)
            if status == 'success':
                payment.sent_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def get_payment(self, transaction_id):
        """Get payment details"""
        return Payment.query.filter_by(transaction_id=transaction_id).first()
    
    def refund_payment(self, payment_id, amount=None):
        """
        Refund a payment
        
        Args:
            payment_id: Payment ID
            amount: Refund amount (if None, full refund)
        
        Returns:
            dict: Refund details
        """
        try:
            payment = Payment.query.filter_by(transaction_id=payment_id).first()
            if not payment:
                return {'success': False, 'error': 'Payment not found'}
            
            gateway_data = json.loads(payment.gateway_response)
            razorpay_payment_id = gateway_data.get('id')
            
            if not razorpay_payment_id:
                return {'success': False, 'error': 'Payment ID not found'}
            
            refund_amount = int((amount or payment.amount) * 100)
            refund = self.razorpay_client.payment.refund(
                razorpay_payment_id,
                {'amount': refund_amount}
            )
            
            payment.status = 'refunded'
            payment.gateway_response = json.dumps(refund)
            db.session.commit()
            
            return {
                'success': True,
                'refund_id': refund['id'],
                'amount': refund['amount'] / 100
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class UPIPayment:
    """Handle UPI payments (PhonePe, GPay, etc.)"""
    
    @staticmethod
    def generate_upi_link(amount, upi_id, name, transaction_note='Library Payment'):
        """
        Generate UPI payment link
        
        Args:
            amount: Amount in rupees
            upi_id: UPI ID of receiver
            name: Receiver name
            transaction_note: Payment note
        
        Returns:
            str: UPI payment link
        """
        upi_link = (
            f"upi://pay?pa={upi_id}"
            f"&pn={name.replace(' ', '%20')}"
            f"&am={amount}"
            f"&cu=INR"
            f"&tn={transaction_note.replace(' ', '%20')}"
        )
        return upi_link
    
    @staticmethod
    def generate_phonepe_link(amount, merchant_id, transaction_id):
        """
        Generate PhonePe payment link
        
        Args:
            amount: Amount in rupees
            merchant_id: PhonePe merchant ID
            transaction_id: Unique transaction ID
        
        Returns:
            str: PhonePe payment URL
        """
        # PhonePe payment link format
        phonepe_url = (
            f"phonepe://pay?pa={merchant_id}@ybl"
            f"&pn=Digital%20Learning%20Library"
            f"&am={amount}"
            f"&cu=INR"
            f"&tn=Transaction%20{transaction_id}"
        )
        return phonepe_url
    
    @staticmethod
    def generate_gpay_link(amount, upi_id, name, transaction_note='Library Payment'):
        """
        Generate Google Pay link
        
        Args:
            amount: Amount in rupees
            upi_id: UPI ID of receiver
            name: Receiver name
            transaction_note: Payment note
        
        Returns:
            str: Google Pay payment link
        """
        gpay_url = (
            f"gpay://upi/pay?pa={upi_id}"
            f"&pn={name.replace(' ', '%20')}"
            f"&am={amount}"
            f"&cu=INR"
            f"&tn={transaction_note.replace(' ', '%20')}"
        )
        return gpay_url
    
    @staticmethod
    def create_upi_qr_code(amount, upi_id, name, transaction_note='Library Payment'):
        """
        Generate data for UPI QR code
        
        Args:
            amount: Amount in rupees
            upi_id: UPI ID of receiver
            name: Receiver name
            transaction_note: Payment note
        
        Returns:
            str: UPI string for QR code generation
        """
        upi_string = (
            f"upi://pay?pa={upi_id}"
            f"&pn={name}"
            f"&am={amount}"
            f"&cu=INR"
            f"&tn={transaction_note}"
        )
        return upi_string


def process_subscription_payment(user_id, plan_id, duration_months):
    """
    Process subscription payment
    
    Args:
        user_id: User ID
        plan_id: Subscription plan ID
        duration_months: Subscription duration
    
    Returns:
        dict: Payment order details
    """
    from models import SubscriptionPlan
    
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return {'success': False, 'error': 'Invalid subscription plan'}
    
    # Calculate amount based on duration
    if duration_months == 12:
        amount = plan.price_yearly
    else:
        amount = plan.price_monthly * duration_months
    
    gateway = PaymentGateway()
    order = gateway.create_order(
        amount=amount,
        purpose='subscription',
        user_id=user_id,
        reference_id=f'plan_{plan_id}'
    )
    
    return order


def process_fine_payment(user_id, borrowing_id, fine_amount):
    """
    Process fine payment
    
    Args:
        user_id: User ID
        borrowing_id: Borrowing ID
        fine_amount: Fine amount
    
    Returns:
        dict: Payment order details
    """
    gateway = PaymentGateway()
    order = gateway.create_order(
        amount=fine_amount,
        purpose='fine',
        user_id=user_id,
        reference_id=f'borrowing_{borrowing_id}'
    )
    
    return order


def verify_and_complete_payment(transaction_id, razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify payment and complete the transaction
    
    Args:
        transaction_id: Our transaction ID
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: Razorpay signature
    
    Returns:
        dict: Verification result
    """
    gateway = PaymentGateway()
    
    # Verify signature
    is_valid = gateway.verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    
    if is_valid:
        # Update payment status
        gateway.update_payment_status(
            transaction_id,
            'success',
            {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id
            }
        )
        
        # Get payment details
        payment = gateway.get_payment(transaction_id)
        
        # Process based on purpose
        if payment.purpose == 'subscription':
            from models import User, Subscription, SubscriptionPlan
            from datetime import timedelta
            
            user = User.query.get(payment.user_id)
            plan_id = int(payment.reference_id.split('_')[1])
            plan = SubscriptionPlan.query.get(plan_id)
            
            # Create or update subscription
            if user.subscription:
                subscription = user.subscription
                subscription.plan_id = plan_id
                subscription.end_date = datetime.utcnow() + timedelta(days=30 * payment.amount)
            else:
                subscription = Subscription(
                    user_id=user.id,
                    plan_id=plan_id,
                    end_date=datetime.utcnow() + timedelta(days=30 * payment.amount),
                    duration_months=12 if payment.amount == plan.price_yearly else 1,
                    amount_paid=payment.amount,
                    payment_id=razorpay_payment_id
                )
                db.session.add(subscription)
            
            db.session.commit()
            
            # Send confirmation email
            from email_service import send_subscription_confirmation
            send_subscription_confirmation(user, subscription, razorpay_payment_id)
        
        elif payment.purpose == 'fine':
            from models import Borrowing
            
            borrowing_id = int(payment.reference_id.split('_')[1])
            borrowing = Borrowing.query.get(borrowing_id)
            if borrowing:
                borrowing.fine_paid = True
                borrowing.fine_amount = payment.amount
                db.session.commit()
        
        # Send payment receipt
        from email_service import send_payment_receipt
        from models import User
        user = User.query.get(payment.user_id)
        send_payment_receipt(user, payment)
        
        return {
            'success': True,
            'message': 'Payment verified successfully',
            'payment': payment
        }
    
    else:
        gateway.update_payment_status(transaction_id, 'failed')
        return {
            'success': False,
            'message': 'Payment verification failed'
        }
