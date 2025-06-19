import streamlit as st

def init_theme():
    """Initialize theme settings in session state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def toggle_theme():
    """Toggle between light and dark mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode

def get_current_theme():
    """Get current theme status"""
    init_theme()
    return "dark" if st.session_state.dark_mode else "light"

def is_dark_mode():
    """Check if dark mode is currently active"""
    init_theme()
    return st.session_state.dark_mode

def get_theme_colors():
    """Get color scheme based on current theme"""
    if st.session_state.get('dark_mode', False):
        return {
            'background': '#1e1e1e',
            'secondary_background': '#2d2d2d',
            'text': '#ffffff',
            'secondary_text': '#b0b0b0',
            'accent': '#4a9eff',
            'border': '#404040',
            'sidebar_bg': '#252525',
            'card_bg': '#333333',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'info': '#2196f3'
        }
    else:
        return {
            'background': '#ffffff',
            'secondary_background': '#f0f2f5',
            'text': '#262730',
            'secondary_text': '#555555',
            'accent': '#0066cc',
            'border': '#e0e0e0',
            'sidebar_bg': '#f0f2f5',
            'card_bg': '#ffffff',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8'
        }

def get_plotly_theme():
    """Get plotly theme configuration based on current theme"""
    colors = get_theme_colors()
    
    if st.session_state.get('dark_mode', False):
        return {
            'template': 'plotly_dark',
            'paper_bgcolor': colors['card_bg'],
            'plot_bgcolor': colors['card_bg'],
            'font_color': colors['text']
        }
    else:
        return {
            'template': 'plotly_white',
            'paper_bgcolor': colors['card_bg'],
            'plot_bgcolor': colors['card_bg'],
            'font_color': colors['text']
        }

def create_theme_aware_donut_chart(data, values, names, title="", hole=0.6, color_map=None):
    """Create a themed donut chart"""
    try:
        import plotly.express as px
        
        colors = get_theme_colors()
        theme = get_plotly_theme()
        
        # Default color map if none provided
        if color_map is None:
            color_map = {
                "Active": colors['success'],
                "Maintenance": colors['warning'], 
                "Offline": colors['error'],
                "Standby": colors['info'],
                "High": colors['success'],
                "Medium": colors['warning'],
                "Low": colors['error'],
                "In Stock": colors['success'],
                "Low Stock": colors['warning'],
                "Out of Stock": colors['error']
            }
        
        fig = px.pie(
            data,
            values=values,
            names=names,
            hole=hole,
            color=names,
            color_discrete_map=color_map,
            title=title
        )
        
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font_color=theme['font_color'],
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.2, 
                xanchor="center", 
                x=0.5,
                font_color=colors['text']
            ),
            title_font_color=colors['text']
        )
        
        # Add center annotation for donut charts
        if hole > 0:
            total = sum(data[values]) if hasattr(data, '__getitem__') else data[values].sum()
            fig.update_layout(
                annotations=[
                    dict(
                        text=f"<b>Total<br>{total}</b>",
                        x=0.5,
                        y=0.5,
                        font_size=20,
                        font_color=colors['text'],
                        showarrow=False,
                    )
                ]
            )
        
        return fig
    except ImportError:
        st.error("Plotly not available for themed charts")
        return None

def create_theme_aware_bar_chart(data, x, y, title="", orientation='v', color=None):
    """Create a themed bar chart"""
    try:
        import plotly.express as px
        
        colors = get_theme_colors()
        theme = get_plotly_theme()
        
        if orientation == 'v':
            fig = px.bar(data, x=x, y=y, title=title, color=color)
        else:
            fig = px.bar(data, x=y, y=x, title=title, color=color, orientation='h')
        
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font_color=theme['font_color'],
            margin=dict(l=20, r=20, t=50, b=20),
            title_font_color=colors['text'],
            xaxis=dict(color=colors['text']),
            yaxis=dict(color=colors['text'])
        )
        
        # Update bar colors to theme accent
        fig.update_traces(marker_color=colors['accent'])
        
        return fig
    except ImportError:
        st.error("Plotly not available for themed charts")
        return None

def create_theme_aware_line_chart(data, x, y, title="", color=None):
    """Create a themed line chart"""
    try:
        import plotly.express as px
        
        colors = get_theme_colors()
        theme = get_plotly_theme()
        
        fig = px.line(data, x=x, y=y, title=title, color=color)
        
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font_color=theme['font_color'],
            margin=dict(l=20, r=20, t=50, b=20),
            title_font_color=colors['text'],
            xaxis=dict(color=colors['text']),
            yaxis=dict(color=colors['text'])
        )
        
        # Update line colors
        fig.update_traces(line_color=colors['accent'])
        
        return fig
    except ImportError:
        st.error("Plotly not available for themed charts")
        return None

def create_theme_aware_bar_line_chart(data, x_col, y_bar_col, y_line_col, bar_name="Bar", line_name="Line", title=""):
    """Create a themed bar chart with line overlay"""
    try:
        import plotly.graph_objects as go
        
        colors = get_theme_colors()
        theme = get_plotly_theme()
        
        fig = go.Figure()
        
        # Add bar trace
        fig.add_trace(
            go.Bar(
                x=data[x_col],
                y=data[y_bar_col],
                name=bar_name,
                marker_color=colors['accent'],
            )
        )
        
        # Add line trace
        fig.add_trace(
            go.Scatter(
                x=data[x_col],
                y=data[y_line_col],
                name=line_name,
                mode="lines+markers",
                line=dict(color=colors['warning'], dash="dash"),
                marker=dict(symbol="diamond", color=colors['warning']),
            )
        )
        
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font_color=theme['font_color'],
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.2, 
                xanchor="center", 
                x=0.5,
                font_color=colors['text']
            ),
            title=title,
            title_font_color=colors['text'],
            xaxis=dict(color=colors['text']),
            yaxis=dict(color=colors['text']),
            hovermode="x unified",
        )
        
        return fig
    except ImportError:
        st.error("Plotly not available for themed charts")
        return None

def render_theme_toggle():
    """Render the theme toggle button"""
    init_theme()
    
    # Create toggle button with custom styling
    colors = get_theme_colors()
    theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
    theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    
    # Container for better positioning
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 1rem;">
            <div style="
                background: linear-gradient(135deg, {colors['accent']}, {colors['accent']}cc);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                cursor: pointer;
                transition: all 0.3s ease;
                user-select: none;
            " title="Toggle between light and dark theme">
                <span style="font-size: 1.1rem;">{theme_icon}</span>
                <span>{theme_text}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle", help="Toggle between light and dark theme"):
        toggle_theme()
        st.rerun()

def inject_theme_css():
    """Inject CSS based on current theme"""
    init_theme()
    colors = get_theme_colors()
    
    css = f"""
    <style>
    /* Theme Variables */
    :root {{
        --bg-primary: {colors['background']};
        --bg-secondary: {colors['secondary_background']};
        --text-primary: {colors['text']};
        --text-secondary: {colors['secondary_text']};
        --accent-color: {colors['accent']};
        --border-color: {colors['border']};
        --sidebar-bg: {colors['sidebar_bg']};
        --card-bg: {colors['card_bg']};
        --success-color: {colors['success']};
        --warning-color: {colors['warning']};
        --error-color: {colors['error']};
        --info-color: {colors['info']};
    }}
    
    /* Force dark mode on ALL elements */
    *, *::before, *::after {{
        color: {colors['text']} !important;
    }}
    
    /* Main App Background - Force override */
    .stApp, .stApp > div, .stApp > div > div {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Main content area - complete override */
    .main, .main > div, .main .block-container, .main .block-container > div {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* All divs and containers */
    div, section, header, footer, main, article, aside {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Sidebar Styling - Complete override */
    .css-1d391kg, .css-1lcbmhc, .css-1lcbmhc > div, 
    div[data-testid="stSidebar"], 
    div[data-testid="stSidebar"] > div,
    div[data-testid="stSidebar"] > div > div {{
        background-color: {colors['sidebar_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Sidebar content */
    div[data-testid="stSidebar"] > div:first-child {{
        background-color: {colors['sidebar_bg']} !important;
        border-right: 1px solid {colors['border']} !important;
    }}
    
    /* All sidebar elements */
    div[data-testid="stSidebar"] * {{
        background-color: transparent !important;
        color: {colors['text']} !important;
    }}
    
    /* Enhanced sidebar buttons with proper contrast */
    div[data-testid="stSidebar"] .stButton>button {{
        background: linear-gradient(135deg, {colors['card_bg']}, {colors['secondary_background']}) !important;
        color: {colors['text']} !important;
        border: 2px solid {colors['border']} !important;
        border-radius: 8px !important;
        margin: 0.25rem 0.5rem !important;
        padding: 0.875rem 1.25rem !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    div[data-testid="stSidebar"] .stButton>button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }}
    
    div[data-testid="stSidebar"] .stButton>button:hover::before {{
        left: 100%;
    }}
    
    div[data-testid="stSidebar"] .stButton>button:hover {{
        background: linear-gradient(135deg, {colors['accent']}, {colors['accent']}dd) !important;
        color: {colors['background']} !important;
        border-color: {colors['accent']} !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Content containers */
    .element-container, .stContainer, 
    div[data-testid="stVerticalBlock"], 
    div[data-testid="stHorizontalBlock"] {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Metrics - complete override */
    div[data-testid="metric-container"], 
    div[data-testid="metric-container"] > div,
    div[data-testid="metric-container"] * {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }}
    
    /* Charts background */
    .js-plotly-plot, .js-plotly-plot > div {{
        background-color: {colors['card_bg']} !important;
    }}
    
    /* Tables */
    .dataframe, .dataframe * {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    .dataframe th {{
        background-color: {colors['secondary_background']} !important;
        color: {colors['text']} !important;
        border-bottom: 1px solid {colors['border']} !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    input, textarea, select {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* Enhanced button styling with proper contrast */
    .stButton > button, button {{
        background: linear-gradient(135deg, {colors['accent']}, {colors['accent']}ee) !important;
        color: {colors['background']} !important;
        border: 2px solid {colors['accent']} !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.025em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        cursor: pointer !important;
        text-transform: none !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .stButton > button::before, button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }}
    
    .stButton > button:hover::before, button:hover::before {{
        left: 100%;
    }}
    
    .stButton > button:hover, button:hover {{
        background: linear-gradient(135deg, {colors['accent']}dd, {colors['accent']}bb) !important;
        color: {colors['background']} !important;
        border-color: {colors['accent']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
    }}
    
    .stButton > button:active, button:active {{
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* Secondary button variant */
    .stButton > button.secondary {{
        background: transparent !important;
        color: {colors['accent']} !important;
        border: 2px solid {colors['accent']} !important;
    }}
    
    .stButton > button.secondary:hover {{
        background: {colors['accent']} !important;
        color: {colors['background']} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {colors['secondary_background']} !important;
        border-bottom: 1px solid {colors['border']} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {colors['text']} !important;
        background-color: transparent !important;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {colors['accent']} !important;
        color: white !important;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div {{
        background-color: {colors['accent']} !important;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader, .streamlit-expanderHeader * {{
        background-color: {colors['secondary_background']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    .streamlit-expanderContent, .streamlit-expanderContent * {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
        border-top: none !important;
    }}
    
    /* Alerts */
    .stAlert, .stAlert * {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* Success alert */
    .stAlert[data-baseweb="notification"][kind="success"] {{
        background-color: {colors['success']}20 !important;
        border-color: {colors['success']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Warning alert */
    .stAlert[data-baseweb="notification"][kind="warning"] {{
        background-color: {colors['warning']}20 !important;
        border-color: {colors['warning']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Error alert */
    .stAlert[data-baseweb="notification"][kind="error"] {{
        background-color: {colors['error']}20 !important;
        border-color: {colors['error']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Info alert */
    .stAlert[data-baseweb="notification"][kind="info"] {{
        background-color: {colors['info']}20 !important;
        border-color: {colors['info']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Spinner */
    .stSpinner {{
        color: {colors['accent']} !important;
    }}
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6, p, span, div, label {{
        color: {colors['text']} !important;
    }}
    
    /* Links */
    a, a:visited {{
        color: {colors['accent']} !important;
    }}
    
    a:hover {{
        color: {colors['text']} !important;
    }}
    
    /* Popover (for AI Assistant) */
    .css-1lcbmhc, [data-baseweb="popover"] {{
        background-color: {colors['card_bg']} !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Custom maintenance calendar dark mode */
    .maintenance-calendar {{
        background: {colors['card_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    .calendar-header {{
        background: linear-gradient(135deg, {colors['accent']}, {colors['accent']}dd) !important;
        color: white !important;
    }}
    
    .calendar-day {{
        background-color: {colors['card_bg']} !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    
    .calendar-day:hover {{
        background-color: {colors['secondary_background']} !important;
    }}
    
    .calendar-day.today {{
        background-color: {colors['accent']}20 !important;
        border: 2px solid {colors['accent']} !important;
    }}
    
    .calendar-day-header {{
        background-color: {colors['secondary_background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Floating AI Assistant */
    .floating-ai-popover {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* Theme toggle button styling */
    .theme-toggle-btn {{
        background: linear-gradient(135deg, {colors['accent']}, {colors['accent']}dd) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }}
    
    .theme-toggle-btn:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        background: linear-gradient(135deg, {colors['accent']}ee, {colors['accent']}cc) !important;
    }}
    
    .theme-toggle-btn:active {{
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }}
    
    /* Override Streamlit's default styles more aggressively */
    .css-1d391kg, .css-1lcbmhc, .css-1wbqy5l, 
    .css-k1vhr4, .css-18e3th9, .css-1d391kg,
    .stApp > header, .stApp > footer,
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
        background-color: {colors['secondary_background']} !important;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {colors['secondary_background']} !important;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {colors['border']} !important;
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {colors['accent']} !important;
    }}
    
    /* Force override for any remaining light backgrounds */
    .element-container > div, .block-container > div,
    .css-k1vhr4 > div, .css-18e3th9 > div {{
        background-color: {colors['background']} !important;
    }}
    
    /* Additional comprehensive background overrides */
    .stApp, .stApp *, 
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainMenu"],
    .main .block-container,
    .main .block-container *,
    section[tabindex="0"],
    section[tabindex="0"] * {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Ensure all widgets respect the theme */
    .stSelectbox, .stTextInput, .stTextArea, .stNumberInput,
    .stMultiSelect, .stSlider, .stRadio, .stCheckbox {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Widget labels */
    .stSelectbox label, .stTextInput label, .stTextArea label,
    .stNumberInput label, .stMultiSelect label, .stSlider label,
    .stRadio label, .stCheckbox label {{
        color: {colors['text']} !important;
    }}
    
    /* File uploader */
    .stFileUploader, .stFileUploader * {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* Date and time inputs */
    .stDateInput, .stTimeInput {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
    }}
    
    /* Code blocks */
    .stCode, pre, code {{
        background-color: {colors['secondary_background']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
    }}
    
    /* Info/warning/error boxes */
    .stInfo, .stWarning, .stError, .stSuccess {{
        background-color: {colors['card_bg']} !important;
        color: {colors['text']} !important;
        border-left: 4px solid {colors['accent']} !important;
    }}
    
    /* Video and audio */
    .stVideo, .stAudio {{
        background-color: {colors['card_bg']} !important;
    }}
    
    /* Images */
    .stImage {{
        background-color: {colors['card_bg']} !important;
        border-radius: 8px !important;
    }}
    
    /* Smooth transitions */
    * {{
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def create_theme_aware_metric(label, value, delta=None, delta_color="normal"):
    """Create a themed metric card"""
    colors = get_theme_colors()
    
    delta_html = ""
    if delta is not None:
        delta_color_hex = colors['success'] if delta_color == "normal" else colors['error']
        delta_html = f'<div style="color: {delta_color_hex}; font-size: 0.8rem; margin-top: 0.2rem;">{delta}</div>'
    
    metric_html = f"""
    <div style="
        background-color: {colors['card_bg']};
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid {colors['border']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)'" 
       onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'">
        <div style="color: {colors['secondary_text']}; font-size: 0.9rem; margin-bottom: 0.5rem;">{label}</div>
        <div style="color: {colors['text']}; font-size: 2rem; font-weight: bold;">{value}</div>
        {delta_html}
    </div>
    """
    
    st.markdown(metric_html, unsafe_allow_html=True)

def create_theme_aware_card(title, content, icon="📊"):
    """Create a themed card component"""
    colors = get_theme_colors()
    
    card_html = f"""
    <div style="
        background-color: {colors['card_bg']};
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid {colors['border']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
    " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.15)'" 
       onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: {colors['text']};
        ">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <h3 style="margin: 0; color: {colors['text']};">{title}</h3>
        </div>
        <div style="color: {colors['text']};">
            {content}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
