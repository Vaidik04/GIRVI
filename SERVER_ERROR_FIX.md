# 🚨 SERVER ERROR - QUICK FIX

## The Problem
Server won't start or crashes when trying to use customer features.

## FASTEST FIX (3 Steps) ⚡

### Step 1: Stop the Server
Press `Ctrl+C` in the terminal

### Step 2: Delete Old Database
```bash
del instance\girvi.db
```

### Step 3: Start Again
```bash
python app.py
```

✅ **Done!** The server will create a fresh database automatically.

---

## Even Faster (Windows)

Just double-click: **`EMERGENCY_FIX.bat`**

It does everything for you!

---

## What to Do After Fix

1. **Open browser:** http://localhost:5000

2. **Login:**
   - Username: `admin`
   - Password: `admin123`

3. **Complete Shop Profile** (first time only)
   - Fill in your shop details
   - Click Save

4. **Try Creating Customer:**
   - Go to Customers
   - Click "Add New Customer"
   - Fill in details
   - Click Save
   - ✅ Should work now!

---

## The Error Message You Might Have Seen

```
OperationalError: no such column: customer.user_id
```
or
```
IntegrityError: NOT NULL constraint failed: customer.user_id
```
or
```
Internal Server Error
```

## Why This Happened

We added a new security feature for **data isolation** between users. The old database doesn't have the new structure.

## Will I Lose Data?

- If this is a **new installation** or **testing** → No data to lose ✅
- If you have **important data** → Use the migration script instead:
  ```bash
  python migrate_customers.py
  ```

But honestly, for most cases, the fresh start is cleaner and easier.

---

## Full Troubleshooting

If the quick fix doesn't work, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Prevention

After fixing, the app will show this message when you start:
```
✓ Database schema is up to date.
```

If you see a warning message instead, run the fix again.

---

## Still Getting Errors?

### Check 1: Python Version
```bash
python --version
```
Should be 3.7 or higher

### Check 2: Dependencies
```bash
pip install -r requirements.txt
```

### Check 3: Instance Folder
Make sure `instance` folder exists:
```bash
mkdir instance
```

### Check 4: Port
If port 5000 is already in use:
- Kill the other process
- Or change port in app.py

---

## Quick Commands

```bash
# Fresh start (recommended)
del instance\girvi.db
python app.py

# With migration (if you have data)
python migrate_customers.py
python app.py

# Emergency fix (Windows)
EMERGENCY_FIX.bat
```

---

**Remember:** After any fix, login and complete shop profile before using the app!
