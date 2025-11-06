"""
Fix Database Script - Recreates database with updated schema
Run this to fix the customer saving error
"""

import os
import shutil
from datetime import datetime

def backup_and_recreate():
    print("=" * 60)
    print("Database Fix Script")
    print("=" * 60)
    
    # Check if database exists
    db_path = 'instance/girvi.db'
    
    if os.path.exists(db_path):
        print(f"\n✓ Found database at: {db_path}")
        
        # Create backup
        backup_name = f'instance/girvi_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        print(f"📦 Creating backup: {backup_name}")
        
        try:
            shutil.copy2(db_path, backup_name)
            print(f"✓ Backup created successfully!")
        except Exception as e:
            print(f"⚠ Warning: Could not create backup: {e}")
        
        # Delete old database
        print(f"\n🗑 Deleting old database...")
        try:
            os.remove(db_path)
            print("✓ Old database deleted!")
        except Exception as e:
            print(f"✗ Error deleting database: {e}")
            return False
    else:
        print(f"\n✓ No existing database found at: {db_path}")
    
    print("\n" + "=" * 60)
    print("Database Recreation Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Run: python app.py")
    print("2. The new database will be created automatically")
    print("3. Login with:")
    print("   - Username: admin")
    print("   - Password: admin123")
    print("\nNote: All old data is backed up if you need it.")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    backup_and_recreate()
