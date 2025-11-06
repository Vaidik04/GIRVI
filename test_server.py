"""Test if all dependencies are installed correctly"""
import sys

def test_imports():
    try:
        import flask
        print(f"[OK] Flask installed")
    except ImportError as e:
        print(f"[FAIL] Flask: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print(f"[OK] Flask-SQLAlchemy installed")
    except ImportError as e:
        print(f"[FAIL] Flask-SQLAlchemy: {e}")
        return False
    
    try:
        import flask_cors
        print("[OK] Flask-CORS installed")
    except ImportError as e:
        print(f"[FAIL] Flask-CORS: {e}")
        return False
    
    try:
        import jwt
        print(f"[OK] PyJWT installed")
    except ImportError as e:
        print(f"[FAIL] PyJWT: {e}")
        return False
    
    try:
        import werkzeug
        print(f"[OK] Werkzeug installed")
    except ImportError as e:
        print(f"[FAIL] Werkzeug: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Girvi Backend Dependencies...")
    print("=" * 50)
    if test_imports():
        print("=" * 50)
        print("[SUCCESS] All dependencies installed!")
        print("\nYou can now run: python app.py")
        sys.exit(0)
    else:
        print("=" * 50)
        print("[ERROR] Some dependencies are missing!")
        print("\nInstall them with: pip install -r requirements.txt")
        sys.exit(1)
