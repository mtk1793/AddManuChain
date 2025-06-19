import streamlit as st
from src.services.auth_service import register_user
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_register_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="Register | MITACS Dashboard",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed", # Keep sidebar collapsed for auth pages
)

# Inject universal CSS styling
inject_universal_css()

# Add AI page context for this page
add_ai_page_context("register", get_register_page_context())

st.markdown("<div class=\'auth-container\'>", unsafe_allow_html=True)
st.markdown("<div class=\'auth-form-box\'>", unsafe_allow_html=True)


st.markdown("<h1>Create Your MITACS Account</h1>", unsafe_allow_html=True) # Updated Title

with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name", placeholder="First Name", label_visibility="collapsed")
    with col2:
        last_name = st.text_input("Last Name", placeholder="Last Name", label_visibility="collapsed")
    
    username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
    email = st.text_input("Email", placeholder="Email", label_visibility="collapsed")
    phone = st.text_input("Phone (optional)", placeholder="Phone (optional)", label_visibility="collapsed")
    password = st.text_input("Password", type="password", placeholder="New Password", label_visibility="collapsed")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm New Password", label_visibility="collapsed")

    # Apply custom class for the register button
    st.markdown("<div class=\'register-button\'>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Sign Up", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not all([username, email, first_name, last_name, password, confirm_password]):
            st.error("Please fill in all required fields.")
        elif len(password) < 8: # Basic password strength check
            st.error("Password must be at least 8 characters long.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = register_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
            if success:
                st.success(message)
                st.info("Registration successful! You can now log in.") # Updated message
                # Add a delay and then switch page or show a button to go to login
                # For now, just info. User has to manually navigate.
                # Consider adding: time.sleep(2); st.switch_page("app.py") (if using st.switch_page)
            else:
                st.error(message)

st.markdown("<p style=\'text-align: center; margin-top: 20px;\'>Already have an account? <a href=\'/\' target=\'_self\'>Log In here</a></p>", unsafe_allow_html=True) # Updated link and text

st.markdown("</div>", unsafe_allow_html=True) # End auth-form-box

st.markdown("""
    <div class='auth-footer'>
        <p>&copy; 2024-2025 MITACS Project. All Rights Reserved.</p>
    </div>
""", unsafe_allow_html=True) # Consistent footer
st.markdown("</div>", unsafe_allow_html=True) # End auth-container

# Render AI assistant for this page
render_page_ai_assistant()
