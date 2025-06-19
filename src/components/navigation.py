# src/components/navigation.py
import streamlit as st

def create_sidebar():
    """Create the sidebar navigation menu based on user role."""

    with st.sidebar:
        st.image("static/images/logo.png", width=200)

        st.subheader(f"User: {st.session_state.username}")
        st.caption(f"Role: {st.session_state.user_role}")

        st.divider()

        # Dashboard navigation
        st.subheader("Navigation")

        # Main dashboard (this page)
        if st.button("📊 Dashboard", use_container_width=True):
            st.rerun()  # Refresh the page to show the main dashboard

        # User management - only for Admin and Manager roles
        if st.session_state.user_role in ["Admin", "Manager"]:
            if st.button(
                "👥 User Management", use_container_width=True, key="user_management"
            ):
                st.switch_page("pages/01_user_management.py")

        # Device management - for all roles
        if st.button("🖨️ Devices", use_container_width=True, key="devices"):
            st.switch_page("pages/02_devices.py")

        # Material management - for all roles
        if st.button("🧱 Materials", use_container_width=True, key="materials"):
            st.switch_page("pages/03_materials.py")

        # Product management - for all roles
        if st.button("📦 Products", use_container_width=True, key="products"):
            st.switch_page("pages/04_products.py")

        # Inventory management - for all roles (MOVED UP FOR VISIBILITY)
        if st.button("📋 Inventory Management", use_container_width=True, key="inventory"):
            st.switch_page("pages/13_inventory.py")

        # OEM management - for Admin and Manager roles
        if st.session_state.user_role in ["Admin", "Manager"]:
            if st.button("🏭 OEMs", use_container_width=True, key="oems"):
                st.switch_page("pages/05_oems.py")

        # Quality Assurance - for all roles
        if st.button(
            "✅ Quality Assurance", use_container_width=True, key="quality_assurance"
        ):
            st.switch_page("pages/06_quality_assurance.py")

        # Certifications - for all roles
        if st.button("📜 Certifications", use_container_width=True, key="certifications"):
            st.switch_page("pages/07_certifications.py")

        # Subscriptions - for Admin and Manager roles
        if st.session_state.user_role in ["Admin", "Manager"]:
            if st.button("💰 Subscriptions", use_container_width=True, key="subscriptions"):
                st.switch_page("pages/08_subscriptions.py")

        # Payments - for Admin and Manager roles
        if st.session_state.user_role in ["Admin", "Manager"]:
            if st.button("💳 Payments", use_container_width=True, key="payments"):
                st.switch_page("pages/09_payments.py")

        # Blueprints - for all roles
        if st.button("📐 Blueprints", use_container_width=True, key="blueprints"):
            st.switch_page("pages/10_blueprints.py")

        # Notifications - for all roles
        if st.button("🔔 Notifications", use_container_width=True, key="notifications"):
            st.switch_page("pages/11_notifications.py")

        # AI Assistant - for all roles
        if st.button("🤖 AI Assistant", use_container_width=True, key="ai_assistant"):
            st.switch_page("pages/12_ai_assistant.py")

        st.divider()

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()  # Call the logout function


def logout():
    # Clear session state for logout
    # Note: Cookie management removed due to import issues with streamlit_extras.cookies
    # This can be re-implemented with a working cookie library if needed
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()
