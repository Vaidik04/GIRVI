# ⚡ Deploy to Heroku in 5 Minutes

## What You Need
1. Heroku account (free): https://signup.heroku.com
2. Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
3. Git: https://git-scm.com

---

## 🚀 Three Ways to Deploy

### Method 1: Automatic Script (Easiest!)

```bash
cd d:\Python\Projects\WebApplications\Girvi
DEPLOY_NOW.bat
```

**That's it!** The script will:
- Check prerequisites
- Login to Heroku
- Create app
- Deploy code
- Initialize database
- Give you the URL

---

### Method 2: Manual Commands (5 minutes)

```bash
cd d:\Python\Projects\WebApplications\Girvi

# 1. Login
heroku login

# 2. Create app
heroku create

# 3. Initialize git
git init
git add .
git commit -m "Deploy Girvi backend"

# 4. Deploy
git push heroku main

# 5. Init database
heroku run python -c "from app import app, init_db; init_db()"

# 6. Open app
heroku open
```

---

### Method 3: Heroku Dashboard (No CLI needed)

1. Go to https://dashboard.heroku.com
2. Click "New" → "Create new app"
3. Name your app → "Create app"
4. Deploy tab → Connect to GitHub:
   - Connect your GitHub account
   - Search for your repo
   - Enable automatic deploys
5. Manual deploy → "Deploy Branch"

---

## ✅ After Deployment

### Get Your App URL

After deployment completes, you'll see:
```
https://your-app-name.herokuapp.com
```

### Test It

**Browser:**
```
https://your-app-name.herokuapp.com/api/mobile/health
```

**Should show:**
```json
{"status":"ok","message":"Server is running"}
```

### Update Mobile App

**Edit:** `d:\Python\Projects\WebApplications\GirviMobile\lib\main.dart`

**Line 16, change:**
```dart
defaultValue: 'https://your-app-name.herokuapp.com'
```

---

## 🎯 Quick Commands

```bash
# View logs
heroku logs --tail

# Restart app
heroku restart

# Open in browser
heroku open

# Run commands on server
heroku run python

# Check app info
heroku info
```

---

## 💡 What Was Done

Files created for Heroku:
- ✅ `Procfile` - Tells Heroku to use Gunicorn
- ✅ `runtime.txt` - Python 3.9.18
- ✅ `requirements.txt` - Added gunicorn
- ✅ `.gitignore` - Ignore sensitive files
- ✅ `app.py` - Updated for Heroku (PostgreSQL support, PORT env var)

---

## 🐛 Troubleshooting

### "Heroku not found"
Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

### "Git not found"
Install Git: https://git-scm.com/download/win

### "App name already taken"
Use different name or let Heroku auto-generate

### "Deployment failed"
```bash
heroku logs --tail
```

### App sleeps (free tier)
- Normal! Wakes up on first request
- Takes 5-10 seconds
- Upgrade to paid plan to prevent sleeping

---

## 💰 Costs

**Free Tier (Eco Dynos):**
- $5/month for 1000 dyno hours
- App sleeps after 30 mins inactivity
- Perfect for testing!

**To prevent sleeping:**
- Upgrade to Basic ($7/month)

---

## 📱 Next: Update Mobile App

After deployment:

1. **Note your Heroku URL**
2. **Update mobile app:**
   ```dart
   // lib/main.dart line 16
   defaultValue: 'https://YOUR-APP.herokuapp.com'
   ```
3. **Rebuild mobile app:**
   ```bash
   cd d:\Python\Projects\WebApplications\GirviMobile
   flutter build apk --release
   ```
4. **Test connection** from mobile app
5. **Publish to Play Store!**

---

**Ready? Run `DEPLOY_NOW.bat` now!**
