"""
Migration script to add user_id to existing customers
Run this ONCE after updating the Customer model
"""

from app import app, db, Customer, User
from datetime import datetime, timezone

def migrate_customers():
    with app.app_context():
        # Get all customers without user_id
        print("Starting customer migration...")
        
        # Get the first admin user to assign existing customers
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin user found. Creating default admin...")
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@girvimanagement.com',
                password=generate_password_hash('admin123'),
                role='admin',
                shop_profile_completed=False
            )
            db.session.add(admin)
            db.session.commit()
        
        # Count customers
        try:
            customers = db.session.query(Customer).all()
            print(f"Found {len(customers)} customers")
            
            # Assign all existing customers to admin
            updated = 0
            for customer in customers:
                if not hasattr(customer, 'user_id') or customer.user_id is None:
                    customer.user_id = admin.id
                    updated += 1
            
            db.session.commit()
            print(f"Migration complete! {updated} customers assigned to admin user.")
            
        except Exception as e:
            print(f"Migration may have already been completed or database needs to be recreated.")
            print(f"Error: {e}")
            print("\nIf you see a 'no such column' error, the database needs to be recreated.")
            print("To recreate the database:")
            print("1. Delete the instance/girvi.db file")
            print("2. Run the application - it will create a fresh database with the new schema")

if __name__ == '__main__':
    migrate_customers()
