# Customer Management Features

## Complete Customer Management System ✅

### Customer List Page (`/customers`)

Each customer row now shows **4 action buttons**:

| Icon | Action | Color | Description |
|------|--------|-------|-------------|
| 👁️ | **View** | Blue | View complete customer details and transaction history |
| ✏️ | **Edit** | Blue (hover) | Edit customer information (name, phone, email, address, ID proof) |
| ➕ | **New Transaction** | Green (hover) | Create a new loan/transaction for this customer |
| 🗑️ | **Delete** | Red (hover) | Delete customer (only if no transactions exist) |

### Customer Details Page (`/customer/<id>`)

Three buttons available:
1. **New Transaction** - Create loan for customer
2. **Edit Customer** - Edit customer information  
3. **Delete Customer** - Delete customer (with safety checks)

## Features

### ✅ View Customer
- Full customer information
- Transaction history
- Active and completed loans
- Contact details
- ID proof information

### ✅ Edit Customer
**Location:** 
- Customers list → Edit button (pencil icon)
- Customer details → Edit Customer button

**Can Edit:**
- Name
- Phone number
- Email
- Address
- ID proof type
- ID proof number

**Security:**
- Users can only edit their own customers
- Redirect if trying to edit another user's customer

### ✅ Delete Customer
**Location:**
- Customers list → Delete button (trash icon)
- Customer details → Delete Customer button

**Safety Checks:**
- ⚠️ Cannot delete if customer has ANY transactions (active or closed)
- ⚠️ Confirmation dialog before deletion
- ✅ Only customers with zero transactions can be deleted

**Security:**
- Users can only delete their own customers
- Redirect if trying to delete another user's customer

### ✅ Search & Filter
- Search by name, phone, or email
- Filter by:
  - All customers
  - Active loans
  - Completed loans

## User Data Isolation

### Each User Has Separate Data
```
User A Login
├── Can see ONLY User A's customers
├── Can edit ONLY User A's customers
├── Can delete ONLY User A's customers
└── Cannot access User B's data

User B Login
├── Can see ONLY User B's customers
├── Can edit ONLY User B's customers
├── Can delete ONLY User B's customers
└── Cannot access User A's data
```

## Visual Guide

### Customers List Page
```
┌─────────────────────────────────────────────────────────────┐
│  👥 Customers                      [+ Add New Customer]     │
├─────────────────────────────────────────────────────────────┤
│  🔍 Search: [                    ] Filter: [All Customers]  │
├─────────────────────────────────────────────────────────────┤
│  Customer Name    Contact         Active Loans   Actions    │
│  ────────────────────────────────────────────────────────── │
│  Rajesh Kumar    📞 9876543210    2 Active     👁️ ✏️ ➕ 🗑️  │
│  Priya Sharma    📞 9876543211    0 Active     👁️ ✏️ ➕ 🗑️  │
│  Amit Patel      📞 9876543212    1 Active     👁️ ✏️ ➕ 🗑️  │
└─────────────────────────────────────────────────────────────┘

Legend:
  👁️ = View Details
  ✏️ = Edit Customer
  ➕ = New Transaction
  🗑️ = Delete Customer
```

### Button Colors (on hover)
- **View** (👁️) - Light blue
- **Edit** (✏️) - Blue highlight
- **New Transaction** (➕) - Green highlight
- **Delete** (🗑️) - Red highlight

## Error Messages

### When Deleting Customer with Transactions
```
❌ Cannot delete customer with existing transactions.
   Please delete or reassign transactions first.
```

### When Accessing Another User's Customer
```
❌ Customer not found.
   (Redirects to customers list)
```

### Success Messages
```
✅ Customer added successfully!
✅ Customer updated successfully!
✅ Customer deleted successfully!
```

## Usage Examples

### Example 1: Edit Customer Information
1. Go to **Customers** page
2. Find customer "Rajesh Kumar"
3. Click **Edit** button (pencil icon)
4. Update phone number: `9876543210` → `9876543299`
5. Click **Save**
6. ✅ "Customer updated successfully!"

### Example 2: Delete Inactive Customer
1. Go to **Customers** page
2. Find customer with "0 Active" loans
3. Click **Delete** button (trash icon)
4. Confirm deletion in popup
5. ✅ "Customer deleted successfully!"

### Example 3: Try to Delete Active Customer
1. Go to **Customers** page
2. Find customer with "2 Active" loans
3. Click **Delete** button (trash icon)
4. Confirm deletion in popup
5. ❌ "Cannot delete customer with existing transactions"

## Security Features

### ✅ Implemented
- User authentication required
- Session management
- User ownership validation
- SQL injection prevention (using SQLAlchemy ORM)
- CSRF protection (via Flask sessions)
- Data isolation per user

### ✅ Access Control
- Cannot view other users' customers
- Cannot edit other users' customers
- Cannot delete other users' customers
- Cannot create transactions for other users' customers
- Search results filtered by user
- API endpoints secured

## Technical Details

### Routes
```python
GET  /customers                    # List all customers (user-specific)
GET  /customer/new                 # New customer form
POST /customer/new                 # Create customer
GET  /customer/<id>                # View customer details
GET  /customer/<id>/edit           # Edit customer form
POST /customer/<id>/edit           # Update customer
POST /customer/<id>/delete         # Delete customer
```

### Database Schema
```sql
CREATE TABLE customer (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,        -- Links to user
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    address VARCHAR(200),
    id_proof_type VARCHAR(50),
    id_proof_number VARCHAR(50),
    created_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES user(id)
);
```

## Mobile App Support

All features available via REST API:
- `GET /api/mobile/customers` - List customers
- `POST /api/mobile/customers` - Create customer
- `GET /api/mobile/customers/<id>` - Get customer
- `PUT /api/mobile/customers/<id>` - Update customer
- `DELETE /api/mobile/customers/<id>` - Delete customer

All endpoints require JWT authentication and enforce user ownership.
