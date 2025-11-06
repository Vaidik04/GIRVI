# Add these features to app.py for better financial management

from datetime import datetime, timedelta
import json

# Smart Interest Calculator
def calculate_smart_interest(principal, rate, start_date, end_date=None):
    """
    Calculate interest with different compounding methods
    """
    if end_date is None:
        end_date = datetime.utcnow()
    
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

# EMI Calculator
def calculate_emi(principal, rate, months):
    """Calculate EMI for installment payments"""
    monthly_rate = rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
    return round(emi, 2)

# Gold Price Integration
@app.route('/api/gold-price')
def get_gold_price():
    """Get current gold price (you can integrate with actual API)"""
    # Placeholder - integrate with actual gold price API
    return jsonify({
        '24k': 6200,  # Price per gram
        '22k': 5850,
        '18k': 4650,
        'last_updated': datetime.now().isoformat()
    })

# Automatic Valuation
def estimate_gold_value(weight, purity, current_price_24k):
    """Estimate gold item value based on current market price"""
    purity_factors = {
        '24k': 1.0,
        '22k': 0.916,
        '20k': 0.833,
        '18k': 0.750,
        '16k': 0.666,
        '14k': 0.583,
        '12k': 0.500,
        '10k': 0.416
    }
    
    factor = purity_factors.get(purity.lower(), 0.916)  # Default to 22k
    estimated_value = weight * current_price_24k * factor * 0.85  # 85% of market value
    
    return round(estimated_value, 2)

# Payment Reminder System
@app.route('/api/payment-reminders')
def get_payment_reminders():
    """Get upcoming payment reminders"""
    today = datetime.utcnow()
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)
    
    # Due this week
    due_this_week = Transaction.query.filter(
        Transaction.status == 'active',
        Transaction.end_date >= today,
        Transaction.end_date <= next_week
    ).all()
    
    # Due next month
    due_next_month = Transaction.query.filter(
        Transaction.status == 'active',
        Transaction.end_date > next_week,
        Transaction.end_date <= next_month
    ).all()
    
    # Overdue
    overdue = Transaction.query.filter(
        Transaction.status == 'active',
        Transaction.end_date < today
    ).all()
    
    return jsonify({
        'due_this_week': [{'id': t.id, 'customer': t.customer.name, 
                          'amount': t.amount, 'due_date': t.end_date.isoformat()} 
                         for t in due_this_week],
        'due_next_month': [{'id': t.id, 'customer': t.customer.name, 
                           'amount': t.amount, 'due_date': t.end_date.isoformat()} 
                          for t in due_next_month],
        'overdue': [{'id': t.id, 'customer': t.customer.name, 
                    'amount': t.amount, 'days_overdue': (today - t.end_date).days} 
                   for t in overdue]
    })

# Daily Cash Flow
@app.route('/cash-flow')
@shop_profile_required
def cash_flow():
    """Daily cash flow management"""
    today = datetime.utcnow().date()
    
    # Today's transactions
    todays_transactions = Transaction.query.filter(
        db.func.date(Transaction.created_at) == today
    ).all()
    
    # Today's payments
    todays_payments = Payment.query.filter(
        db.func.date(Payment.payment_date) == today
    ).all()
    
    cash_in = sum(p.amount for p in todays_payments)
    cash_out = sum(t.amount for t in todays_transactions)
    net_cash_flow = cash_in - cash_out
    
    return render_template('cash_flow.html',
                         cash_in=cash_in,
                         cash_out=cash_out,
                         net_cash_flow=net_cash_flow,
                         todays_transactions=todays_transactions,
                         todays_payments=todays_payments)

# Profit Calculator
def calculate_monthly_profit(month, year):
    """Calculate monthly profit from interest"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get all payments in this month
    payments = Payment.query.filter(
        Payment.payment_date >= start_date,
        Payment.payment_date < end_date,
        Payment.payment_type == 'interest'
    ).all()
    
    total_interest = sum(p.amount for p in payments)
    
    # Calculate expenses (you can add expense tracking)
    expenses = 0  # Placeholder
    
    profit = total_interest - expenses
    
    return {
        'interest_income': total_interest,
        'expenses': expenses,
        'net_profit': profit,
        'transactions_count': len(payments)
    }
