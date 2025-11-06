# Quick Start Guide - Updated Girvi Management System

## What's New? 🎉

✅ **Customer Edit** - Edit customer information anytime
✅ **Customer Delete** - Delete customers (if no transactions)
✅ **User Data Isolation** - Each user sees only their own customers and loans

## Getting Started

### Step 1: Clean Database (Recommended)
```bash
# Delete old database
del instance\girvi.db
```

### Step 2: Start Application
```bash
python app.py
```

### Step 3: Login
- Username: `admin`
- Password: `admin123`

### Step 4: Setup Shop Profile
- Complete your shop profile (required before using the system)

## How to Use

### Managing Customers

#### Add New Customer
1. Go to **Customers** menu
2. Click **Add New Customer**
3. Fill in details (name and phone are required)
4. Click **Save**

#### Edit Customer
1. Go to **Customers** > Click on a customer
2. Click **Edit Customer** button
3. Update information
4. Click **Save**

#### Delete Customer
1. Go to **Customers** > Click on a customer
2. Click **Delete Customer** button (red button)
3. Confirm deletion
   - ⚠️ Note: Cannot delete if customer has transactions

### Managing Loans/Transactions

#### Create New Loan
1. Go to **New Transaction**
2. Select existing customer OR create new customer inline
3. Fill in loan details:
   - Amount
   - Interest rate
   - Duration (months)
4. Add jewelry items
5. Submit

#### View Loan Details
1. Go to **Transactions** or **Dashboard**
2. Click on any transaction
3. View complete details:
   - Customer info
   - Loan amount and interest
   - Items pledged
   - Payment history
   - Remaining balance

#### Add Payment
1. Open transaction details
2. Click **Add Payment**
3. Enter amount and type
4. Submit

## Data Isolation - How It Works

### Multiple Users
Each user has their own separate data:
- User A cannot see User B's customers
- User A cannot see User B's transactions
- Each user manages their own business independently

### Example:
```
User: shop1@example.com
├── Customer: Rajesh Kumar
│   └── Transaction: TRX-20231105-ABC123
└── Customer: Priya Sharma
    └── Transaction: TRX-20231106-DEF456

User: shop2@example.com
├── Customer: Amit Patel
│   └── Transaction: TRX-20231105-GHI789
└── Customer: Sneha Reddy
    └── Transaction: TRX-20231107-JKL012
```

## Features

### Customer Management
- ✅ Create customers with full details
- ✅ Edit customer information
- ✅ Delete customers (if no transactions)
- ✅ Search customers
- ✅ View customer transaction history

### Loan Management
- ✅ Create loans with multiple items
- ✅ Track jewelry items (weight, purity, value)
- ✅ Calculate interest automatically
- ✅ Record payments
- ✅ Generate bills/receipts
- ✅ WhatsApp reminders

### Reports & Tracking
- ✅ Dashboard with statistics
- ✅ Due payments tracking
- ✅ Overdue loans
- ✅ Cash flow reports
- ✅ Customer transaction history

## Important Notes

### Security
- Each user can only access their own data
- URLs are protected - cannot access other users' customers
- API endpoints secured with user authentication

### Database Changes
- If you have existing data, run `python migrate_customers.py`
- Existing customers will be assigned to admin user
- New users start with empty customer list

### Best Practices
1. **Complete shop profile first** - Required for proper operation
2. **Create customers before transactions** - Can also create inline
3. **Delete carefully** - Cannot delete customers with transactions
4. **Regular backups** - Backup `instance/girvi.db` regularly

## Troubleshooting

### "Customer not found" error
- Customer belongs to different user
- You can only access your own customers

### Cannot delete customer
- Customer has existing transactions
- Delete transactions first, then delete customer

### Database errors after update
1. Delete `instance/girvi.db`
2. Restart application
3. Database will be recreated with new schema

## Need Help?

Check the documentation files:
- `DATA_ISOLATION_UPDATE.md` - Technical details
- `README.md` - Full feature list
- `DEPLOYMENT.md` - Deployment instructions
