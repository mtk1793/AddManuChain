# init_db.py

import os
from dotenv import load_dotenv

# Import the init_db function from the centralized connection module
from src.db.connection import init_db as initialize_database, get_db_session
from src.db.models.user import User  # For admin creation
from src.utils.auth import hash_password

def main():
    load_dotenv()
    
    print("🚀 Starting database initialization...")
    initialize_database() # This will create all tables using the shared Base and engine

    print("🔍 Checking for admin user...")
    # Create admin user (if not exists) - logic moved from connection.py or kept here for clarity
    # This requires a session.
    with get_db_session() as db:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
        admin_last_name = os.getenv("ADMIN_LAST_NAME", "User")

        existing_admin = db.query(User).filter_by(username=admin_username).first()

        if not existing_admin:
            admin_user = User(
                username=admin_username,
                password=hash_password(admin_password), # Ensure hash_password is appropriately defined/imported
                email=admin_email,
                first_name=admin_first_name,
                last_name=admin_last_name,
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            # The commit is handled by the get_db_session context manager
            print("✅ Admin user created.")
        else:
            print("ℹ️ Admin user already exists.")
        
        # Create fixed standard test user (optional, can be moved to a seed script)
        test_username = "user"
        test_password = "user123"
        existing_user = db.query(User).filter_by(username=test_username).first()
        if not existing_user:
            test_user = User(
                username=test_username,
                password=hash_password(test_password),
                email="user@example.com",
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True
            )
            db.add(test_user)
            print("✅ Standard test user created.")
        else:
            print("ℹ️ Standard test user already exists.")

    print("🎉 Database initialization process complete.")

if __name__ == "__main__":
    main()

