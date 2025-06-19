# pages/01_user_management.py
import streamlit as st
import pandas as pd
from src.services.auth_service import (
    get_all_users,
    create_user,
    update_user,
    deactivate_user,
)
from src.utils.auth import check_authentication, check_authorization
from src.components.navigation import create_sidebar
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_user_management_page_context
from src.components.universal_css import inject_universal_css
from src.db.connection import get_db_session
from src.db.models.user import User

# Page configuration
st.set_page_config(
    page_title="User Management | MITACS Dashboard",
    page_icon="👥",
    layout="wide",
)

# Inject universal CSS styling
inject_universal_css()

# Role definitions - keep this consistent throughout the app
ROLES = ["Admin", "Manager", "Technician", "End User", "Certification Authority"]


def display_users():
    """Display the list of users with filtering options."""
    st.subheader("User Management")

    # Fetch users and convert to dictionaries while session is open
    with get_db_session() as session:
        users = session.query(User).all()

        # Convert to dictionaries to avoid DetachedInstanceError
        user_dicts = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "created_at": user.created_at,
                "phone": user.phone if hasattr(user, "phone") else None,
                # Add any other fields you need
            }
            for user in users
        ]

    # Now use user_dicts instead of the original user objects
    # Filters section
    col1, col2, col3 = st.columns(3)
    with col1:
        role_filter = st.multiselect(
            "Filter by Role", options=["All"] + ROLES, default=["All"]
        )

    with col2:
        status_filter = st.radio(
            "Status", options=["All", "Active", "Inactive"], horizontal=True
        )

    with col3:
        search_term = st.text_input(
            "Search by name or email", placeholder="Type to search..."
        )

    # Display users in a table
    st.markdown(f"### Users ({len(user_dicts)})")

    # Example of using the dictionaries
    users_data = [
        {
            "ID": u["id"],
            "Username": u["username"],
            "Email": u["email"],
            "Full Name": f"{u['first_name']} {u['last_name']}",
            "Role": u["role"],
            "Status": "Active" if u["is_active"] else "Inactive",
            "Last Login": u["last_login"].strftime("%Y-%m-%d %H:%M")
            if u["last_login"]
            else "Never",
        }
        for u in user_dicts
    ]

    # Apply filters
    filtered_df = pd.DataFrame(users_data)

    if "All" not in role_filter:
        filtered_df = filtered_df[filtered_df["Role"].isin(role_filter)]

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

    if search_term:
        filtered_df = filtered_df[
            filtered_df["Full Name"].str.contains(search_term, case=False)
            | filtered_df["Email"].str.contains(search_term, case=False)
            | filtered_df["Username"].str.contains(search_term, case=False)
        ]

    # Display user count
    st.caption(f"Showing {len(filtered_df)} of {len(users_data)} users")

    # Style the dataframe for better visibility
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="User account status",
                width="small",
                required=True,
            ),
            "Role": st.column_config.SelectboxColumn(
                "Role",
                help="User role defines permissions",
                width="medium",
                options=ROLES,
                required=True,
            ),
            "Email": st.column_config.LinkColumn(
                "Email",
                help="User's email address",
                width="medium",
                validate="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            ),
        },
        hide_index=True,
    )

    # Add action buttons below the table
    if st.button("Refresh User List"):
        st.rerun()

    if st.session_state.user_role == "Admin":
        if st.button("Export User List (CSV)"):
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv_data,
                file_name="users_export.csv",
                mime="text/csv",
            )


def add_user_form():
    """Display form to add a new user with improved validation."""
    st.subheader("Add New User")
    st.write("Create a new user account with appropriate role and permissions.")

    # Form for adding a new user
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Username*",
                placeholder="Enter username (lowercase, no spaces)",
                help="Username must be unique and will be used for login",
            )
            password = st.text_input(
                "Password*",
                type="password",
                help="Password should be at least 8 characters long",
            )
            confirm_password = st.text_input("Confirm Password*", type="password")
            first_name = st.text_input("First Name*", placeholder="Enter first name")

        with col2:
            last_name = st.text_input("Last Name*", placeholder="Enter last name")
            email = st.text_input(
                "Email*",
                placeholder="name@example.com",
                help="Enter a valid email address",
            )
            role = st.selectbox(
                "Role*", ROLES, help="Select the appropriate role for this user"
            )
            is_active = st.checkbox(
                "Active", value=True, help="Uncheck to create an inactive account"
            )

        # Additional information (optional)
        with st.expander("Additional Information (Optional)"):
            phone = st.text_input(
                "Phone Number",
                placeholder="Enter phone number",
                help="Format: +1-555-555-5555",
            )
            department = st.text_input("Department")
            notes = st.text_area("Notes")

        # Submit button for the form
        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
        with submit_col2:
            submit = st.form_submit_button("Create User", use_container_width=True)

        if submit:
            # Form validation
            if not (
                username
                and password
                and confirm_password
                and first_name
                and last_name
                and email
            ):
                st.error("Please fill in all required fields marked with *")
                return

            if password != confirm_password:
                st.error("Passwords do not match. Please try again.")
                return

            if len(password) < 8:
                st.error("Password must be at least 8 characters long.")
                return

            # Email validation (basic check)
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
                return

            # Create the user
            success = create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                phone=phone,
                is_active=is_active,
            )

            if success:
                st.success(f"User '{username}' has been created successfully!")
                st.info("The form will be cleared automatically. You can add another user now.")
            else:
                st.error(
                    "Failed to create user. The username or email may already be in use."
                )


def edit_user_form():
    """Display form to edit an existing user with improved UX."""
    st.subheader("Edit User")
    st.write("Modify an existing user's information or change their role/status.")

    # Fetch users and convert to dictionaries while session is open (like in display_users)
    with get_db_session() as session:
        users = session.query(User).all()

        # Convert to dictionaries to avoid DetachedInstanceError
        user_dicts = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "phone": user.phone if hasattr(user, "phone") else "",
                "display_name": f"{user.first_name} {user.last_name} ({user.username})",
            }
            for user in users
        ]

    if not user_dicts:
        st.info("No users available to edit.")
        return

    # Create a more user-friendly selection mechanism using dictionaries
    user_df = pd.DataFrame(user_dicts)

    # User selection with search capability
    selected_user_name = st.selectbox(
        "Select user to edit",
        user_df["display_name"].tolist(),
        index=0,
        help="Select a user to edit their information",
    )

    # Find the selected user in the DataFrame
    selected_user_data = user_df[user_df["display_name"] == selected_user_name].iloc[0]
    selected_user_id = selected_user_data["id"]

    # Edit form for the selected user
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Username*",
                value=selected_user_data["username"],
                help="Username cannot be changed if linked to existing data",
            )
            password = st.text_input(
                "New Password",
                type="password",
                placeholder="Leave blank to keep current password",
                help="Only enter if you want to change the password",
            )
            first_name = st.text_input(
                "First Name*", value=selected_user_data["first_name"]
            )
            last_name = st.text_input(
                "Last Name*", value=selected_user_data["last_name"]
            )

        with col2:
            email = st.text_input("Email*", value=selected_user_data["email"])

            # Fix for the role selection issue - we first find the index case-insensitively
            try:
                role_index = next(
                    (
                        i
                        for i, r in enumerate(ROLES)
                        if r.lower() == selected_user_data["role"].lower()
                    ),
                    0,
                )
            except:
                # Fallback if role is not in the list or there's another issue
                role_index = 0

            role = st.selectbox("Role*", ROLES, index=role_index)

            phone = st.text_input("Phone", value=selected_user_data["phone"])
            is_active = st.checkbox(
                "Active",
                value=selected_user_data["is_active"],
                help="Uncheck to deactivate this user account",
            )

        # Add danger zone for account actions
        st.write("---")
        st.markdown("#### Account Actions")

        col1, col2 = st.columns(2)
        with col1:
            reset_password = st.checkbox(
                "Send password reset email",
                help="This will send a password reset link to the user's email",
            )

        with col2:
            if not is_active:
                st.warning("⚠️ This user account will be deactivated")

        # Submit button for the edit form
        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
        with submit_col2:
            submit = st.form_submit_button("Update User", use_container_width=True)

        if submit:
            # Validate required fields
            if not (username and first_name and last_name and email):
                st.error("Please fill in all required fields marked with *")
                return

            # Email validation (basic check)
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
                return

            # Prepare user data for update
            user_data = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "role": role,
                "phone": phone,
                "is_active": is_active,
            }

            # Only include password if it was provided
            if password:
                user_data["password"] = password

            # Handle reset password option
            if reset_password:
                user_data["reset_password"] = True

            # Update the user
            success = update_user(selected_user_id, user_data)

            if success:
                st.success(f"User '{username}' has been updated successfully!")
                time_delay = 2  # seconds
                st.rerun()  # Refresh the page to show the updated user list
            else:
                st.error(
                    "Failed to update user. The username or email may already be in use."
                )


def main():
    """Main function to display the User Management page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="User Management",
        page_type="management",
        **get_user_management_page_context()
    )
    
    # Render the floating AI assistant
    render_page_ai_assistant()
    
    # Check if user is authenticated
    check_authentication()

    # Check if user has authorization
    check_authorization(["Admin", "Manager"])

    # Create sidebar navigation
    create_sidebar()

    # Page header
    st.title("👥 User Management")

    # Add some helpful information
    with st.expander("About User Management", expanded=False):
        st.markdown(
            """
        ### Managing Users
        
        This section allows you to manage user accounts in the system. You can:
        
        - **View all users** and filter by role, status, or search terms
        - **Create new users** with specific roles and permissions
        - **Edit existing users** to update their information or change their status
        - **Export user data** for reporting or backup purposes
        
        > Note: Only Admin users can deactivate accounts or change user roles.
        """
        )

    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["User List", "Add New User", "Edit User"])

    with tab1:
        display_users()

    with tab2:
        add_user_form()

    with tab3:
        edit_user_form()


if __name__ == "__main__":
    main()
