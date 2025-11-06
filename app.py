from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import and_
import jwt
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)

# Database configuration - supports both SQLite (local) and PostgreSQL (Heroku)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Heroku provides postgres://, but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///girvi.db'

# Use environment variables for secrets in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '38a0b87477399b6e88676dd3da2508e76d7ff07c56597b6d24f4f3a13a40f1bd')

db = SQLAlchemy(app)

# Enable CORS for API routes (adjust origins as needed)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', app.config['SECRET_KEY'])
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_MINUTES = int(os.environ.get('JWT_EXPIRY_MINUTES', '1440'))  # 24h default

def generate_jwt(user_id, username, role):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'username': username,
        'role': role,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=JWT_EXPIRY_MINUTES)).timestamp())
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # pyjwt>=2 returns str, but ensure str
    return token if isinstance(token, str) else token.decode('utf-8')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = int(payload.get('sub'))
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 401
            request.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin, staff
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    shop_profile_completed = db.Column(db.Boolean, default=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    shop_profile = db.relationship('ShopProfile', backref='user', uselist=False, lazy=True)

    def __init__(self, username, email, password, role='staff', created_at=None, shop_profile_completed=False):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at or datetime.now(timezone.utc)
        self.shop_profile_completed = shop_profile_completed

class ShopProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shop_name = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    gstin = db.Column(db.String(15))  # GST number
    license_number = db.Column(db.String(50))  # Business license
    logo_filename = db.Column(db.String(200))  # Logo file
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, user_id, shop_name, owner_name, address_line1, city, state, pincode, phone, address_line2='', email='', gstin='', license_number='', logo_filename=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.shop_name = shop_name
        self.owner_name = owner_name
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.pincode = pincode
        self.phone = phone
        self.email = email
        self.gstin = gstin
        self.license_number = license_number
        self.logo_filename = logo_filename
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    id_proof_type = db.Column(db.String(50))  # Aadhar, PAN, etc.
    id_proof_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    transactions = db.relationship('Transaction', backref='customer', lazy=True)

    def __init__(self, user_id, name, phone, email='', address='', id_proof_type='', id_proof_number='', created_at=None):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.id_proof_type = id_proof_type
        self.id_proof_number = id_proof_number
        self.created_at = created_at or datetime.now(timezone.utc)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Gold, Diamond, Gemstone, etc.
    weight = db.Column(db.Float)  # in grams
    purity = db.Column(db.String(50))  # 24K, 22K, etc.
    estimated_value = db.Column(db.Float)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    images = db.relationship('ItemImage', backref='item', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, transaction_id, description='', category='', weight=None, purity='', estimated_value=None):
        self.name = name
        self.description = description
        self.category = category
        self.weight = weight
        self.purity = purity
        self.estimated_value = estimated_value
        self.transaction_id = transaction_id

class ItemImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def __init__(self, filename, item_id):
        self.filename = filename
        self.item_id = item_id

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, closed, defaulted
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    items = db.relationship('Item', backref='transaction', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='transaction', lazy=True, cascade="all, delete-orphan")

    def __init__(self, transaction_number, customer_id, user_id, amount, interest_rate, duration_months, start_date=None, end_date=None, status='active', notes='', created_at=None):
        self.transaction_number = transaction_number
        self.customer_id = customer_id
        self.user_id = user_id
        self.amount = amount
        self.interest_rate = interest_rate
        self.duration_months = duration_months
        self.start_date = start_date or datetime.now(timezone.utc)
        self.end_date = end_date
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now(timezone.utc)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20))  # interest, principal, penalty, recovery
    payment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    receipt_number = db.Column(db.String(50), unique=True)
    notes = db.Column(db.Text)

    def __init__(self, transaction_id, amount, payment_type='', payment_date=None, receipt_number=None, notes=''):
        self.transaction_id = transaction_id
        self.amount = amount
        self.payment_type = payment_type
        self.payment_date = payment_date or datetime.now(timezone.utc)
        self.receipt_number = receipt_number
        self.notes = notes

class ItemStatus(db.Model):
    """Track status changes of jewelry items"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # pledged, released, auctioned, sold
    status_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, item_id, status, status_date=None, notes='', created_by=None):
        self.item_id = item_id
        self.status = status
        self.status_date = status_date or datetime.now(timezone.utc)
        self.notes = notes
        self.created_by = created_by

class AuctionItem(db.Model):
    """Items that go to auction after default"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    auction_date = db.Column(db.DateTime)
    reserve_price = db.Column(db.Float)  # Minimum price
    final_price = db.Column(db.Float)    # Sold price
    buyer_name = db.Column(db.String(100))
    buyer_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')  # pending, sold, unsold
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, item_id, transaction_id, auction_date=None, reserve_price=None, final_price=None, buyer_name='', buyer_phone='', status='pending', created_at=None):
        self.item_id = item_id
        self.transaction_id = transaction_id
        self.auction_date = auction_date
        self.reserve_price = reserve_price
        self.final_price = final_price
        self.buyer_name = buyer_name
        self.buyer_phone = buyer_phone
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)

class BusinessAlert(db.Model):
    """System alerts for business management"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # payment_due, overdue, high_value
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    is_read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, user_id, alert_type, title, message, priority='medium', is_read=False, action_url=None, created_at=None):
        self.user_id = user_id
        self.alert_type = alert_type
        self.title = title
        self.message = message
        self.priority = priority
        self.is_read = is_read
        self.action_url = action_url
        self.created_at = created_at or datetime.now(timezone.utc)

class NotificationLog(db.Model):
    """Track sent notifications"""
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    notification_type = db.Column(db.String(50))  # reminder, receipt, greeting
    message = db.Column(db.Text)
    sent_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sent_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, transaction_id=None, customer_id=None, notification_type='', message='', sent_date=None, sent_by=None):
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.notification_type = notification_type
        self.message = message
        self.sent_date = sent_date or datetime.now(timezone.utc)
        self.sent_by = sent_by

# --- Gemstone Management ---
# (REMOVE THE GEMSTONE MODEL)

# Shop Profile Check Decorator
def shop_profile_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = db.session.get(User, session['user_id'])
        if user and not user.shop_profile_completed:
            flash('Please complete your shop profile first.')
            return redirect(url_for('shop_profile_setup'))
        
        return f(*args, **kwargs)
    return decorated_function

# Utility Functions
def calculate_smart_interest(principal, rate, start_date, end_date=None):
    """Calculate interest with different compounding methods"""
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    
    days = (end_date - start_date).days
    
    # Simple Interest (most common for girvi)
    simple_interest = (principal * rate * days) / (100 * 365)
    
    # Compound Interest (monthly)
    months = days / 30
    compound_interest = principal * ((1 + rate/1200) ** months) - principal
    
    # Penalty calculation for overdue
    penalty = 0
    if days > 365:  # If loan is more than 1 year old
        overdue_days = days - 365
        penalty = (principal * 2 / 100) * (overdue_days / 30)  # 2% per month penalty
    
    return {
        'simple_interest': round(simple_interest, 2),
        'compound_interest': round(compound_interest, 2),
        'penalty': round(penalty, 2),
        'total_simple': round(principal + simple_interest + penalty, 2),
        'total_compound': round(principal + compound_interest + penalty, 2),
        'days': days
    }

def estimate_gold_value(weight, purity, current_price_24k):
    """Estimate gold item value based on current market price"""
    purity_factors = {
        '24k': 1.0, '22k': 0.916, '20k': 0.833, '18k': 0.750,
        '16k': 0.666, '14k': 0.583, '12k': 0.500, '10k': 0.416
    }
    
    factor = purity_factors.get(purity.lower(), 0.916)  # Default to 22k
    estimated_value = weight * current_price_24k * factor * 0.85  # 85% of market value
    
    return round(estimated_value, 2)

class NotificationManager:
    def __init__(self):
        self.whatsapp_api_url = "https://api.whatsapp.com/send"
        
    def send_whatsapp_message(self, phone, message):
        """Send WhatsApp message to customer"""
        # Format phone number (remove +91, spaces, etc.)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('91'):
            clean_phone = clean_phone[2:]
        
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/91{clean_phone}?text={encoded_message}"
        return whatsapp_url
    
    def generate_payment_reminder_message(self, transaction, days_until_due, shop_profile):
        """Generate payment reminder message"""
        if days_until_due > 0:
            message = f"""🔔 *Payment Reminder*

Dear {transaction.customer.name},

Your Girvi payment is due in {days_until_due} days.

📋 *Details:*
• Transaction: {transaction.transaction_number}
• Amount: ₹{transaction.amount:,.2f}
• Due Date: {transaction.end_date.strftime('%d/%m/%Y')}

Please visit our shop to make the payment.

📍 {shop_profile.shop_name}
{shop_profile.address_line1}, {shop_profile.city}
📞 {shop_profile.phone}

Thank you!"""
        else:
            overdue_days = abs(days_until_due)
            message = f"""⚠️ *URGENT: Payment Overdue*

Dear {transaction.customer.name},

Your Girvi payment is overdue by {overdue_days} days.

📋 *Details:*
• Transaction: {transaction.transaction_number}
• Amount: ₹{transaction.amount:,.2f}
• Due Date: {transaction.end_date.strftime('%d/%m/%Y')}

Please visit our shop immediately to avoid penalties.

📍 {shop_profile.shop_name}
{shop_profile.address_line1}, {shop_profile.city}
📞 {shop_profile.phone}"""
        
        return message
    
    def generate_receipt_message(self, payment, shop_profile):
        """Generate payment receipt message"""
        transaction = payment.transaction
        message = f"""✅ *Payment Received*

Dear {transaction.customer.name},

We have received your payment. Thank you!

📋 *Receipt Details:*
• Receipt No: {payment.receipt_number}
• Amount Paid: ₹{payment.amount:,.2f}
• Date: {payment.payment_date.strftime('%d/%m/%Y')}
• Transaction: {transaction.transaction_number}

Visit our shop for any queries.
📞 {shop_profile.phone}

{shop_profile.shop_name}"""
        
        return message

# Alert Management
def create_alert(user_id, alert_type, title, message, priority='medium', action_url=None):
    """Create a new business alert"""
    alert = BusinessAlert(
        user_id=user_id,
        alert_type=alert_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url
    )
    db.session.add(alert)
    db.session.commit()
    return alert

def generate_daily_alerts():
    """Generate daily alerts for all users"""
    users = User.query.filter_by(shop_profile_completed=True).all()
    
    for user in users:
        today = datetime.now(timezone.utc)
        
        # Check for upcoming due payments
        next_week = today + timedelta(days=7)
        if user and user.id:
            upcoming_due_query = Transaction.query.filter(
                Transaction.user_id == user.id,
                Transaction.status == 'active',
                Transaction.end_date != None
            )
            upcoming_due = upcoming_due_query.filter(
                Transaction.end_date >= today,
                Transaction.end_date <= next_week
            ).count()
        else:
            upcoming_due = 0
        
        if upcoming_due > 0:
            create_alert(
                user.id,
                'payment_due',
                f'{upcoming_due} Payments Due This Week',
                f'You have {upcoming_due} transactions with payments due in the next 7 days.',
                'medium',
                '/dashboard'
            )
        
        # Check for overdue payments
        if user and user.id:
            overdue_query = Transaction.query.filter(
                Transaction.user_id == user.id,
                Transaction.status == 'active',
                Transaction.end_date != None
            )
            overdue = overdue_query.filter(
                Transaction.end_date < today
            ).count()
        else:
            overdue = 0
        
        if overdue > 0:
            create_alert(
                user.id,
                'overdue',
                f'{overdue} Overdue Payments',
                f'You have {overdue} transactions that are overdue and need attention.',
                'high',
                '/dashboard'
            )
        
        # Check for high-value transactions
        if user and user.id:
            high_value = Transaction.query.filter(
                Transaction.user_id == user.id,
                Transaction.status == 'active',
                Transaction.amount != None,
                Transaction.amount > 100000
            ).count()
        else:
            high_value = 0
        
        if high_value > 0:
            create_alert(
                user.id,
                'high_value',
                f'{high_value} High-Value Transactions',
                f'You have {high_value} active transactions above ₹1,00,000.',
                'low',
                '/inventory'
            )

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Logged in successfully!')
            
            # Check if shop profile is completed
            if not user.shop_profile_completed:
                return redirect(url_for('shop_profile_setup'))
            
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/shop-profile-setup', methods=['GET', 'POST'])
def shop_profile_setup():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # If profile already completed, redirect to edit
    if user.shop_profile_completed:
        return redirect(url_for('shop_profile_edit'))
    
    if request.method == 'POST':
        # Create new shop profile
        shop_profile = ShopProfile(
            user_id=user.id,
            shop_name=request.form['shop_name'],
            owner_name=request.form['owner_name'],
            address_line1=request.form['address_line1'],
            address_line2=request.form.get('address_line2', ''),
            city=request.form['city'],
            state=request.form['state'],
            pincode=request.form['pincode'],
            phone=request.form['phone'],
            email=request.form.get('email', ''),
            gstin=request.form.get('gstin', ''),
            license_number=request.form.get('license_number', '')
        )
        
        # Mark profile as completed
        user.shop_profile_completed = True
        
        db.session.add(shop_profile)
        db.session.commit()
        
        flash('Shop profile created successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('shop_profile_setup.html', user=user)

@app.route('/shop-profile-edit', methods=['GET', 'POST'])
def shop_profile_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user or not user.shop_profile_completed:
        return redirect(url_for('shop_profile_setup'))
    shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        flash('Shop profile not found. Please set up your shop profile.')
        return redirect(url_for('shop_profile_setup'))
    if request.method == 'POST':
        shop_profile.shop_name = request.form['shop_name']
        shop_profile.owner_name = request.form['owner_name']
        shop_profile.address_line1 = request.form['address_line1']
        shop_profile.address_line2 = request.form.get('address_line2', '')
        shop_profile.city = request.form['city']
        shop_profile.state = request.form['state']
        shop_profile.pincode = request.form['pincode']
        shop_profile.phone = request.form['phone']
        shop_profile.email = request.form.get('email', '')
        shop_profile.gstin = request.form.get('gstin', '')
        shop_profile.license_number = request.form.get('license_number', '')
        shop_profile.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash('Shop profile updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('shop_profile_edit.html', user=user, shop_profile=shop_profile)

@app.route('/dashboard')
@shop_profile_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please login again.')
        return redirect(url_for('login'))
    
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    
    # Calculate summary statistics
    total_transactions = len(transactions)
    active_transactions = len([t for t in transactions if t.status == 'active'])
    total_amount = sum(t.amount for t in transactions)
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Get upcoming payments (next 7 days)
    today = datetime.now(timezone.utc)
    next_week = today + timedelta(days=7)
    upcoming_payments = Payment.query.filter(and_(
        Payment.payment_date >= today,
        Payment.payment_date <= next_week
    )).order_by(Payment.payment_date).all()
    
    return render_template('dashboard.html', 
                          user=user, 
                          transactions=transactions,
                          total_transactions=total_transactions,
                          active_transactions=active_transactions,
                          total_amount=total_amount,
                          recent_transactions=recent_transactions,
                          upcoming_payments=upcoming_payments)

@app.route('/transactions')
@shop_profile_required
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    filter_type = request.args.get('filter', 'all')
    user_id = session['user_id']
    
    # Base query
    base_query = Transaction.query.filter_by(user_id=user_id)
    
    # Apply filters
    if filter_type == 'active':
        transactions = base_query.filter_by(status='active').order_by(Transaction.created_at.desc()).all()
    elif filter_type == 'overdue':
        today = datetime.now(timezone.utc)
        transactions = base_query.filter(and_(
            Transaction.status == 'active',
            Transaction.end_date != None,
            Transaction.end_date < today
        )).order_by(Transaction.end_date).all()
    elif filter_type == 'closed':
        transactions = base_query.filter_by(status='closed').order_by(Transaction.created_at.desc()).all()
    else:
        transactions = base_query.order_by(Transaction.created_at.desc()).all()
    
    # Get counts
    all_count = base_query.count()
    active_count = base_query.filter_by(status='active').count()
    closed_count = base_query.filter_by(status='closed').count()
    today = datetime.now(timezone.utc)
    overdue_count = base_query.filter(and_(
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date < today
    )).count()
    
    return render_template('transactions.html', 
                          transactions=transactions,
                          filter=filter_type,
                          all_count=all_count,
                          active_count=active_count,
                          overdue_count=overdue_count,
                          closed_count=closed_count)

@app.route('/customers')
@shop_profile_required
def customers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customers = Customer.query.filter_by(user_id=session['user_id']).order_by(Customer.name).all()
    return render_template('customers.html', customers=customers)

@app.route('/customer/new', methods=['GET', 'POST'])
@shop_profile_required
def new_customer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        address = request.form.get('address', '')
        id_proof_type = request.form.get('id_proof_type', '')
        id_proof_number = request.form.get('id_proof_number', '')
        
        new_customer = Customer(
            user_id=session['user_id'],
            name=name,
            phone=phone,
            email=email,
            address=address,
            id_proof_type=id_proof_type,
            id_proof_number=id_proof_number
        )
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Customer added successfully!')
        return redirect(url_for('customers'))
    
    return render_template('new_customer.html')

@app.route('/customer/<int:customer_id>')
def customer_details(customer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customer = db.session.get(Customer, customer_id)
    if not customer or customer.user_id != session['user_id']:
        flash('Customer not found.')
        return redirect(url_for('customers'))
    
    transactions = Transaction.query.filter_by(customer_id=customer_id, user_id=session['user_id']).all()
    return render_template('customer_details.html', customer=customer, transactions=transactions)

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
@shop_profile_required
def edit_customer(customer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customer = db.session.get(Customer, customer_id)
    if not customer or customer.user_id != session['user_id']:
        flash('Customer not found.')
        return redirect(url_for('customers'))
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form['phone']
        customer.email = request.form.get('email', '')
        customer.address = request.form.get('address', '')
        customer.id_proof_type = request.form.get('id_proof_type', '')
        customer.id_proof_number = request.form.get('id_proof_number', '')
        
        db.session.commit()
        flash('Customer updated successfully!')
        return redirect(url_for('customer_details', customer_id=customer_id))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
@shop_profile_required
def delete_customer(customer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    customer = db.session.get(Customer, customer_id)
    if not customer or customer.user_id != session['user_id']:
        flash('Customer not found.')
        return redirect(url_for('customers'))
    
    # Check if customer has any transactions
    transactions = Transaction.query.filter_by(customer_id=customer_id, user_id=session['user_id']).all()
    if transactions:
        flash('Cannot delete customer with existing transactions. Please delete or reassign transactions first.', 'error')
        return redirect(url_for('customer_details', customer_id=customer_id))
    
    # Delete the customer
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!')
    return redirect(url_for('customers'))

@app.route('/transaction/new', methods=['GET', 'POST'])
@shop_profile_required
def new_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Check if creating new customer or using existing
        customer_type = request.form.get('customer_type', 'existing')
        
        if customer_type == 'new':
            # Create new customer inline
            new_customer = Customer(
                user_id=session['user_id'],
                name=request.form['new_customer_name'],
                phone=request.form['new_customer_phone'],
                email=request.form.get('new_customer_email', ''),
                address=request.form.get('new_customer_address', ''),
                id_proof_type=request.form.get('new_customer_id_type', ''),
                id_proof_number=request.form.get('new_customer_id_number', '')
            )
            db.session.add(new_customer)
            db.session.flush()  # Get the ID without committing
            customer_id = new_customer.id
        else:
            # Use existing customer
            customer_id = int(request.form['customer_id'])
            # Verify customer belongs to current user
            customer = db.session.get(Customer, customer_id)
            if not customer or customer.user_id != session['user_id']:
                flash('Invalid customer selected.')
                return redirect(url_for('new_transaction'))
        
        amount = float(request.form['amount'])
        interest_rate = float(request.form['interest_rate'])
        duration_months = int(request.form['duration_months'])
        notes = request.form.get('notes', '')
        
        # Generate unique transaction number
        transaction_number = f"TRX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate end date
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=duration_months*30)
        
        new_transaction = Transaction(
            transaction_number=transaction_number,
            customer_id=customer_id,
            user_id=session['user_id'],
            amount=amount,
            interest_rate=interest_rate,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        db.session.add(new_transaction)
        db.session.commit()
        
        # Handle item details
        item_names = request.form.getlist('item_name[]')
        item_descriptions = request.form.getlist('item_description[]')
        item_categories = request.form.getlist('item_category[]')
        item_weights = request.form.getlist('item_weight[]')
        item_purities = request.form.getlist('item_purity[]')
        item_values = request.form.getlist('item_value[]')
        
        for i in range(len(item_names)):
            if item_names[i]:
                new_item = Item(
                    name=item_names[i],
                    description=item_descriptions[i] if i < len(item_descriptions) else '',
                    category=item_categories[i] if i < len(item_categories) else '',
                    weight=float(item_weights[i]) if i < len(item_weights) and item_weights[i] else None,
                    purity=item_purities[i] if i < len(item_purities) else '',
                    estimated_value=float(item_values[i]) if i < len(item_values) and item_values[i] else None,
                    transaction_id=new_transaction.id
                )
                db.session.add(new_item)
        
        db.session.commit()
        
        flash('Transaction created successfully!')
        return redirect(url_for('transaction_details', transaction_id=new_transaction.id))
    
    customers = Customer.query.filter_by(user_id=session['user_id']).order_by(Customer.name).all()
    return render_template('new_transaction.html', customers=customers)

@app.route('/transaction/<int:transaction_id>')
def transaction_details(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    
    customer = db.session.get(Customer, transaction.customer_id)
    items = Item.query.filter_by(transaction_id=transaction_id).all()
    payments = Payment.query.filter_by(transaction_id=transaction_id).order_by(Payment.payment_date).all()
    
    # Calculate interest and total amount
    days_passed = (datetime.now(timezone.utc) - transaction.start_date).days
    interest_amount = (transaction.amount * transaction.interest_rate / 100) * (days_passed / 30)
    total_amount = transaction.amount + interest_amount
    
    # Calculate paid amount
    paid_amount = sum(payment.amount for payment in payments)
    remaining_amount = total_amount - paid_amount
    
    return render_template('transaction_details.html', 
                          transaction=transaction,
                          customer=customer,
                          items=items,
                          payments=payments,
                          interest_amount=interest_amount,
                          total_amount=total_amount,
                          paid_amount=paid_amount,
                          remaining_amount=remaining_amount)

@app.route('/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
@shop_profile_required
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        transaction.amount = float(request.form['amount'])
        transaction.interest_rate = float(request.form['interest_rate'])
        transaction.duration_months = int(request.form['duration_months'])
        transaction.notes = request.form.get('notes', '')
        transaction.status = request.form.get('status', 'active')
        
        # Recalculate end date if duration changed
        if transaction.start_date:
            transaction.end_date = transaction.start_date + timedelta(days=transaction.duration_months*30)
        
        db.session.commit()
        flash('Loan updated successfully!')
        return redirect(url_for('transaction_details', transaction_id=transaction_id))
    
    customers = Customer.query.order_by(Customer.name).all()
    items = Item.query.filter_by(transaction_id=transaction_id).all()
    return render_template('edit_transaction.html', transaction=transaction, customers=customers, items=items)

@app.route('/transaction/<int:transaction_id>/payment', methods=['GET', 'POST'])
def add_payment(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        payment_type = request.form['payment_type']
        payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        notes = request.form.get('notes', '')
        
        # Generate unique receipt number
        receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        new_payment = Payment(
            transaction_id=transaction_id,
            amount=amount,
            payment_type=payment_type,
            payment_date=payment_date,
            receipt_number=receipt_number,
            notes=notes
        )
        db.session.add(new_payment)
        
        # Check if transaction is fully paid
        days_passed = (datetime.now(timezone.utc) - transaction.start_date).days
        interest_amount = (transaction.amount * transaction.interest_rate / 100) * (days_passed / 30)
        total_amount = transaction.amount + interest_amount
        
        payments = Payment.query.filter_by(transaction_id=transaction_id).all()
        paid_amount = sum(payment.amount for payment in payments) + amount
        
        if paid_amount >= total_amount:
            transaction.status = 'closed'
        
        db.session.commit()
        
        flash('Payment recorded successfully!')
        return redirect(url_for('transaction_details', transaction_id=transaction_id))
    
    return render_template('add_payment.html', transaction=transaction)

@app.route('/transaction/<int:transaction_id>/print')
@shop_profile_required
def print_bill(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    user = db.session.get(User, session['user_id'])
    shop_profile = None
    if user:
        shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        flash('Shop profile not found. Please set up your shop profile.')
        return redirect(url_for('shop_profile_setup'))
    customer = db.session.get(Customer, transaction.customer_id)
    items = Item.query.filter_by(transaction_id=transaction_id).all()
    payments = Payment.query.filter_by(transaction_id=transaction_id).order_by(Payment.payment_date).all()
    days_passed = (datetime.now(timezone.utc) - transaction.start_date).days
    interest_amount = (transaction.amount * transaction.interest_rate / 100) * (days_passed / 30)
    total_amount = transaction.amount + interest_amount
    paid_amount = sum(payment.amount for payment in payments)
    remaining_amount = total_amount - paid_amount
    return render_template('print_bill.html',
                          transaction=transaction,
                          customer=customer,
                          items=items,
                          payments=payments,
                          interest_amount=interest_amount,
                          total_amount=total_amount,
                          paid_amount=paid_amount,
                          remaining_amount=remaining_amount,
                          shop_profile=shop_profile)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Logged out successfully!')
    return redirect(url_for('home'))

# API Routes
@app.route('/api/search')
@shop_profile_required
def api_search():
    """API endpoint for quick search"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'customers': [], 'transactions': []})
    
    # Search customers - only current user's customers
    customers = Customer.query.filter(
        and_(
            Customer.user_id == session['user_id'],
            db.or_(
                Customer.name.contains(query),
                Customer.phone.contains(query)
            )
        )
    ).limit(5).all()
    
    # Search transactions - only current user's transactions
    transactions = Transaction.query.filter(
        and_(
            Transaction.user_id == session['user_id'],
            Transaction.transaction_number.contains(query)
        )
    ).limit(5).all()
    
    return jsonify({
        'customers': [{
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'email': c.email
        } for c in customers],
        'transactions': [{
            'id': t.id,
            'transaction_number': t.transaction_number,
            'customer': {'name': t.customer.name},
            'amount': t.amount,
            'status': t.status
        } for t in transactions]
    })

@app.route('/api/gold-price')
def api_gold_price():
    """Get current gold price"""
    # You can integrate with actual gold price API here
    return jsonify({
        '24k': 6200,  # Price per gram
        '22k': 5850,
        '18k': 4650,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/alerts')
@shop_profile_required
def api_alerts():
    """Get user alerts"""
    alerts = BusinessAlert.query.filter(and_(
        BusinessAlert.user_id == session['user_id'],
        BusinessAlert.is_read == False
    )).order_by(BusinessAlert.created_at.desc()).limit(10).all()
    
    return jsonify([{
        'id': alert.id,
        'type': alert.alert_type,
        'title': alert.title,
        'message': alert.message,
        'priority': alert.priority,
        'action_url': alert.action_url,
        'created_at': alert.created_at.isoformat()
    } for alert in alerts])

@app.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@shop_profile_required
def mark_alert_read(alert_id):
    """Mark alert as read"""
    alert = BusinessAlert.query.filter(and_(
        BusinessAlert.id == alert_id,
        BusinessAlert.user_id == session['user_id']
    )).first()
    
    if alert:
        alert.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 404

@app.route('/api/calculate-interest')
@shop_profile_required
def api_calculate_interest():
    """Calculate interest for given parameters"""
    principal = float(request.args.get('principal', 0))
    rate = float(request.args.get('rate', 0))
    days = int(request.args.get('days', 0))
    
    if principal <= 0 or rate <= 0 or days <= 0:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    interest_data = calculate_smart_interest(principal, rate, start_date)
    
    return jsonify(interest_data)

# -------- Mobile API (JWT Auth) --------
@app.route('/api/mobile/auth/register', methods=['POST'])
def api_mobile_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not email or not password:
        return jsonify({'error': 'username, email, password are required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    token = generate_jwt(user.id, user.username, user.role)
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'shop_profile_completed': user.shop_profile_completed}})

@app.route('/api/mobile/auth/login', methods=['POST'])
def api_mobile_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401
    token = generate_jwt(user.id, user.username, user.role)
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'shop_profile_completed': user.shop_profile_completed}})

@app.route('/api/mobile/auth/me', methods=['GET'])
@token_required
def api_mobile_me():
    user = request.current_user
    profile = ShopProfile.query.filter_by(user_id=user.id).first()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'shop_profile_completed': user.shop_profile_completed,
        'shop_profile': ({
            'shop_name': profile.shop_name,
            'owner_name': profile.owner_name,
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
            'phone': profile.phone,
            'email': profile.email,
            'gstin': profile.gstin,
            'license_number': profile.license_number,
        } if profile else None)
    })

# Customers CRUD
@app.route('/api/mobile/customers', methods=['GET', 'POST'])
@token_required
def api_mobile_customers():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        phone = (data.get('phone') or '').strip()
        if not name or not phone:
            return jsonify({'error': 'name and phone are required'}), 400
        customer = Customer(
            user_id=request.current_user.id,
            name=name,
            phone=phone,
            email=data.get('email', ''),
            address=data.get('address', ''),
            id_proof_type=data.get('id_proof_type', ''),
            id_proof_number=data.get('id_proof_number', '')
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'id': customer.id}), 201
    # GET - only current user's customers
    query = Customer.query.filter_by(user_id=request.current_user.id).order_by(Customer.name)
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(db.or_(Customer.name.contains(q), Customer.phone.contains(q)))
    customers = query.limit(100).all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'email': c.email,
            'address': c.address,
            'id_proof_type': c.id_proof_type,
            'id_proof_number': c.id_proof_number,
            'created_at': c.created_at.isoformat()
        } for c in customers
    ])

@app.route('/api/mobile/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def api_mobile_customer_detail(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer or customer.user_id != request.current_user.id:
        return jsonify({'error': 'Customer not found'}), 404
    if request.method == 'GET':
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address,
            'id_proof_type': customer.id_proof_type,
            'id_proof_number': customer.id_proof_number,
            'created_at': customer.created_at.isoformat()
        })
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        customer.name = data.get('name', customer.name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)
        customer.address = data.get('address', customer.address)
        customer.id_proof_type = data.get('id_proof_type', customer.id_proof_type)
        customer.id_proof_number = data.get('id_proof_number', customer.id_proof_number)
        db.session.commit()
        return jsonify({'success': True})
    # DELETE
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'success': True})

# Transactions
@app.route('/api/mobile/transactions', methods=['GET', 'POST'])
@token_required
def api_mobile_transactions():
    user = request.current_user
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            customer_id = int(data.get('customer_id'))
            amount = float(data.get('amount'))
            interest_rate = float(data.get('interest_rate'))
            duration_months = int(data.get('duration_months'))
        except Exception:
            return jsonify({'error': 'Invalid transaction parameters'}), 400
        notes = data.get('notes', '')
        transaction_number = f"TRX-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=duration_months * 30)
        trx = Transaction(
            transaction_number=transaction_number,
            customer_id=customer_id,
            user_id=user.id,
            amount=amount,
            interest_rate=interest_rate,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        db.session.add(trx)
        db.session.commit()
        # Items
        items = data.get('items') or []
        for it in items:
            if not it:
                continue
            new_item = Item(
                name=it.get('name', ''),
                description=it.get('description', ''),
                category=it.get('category', ''),
                weight=float(it['weight']) if it.get('weight') is not None else None,
                purity=it.get('purity', ''),
                estimated_value=float(it['estimated_value']) if it.get('estimated_value') is not None else None,
                transaction_id=trx.id
            )
            db.session.add(new_item)
        db.session.commit()
        return jsonify({'id': trx.id, 'transaction_number': trx.transaction_number}), 201
    # GET
    q = request.args.get('q', '').strip()
    query = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc())
    if q:
        query = query.filter(Transaction.transaction_number.contains(q))
    trxs = query.limit(100).all()
    return jsonify([
        {
            'id': t.id,
            'transaction_number': t.transaction_number,
            'customer': {
                'id': t.customer.id,
                'name': t.customer.name,
                'phone': t.customer.phone
            } if t.customer else None,
            'amount': t.amount,
            'interest_rate': t.interest_rate,
            'duration_months': t.duration_months,
            'start_date': t.start_date.isoformat() if t.start_date else None,
            'end_date': t.end_date.isoformat() if t.end_date else None,
            'status': t.status
        } for t in trxs
    ])

@app.route('/api/mobile/transactions/<int:transaction_id>', methods=['GET'])
@token_required
def api_mobile_transaction_detail(transaction_id):
    t = db.session.get(Transaction, transaction_id)
    if not t:
        return jsonify({'error': 'Transaction not found'}), 404
    items = Item.query.filter_by(transaction_id=transaction_id).all()
    payments = Payment.query.filter_by(transaction_id=transaction_id).order_by(Payment.payment_date).all()
    days_passed = (datetime.now(timezone.utc) - t.start_date).days if t.start_date else 0
    interest_amount = (t.amount * t.interest_rate / 100) * (days_passed / 30) if t.amount and t.interest_rate else 0
    total_amount = (t.amount or 0) + interest_amount
    paid_amount = sum(p.amount for p in payments)
    remaining_amount = total_amount - paid_amount
    return jsonify({
        'id': t.id,
        'transaction_number': t.transaction_number,
        'customer': {
            'id': t.customer.id,
            'name': t.customer.name,
            'phone': t.customer.phone
        } if t.customer else None,
        'amount': t.amount,
        'interest_rate': t.interest_rate,
        'duration_months': t.duration_months,
        'start_date': t.start_date.isoformat() if t.start_date else None,
        'end_date': t.end_date.isoformat() if t.end_date else None,
        'status': t.status,
        'items': [{
            'id': i.id,
            'name': i.name,
            'category': i.category,
            'weight': i.weight,
            'purity': i.purity,
            'estimated_value': i.estimated_value,
            'description': i.description
        } for i in items],
        'payments': [{
            'id': p.id,
            'amount': p.amount,
            'payment_type': p.payment_type,
            'payment_date': p.payment_date.isoformat(),
            'receipt_number': p.receipt_number
        } for p in payments],
        'calculation': {
            'interest_amount': round(interest_amount, 2),
            'total_amount': round(total_amount, 2),
            'paid_amount': round(paid_amount, 2),
            'remaining_amount': round(remaining_amount, 2)
        }
    })

@app.route('/api/mobile/transactions/<int:transaction_id>/payments', methods=['POST'])
@token_required
def api_mobile_add_payment(transaction_id):
    t = db.session.get(Transaction, transaction_id)
    if not t:
        return jsonify({'error': 'Transaction not found'}), 404
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'Valid amount is required'}), 400
    payment_type = data.get('payment_type', 'interest')
    payment_date_str = data.get('payment_date')
    payment_date = datetime.now(timezone.utc)
    if payment_date_str:
        try:
            payment_date = datetime.fromisoformat(payment_date_str)
            if payment_date.tzinfo is None:
                payment_date = payment_date.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    notes = data.get('notes', '')
    receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    payment = Payment(
        transaction_id=transaction_id,
        amount=amount,
        payment_type=payment_type,
        payment_date=payment_date,
        receipt_number=receipt_number,
        notes=notes
    )
    db.session.add(payment)
    # Close transaction if fully paid
    days_passed = (datetime.now(timezone.utc) - t.start_date).days
    interest_amount = (t.amount * t.interest_rate / 100) * (days_passed / 30)
    total_amount = t.amount + interest_amount
    existing = Payment.query.filter_by(transaction_id=transaction_id).all()
    paid_amount = sum(p.amount for p in existing) + amount
    if paid_amount >= total_amount:
        t.status = 'closed'
    db.session.commit()
    return jsonify({'id': payment.id, 'receipt_number': payment.receipt_number})

@app.route('/api/mobile/alerts', methods=['GET'])
@token_required
def api_mobile_alerts():
    alerts = BusinessAlert.query.filter(and_(
        BusinessAlert.user_id == request.current_user.id,
        BusinessAlert.is_read == False
    )).order_by(BusinessAlert.created_at.desc()).limit(20).all()
    return jsonify([
        {
            'id': a.id,
            'type': a.alert_type,
            'title': a.title,
            'message': a.message,
            'priority': a.priority,
            'action_url': a.action_url,
            'created_at': a.created_at.isoformat()
        } for a in alerts
    ])

@app.route('/api/mobile/alerts/<int:alert_id>/read', methods=['POST'])
@token_required
def api_mobile_alert_read(alert_id):
    alert = BusinessAlert.query.filter(and_(
        BusinessAlert.id == alert_id,
        BusinessAlert.user_id == request.current_user.id
    )).first()
    if not alert:
        return jsonify({'error': 'Not found'}), 404
    alert.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/mobile/whatsapp/reminder/<int:transaction_id>', methods=['POST'])
@token_required
def api_mobile_whatsapp_reminder(transaction_id):
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    user = request.current_user
    shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        return jsonify({'error': 'Shop profile not found'}), 400
    customer = db.session.get(Customer, transaction.customer_id)
    nm = NotificationManager()
    today = datetime.now(timezone.utc).date()
    due_date = transaction.end_date.date() if transaction.end_date else today
    days_until_due = (due_date - today).days
    message = nm.generate_payment_reminder_message(transaction, days_until_due, shop_profile)
    whatsapp_url = nm.send_whatsapp_message(customer.phone if customer else '', message)
    log = NotificationLog(
        transaction_id=transaction.id,
        customer_id=transaction.customer_id,
        notification_type='reminder',
        message=message,
        sent_by=user.id
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'whatsapp_url': whatsapp_url})

# Shop profile
@app.route('/api/mobile/shop-profile', methods=['GET', 'PUT'])
@token_required
def api_mobile_shop_profile():
    user = request.current_user
    profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if request.method == 'GET':
        return jsonify({
            'exists': profile is not None,
            'shop_profile_completed': user.shop_profile_completed,
            'profile': ({
                'shop_name': profile.shop_name,
                'owner_name': profile.owner_name,
                'address_line1': profile.address_line1,
                'address_line2': profile.address_line2,
                'city': profile.city,
                'state': profile.state,
                'pincode': profile.pincode,
                'phone': profile.phone,
                'email': profile.email,
                'gstin': profile.gstin,
                'license_number': profile.license_number
            } if profile else None)
        })
    # PUT upsert
    data = request.get_json(silent=True) or {}
    if not profile:
        profile = ShopProfile(
            user_id=user.id,
            shop_name=data.get('shop_name', ''),
            owner_name=data.get('owner_name', ''),
            address_line1=data.get('address_line1', ''),
            address_line2=data.get('address_line2', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            pincode=data.get('pincode', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            gstin=data.get('gstin', ''),
            license_number=data.get('license_number', '')
        )
        db.session.add(profile)
        user.shop_profile_completed = True
    else:
        profile.shop_name = data.get('shop_name', profile.shop_name)
        profile.owner_name = data.get('owner_name', profile.owner_name)
        profile.address_line1 = data.get('address_line1', profile.address_line1)
        profile.address_line2 = data.get('address_line2', profile.address_line2)
        profile.city = data.get('city', profile.city)
        profile.state = data.get('state', profile.state)
        profile.pincode = data.get('pincode', profile.pincode)
        profile.phone = data.get('phone', profile.phone)
        profile.email = data.get('email', profile.email)
        profile.gstin = data.get('gstin', profile.gstin)
        profile.license_number = data.get('license_number', profile.license_number)
        profile.updated_at = datetime.now(timezone.utc)
        user.shop_profile_completed = True
    db.session.commit()
    return jsonify({'success': True})

# Quick Actions Routes
@app.route('/quick-actions')
@shop_profile_required
def quick_actions():
    """Mobile-friendly quick actions dashboard"""
    today = datetime.now(timezone.utc).date()
    
    # Today's statistics
    todays_transactions = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        db.func.date(Transaction.created_at) == today
    )).count()
    
    todays_payments = Payment.query.join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        db.func.date(Payment.payment_date) == today
    )).count()
    
    todays_amount = db.session.query(db.func.sum(Payment.amount)).join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        db.func.date(Payment.payment_date) == today
    )).scalar() or 0
    
    overdue_count = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date < datetime.now(timezone.utc)
    )).count()
    
    return render_template('quick_actions.html',
                         todays_transactions=todays_transactions,
                         todays_payments=todays_payments,
                         todays_amount=f"{todays_amount:,.0f}",
                         overdue_count=overdue_count)

# WhatsApp Integration Routes
@app.route('/send-reminder/<int:transaction_id>')
@shop_profile_required
def send_payment_reminder(transaction_id):
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('dashboard'))
    user = db.session.get(User, session['user_id'])
    shop_profile = None
    if user:
        shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        flash('Shop profile not found. Please set up your shop profile.')
        return redirect(url_for('shop_profile_setup'))
    notification_manager = NotificationManager()
    today = datetime.now(timezone.utc).date()
    due_date = None
    if transaction.end_date:
        due_date = transaction.end_date.date()
    else:
        due_date = today
    days_until_due = (due_date - today).days
    customer = db.session.get(Customer, transaction.customer_id)
    message = notification_manager.generate_payment_reminder_message(transaction, days_until_due, shop_profile)
    whatsapp_url = notification_manager.send_whatsapp_message(customer.phone if customer else '', message)
    notification_log = NotificationLog(
        transaction_id=transaction_id,
        customer_id=transaction.customer_id,
        notification_type='reminder',
        message=message,
        sent_by=session['user_id']
    )
    db.session.add(notification_log)
    db.session.commit()
    flash(f'Reminder prepared for {customer.name if customer else "customer"}')
    return redirect(whatsapp_url)

@app.route('/send-receipt/<int:payment_id>')
@shop_profile_required
def send_payment_receipt(payment_id):
    payment = db.session.get(Payment, payment_id)
    if not payment:
        flash('Payment not found.')
        return redirect(url_for('dashboard'))
    user = db.session.get(User, session['user_id'])
    shop_profile = None
    if user:
        shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        flash('Shop profile not found. Please set up your shop profile.')
        return redirect(url_for('shop_profile_setup'))
    notification_manager = NotificationManager()
    transaction = db.session.get(Transaction, payment.transaction_id)
    customer = db.session.get(Customer, transaction.customer_id if transaction else None)
    message = notification_manager.generate_receipt_message(payment, shop_profile)
    whatsapp_url = notification_manager.send_whatsapp_message(customer.phone if customer else '', message)
    notification_log = NotificationLog(
        transaction_id=payment.transaction_id,
        customer_id=transaction.customer_id if transaction else None,
        notification_type='receipt',
        message=message,
        sent_by=session['user_id']
    )
    db.session.add(notification_log)
    db.session.commit()
    flash(f'Receipt sent to {customer.name if customer else "customer"}')
    return redirect(whatsapp_url)

@app.route('/bulk-reminders')
@shop_profile_required
def bulk_reminders():
    """Send bulk payment reminders"""
    today = datetime.now(timezone.utc)
    next_week = today + timedelta(days=7)
    
    # Get transactions due in next 7 days
    upcoming_due = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date >= today,
        Transaction.end_date <= next_week
    )).all()
    
    # Get overdue transactions
    overdue = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date < today
    )).all()
    
    user = db.session.get(User, session['user_id'])
    shop_profile = None
    if user:
        shop_profile = ShopProfile.query.filter_by(user_id=user.id).first()
    if not shop_profile:
        flash('Shop profile not found. Please set up your shop profile.')
        return redirect(url_for('shop_profile_setup'))
    notification_manager = NotificationManager()
    reminder_links = []
    
    for transaction in upcoming_due + overdue:
        days_until_due = (transaction.end_date.date() - today.date()).days if transaction.end_date else 0
        customer = db.session.get(Customer, transaction.customer_id)
        message = notification_manager.generate_payment_reminder_message(transaction, days_until_due, shop_profile)
        whatsapp_url = notification_manager.send_whatsapp_message(customer.phone if customer else '', message)
        reminder_links.append({
            'customer': customer.name if customer else 'N/A',
            'phone': customer.phone if customer else '',
            'whatsapp_url': whatsapp_url,
            'days_until_due': days_until_due,
            'amount': transaction.amount
        })
    
    return render_template('bulk_reminders.html', reminder_links=reminder_links)

# Financial Management Routes
@app.route('/cash-flow')
@shop_profile_required
def cash_flow():
    """Daily cash flow management"""
    today = datetime.now(timezone.utc).date()
    
    # Today's transactions (money out)
    todays_transactions = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        db.func.date(Transaction.created_at) == today
    )).all()
    
    # Today's payments (money in)
    todays_payments = Payment.query.join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        db.func.date(Payment.payment_date) == today
    )).all()
    
    cash_in = sum(p.amount for p in todays_payments)
    cash_out = sum(t.amount for t in todays_transactions)
    net_cash_flow = cash_in - cash_out
    
    # Weekly summary
    week_start = today - timedelta(days=6)
    weekly_payments = Payment.query.join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Payment.payment_date >= week_start
    )).all()
    
    weekly_transactions = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.created_at >= week_start
    )).all()
    
    weekly_cash_in = sum(p.amount for p in weekly_payments)
    weekly_cash_out = sum(t.amount for t in weekly_transactions)
    
    return render_template('cash_flow.html',
                         cash_in=cash_in,
                         cash_out=cash_out,
                         net_cash_flow=net_cash_flow,
                         todays_transactions=todays_transactions,
                         todays_payments=todays_payments,
                         weekly_cash_in=weekly_cash_in,
                         weekly_cash_out=weekly_cash_out,
                         today=today)

@app.route('/reports')
@shop_profile_required
def reports():
    """Business reports dashboard"""
    today = datetime.now(timezone.utc)
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    # Monthly revenue (current month)
    current_month_payments = Payment.query.join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Payment.payment_date >= current_month_start,
        Payment.payment_type == 'interest'
    )).all()
    
    # Last month revenue
    last_month_payments = Payment.query.join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Payment.payment_date >= last_month_start,
        Payment.payment_date < current_month_start,
        Payment.payment_type == 'interest'
    )).all()
    
    current_month_revenue = sum(p.amount for p in current_month_payments)
    last_month_revenue = sum(p.amount for p in last_month_payments)
    
    # Top customers by transaction value
    top_customers = db.session.query(
        Customer.name.label('name'),
        db.func.sum(Transaction.amount).label('total_amount'),
        db.func.count(Transaction.id).label('transaction_count')
    ).join(Transaction).filter(
        Transaction.user_id == session['user_id']
    ).group_by(Customer.id).order_by(db.desc('total_amount')).limit(10).all()
    
    # Overdue analysis
    overdue_transactions = Transaction.query.filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date < today
    )).all()
    
    total_overdue_amount = sum(t.amount for t in overdue_transactions)
    
    # Category-wise breakdown
    category_stats = db.session.query(
        Item.category,
        db.func.count(Item.id).label('count'),
        db.func.sum(Item.estimated_value).label('total_value')
    ).join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active'
    )).group_by(Item.category).all()
    
    return render_template('reports.html',
                         current_month_revenue=current_month_revenue,
                         last_month_revenue=last_month_revenue,
                         top_customers=top_customers,
                         overdue_transactions=overdue_transactions,
                         total_overdue_amount=total_overdue_amount,
                         category_stats=category_stats)

# Inventory Management Routes
@app.route('/inventory')
@shop_profile_required
def inventory():
    """View all jewelry items in inventory"""
    # Active pledged items
    active_items = db.session.query(Item, Transaction).join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active'
    )).all()
    
    # Items ready for auction (overdue by 30+ days)
    overdue_threshold = datetime.now(timezone.utc) - timedelta(days=30)
    auction_ready = db.session.query(Item, Transaction).join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active',
        Transaction.end_date != None,
        Transaction.end_date < overdue_threshold
    )).all()
    
    # Auctioned items
    auctioned_items = AuctionItem.query.join(Transaction).filter(
        Transaction.user_id == session['user_id']
    ).all()
    
    return render_template('inventory.html',
                         active_items=active_items,
                         auction_ready=auction_ready,
                         auctioned_items=auctioned_items)

@app.route('/stock-valuation')
@shop_profile_required
def stock_valuation():
    """Generate stock valuation report"""
    # Active inventory
    active_items = db.session.query(Item, Transaction).join(Transaction).filter(and_(
        Transaction.user_id == session['user_id'],
        Transaction.status == 'active'
    )).all()
    
    total_loan_value = sum(transaction.amount for item, transaction in active_items)
    total_estimated_value = sum(item.estimated_value or 0 for item, transaction in active_items)
    
    # Category-wise breakdown
    category_breakdown = {}
    for item, transaction in active_items:
        category = item.category or 'Unknown'
        if category not in category_breakdown:
            category_breakdown[category] = {
                'count': 0,
                'loan_value': 0,
                'estimated_value': 0
            }
        category_breakdown[category]['count'] += 1
        category_breakdown[category]['loan_value'] += transaction.amount
        category_breakdown[category]['estimated_value'] += item.estimated_value or 0
    
    return render_template('stock_valuation.html',
                         active_items=active_items,
                         total_loan_value=total_loan_value,
                         total_estimated_value=total_estimated_value,
                         category_breakdown=category_breakdown)

@app.context_processor
def inject_now():
    from datetime import datetime, timezone
    return {'now': lambda: datetime.now(timezone.utc)}

def init_db():
    with app.app_context():
        # Create all tables (don't drop existing ones)
        db.create_all()
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user only if it doesn't exist
            admin = User(
                username='admin',
                email='admin@girvimanagement.com',
                password=generate_password_hash('admin123'),
                role='admin',
                shop_profile_completed=False  # Admin will need to complete profile
            )
            db.session.add(admin)
            db.session.commit()
            print("Database initialized with admin user.")
            print("Login with: username='admin', password='admin123'")
            print("You'll be prompted to complete shop profile after login.")
        else:
            print("Database already exists. Admin user found.")

@app.route('/api/mobile/health', methods=['GET'])
def api_health():
    """Health check endpoint for mobile app"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

if __name__ == '__main__':
    try:
        init_db()  # Initialize database on startup
        
        # Check database schema
        with app.app_context():
            try:
                db.session.execute(db.text("SELECT user_id FROM customer LIMIT 1"))
                print("✓ Database schema is up to date.")
            except Exception:
                print("\n" + "="*70)
                print("⚠ WARNING: DATABASE SCHEMA IS OUTDATED!")
                print("="*70)
                print("The application will start but CUSTOMER OPERATIONS WILL FAIL.")
                print("\nTO FIX:")
                print("1. Press Ctrl+C to stop the server")
                print("2. Run: python fix_database.py")
                print("3. Start the server again")
                print("\nQuick fix: Delete instance/girvi.db and restart")
                print("="*70 + "\n")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("\nDelete instance/girvi.db and restart the server.")
    
    # Get port from environment variable (Heroku) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Disable debug in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    # Run on 0.0.0.0 to accept connections from network (mobile devices)
    app.run(debug=debug, host='0.0.0.0', port=port)
