# Inventory Management for Jewelry Items

from datetime import datetime, timedelta
from sqlalchemy import or_

# Add these models to app.py

class ItemStatus(db.Model):
    """Track status changes of jewelry items"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # pledged, released, auctioned, sold
    status_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Inventory Management Routes

@app.route('/inventory')
@shop_profile_required
def inventory():
    """View all jewelry items in inventory"""
    # Active pledged items
    active_items = db.session.query(Item, Transaction).join(Transaction).filter(
        Transaction.status == 'active'
    ).all()
    
    # Items ready for auction (overdue by 30+ days)
    overdue_threshold = datetime.utcnow() - timedelta(days=30)
    auction_ready = db.session.query(Item, Transaction).join(Transaction).filter(
        Transaction.status == 'active',
        Transaction.end_date < overdue_threshold
    ).all()
    
    # Auctioned items
    auctioned_items = AuctionItem.query.all()
    
    return render_template('inventory.html',
                         active_items=active_items,
                         auction_ready=auction_ready,
                         auctioned_items=auctioned_items)

@app.route('/inventory/search')
@shop_profile_required
def inventory_search():
    """Search inventory by various criteria"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    base_query = db.session.query(Item, Transaction).join(Transaction)
    
    if query:
        base_query = base_query.filter(
            or_(
                Item.name.contains(query),
                Item.description.contains(query),
                Transaction.transaction_number.contains(query),
                Transaction.customer.has(Customer.name.contains(query))
            )
        )
    
    if category:
        base_query = base_query.filter(Item.category == category)
    
    if status:
        base_query = base_query.filter(Transaction.status == status)
    
    results = base_query.all()
    
    return render_template('inventory_search.html', results=results, 
                         query=query, category=category, status=status)

@app.route('/auction/prepare/<int:transaction_id>')
@shop_profile_required
def prepare_auction(transaction_id):
    """Prepare items for auction"""
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction:
        flash('Transaction not found.')
        return redirect(url_for('inventory'))
    
    # Check if transaction is overdue enough for auction
    days_overdue = (datetime.utcnow() - transaction.end_date).days
    if days_overdue < 30:
        flash('Transaction must be overdue by at least 30 days for auction.')
        return redirect(url_for('inventory'))
    
    items = Item.query.filter_by(transaction_id=transaction_id).all()
    
    return render_template('prepare_auction.html', 
                         transaction=transaction, 
                         items=items,
                         days_overdue=days_overdue)

@app.route('/auction/create', methods=['POST'])
@shop_profile_required
def create_auction():
    """Create auction entries for items"""
    transaction_id = request.form['transaction_id']
    item_ids = request.form.getlist('item_ids')
    auction_date = datetime.strptime(request.form['auction_date'], '%Y-%m-%d')
    
    for item_id in item_ids:
        item = db.session.get(Item, item_id)
        reserve_price = float(request.form.get(f'reserve_price_{item_id}', item.estimated_value))
        
        auction_item = AuctionItem(
            item_id=item_id,
            transaction_id=transaction_id,
            auction_date=auction_date,
            reserve_price=reserve_price
        )
        db.session.add(auction_item)
        
        # Update item status
        status_update = ItemStatus(
            item_id=item_id,
            status='auctioned',
            notes=f'Item prepared for auction on {auction_date.strftime("%Y-%m-%d")}',
            created_by=session['user_id']
        )
        db.session.add(status_update)
    
    # Update transaction status
    transaction = db.session.get(Transaction, transaction_id)
    transaction.status = 'defaulted'
    
    db.session.commit()
    flash(f'{len(item_ids)} items prepared for auction.')
    return redirect(url_for('inventory'))

@app.route('/auction/record-sale/<int:auction_id>', methods=['GET', 'POST'])
@shop_profile_required
def record_auction_sale(auction_id):
    """Record the sale of an auctioned item"""
    auction_item = db.session.get(AuctionItem, auction_id)
    if not auction_item:
        flash('Auction item not found.')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        final_price = float(request.form['final_price'])
        buyer_name = request.form['buyer_name']
        buyer_phone = request.form['buyer_phone']
        
        auction_item.final_price = final_price
        auction_item.buyer_name = buyer_name
        auction_item.buyer_phone = buyer_phone
        auction_item.status = 'sold'
        
        # Calculate recovery for the original loan
        transaction = auction_item.transaction
        recovery_amount = min(final_price, transaction.amount * 1.2)  # Max 120% of loan
        
        # Create recovery payment
        recovery_payment = Payment(
            transaction_id=transaction.id,
            amount=recovery_amount,
            payment_type='recovery',
            payment_date=datetime.utcnow(),
            receipt_number=f"AUC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            notes=f'Auction recovery - Item sold for ₹{final_price:,.2f}'
        )
        db.session.add(recovery_payment)
        
        # Update item status
        status_update = ItemStatus(
            item_id=auction_item.item_id,
            status='sold',
            notes=f'Sold at auction for ₹{final_price:,.2f} to {buyer_name}',
            created_by=session['user_id']
        )
        db.session.add(status_update)
        
        db.session.commit()
        flash('Auction sale recorded successfully.')
        return redirect(url_for('inventory'))
    
    return render_template('record_auction_sale.html', auction_item=auction_item)

# Item Release Management
@app.route('/release-item/<int:item_id>')
@shop_profile_required
def release_item(item_id):
    """Release item back to customer after full payment"""
    item = db.session.get(Item, item_id)
    if not item:
        flash('Item not found.')
        return redirect(url_for('inventory'))
    
    transaction = item.transaction
    
    # Check if transaction is fully paid
    total_payments = sum(p.amount for p in transaction.payments)
    days_passed = (datetime.utcnow() - transaction.start_date).days
    interest = (transaction.amount * transaction.interest_rate / 100) * (days_passed / 30)
    total_due = transaction.amount + interest
    
    if total_payments < total_due:
        flash('Transaction is not fully paid. Cannot release item.')
        return redirect(url_for('inventory'))
    
    # Mark item as released
    status_update = ItemStatus(
        item_id=item_id,
        status='released',
        notes='Item released to customer after full payment',
        created_by=session['user_id']
    )
    db.session.add(status_update)
    
    # Check if all items are released, then close transaction
    remaining_items = Item.query.filter_by(transaction_id=transaction.id).join(ItemStatus).filter(
        ItemStatus.status != 'released'
    ).count()
    
    if remaining_items == 0:
        transaction.status = 'closed'
    
    db.session.commit()
    flash('Item released successfully.')
    return redirect(url_for('inventory'))

# Stock Valuation Report
@app.route('/stock-valuation')
@shop_profile_required
def stock_valuation():
    """Generate stock valuation report"""
    # Active inventory
    active_items = db.session.query(Item, Transaction).join(Transaction).filter(
        Transaction.status == 'active'
    ).all()
    
    total_loan_value = sum(item.transaction.amount for item, transaction in active_items)
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

# Automatic Stock Alerts
def get_stock_alerts():
    """Get alerts for inventory management"""
    alerts = []
    
    # Overdue items (30+ days)
    overdue_threshold = datetime.utcnow() - timedelta(days=30)
    overdue_items = db.session.query(Item, Transaction).join(Transaction).filter(
        Transaction.status == 'active',
        Transaction.end_date < overdue_threshold
    ).count()
    
    if overdue_items > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{overdue_items} items are ready for auction',
            'action_url': '/inventory'
        })
    
    # High-value items (above 1 lakh)
    high_value_items = db.session.query(Item, Transaction).join(Transaction).filter(
        Transaction.status == 'active',
        Transaction.amount > 100000
    ).count()
    
    if high_value_items > 0:
        alerts.append({
            'type': 'info',
            'message': f'{high_value_items} high-value items in inventory',
            'action_url': '/stock-valuation'
        })
    
    return alerts
