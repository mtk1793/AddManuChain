"""
Universal CSS styling for all MITACS Dashboard pages.
This module provides consistent, modern styling across all pages.
"""

def inject_universal_css():
    """Inject clean, comprehensive CSS styling for all dashboard pages."""
    import streamlit as st
    
    st.markdown("""
    <style>
    /* Root variables for consistent theming */
    :root {
        --primary-color: #2E86C1;
        --primary-hover: #1B4F72;
        --secondary-color: #148F77;
        --secondary-hover: #0E6655;
        --accent-color: #F39C12;
        --accent-hover: #D68910;
        --background-primary: #FFFFFF;
        --background-secondary: #F8F9FA;
        --background-tertiary: #E8F4FD;
        --text-primary: #2C3E50;
        --text-secondary: #5D6D7E;
        --text-white: #FFFFFF;
        --text-muted: #85929E;
        --border-color: #D5DBDB;
        --border-light: #EBF5FB;
        --success-color: #27AE60;
        --warning-color: #F39C12;
        --danger-color: #E74C3C;
        --info-color: #3498DB;
        --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        --box-shadow-lg: 0 4px 20px rgba(0, 0, 0, 0.15);
        --border-radius: 12px;
        --border-radius-sm: 8px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Global page styling */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Hide Streamlit components */
    .stDeployButton, 
    footer,
    #MainMenu {
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }

    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }

    /* Metric cards styling */
    div[data-testid="metric-container"] {
        background: var(--background-primary) !important;
        border: 1px solid var(--border-light) !important;
        padding: 1.5rem !important;
        border-radius: var(--border-radius) !important;
        box-shadow: var(--box-shadow) !important;
        transition: var(--transition) !important;
        margin-bottom: 1rem !important;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--box-shadow-lg) !important;
    }

    div[data-testid="metric-container"] > div {
        color: var(--text-primary) !important;
    }

    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, var(--background-primary), var(--background-secondary)) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
        box-shadow: var(--box-shadow) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--box-shadow-lg) !important;
        background: linear-gradient(135deg, var(--primary-hover), var(--primary-color)) !important;
    }

    /* Select box styling */
    .stSelectbox > div > div {
        background: var(--background-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius-sm) !important;
    }

    /* Chart container styling */
    .js-plotly-plot {
        border-radius: var(--border-radius) !important;
        box-shadow: var(--box-shadow) !important;
        overflow: hidden !important;
        background: var(--background-primary) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Data frame styling */
    .stDataFrame {
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--box-shadow-lg) !important;
        backdrop-filter: blur(15px) !important;
        animation: fadeInScale 0.7s ease-out !important;
    }

    .stDataFrame thead th, table thead th, .dataframe thead th {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        font-weight: 700 !important;
        padding: 1.5rem 1rem !important;
        text-align: left !important;
        border: none !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
        letter-spacing: 0.5px !important;
    }

    .stDataFrame tbody td, table tbody td, .dataframe tbody td {
        padding: 1rem !important;
        border-bottom: 1px solid var(--border-light) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }

    .stDataFrame tbody tr:hover, table tbody tr:hover, .dataframe tbody tr:hover {
        background: var(--background-tertiary) !important;
        transform: scale(1.02) !important;
    }

    /* Text styling */
    .stMarkdown p {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
        font-size: 1rem !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--background-secondary) !important;
        border-radius: var(--border-radius-sm) !important;
        border: 1px solid var(--border-color) !important;
        padding: 0.75rem 1.5rem !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border-color: var(--primary-color) !important;
    }

    /* Animations */
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Column animations */
    div[data-testid="column"] {
        animation: slideInFromLeft 0.6s ease-out !important;
    }

    div[data-testid="column"]:nth-child(2) {
        animation-delay: 0.1s !important;
    }

    div[data-testid="column"]:nth-child(3) {
        animation-delay: 0.2s !important;
    }

    div[data-testid="column"]:nth-child(4) {
        animation-delay: 0.3s !important;
    }

    /* Error and success message styling */
    .stAlert {
        border-radius: var(--border-radius) !important;
        border: none !important;
        box-shadow: var(--box-shadow) !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
    }

    ::-webkit-scrollbar-track {
        background: var(--background-secondary) !important;
        border-radius: var(--border-radius-sm) !important;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-color) !important;
        border-radius: var(--border-radius-sm) !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-hover) !important;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        div[data-testid="column"] > div {
            margin: 0.25rem !important;
            padding: 1rem !important;
        }
    }
    </style>
    <script>
    (function() {
        const classNameToRemove = 'st-emotion-cache-1n5xqho'; // Primary class
        const secondaryClassName = 'eczjsme4'; // Secondary class

        function removeElements() {
            const elements = document.querySelectorAll('.' + classNameToRemove + '.' + secondaryClassName);
            elements.forEach(el => {
                if (el.parentNode) {
                    el.parentNode.removeChild(el);
                }
            });
        }

        // Initial removal attempt on script load
        removeElements();

        // Observe DOM changes to remove elements if they reappear
        const observer = new MutationObserver((mutationsList, obs) => {
            let needsRemoval = false;
            for (const mutation of mutationsList) {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.matches && node.matches('.' + classNameToRemove + '.' + secondaryClassName)) {
                            needsRemoval = true;
                        } else if (node.nodeType === 1 && node.querySelector && node.querySelector('.' + classNameToRemove + '.' + secondaryClassName)) {
                            needsRemoval = true;
                        }
                    });
                }
            }
            if (needsRemoval) {
                removeElements();
            }
        });

        // Start observing the body for added nodes and subtree modifications
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    })();
    </script>
    """, unsafe_allow_html=True)
