"""
Helper functions to add AI assistant context to any page
"""
import streamlit as st

def add_ai_page_context(page_title, page_type, visible_elements=None, key_metrics=None, key_features=None, additional_context=None):
    """
    Add context for the AI assistant about the current page
    
    Args:
        page_title (str): Title of the current page
        page_type (str): Type of page (dashboard, management, analysis, etc.)
        visible_elements (list): List of visible UI elements and features
        key_metrics (dict): Key metrics or data visible on the page
        key_features (list): List of key features available on the page
        additional_context (dict): Any additional context specific to the page
    """
    if "current_page_data" not in st.session_state:
        st.session_state.current_page_data = {}
    
    context = {
        "page_title": page_title,
        "page_type": page_type,
        "visible_elements": visible_elements or [],
        "key_metrics": key_metrics or {},
        "key_features": key_features or [],
        "user_role": st.session_state.get("user_role", "user"),
        "username": st.session_state.get("username", "user")
    }
    
    if additional_context:
        context.update(additional_context)
    
    st.session_state.current_page_data.update(context)

def render_page_ai_assistant():
    """
    Render the floating AI assistant for any page
    Should be called at the end of each page's content
    """
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        from src.components.floating_ai_assistant import render_floating_ai_assistant
        
        # Render the floating AI assistant with custom positioning
        st.markdown('<div class="floating-ai-popover">', unsafe_allow_html=True)
        render_floating_ai_assistant()
        st.markdown('</div>', unsafe_allow_html=True)

# Page-specific context helpers
def get_device_page_context():
    """Context for device management page"""
    return {
        "visible_elements": [
            "Device list/table",
            "Add new device form", 
            "Device status filters",
            "Device details and specifications",
            "Maintenance schedules",
            "Device performance metrics"
        ],
        "key_features": [
            "Add/edit/delete devices",
            "Monitor device status",
            "Schedule maintenance",
            "View device history"
        ]
    }

def get_materials_page_context():
    """Context for materials management page"""
    return {
        "visible_elements": [
            "Materials inventory table",
            "Stock levels and alerts",
            "Material specifications",
            "Supplier information",
            "Reorder management",
            "Material usage statistics"
        ],
        "key_features": [
            "Manage material inventory",
            "Set reorder levels",
            "Track material usage",
            "Manage suppliers"
        ]
    }

def get_quality_page_context():
    """Context for quality assurance page"""
    return {
        "visible_elements": [
            "Quality metrics dashboard",
            "Test results table",
            "Quality standards checklist",
            "Defect tracking",
            "Quality reports",
            "Certification status"
        ],
        "key_features": [
            "Track quality metrics",
            "Manage quality tests",
            "Monitor compliance",
            "Generate quality reports"
        ]
    }

def get_blueprints_page_context():
    """Context for blueprints page"""
    return {
        "visible_elements": [
            "Blueprint library",
            "Upload new blueprints",
            "Blueprint specifications",
            "Version control",
            "Blueprint sharing",
            "Print history for blueprints"
        ],
        "key_features": [
            "Manage blueprint files",
            "Version tracking",
            "Blueprint specifications",
            "Print job integration"
        ]
    }

def get_user_management_page_context():
    """Context for user management page"""
    return {
        "visible_elements": [
            "User list/table",
            "Add new user form",
            "User roles and permissions",
            "User status filters",
            "User activity logs",
            "Profile management"
        ],
        "key_features": [
            "Add/edit/delete users",
            "Manage user roles",
            "Monitor user activity",
            "Control access permissions"
        ]
    }

def get_products_page_context():
    """Context for products page"""
    return {
        "visible_elements": [
            "Product catalog",
            "Product specifications",
            "Inventory levels",
            "Product categories",
            "Pricing information",
            "Product status tracking"
        ],
        "key_features": [
            "Manage product catalog",
            "Track inventory",
            "Update specifications",
            "Monitor product status"
        ]
    }

def get_oems_page_context():
    """Context for OEMs page"""
    return {
        "visible_elements": [
            "OEM partners list",
            "Partnership details",
            "Contract management",
            "Performance metrics",
            "Communication logs",
            "Collaboration tools"
        ],
        "key_features": [
            "Manage OEM partnerships",
            "Track performance",
            "Handle contracts",
            "Monitor collaboration"
        ]
    }

def get_certifications_page_context():
    """Context for certifications page"""
    return {
        "visible_elements": [
            "Certification list",
            "Certification status",
            "Compliance tracking",
            "Document management",
            "Renewal schedules",
            "Audit trails"
        ],
        "key_features": [
            "Manage certifications",
            "Track compliance",
            "Schedule renewals",
            "Monitor audit status"
        ]
    }

def get_subscriptions_page_context():
    """Context for subscriptions page"""
    return {
        "visible_elements": [
            "Subscription plans",
            "User subscriptions",
            "Billing information",
            "Usage metrics",
            "Plan comparisons",
            "Subscription status"
        ],
        "key_features": [
            "Manage subscription plans",
            "Track user subscriptions",
            "Monitor billing",
            "Analyze usage"
        ]
    }

def get_payments_page_context():
    """Context for payments page"""
    return {
        "visible_elements": [
            "Payment history",
            "Transaction details",
            "Payment methods",
            "Billing statements",
            "Payment status",
            "Financial reports"
        ],
        "key_features": [
            "Process payments",
            "Track transactions",
            "Manage billing",
            "Generate reports"
        ]
    }

def get_notifications_page_context():
    """Context for notifications page"""
    return {
        "visible_elements": [
            "Notification center",
            "Alert settings",
            "Message templates",
            "Delivery status",
            "Notification history",
            "User preferences"
        ],
        "key_features": [
            "Send notifications",
            "Configure alerts",
            "Manage templates",
            "Track delivery"
        ]
    }

def get_ai_assistant_page_context():
    """Context for AI assistant page"""
    return {
        "visible_elements": [
            "AI chat interface",
            "Conversation history",
            "AI capabilities",
            "Usage statistics",
            "Configuration settings",
            "Training data"
        ],
        "key_features": [
            "Chat with AI",
            "View history",
            "Configure AI",
            "Monitor usage"
        ]
    }

def get_register_page_context():
    """Context for registration page"""
    return {
        "visible_elements": [
            "Registration form",
            "User information fields",
            "Terms and conditions",
            "Email verification",
            "Password requirements",
            "Account setup"
        ],
        "key_features": [
            "Create new account",
            "Verify email",
            "Set password",
            "Complete profile"
        ]
    }
