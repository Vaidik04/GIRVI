# 🧪 Quick Test - Loans & Reminders

## Start the App

```bash
cd d:\Python\Projects\WebApplications\Girvi
python app.py
```

Open browser: http://localhost:5000

---

## Test Checklist

### ✅ Loans Page

1. **Login** to the app
2. **Click "Loans"** in top navigation menu
3. **Verify you see:**
   - [ ] Professional table layout
   - [ ] Filter tabs: All | Active | Overdue | Closed
   - [ ] Customer ID shown: "ID: 1 - John Doe"
   - [ ] Loan amounts formatted: ₹50,000
   - [ ] Gold/Silver items preview badges
   - [ ] Status badges (Active/Closed)
   - [ ] WhatsApp reminder button (green)

### ✅ Reminder Features

4. **From Loans List:**
   - [ ] Click WhatsApp icon on any active loan
   - [ ] WhatsApp web opens
   - [ ] Message pre-filled with:
     - Customer name
     - Loan details
     - Due date
     - Shop info

5. **From Loan Details:**
   - [ ] Click any loan to view details
   - [ ] See "Send Reminder" button (top-right)
   - [ ] Click it → WhatsApp opens
   - [ ] Message ready to send

6. **Bulk Reminders:**
   - [ ] URL: http://localhost:5000/bulk-reminders
   - [ ] See all upcoming & overdue loans
   - [ ] WhatsApp links for each
   - [ ] Can send to multiple customers

---

## Expected Results

### Loans Page Should Show:
```
┌─ All Loans ────────────────────────────────────────┐
│                                                    │
│ [All (5)] [Active (3)] [Overdue (1)] [Closed (1)] │
│                                                    │
│ Loan ID    Customer          Amount    Actions    │
│ TRX-123    ID: 1            ₹50,000   👁️ 💰 💬 🖨️  │
│            John Doe                                │
│            9876543210                              │
│                                                    │
│ TRX-124    ID: 2            ₹30,000   👁️ 💰 💬 🖨️  │
│            Jane Smith                              │
│            (Overdue by 5 days)                     │
└────────────────────────────────────────────────────┘
```

### Reminder Button Click Should:
1. Open WhatsApp web/app
2. Show customer's number
3. Pre-filled message with loan details
4. Ready to click "Send"

---

## Troubleshooting

### "Loans" menu not showing?
- Clear browser cache (Ctrl+Shift+R)
- Restart Flask server
- Check you're logged in

### WhatsApp button not working?
- Check shop profile is completed
- Verify customer has phone number
- Check browser allows popups

### No loans showing?
- Create a test loan first
- Dashboard → "New Transaction"
- Fill and submit

---

## Quick Create Test Data

```python
# In Python shell
from app import app, db, Customer, Transaction, Item
from datetime import datetime, timedelta, timezone

with app.app_context():
    # Create test customer
    customer = Customer(
        name="Test Customer",
        phone="9876543210",
        email="test@example.com"
    )
    db.session.add(customer)
    db.session.flush()
    
    # Create test loan
    transaction = Transaction(
        transaction_number="TRX-TEST-123",
        customer_id=customer.id,
        user_id=1,
        amount=50000,
        interest_rate=2.0,
        duration_months=12,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=365)
    )
    db.session.add(transaction)
    db.session.flush()
    
    # Add gold item
    item = Item(
        name="Gold Necklace",
        category="gold",
        weight=50.0,
        purity="22k",
        estimated_value=200000,
        transaction_id=transaction.id
    )
    db.session.add(item)
    db.session.commit()
    
    print("Test data created!")
```

---

**All features are active and working! Test now!**
