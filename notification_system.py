# WhatsApp & SMS Integration for Customer Communication

import requests
import json
from datetime import datetime, timedelta

class NotificationManager:
    def __init__(self):
        # You can integrate with services like:
        # - Twilio for SMS/WhatsApp
        # - WhatsApp Business API
        # - MSG91 for Indian SMS
        self.whatsapp_api_url = "https://api.whatsapp.com/send"
        self.sms_api_url = "YOUR_SMS_PROVIDER_API"
        
    def send_whatsapp_message(self, phone, message):
        """Send WhatsApp message to customer"""
        # Format phone number (remove +91, spaces, etc.)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('91'):
            clean_phone = clean_phone[2:]
        
        whatsapp_url = f"https://wa.me/91{clean_phone}?text={message}"
        return whatsapp_url
    
    def send_payment_reminder(self, transaction, days_until_due):
        """Send payment reminder to customer"""
        customer = transaction.customer
        message = self.generate_payment_reminder_message(transaction, days_until_due)
        
        # Return WhatsApp link for manual sending
        return self.send_whatsapp_message(customer.phone, message)
    
    def generate_payment_reminder_message(self, transaction, days_until_due):
        """Generate payment reminder message"""
        if days_until_due > 0:
            message = f"""
🔔 *Payment Reminder*

Dear {transaction.customer.name},

Your Girvi payment is due in {days_until_due} days.

📋 *Details:*
• Transaction: {transaction.transaction_number}
• Amount: ₹{transaction.amount:,.2f}
• Due Date: {transaction.end_date.strftime('%d/%m/%Y')}

Please visit our shop to make the payment.

📍 Address: [Shop Address]
📞 Phone: [Shop Phone]

Thank you!
            """.strip()
        else:
            overdue_days = abs(days_until_due)
            message = f"""
⚠️ *URGENT: Payment Overdue*

Dear {transaction.customer.name},

Your Girvi payment is overdue by {overdue_days} days.

📋 *Details:*
• Transaction: {transaction.transaction_number}
• Amount: ₹{transaction.amount:,.2f}
• Due Date: {transaction.end_date.strftime('%d/%m/%Y')}

Please visit our shop immediately to avoid penalties.

📍 Address: [Shop Address]
📞 Phone: [Shop Phone]
            """.strip()
        
        return message
    
    def generate_receipt_message(self, payment):
        """Generate payment receipt message"""
        transaction = payment.transaction
        message = f"""
✅ *Payment Received*

Dear {transaction.customer.name},

We have received your payment. Thank you!

📋 *Receipt Details:*
• Receipt No: {payment.receipt_number}
• Amount Paid: ₹{payment.amount:,.2f}
• Date: {payment.payment_date.strftime('%d/%m/%Y')}
• Transaction: {transaction.transaction_number}

Visit our shop for any queries.
📞 Phone: [Shop Phone]
        """.strip()
        
        return message

# Add these routes to app.py
@app.route('/send-reminder/<int:transaction_id>')
@shop_profile_required
def send_payment_reminder(transaction_id):
    """Send payment reminder via WhatsApp"""
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    
    notification_manager = NotificationManager()
    today = datetime.utcnow().date()
    due_date = transaction.end_date.date()
    days_until_due = (due_date - today).days
    
    whatsapp_url = notification_manager.send_payment_reminder(transaction, days_until_due)
    
    # Log the reminder
    # You can add a RemindersLog table to track sent reminders
    
    flash(f'Reminder prepared for {transaction.customer.name}')
    return redirect(whatsapp_url)

@app.route('/send-receipt/<int:payment_id>')
@shop_profile_required
def send_payment_receipt(payment_id):
    """Send payment receipt via WhatsApp"""
    payment = db.session.get(Payment, payment_id)
    if not payment:
        flash('Payment not found.')
        return redirect(url_for('dashboard'))
    
    notification_manager = NotificationManager()
    message = notification_manager.generate_receipt_message(payment)
    whatsapp_url = notification_manager.send_whatsapp_message(payment.transaction.customer.phone, message)
    
    flash(f'Receipt sent to {payment.transaction.customer.name}')
    return redirect(whatsapp_url)

# Bulk Reminder System
@app.route('/bulk-reminders')
@shop_profile_required
def bulk_reminders():
    """Send bulk payment reminders"""
    today = datetime.utcnow()
    next_week = today + timedelta(days=7)
    
    # Get transactions due in next 7 days
    upcoming_due = Transaction.query.filter(
        Transaction.status == 'active',
        Transaction.end_date >= today,
        Transaction.end_date <= next_week
    ).all()
    
    # Get overdue transactions
    overdue = Transaction.query.filter(
        Transaction.status == 'active',
        Transaction.end_date < today
    ).all()
    
    notification_manager = NotificationManager()
    reminder_links = []
    
    for transaction in upcoming_due + overdue:
        days_until_due = (transaction.end_date.date() - today.date()).days
        whatsapp_url = notification_manager.send_payment_reminder(transaction, days_until_due)
        reminder_links.append({
            'customer': transaction.customer.name,
            'phone': transaction.customer.phone,
            'whatsapp_url': whatsapp_url,
            'days_until_due': days_until_due
        })
    
    return render_template('bulk_reminders.html', reminder_links=reminder_links)

# Auto-reminder scheduler (you can set this up with a cron job)
def daily_reminder_check():
    """Run this daily to check for due payments"""
    today = datetime.utcnow()
    reminder_dates = [
        today + timedelta(days=7),  # 7 days before
        today + timedelta(days=3),  # 3 days before
        today + timedelta(days=1),  # 1 day before
        today,                      # Due today
    ]
    
    for reminder_date in reminder_dates:
        transactions = Transaction.query.filter(
            Transaction.status == 'active',
            db.func.date(Transaction.end_date) == reminder_date.date()
        ).all()
        
        for transaction in transactions:
            # Send automatic reminder
            # You can implement this with background tasks
            pass

# Festival/Special Occasion Messages
def send_festival_greetings():
    """Send festival greetings to all customers"""
    customers = Customer.query.all()
    message = """
🎉 *Festival Greetings*

Wishing you and your family a very Happy [Festival Name]!

May this auspicious occasion bring prosperity and happiness to your life.

Thank you for trusting us with your precious jewelry.

Best Regards,
[Shop Name]
📞 [Phone Number]
    """.strip()
    
    links = []
    notification_manager = NotificationManager()
    
    for customer in customers:
        whatsapp_url = notification_manager.send_whatsapp_message(customer.phone, message)
        links.append({
            'customer': customer.name,
            'phone': customer.phone,
            'whatsapp_url': whatsapp_url
        })
    
    return links
