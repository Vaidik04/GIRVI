# Test Web Application

## The 401 Error You're Seeing

The error you're seeing is from the **Mobile API**, not the web application. 

```
DioException [bad response]: status code of 401
```

This means:
- ✅ The server IS running
- ❌ But the mobile app can't authenticate

## Let's Test the Web App First

### Step 1: Open Web Browser
Go to: **http://localhost:5000**

### Step 2: You Should See
- Home page with login/register options
- OR if already logged in, you'll see the dashboard

### Step 3: Login
- Username: `admin`
- Password: `admin123`

### Step 4: Complete Shop Profile
- Fill in your shop details
- Click Save

### Step 5: Test Customer Features
1. Go to **Customers** menu
2. Click **Add New Customer**
3. Fill in:
   - Name: `Test Customer`
   - Phone: `9876543210`
4. Click **Save**

✅ **If this works, the web app is fine!**

---

## If You're Testing Mobile API

The 401 error means you need to:

### 1. Register a User via API
```bash
POST http://localhost:5000/api/mobile/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

### 2. Login to Get Token
```bash
POST http://localhost:5000/api/mobile/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {...}
}
```

### 3. Use Token in Requests
```bash
GET http://localhost:5000/api/mobile/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Quick Test Commands

### Test Server is Running
```bash
curl http://localhost:5000/api/mobile/health
```

Should return:
```json
{"status": "ok", "message": "Server is running"}
```

### Test Login Endpoint
```bash
curl -X POST http://localhost:5000/api/mobile/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Should return a JWT token.

---

## What To Do Now

**Option 1: Use Web Application**
- Open browser: http://localhost:5000
- Login with admin/admin123
- Everything should work!

**Option 2: Fix Mobile App**
- Make sure mobile app is sending JWT token
- Token format: `Authorization: Bearer <token>`
- Get token from login API first

---

## Is Server Running?

Check terminal where you ran `python app.py`:

✅ **Good:**
```
Database initialized with admin user.
✓ Database schema is up to date.
* Running on http://0.0.0.0:5000
```

❌ **Bad:**
```
⚠ WARNING: DATABASE SCHEMA IS OUTDATED!
```

If you see the warning, run:
```bash
del instance\girvi.db
python app.py
```

---

## Summary

**The 401 error is NORMAL for mobile API without authentication!**

To use the system:
1. ✅ Open **web browser**: http://localhost:5000
2. ✅ Login: admin / admin123
3. ✅ Use the web interface

For mobile API:
1. First call `/api/mobile/auth/login` to get token
2. Then use that token in all other requests
3. Format: `Authorization: Bearer <token>`
