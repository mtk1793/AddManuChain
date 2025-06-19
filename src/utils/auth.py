# src/utils/auth.py
import streamlit as st
import hashlib
import os
import secrets
from datetime import datetime
from src.db.connection import get_db_session
from src.db.models.user import User


def hash_password(password, salt=None):
    """Hash a password with a salt for secure storage."""
    if salt is None:
        salt = secrets.token_hex(16)

    # Combine password and salt, and hash using SHA-256
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()

    return f"{salt}${pwdhash}"


def verify_password(stored_password, provided_password):
    salt, _ = stored_password.split("$")
    recomputed = hash_password(provided_password, salt)
    print(f"🔐 Stored password:    {stored_password}")
    print(f"🔁 Recomputed password: {recomputed}")
    return stored_password == recomputed


def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    db_session = next(get_db_session())

    try:
        user = db_session.query(User).filter(User.username == username).first()

        if user and verify_password(user.password, password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db_session.commit()
            return user

        return None
    except Exception as e:
        db_session.rollback()
        return None


def check_authentication():
    """Check if the user is authenticated, and redirect to login if not."""
    if not st.session_state.get("authenticated", False):
        st.error("You are not logged in. Please login to access this page.")
        st.stop()


def check_authorization(allowed_roles):
    """Check if the authenticated user has one of the allowed roles or is admin."""
    check_authentication()

    user_role = st.session_state.get("user_role", "").lower()
    allowed_roles = [role.lower() for role in allowed_roles]

    if user_role == "admin" or user_role in allowed_roles:
        return  # Authorized

    st.error(
        f"Access denied. Your role ({user_role}) does not have permission to view this page."
    )
    st.stop()


def create_initial_admin(username=None, password=None, email=None, first_name=None, last_name=None):
    """Create an initial admin user if none exists."""
    with get_db_session() as db_session:  # CORRECT: using with statement for context manager
        # Check if any users exist
        user_count = db_session.query(User).count()

        if user_count == 0:
            # Use default credentials if none provided
            username = username or "admin"
            password = password or "admin123"
            email = email or "admin@mitacs.com"
            first_name = first_name or "System"
            last_name = last_name or "Administrator"
            
            # Create admin user with provided or default credentials
            # Generate salt and hash password
            hashed_password = hash_password(password)

            admin_user = User(
                username=username,
                password=hashed_password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role="Admin",
                is_active=True,
                created_at=datetime.now(),
            )

            db_session.add(admin_user)
            db_session.commit()

            print(f"✅ Initial admin user created: {username}")
            return True

        return False
