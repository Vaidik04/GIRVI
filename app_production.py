# Production-ready modifications for app.py
# These changes should be made to app.py for Heroku deployment

import os

# Use PostgreSQL on Heroku, SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Heroku provides postgres://, but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///girvi.db'

# Use environment variables for secrets
SECRET_KEY = os.environ.get('SECRET_KEY', '38a0b87477399b6e88676dd3da2508e76d7ff07c56597b6d24f4f3a13a40f1bd')
JWT_SECRET = os.environ.get('JWT_SECRET', SECRET_KEY)

# Disable debug in production
DEBUG = os.environ.get('FLASK_ENV') != 'production'

# Port configuration for Heroku
PORT = int(os.environ.get('PORT', 5000))

# Add these lines at the bottom of app.py instead of the current if __name__ == '__main__':
# if __name__ == '__main__':
#     init_db()
#     app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
