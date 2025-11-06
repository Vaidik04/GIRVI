# Girvi Backend Deployment

## Local run
```
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:JWT_SECRET = "your-strong-secret"
$env:FLASK_ENV = "development"
python app.py
```
App runs at http://127.0.0.1:5000

## Docker
```
docker build -t girvi-backend .
docker run -p 5000:5000 -e JWT_SECRET=your-strong-secret girvi-backend
```

## Production (Gunicorn)
- Ensure HTTPS via reverse proxy (Nginx) and set `FLASK_ENV=production`.
- Recommended env vars:
  - `JWT_SECRET`
  - `SQLALCHEMY_DATABASE_URI` (use PostgreSQL/MySQL in production) 
  - `SECRET_KEY` (override Flask secret)

Example systemd service behind Nginx is typical; or deploy on Render/Railway/Fly.io using the Dockerfile or Procfile.

