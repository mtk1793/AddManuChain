# src/services/auth_service.py
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.db.connection import get_db_session
from src.db.models.user import User
from src.utils.auth import hash_password


def verify_password(stored_password, provided_password):
    salt, _ = stored_password.split("$")
    recomputed = hash_password(provided_password, salt)
    print(f"🔐 Stored password:    {stored_password}")
    print(f"🔁 Recomputed password: {recomputed}")
    return stored_password == recomputed


def get_all_users():
    """Get all users from the database."""
    with get_db_session() as db_session:
        try:
            users = db_session.query(User).all()
            return users
        except Exception as e:
            return []


def get_user_by_id(user_id, db_session=None):
    """
    Get a user by ID.
    
    Args:
        user_id: The ID of the user to fetch
        db_session: Optional SQLAlchemy session. If not provided, a new session will be created.
    
    Returns:
        User object or None
    """
    if db_session:
        # Use the provided session
        try:
            return db_session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            print(f"Error fetching user by ID with provided session: {e}")
            return None
    else:
        # Create a new session
        with get_db_session() as new_session:
            try:
                return new_session.query(User).filter(User.id == user_id).first()
            except Exception as e:
                print(f"Error fetching user by ID: {e}")
                return None


def create_user(
    username, password, first_name, last_name, email, role, phone=None, is_active=True
):
    """Create a new user in the database."""
    with get_db_session() as db_session:  # Use context manager properly
        try:
            # Hash the password
            hashed_password = hash_password(password)

            # Create the user
            new_user = User(
                username=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                phone=phone,
                is_active=is_active,
                created_at=datetime.utcnow(),
            )

            db_session.add(new_user)
            db_session.commit()

            return True
        except IntegrityError:
            db_session.rollback()
            return False
        except Exception as e:
            db_session.rollback()
            return False


def update_user(user_id, user_data):
    """Update an existing user in the database."""
    with get_db_session() as db_session:  # Use context manager properly
        try:
            user = db_session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            # Update user properties
            if "username" in user_data:
                user.username = user_data["username"]
            if "password" in user_data:
                user.password = hash_password(user_data["password"])
            if "first_name" in user_data:
                user.first_name = user_data["first_name"]
            if "last_name" in user_data:
                user.last_name = user_data["last_name"]
            if "email" in user_data:
                user.email = user_data["email"]
            if "role" in user_data:
                user.role = user_data["role"]
            if "phone" in user_data:
                user.phone = user_data["phone"]
            if "is_active" in user_data:
                user.is_active = user_data["is_active"]

            db_session.commit()

            return True
        except IntegrityError:
            db_session.rollback()
            return False
        except Exception as e:
            db_session.rollback()
            return False


def deactivate_user(user_id):
    """Deactivate a user (soft delete)."""
    with get_db_session() as db_session:  # Use context manager properly
        try:
            user = db_session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            user.is_active = False
            db_session.commit()

            return True
        except Exception as e:
            db_session.rollback()
            return False


# ✅ ADDED FUNCTION: authenticate_user
def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    with get_db_session() as db_session:
        try:
            user = db_session.query(User).filter(User.username == username).first()

            if user and verify_password(user.password, password):
                # Update last login time
                user.last_login = datetime.utcnow()
                db_session.commit()

                # Convert user to dictionary before returning
                return {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_active": user.is_active,
                }

            return None
        except Exception as e:
            db_session.rollback()
            return None


def register_user(
    username, password, first_name, last_name, email, role="End User", phone=None
):
    with get_db_session() as db_session:  # Use context manager properly
        try:
            existing_user = db_session.query(User).filter_by(username=username).first()
            if existing_user:
                return False, "Username already exists"

            hashed_password = hash_password(password)
            new_user = User(
                username=username,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                phone=phone,
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db_session.add(new_user)
            db_session.commit()
            print(f"✅ Registered new user: {username}")
            return True, "User registered successfully"
        except Exception as e:
            db_session.rollback()
            print(f"❌ Error registering user: {e}")
            return False, f"Error: {e}"


def get_current_user_id(db_session):
    """
    Get the ID of the currently logged-in user.
    In a real app, this would typically check session data or authentication tokens.
    For mock purposes, we'll return a fixed ID.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        int: A user ID for the current session
    """
    # This is a placeholder implementation
    # In a real app, you'd get this from the session/cookies/token
    try:
        # For testing purposes, return the ID of the first admin user
        # or any user if no admin is found
        admin_user = db_session.query(User).filter(User.role == "admin").first()
        if admin_user:
            return admin_user.id

        # Fallback to any user
        any_user = db_session.query(User).first()
        if any_user:
            return any_user.id

        # No users in database
        return None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None
