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
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --primary-dark: #1e40af;
        --accent-color: #3b82f6;
        --secondary-color: #64748b;
        --success-color: #059669;
        --success-hover: #047857;
        --warning-color: #d97706;
        --warning-hover: #b45309;
        --danger-color: #dc2626;
        --danger-hover: #b91c1c;
        --info-color: #0891b2;
        --text-white: #ffffff;
        --text-dark: #1e293b;
        --border-color: #e2e8f0;
        --border-radius: 8px;
        --border-radius-lg: 12px;
        --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        --box-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --transition: all 0.3s ease;
    }

    /* Full width container */
    .stApp {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }

    /* Main content area */
    .main .block-container {
        max-width: 100% !important;
        padding: 1rem 2rem !important;
        margin: 0 !important;
    }
    
    /* Hide Streamlit specific elements */
    .st-emotion-cache-1kyxreq.e115fcil2 {
        display: none !important;
    }

    /* Global animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

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

    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0); }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(37, 99, 235, 0.5); }
        50% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.7); }
        100% { box-shadow: 0 0 5px rgba(37, 99, 235, 0.5); }
    }

    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: 200px 0; }
    }

    /* Enhanced button styling */
    .stButton > button, button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: var(--transition) !important;
        box-shadow: var(--box-shadow) !important;
        cursor: pointer !important;
        animation: fadeIn 0.5s ease-out !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
        min-height: 44px !important;
    }

    .stButton > button:hover, button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3) !important;
        background: linear-gradient(135deg, var(--primary-hover), var(--primary-color)) !important;
    }

    .stButton > button:active, button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2) !important;
    }

    /* Button variants */
    .stButton > button.secondary {
        background: transparent !important;
        color: var(--primary-color) !important;
        border: 2px solid var(--primary-color) !important;
    }

    .stButton > button.secondary:hover {
        background: var(--primary-color) !important;
        color: var(--text-white) !important;
    }

    .stButton > button.success {
        background: linear-gradient(135deg, var(--success-color), var(--success-hover)) !important;
    }

    .stButton > button.warning {
        background: linear-gradient(135deg, var(--warning-color), var(--warning-hover)) !important;
    }

    .stButton > button.danger {
        background: linear-gradient(135deg, var(--danger-color), var(--danger-hover)) !important;
    }

    /* Enhanced Sidebar */
    div[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.9) 100%) !important;
        border-right: 4px solid var(--primary-color) !important;
        box-shadow: 8px 0 25px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(20px) !important;
        animation: slideInLeft 0.8s ease-out !important;
        position: relative !important;
    }

    div[data-testid="stSidebar"] > div:first-child::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 2px;
        height: 100%;
        background: linear-gradient(180deg, var(--primary-color), var(--accent-color));
        box-shadow: 0 0 15px var(--primary-color);
    }

    div[data-testid="stSidebar"] h1 {
        color: var(--primary-color) !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        padding: 2rem 1rem 1rem !important;
        text-align: center !important;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.2) !important;
        animation: slideInUp 1s ease-out !important;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px !important;
    }

    /* Enhanced Sidebar Navigation Buttons */
    div[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(248, 249, 250, 0.6)) !important;
        color: var(--text-dark) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        text-align: left !important;
        padding: 1.2rem 1.8rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: var(--border-radius-lg) !important;
        margin: 0.5rem 1rem !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        min-height: 56px !important;
    }

    div[data-testid="stSidebar"] .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.6s ease;
        z-index: 1;
    }

    div[data-testid="stSidebar"] .stButton>button:hover::before {
        left: 100%;
    }

    div[data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border-color: var(--primary-color) !important;
        transform: translateX(8px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    div[data-testid="stSidebar"] .stButton>button:active {
        transform: translateX(4px) scale(1.01) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Active page button styling */
    div[data-testid="stSidebar"] .stButton>button.active-page {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }

    /* Enhanced Cards and Containers */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
        background: rgba(255, 255, 255, 0.35) !important;
    }
    
    /* Enhanced Metric Values */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary-color), var(--info-color)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        animation: slideInUp 1s ease-out !important;
    }

    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-top: 0.5rem !important;
    }

    /* Enhanced Table Styling */
    .stDataFrame, table, .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--border-radius-lg) !important;
        border: 2px solid rgba(37, 99, 235, 0.1) !important;
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

    .stDataFrame tbody tr, table tbody tr, .dataframe tbody tr {
        transition: var(--transition) !important;
        border-bottom: 1px solid rgba(37, 99, 235, 0.1) !important;
    }

    .stDataFrame tbody tr:hover, table tbody tr:hover, .dataframe tbody tr:hover {
        background: rgba(37, 99, 235, 0.05) !important;
        transform: scale(1.01) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }

    .stDataFrame tbody td, table tbody td, .dataframe tbody td {
        padding: 1.2rem 1rem !important;
        color: var(--text-dark) !important;
        font-weight: 500 !important;
        border: none !important;
    }

    /* ENHANCED CHARTS AND GRAPHS */
    div[data-testid="stPlotlyChart"], .js-plotly-plot, .stPyplot {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--border-radius-lg) !important;
        border: 2px solid rgba(37, 99, 235, 0.1) !important;
        box-shadow: var(--box-shadow-lg) !important;
        backdrop-filter: blur(15px) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        animation: fadeInScale 0.8s ease-out !important;
        position: relative !important;
        overflow: hidden !important;
    }

    div[data-testid="stPlotlyChart"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color), var(--info-color));
    }

    /* Enhanced Form Elements */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem !important;
        transition: var(--transition) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    /* Enhanced Number Inputs */
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem 1rem !important;
        transition: var(--transition) !important;
    }

    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* Enhanced Date Inputs */
    .stDateInput, .stTimeInput {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--border-radius) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: var(--transition) !important;
    }

    .stDateInput:focus-within, .stTimeInput:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), 0 8px 20px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }

    /* Enhanced Headers */
    h1, h2, h3 {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        animation: slideInUp 0.6s ease-out !important;
    }

    h1, h2, h3 {
        background: linear-gradient(135deg, var(--primary-color), var(--info-color)) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* Enhanced Text Elements */
    p, .stMarkdown {
        color: var(--text-dark) !important;
        line-height: 1.6 !important;
    }

    /* ENHANCED NOTIFICATIONS AND ALERTS */
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: var(--border-radius-lg) !important;
        border: none !important;
        backdrop-filter: blur(15px) !important;
        box-shadow: var(--box-shadow) !important;
        padding: 1.5rem 2rem !important;
        margin: 1rem 0 !important;
        font-weight: 600 !important;
        animation: slideInRight 0.5s ease-out !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stSuccess {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.9), rgba(4, 120, 87, 0.8)) !important;
        color: var(--text-white) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(8, 145, 178, 0.9), rgba(14, 116, 144, 0.8)) !important;
        color: var(--text-white) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(217, 119, 6, 0.9), rgba(180, 83, 9, 0.8)) !important;
        color: var(--text-white) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    .stError {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.9), rgba(185, 28, 28, 0.8)) !important;
        color: var(--text-white) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    /* ENHANCED FILE UPLOADER */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 3px dashed rgba(37, 99, 235, 0.3) !important;
        border-radius: var(--border-radius-lg) !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: var(--transition) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    .stFileUploader:hover {
        border-color: var(--primary-color) !important;
        background: rgba(37, 99, 235, 0.05) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.15) !important;
    }

    /* ENHANCED PROGRESS BARS */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color)) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
        animation: shimmer 2s infinite !important;
    }

    .stProgress {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
    }

    /* ENHANCED CHECKBOX AND RADIO BUTTONS */
    .stCheckbox, .stRadio {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        transition: var(--transition) !important;
    }

    .stCheckbox:hover, .stRadio:hover {
        border-color: var(--primary-color) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.1) !important;
        transform: translateY(-2px) !important;
    }

    /* ENHANCED SELECTBOX AND MULTISELECT */
    .stSelectbox, .stMultiSelect {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--border-radius) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: var(--transition) !important;
    }

    .stSelectbox:focus-within, .stMultiSelect:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), 0 8px 20px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }

    /* ENHANCED EXPANDER */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(248, 249, 250, 0.8)) !important;
        border-radius: var(--border-radius) !important;
        border: 2px solid rgba(37, 99, 235, 0.2) !important;
        padding: 1.2rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: var(--text-dark) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: var(--transition) !important;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border-color: var(--primary-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.2) !important;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 0 0 var(--border-radius) var(--border-radius) !important;
        border: 1px solid rgba(37, 99, 235, 0.1) !important;
        border-top: none !important;
        backdrop-filter: blur(10px) !important;
        padding: 1.5rem !important;
        animation: slideInUp 0.4s ease-out !important;
    }

    /* ENHANCED TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: var(--border-radius) !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(37, 99, 235, 0.1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        padding: 0.5rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-dark) !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
        border: 2px solid transparent !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(37, 99, 235, 0.1) !important;
        border-color: rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        color: var(--text-white) !important;
        border-color: var(--primary-color) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    /* ENHANCED SCROLLBAR */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-hover), var(--primary-dark));
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
    }

    /* Fade-in animation for sections */
    .fade-in-section {
        opacity: 0;
        transform: translateY(20px);
        animation: fadeInSection 0.8s ease-out forwards;
    }

    @keyframes fadeInSection {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Staggered animation delays */
    .fade-in-section:nth-child(1) { animation-delay: 0.1s; }
    .fade-in-section:nth-child(2) { animation-delay: 0.2s; }
    .fade-in-section:nth-child(3) { animation-delay: 0.3s; }
    .fade-in-section:nth-child(4) { animation-delay: 0.4s; }
    .fade-in-section:nth-child(5) { animation-delay: 0.5s; }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem 1rem !important;
        }
        
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
        }

        div[data-testid="metric-container"] {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-size: 2rem !important;
        }
        
        div[data-testid="column"] > div {
            margin: 0.25rem !important;
            padding: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
