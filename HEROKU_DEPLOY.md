# 🚀 Deploy Flask Backend to Heroku - Step by Step

## Prerequisites
- Git installed
- Heroku account (free): https://signup.heroku.com
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli

---

## 📋 Files Created for Heroku

All required files have been created:
- ✅ `Procfile` - Tells Heroku how to run your app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `.gitignore` - Prevents sensitive files from being committed

---

## 🎯 Deployment Steps

### Step 1: Install Heroku CLI

**Download and Install:**
- Windows: https://devcenter.heroku.com/articles/heroku-cli#download-and-install
- Or run:
```bash
# Windows (using winget)
winget install Heroku.HerokuCLI

# Or download installer from Heroku website
```

**Verify installation:**
```bash
heroku --version
```

### Step 2: Login to Heroku

```bash
heroku login
```
- Browser will open
- Login with your Heroku credentials

### Step 3: Initialize Git Repository

```bash
cd d:\Python\Projects\WebApplications\Girvi

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Girvi backend"
```

### Step 4: Create Heroku App

```bash
# Create app with unique name
heroku create girvi-backend-yourname

# Or let Heroku generate a name
heroku create

# Note the URL shown: https://your-app-name.herokuapp.com
```

### Step 5: Deploy to Heroku

```bash
# Push to Heroku
git push heroku main

# Or if your branch is named master:
git push heroku master
```

**Wait 2-3 minutes for deployment...**

### Step 6: Initialize Database

```bash
# Run one-time database setup
heroku run python -c "from app import app, init_db; init_db()"

# Or open Python shell on Heroku
heroku run python
>>> from app import app, init_db
>>> init_db()
>>> exit()
```

### Step 7: Test Deployment

```bash
# Open in browser
heroku open

# Or test API health endpoint
curl https://your-app-name.herokuapp.com/api/mobile/health
```

**Expected response:**
```json
{"status":"ok","message":"Server is running"}
```

### Step 8: View Logs (if issues)

```bash
heroku logs --tail
```

---

## 🔧 Update Mobile App to Use Heroku URL

### Option 1: Update Default URL

Edit `d:\Python\Projects\WebApplications\GirviMobile\lib\main.dart` line 16:

```dart
const defaultUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://your-app-name.herokuapp.com'  // ← CHANGE THIS!
);
```

### Option 2: Use Settings Screen (No code change needed)

1. Run mobile app
2. Login screen → Tap ⚙️ Settings
3. Enter: `https://your-app-name.herokuapp.com`
4. Test Connection → Should show green ✓
5. Login

---

## 🎛️ Heroku Dashboard Management

**View your app:**
```bash
heroku open
```

**Open dashboard:**
```bash
heroku dashboard
```

**Or visit:** https://dashboard.heroku.com/apps

**Common commands:**
```bash
# View logs
heroku logs --tail

# Restart app
heroku restart

# Open database (if using Postgres)
heroku pg:info

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key

# View environment variables
heroku config
```

---

## 🗄️ Database Options

### Option 1: SQLite (Default - Temporary!)
- ⚠️ **WARNING:** SQLite data is lost when app restarts!
- Free tier apps sleep after 30 mins → Data lost!
- Only use for testing

### Option 2: PostgreSQL (Recommended for Production)

**Add Postgres:**
```bash
heroku addons:create heroku-postgresql:mini
```

**Update app.py for Postgres:**

```python
import os

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku uses postgres://, SQLAlchemy needs postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///girvi.db'
```

**Then redeploy:**
```bash
git add app.py
git commit -m "Add PostgreSQL support"
git push heroku main
```

---

## 🔒 Environment Variables (Security)

**Set production secrets:**
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set it on Heroku
heroku config:set SECRET_KEY=your-generated-secret-key
heroku config:set JWT_SECRET=your-jwt-secret
```

**Update app.py to use environment variables:**
Already done! The app checks for:
- `JWT_SECRET` environment variable
- Falls back to `SECRET_KEY`

---

## 📊 Monitor Your App

```bash
# View metrics
heroku logs --tail

# View app info
heroku info

# View running processes
heroku ps

# Scale dynos (if needed)
heroku ps:scale web=1
```

---

## 💰 Pricing & Limits

### Free Tier (Eco Dynos - $5/month for 1000 hours)
- App sleeps after 30 mins of inactivity
- Wakes up on first request (slow first load)
- 550-1000 hours/month
- Shared database

### Paid Tiers
- **Basic ($7/month):** Never sleeps, custom domain
- **Standard ($25/month):** More memory, better performance

**For testing: Free tier is fine!**

---

## 🐛 Troubleshooting

### Build fails?

**Check logs:**
```bash
heroku logs --tail
```

**Common issues:**
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Procfile syntax error

### App crashes?

**View crash logs:**
```bash
heroku logs --tail
```

**Restart app:**
```bash
heroku restart
```

### Can't connect from mobile?

**Test URL in browser:**
```
https://your-app-name.herokuapp.com/api/mobile/health
```

**Should return:**
```json
{"status":"ok","message":"Server is running"}
```

### Database not working?

**Check if using SQLite:**
- SQLite resets on every restart (dyno sleep)
- Upgrade to Postgres for persistence

---

## 🔄 Update Deployed App

**After making code changes:**

```bash
cd d:\Python\Projects\WebApplications\Girvi

# Stage changes
git add .

# Commit
git commit -m "Your update message"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## ✅ Deployment Checklist

Initial Setup:
- [ ] Heroku CLI installed
- [ ] Logged in: `heroku login`
- [ ] Git initialized: `git init`
- [ ] Files committed: `git commit -m "Initial"`

Deploy:
- [ ] Heroku app created: `heroku create`
- [ ] Code pushed: `git push heroku main`
- [ ] Database initialized: `heroku run python...`
- [ ] App tested: `heroku open`

Mobile App:
- [ ] Heroku URL noted
- [ ] Mobile app updated with URL
- [ ] Connection tested
- [ ] Login works

Production (Optional):
- [ ] PostgreSQL added
- [ ] Environment variables set
- [ ] Custom domain configured (paid plans)

---

## 🎯 Quick Commands Reference

```bash
# Deploy workflow
cd d:\Python\Projects\WebApplications\Girvi
git add .
git commit -m "Update"
git push heroku main

# Monitor
heroku logs --tail

# Manage
heroku restart
heroku ps
heroku config

# Database
heroku run python
heroku addons:create heroku-postgresql:mini
```

---

## 🌐 Your App URLs

After deployment, your app will be accessible at:

**API Base URL:**
```
https://your-app-name.herokuapp.com
```

**Health Check:**
```
https://your-app-name.herokuapp.com/api/mobile/health
```

**Admin Login (web interface):**
```
https://your-app-name.herokuapp.com/login
```

**Use this URL in your mobile app!**

---

## 🚀 Next Steps

1. **Deploy now** (follow steps above)
2. **Get your Heroku URL**
3. **Update mobile app** with URL
4. **Test connection**
5. **Publish mobile app** to Play Store

---

**Need help? Check Heroku documentation: https://devcenter.heroku.com**
