# Troubleshooting Guide

## Error: Cannot Save Customer

### Symptoms
- Error when creating new customer
- Error when editing existing customer
- Database error messages
- "no such column: customer.user_id" error

### Root Cause
The database schema is outdated. After adding the `user_id` field to the Customer model, the existing database doesn't have this column.

### Solution: Quick Fix (Recommended)

**Step 1: Run the fix script**
```bash
python fix_database.py
```

This will:
- ✅ Backup your existing database
- ✅ Delete the old database
- ✅ Prepare for fresh database creation

**Step 2: Start the application**
```bash
python app.py
```

The application will automatically create a new database with the correct schema.

**Step 3: Login**
- Username: `admin`
- Password: `admin123`

**Step 4: Complete shop profile**
- Fill in your shop details
- Now you can add customers!

### Solution: Manual Fix

If you prefer to do it manually:

**Option A: Delete and Recreate**
```bash
# Windows
del instance\girvi.db

# Linux/Mac
rm instance/girvi.db

# Then run
python app.py
```

**Option B: Backup First**
```bash
# Windows
copy instance\girvi.db instance\girvi_backup.db
del instance\girvi.db

# Linux/Mac
cp instance/girvi.db instance/girvi_backup.db
rm instance/girvi.db

# Then run
python app.py
```

## Common Errors and Solutions

### 1. "IntegrityError: NOT NULL constraint failed: customer.user_id"

**Cause:** Database has old schema without user_id field

**Solution:**
```bash
python fix_database.py
python app.py
```

### 2. "OperationalError: no such column: customer.user_id"

**Cause:** Database schema is outdated

**Solution:**
```bash
del instance\girvi.db
python app.py
```

### 3. "Customer not found" when editing your own customer

**Cause:** Session issue or customer belongs to different user

**Solution:**
1. Logout and login again
2. Check if you're logged in as the correct user
3. Verify customer was created by your current user

### 4. Cannot delete customer - "has existing transactions"

**This is NOT an error - it's a safety feature!**

**Reason:** The customer has loan transactions

**Solution:**
- This is intentional to prevent data loss
- You cannot delete customers with transaction history
- Only customers with zero transactions can be deleted

### 5. "Shop profile required" error

**Cause:** Shop profile not completed

**Solution:**
1. Login to your account
2. Complete shop profile form
3. Then you can access all features

### 6. Changes not reflected after editing customer

**Solution:**
1. Hard refresh the page (Ctrl+F5)
2. Clear browser cache
3. Check if edit was successful (look for success message)

## Database Migration (For Existing Data)

If you have important customer data and want to keep it:

**Step 1: Run migration script**
```bash
python migrate_customers.py
```

This will:
- Add user_id field to existing customers
- Assign all existing customers to admin user
- Preserve all transaction data

**Note:** This might fail if database structure is too different. In that case, use the fresh start approach.

## Starting Fresh (Recommended for Development)

If you want a clean slate:

```bash
# 1. Backup (optional)
copy instance\girvi.db instance\backup_girvi.db

# 2. Delete database
del instance\girvi.db

# 3. Start app
python app.py

# 4. Login
# Username: admin
# Password: admin123

# 5. Complete shop profile

# 6. Start adding customers!
```

## Testing After Fix

To verify everything works:

**Test 1: Create Customer**
1. Login as admin
2. Go to Customers → Add New Customer
3. Fill in details
4. Click Save
5. ✅ Should see "Customer added successfully!"

**Test 2: Edit Customer**
1. Go to Customers list
2. Click Edit button (pencil icon)
3. Change customer name
4. Click Save
5. ✅ Should see "Customer updated successfully!"

**Test 3: Delete Customer**
1. Create a new customer (with no transactions)
2. Click Delete button (trash icon)
3. Confirm deletion
4. ✅ Should see "Customer deleted successfully!"

**Test 4: Multi-User Isolation**
1. Create second user account (register new user)
2. Login as new user
3. Complete shop profile
4. Go to Customers
5. ✅ Should see empty list (no access to admin's customers)

## Still Having Issues?

### Check These:

1. **Python version**: Make sure you're using Python 3.7+
   ```bash
   python --version
   ```

2. **Dependencies installed**: 
   ```bash
   pip install -r requirements.txt
   ```

3. **Instance folder exists**:
   ```bash
   # Create if missing
   mkdir instance
   ```

4. **Permissions**: Make sure you have write permissions in the project directory

5. **Port already in use**:
   ```bash
   # Change port in app.py or kill existing process
   ```

## Error Messages Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| `IntegrityError` | Database constraint violation | Delete and recreate DB |
| `OperationalError` | Database schema mismatch | Run fix_database.py |
| `AttributeError` | Code trying to access missing property | Update code/DB |
| `Customer not found` | Access denied or doesn't exist | Check user ownership |
| `Session expired` | Need to login again | Logout and login |

## Prevention

To avoid these issues in future:

1. **Always backup before major changes**
   ```bash
   copy instance\girvi.db instance\backup_YYYYMMDD.db
   ```

2. **Use version control** (Git)
   ```bash
   git add .
   git commit -m "Before database changes"
   ```

3. **Test in development first**
   - Use separate database for testing
   - Don't test on production data

4. **Document your changes**
   - Keep notes of what you changed
   - Makes rollback easier

## Contact Support

If none of these solutions work:
1. Check the error message carefully
2. Note what you were trying to do
3. Check if you have the latest code version
4. Try the fresh start approach as last resort

## Quick Command Reference

```bash
# Fresh start (Windows)
del instance\girvi.db
python app.py

# With backup (Windows)
copy instance\girvi.db instance\backup.db
del instance\girvi.db
python app.py

# Fix database
python fix_database.py
python app.py

# Migrate existing data
python migrate_customers.py

# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt
```
