# app.py
import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from src.db.connection import init_db
from src.utils.auth import create_initial_admin
from src.components.ai_page_context import add_ai_page_context # Removed render_page_ai_assistant as it's not directly called here
from src.services import device_service, material_service, certification_service, auth_service # Added auth_service
from src.components.universal_css import inject_universal_css
from src.components.navigation import create_sidebar

# Page configuration
st.set_page_config(
    page_title="MITACS Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject universal CSS
inject_universal_css()

# Function to load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load custom CSS
load_css("static/css/custom.css")


# Initialize session state for authentication if not already done
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'dashboard_tab' not in st.session_state:
    st.session_state.dashboard_tab = "Production Overview"

# --- LOGIN LOGIC ---
def display_login_form():
    # st.markdown("<div class='auth-container'>", unsafe_allow_html=True) # Removed auth-container

    st.markdown("<h1>MITACS Dashboard Login</h1>", unsafe_allow_html=True)

    with st.form("login_form"):
        username_input = st.text_input("Username or Email", placeholder="Enter your username or email", key="login_username", label_visibility="collapsed")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password", label_visibility="collapsed")
        
        # Apply custom class for the login button
        st.markdown("<div class='login-button'>", unsafe_allow_html=True)
        login_button = st.form_submit_button("Login", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if login_button:
            if not username_input or not password_input:
                st.error("Username and password are required.")
            else:
                user = auth_service.authenticate_user(username_input, password_input)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.session_state.user_info = user # Store full user info if needed
                    st.success("Login successful!")
                    time.sleep(1) # Brief pause
                    st.rerun() # Rerun to show the main app
                else:
                    st.error("Invalid username or password.")
    
    st.markdown("<p style='text-align: center; margin-top: 20px;'>Don\'t have an account? <a href='/Register' target='_self'>Register here</a></p>", unsafe_allow_html=True)
    # st.markdown("</div>", unsafe_allow_html=True) # End auth-form-box
    # st.markdown("</div>", unsafe_allow_html=True) # End auth-container

# --- MAIN APPLICATION ---
def main_dashboard():
    # --- Import necessary modules for advanced dashboard ---
    from src.services import print_job_service, quality_service, maintenance_service
    import calendar
    from datetime import date, timedelta

    # Create sidebar navigation
    create_sidebar()

    # --- Dashboard Header with Enhanced View Options ---
    st.markdown("""
    <div class="dashboard-header">
        <div style="display:flex; justify-content:space-between; align-items:center">
            <div>
                <h1>MITACS Advanced Manufacturing Hub</h1>
                <p>Enterprise-grade manufacturing intelligence platform with real-time optimization</p>
            </div>
            <div style="text-align:right">
                <span class="last-updated">Last updated: {}</span>
            </div>
        </div>
    </div>
    """.format(datetime.now().strftime("%b %d, %Y %H:%M:%S")), unsafe_allow_html=True)
    
    # --- Dashboard Controls ---
    with st.expander("Dashboard Controls", expanded=False):
        control_col1, control_col2, control_col3 = st.columns([1,1,1])
        
        with control_col1:
            time_range = st.selectbox(
                "Time Range",
                ["Today", "Last 7 Days", "Last 30 Days", "Last Quarter", "Year to Date", "Custom Range"],
                index=2
            )
        
        with control_col2:
            location_filter = st.multiselect(
                "Manufacturing Location",
                ["Main Factory", "East Wing", "West Wing", "Remote Site 1", "Remote Site 2"],
                default=["Main Factory"]
            )
        
        with control_col3:
            refresh_rate = st.selectbox(
                "Auto-refresh Rate",
                ["Off", "30 seconds", "1 minute", "5 minutes", "15 minutes", "30 minutes"],
                index=3
            )
        
        if time_range == "Custom Range":
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            with date_col2:
                end_date = st.date_input("End Date", value=datetime.now())
    
    # Initialize session state for dashboard tabs if not exists
    if 'dashboard_tab' not in st.session_state:
        st.session_state.dashboard_tab = "Production Overview"
    
    # --- Executive Dashboard Navigation Tabs ---
    st.markdown('<div class="dashboard-tabs">', unsafe_allow_html=True)
    tab_col1, tab_col2, tab_col3, tab_col4, tab_col5, tab_col6 = st.columns([1,1,1,1,1,1])
    
    with tab_col1:
        if st.button("📊 Production", use_container_width=True, 
                    type="primary" if st.session_state.dashboard_tab == "Production Overview" else "secondary"):
            st.session_state.dashboard_tab = "Production Overview"
            
    with tab_col2:
        if st.button("🧪 Quality", use_container_width=True,
                    type="primary" if st.session_state.dashboard_tab == "Quality Metrics" else "secondary"):
            st.session_state.dashboard_tab = "Quality Metrics"
            
    with tab_col3:
        if st.button("⚙️ Equipment", use_container_width=True,
                    type="primary" if st.session_state.dashboard_tab == "Equipment Health" else "secondary"):
            st.session_state.dashboard_tab = "Equipment Health"
            
    with tab_col4:
        if st.button("🧰 Materials", use_container_width=True,
                    type="primary" if st.session_state.dashboard_tab == "Materials Analysis" else "secondary"):
            st.session_state.dashboard_tab = "Materials Analysis"
            
    with tab_col5:
        if st.button("📈 Analytics", use_container_width=True,
                    type="primary" if st.session_state.dashboard_tab == "Advanced Analytics" else "secondary"):
            st.session_state.dashboard_tab = "Advanced Analytics"
            
    with tab_col6:
        if st.button("🔮 Predictive", use_container_width=True,
                    type="primary" if st.session_state.dashboard_tab == "Predictive Insights" else "secondary"):
            st.session_state.dashboard_tab = "Predictive Insights"
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Horizontal Rule ---
    st.markdown("<hr/>", unsafe_allow_html=True)
    
    # --- Enhanced KPI Section with Trend Indicators ---
    st.markdown('<div class="section-header"><h3><span class="section-icon">📊</span>Manufacturing Intelligence - Key Performance Indicators</h3></div>', unsafe_allow_html=True)
    
    # Get core metrics data
    total_devices = device_service.get_total_devices()
    active_materials = material_service.get_active_materials_count()
    pending_certs = certification_service.get_pending_certifications_count()
    user_count = len(auth_service.get_all_users())


    # Fetch print job stats
    try:
        production_stats = print_job_service.get_print_job_statistics()
        success_rate = production_stats.get("success_rate", 0)
        avg_duration = production_stats.get("average_duration_minutes", 0)
        total_material_used = production_stats.get("total_material_used", 0)
    except Exception as e:
        print(f"Error fetching production stats: {str(e)}")
        success_rate = 85.5
        avg_duration = 120
        total_material_used = 1250.75
    
    # Create two rows of KPIs for better organization
    kpi_row1_col1, kpi_row1_col2, kpi_row1_col3, kpi_row1_col4 = st.columns(4)
    
    # Row 1: Device/Asset KPIs with enhanced styling
    with kpi_row1_col1:
        st.markdown("""
        <div class="kpi-card device-kpi">
            <div class="kpi-title">Total Devices</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-trend positive">↑ 5% from last month</div>
        </div>
        """.format(total_devices), unsafe_allow_html=True)
        st.metric(label="Total Devices", value=total_devices, delta="5%", delta_color="normal", label_visibility="collapsed")
        
    with kpi_row1_col2:
        st.markdown("""
        <div class="kpi-card material-kpi">
            <div class="kpi-title">Active Materials</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-trend negative">↓ 2% inventory decrease</div>
        </div>
        """.format(active_materials), unsafe_allow_html=True)
        st.metric(label="Active Materials", value=active_materials, delta="-2%", delta_color="inverse", label_visibility="collapsed")
        
    with kpi_row1_col3:
        st.markdown("""
        <div class="kpi-card cert-kpi">
            <div class="kpi-title">Pending Certifications</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-trend neutral">+10 since last week</div>
        </div>
        """.format(pending_certs), unsafe_allow_html=True)
        st.metric(label="Pending Certifications", value=pending_certs, delta="10 New", delta_color="off", label_visibility="collapsed")
        
    with kpi_row1_col4:
        st.markdown("""
        <div class="kpi-card user-kpi">
            <div class="kpi-title">Registered Users</div>
            <div class="kpi-value">{}</div>
            <div class="kpi-trend positive">+1 new this week</div>
        </div>
        """.format(user_count), unsafe_allow_html=True)
        st.metric(label="Registered Users", value=user_count, delta="1 new", delta_color="normal", label_visibility="collapsed")
    
    # Row 2: Production KPIs
    kpi_row2_col1, kpi_row2_col2, kpi_row2_col3, kpi_row2_col4 = st.columns(4)
    
    with kpi_row2_col1:
        st.markdown("""
        <div class="kpi-card production-kpi">
            <div class="kpi-title">Production Success Rate</div>
            <div class="kpi-value">{}%</div>
            <div class="kpi-trend positive">↑ 3.2% improvement</div>
        </div>
        """.format(success_rate), unsafe_allow_html=True)
        st.metric(label="Production Success Rate", value=f"{success_rate}%", delta="3.2%", delta_color="normal", label_visibility="collapsed")
        
    with kpi_row2_col2:
        st.markdown("""
        <div class="kpi-card time-kpi">
            <div class="kpi-title">Avg. Production Time</div>
            <div class="kpi-value">{} min</div>
            <div class="kpi-trend positive">↓ 8% faster</div>
        </div>
        """.format(avg_duration), unsafe_allow_html=True)
        st.metric(label="Avg. Production Time", value=f"{avg_duration} min", delta="-8%", delta_color="normal", label_visibility="collapsed")
        
    with kpi_row2_col3:
        st.markdown("""
        <div class="kpi-card material-usage-kpi">
            <div class="kpi-title">Material Consumption</div>
            <div class="kpi-value">{} kg</div>
            <div class="kpi-trend negative">↑ 5.3% usage</div>
        </div>
        """.format(round(total_material_used/1000, 2)), unsafe_allow_html=True)
        st.metric(label="Material Consumption", value=f"{round(total_material_used/1000, 2)} kg", delta="5.3%", delta_color="inverse", label_visibility="collapsed")
        
    with kpi_row2_col4:
        on_time_delivery = 93.7
        st.markdown("""
        <div class="kpi-card delivery-kpi">
            <div class="kpi-title">On-Time Delivery</div>
            <div class="kpi-value">{}%</div>
            <div class="kpi-trend positive">↑ 1.8% improvement</div>
        </div>
        """.format(on_time_delivery), unsafe_allow_html=True)
        st.metric(label="On-Time Delivery", value=f"{on_time_delivery}%", delta="1.8%", delta_color="normal", label_visibility="collapsed")
    
    # Add CSS for KPI cards
    st.markdown("""
    <style>
        .kpi-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-left: 4px solid #4CAF50;
            margin-bottom: 10px;
            transition: transform 0.3s ease;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        .kpi-title {
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            margin-bottom: 5px;
        }
        .kpi-trend {
            font-size: 0.8rem;
            font-style: italic;
        }
        .kpi-trend.positive {
            color: #4CAF50;
        }
        .kpi-trend.negative {
            color: #F44336;
        }
        .kpi-trend.neutral {
            color: #FFC107;
        }
        .device-kpi { border-left-color: #2196F3; }
        .material-kpi { border-left-color: #FF9800; }
        .cert-kpi { border-left-color: #E91E63; }
        .user-kpi { border-left-color: #9C27B0; }
        .production-kpi { border-left-color: #4CAF50; }
        .time-kpi { border-left-color: #00BCD4; }
        .material-usage-kpi { border-left-color: #FF5722; }
        .delivery-kpi { border-left-color: #8BC34A; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    
    # Display content based on selected tab
    if st.session_state.dashboard_tab == "Production Overview":
        # --- Production Overview Section ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">📊</span>Production Performance Analysis</h3></div>', unsafe_allow_html=True)
        
        # Production overview with monthly trend
        prod_col1, prod_col2 = st.columns([3, 2])
        
        with prod_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Monthly Production Output Trend")
            
            # Generate monthly production data
            months = list(calendar.month_abbr)[1:]
            current_month = datetime.now().month
            
            # Create production data with trend and seasonal pattern
            production_values = [
                4200, 4500, 4800, 5100, 5300, 5600,
                5900, 5700, 5500, 5800, 6000, 6200
            ]
            
            # Highlight current and future months differently
            highlight = [i >= current_month for i in range(1, 13)]
            
            # Create DataFrame for visualization
            monthly_production_df = pd.DataFrame({
                "Month": months,
                "Output": production_values,
                "Projected": highlight
            })
            
            # Create line chart with different colors for actual vs projected
            fig_monthly_prod = px.line(
                monthly_production_df, 
                x="Month", 
                y="Output",
                markers=True,
                color="Projected",
                color_discrete_map={True: "rgba(151, 166, 232, 0.8)", False: "rgba(0, 91, 150, 0.9)"},
                title="Production Volume by Month",
                line_shape="spline"
            )
            
            # Add goal line
            fig_monthly_prod.add_hline(
                y=5500, 
                line_dash="dash", 
                line_color="green", 
                annotation_text="Target",
                annotation_position="bottom right"
            )
            
            # Customize layout
            fig_monthly_prod.update_layout(
                xaxis_title="Month",
                yaxis_title="Units Produced",
                legend_title="Data Type",
                hovermode="x unified"
            )
            
            # Add annotations for key events
            fig_monthly_prod.add_annotation(
                x="Mar", 
                y=production_values[2] + 200, 
                text="New equipment",
                showarrow=True,
                arrowhead=1
            )
            
            fig_monthly_prod.add_annotation(
                x="Aug", 
                y=production_values[7] - 200, 
                text="Maintenance",
                showarrow=True,
                arrowhead=1
            )
            
            st.plotly_chart(fig_monthly_prod, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with prod_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Production Success Rate")
            
            # Create gauge chart for success rate
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Success Rate (%)"},
                delta={"reference": 80},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "rgba(50, 200, 100, 0.8)"},
                    "steps": [
                        {"range": [0, 50], "color": "rgba(255, 0, 0, 0.3)"},
                        {"range": [50, 80], "color": "rgba(255, 255, 0, 0.3)"},
                        {"range": [80, 100], "color": "rgba(0, 255, 0, 0.3)"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Add production breakdown pie chart
            status_data = {"Status": ["Completed", "In Progress", "Failed", "Scheduled"],
                           "Count": [62, 15, 8, 15]}
            status_df = pd.DataFrame(status_data)
            
            fig_status = px.pie(
                status_df, 
                values="Count", 
                names="Status",
                color="Status",
                color_discrete_map={
                    "Completed": "#4CAF50",
                    "In Progress": "#2196F3",
                    "Failed": "#F44336",
                    "Scheduled": "#FFC107"
                },
                title="Production Status Breakdown"
            )
            
            fig_status.update_traces(
                textposition="inside", 
                textinfo="percent+label",
                hole=0.4
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Detailed production table
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.subheader("Recent Production Runs")
        
        # Get recent print jobs
        recent_jobs = []
        try:
            recent_jobs = print_job_service.get_recent_print_jobs(limit=5)
        except:
            # Sample data if service fails
            recent_jobs = [
                {"id": 1, "name": "Prototype Bracket", "status": "Completed", "start_time": "2023-05-28 09:30:00", "end_time": "2023-05-28 14:45:00", "device_id": 1, "material_used": 125.5},
                {"id": 2, "name": "Medical Housing", "status": "Completed", "start_time": "2023-05-29 08:15:00", "end_time": "2023-05-29 11:30:00", "device_id": 2, "material_used": 89.3},
                {"id": 3, "name": "Gear Assembly", "status": "In Progress", "start_time": "2023-05-30 13:00:00", "end_time": None, "device_id": 3, "material_used": 67.8},
                {"id": 4, "name": "Container Lid", "status": "Failed", "start_time": "2023-05-27 14:20:00", "end_time": "2023-05-27 15:10:00", "device_id": 1, "material_used": 45.2},
                {"id": 5, "name": "Custom Fixture", "status": "Scheduled", "start_time": "2023-05-31 09:00:00", "end_time": None, "device_id": 2, "material_used": 0.0}
            ]
            
        # Convert to DataFrame for display
        if recent_jobs:
            recent_jobs_df = pd.DataFrame(recent_jobs)
            
            # Add styling for status column
            def highlight_status(val):
                color_map = {
                    "Completed": "background-color: rgba(76, 175, 80, 0.2)",
                    "In Progress": "background-color: rgba(33, 150, 243, 0.2)",
                    "Failed": "background-color: rgba(244, 67, 54, 0.2)",
                    "Scheduled": "background-color: rgba(255, 193, 7, 0.2)"
                }
                return color_map.get(val, "")
            
            # Apply styling and display
            st.dataframe(
                recent_jobs_df.style.applymap(highlight_status, subset=["status"]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent production jobs available")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif st.session_state.dashboard_tab == "Quality Metrics":
        # --- Quality Metrics Section ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">🧪</span>Quality Control Dashboard</h3></div>', unsafe_allow_html=True)
        
        # Quality metrics layout
        qual_col1, qual_col2 = st.columns([2, 1])
        
        with qual_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Quality Defect Rates by Product Line")
            
            # Sample quality data
            product_lines = ["Medical", "Automotive", "Aerospace", "Consumer", "Industrial"]
            defect_rates = [1.2, 2.7, 0.8, 3.5, 2.1]  # percentage
            target_rates = [1.5, 2.0, 1.0, 3.0, 2.5]  # targets
            
            # Create DataFrame
            quality_df = pd.DataFrame({
                "Product Line": product_lines,
                "Defect Rate": defect_rates,
                "Target": target_rates
            })
            
            # Create grouped bar chart
            fig_quality = px.bar(
                quality_df,
                x="Product Line",
                y=["Defect Rate", "Target"],
                barmode="group",
                color_discrete_sequence=["#FF5722", "#2196F3"],
                title="Defect Rates vs. Targets (%)"
            )
            
            # Customize layout
            fig_quality.update_layout(
                xaxis_title="Product Line",
                yaxis_title="Defect Rate (%)",
                legend_title="Metric"
            )
            
            st.plotly_chart(fig_quality, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quality test results over time
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Quality Test Results Over Time")
            
            # Generate date range for the last 14 days
            date_range = pd.date_range(end=datetime.now(), periods=14).tolist()
            date_labels = [d.strftime("%m-%d") for d in date_range]
            
            # Sample data for pass/fail/pending tests
            pass_counts = [42, 45, 39, 47, 50, 48, 52, 49, 46, 51, 53, 48, 50, 55]
            fail_counts = [3, 5, 7, 4, 2, 6, 3, 5, 4, 2, 3, 5, 3, 2]
            pending_counts = [5, 3, 8, 6, 7, 4, 5, 7, 9, 6, 4, 7, 8, 3]
            
            # Create stacked area chart
            fig_quality_time = go.Figure()
            
            # Add traces
            fig_quality_time.add_trace(go.Scatter(
                x=date_labels, y=pass_counts,
                mode='lines',
                line=dict(width=0.5, color='#4CAF50'),
                stackgroup='one',
                fillcolor='rgba(76, 175, 80, 0.5)',
                name='Pass'
            ))
            
            fig_quality_time.add_trace(go.Scatter(
                x=date_labels, y=fail_counts,
                mode='lines',
                line=dict(width=0.5, color='#F44336'),
                stackgroup='one',
                fillcolor='rgba(244, 67, 54, 0.5)',
                name='Fail'
            ))
            
            fig_quality_time.add_trace(go.Scatter(
                x=date_labels, y=pending_counts,
                mode='lines',
                line=dict(width=0.5, color='#FFC107'),
                stackgroup='one',
                fillcolor='rgba(255, 193, 7, 0.5)',
                name='Pending'
            ))
            
            # Customize layout
            fig_quality_time.update_layout(
                title='Daily Quality Test Results',
                xaxis_title='Date',
                yaxis_title='Number of Tests',
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_quality_time, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with qual_col2:
            # Quality KPIs
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Quality KPIs")
            
            # First Day Pass Rate
            fdpr = 92.5
            st.markdown(f"""
            <div class="quality-kpi-card">
                <div class="quality-kpi-title">First Day Pass Rate</div>
                <div class="quality-kpi-value">{fdpr}%</div>
                <div class="quality-kpi-trend positive">↑ 1.5% from last month</div>
                <div class="quality-kpi-bar">
                    <div class="quality-kpi-fill" style="width: {fdpr}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Overall Equipment Efficiency 
            oee = 87.3
            st.markdown(f"""
            <div class="quality-kpi-card">
                <div class="quality-kpi-title">Overall Equipment Efficiency</div>
                <div class="quality-kpi-value">{oee}%</div>
                <div class="quality-kpi-trend positive">↑ 0.8% from last month</div>
                <div class="quality-kpi-bar">
                    <div class="quality-kpi-fill" style="width: {oee}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Scrap Rate
            scrap = 2.1
            st.markdown(f"""
            <div class="quality-kpi-card">
                <div class="quality-kpi-title">Scrap Rate</div>
                <div class="quality-kpi-value">{scrap}%</div>
                <div class="quality-kpi-trend negative">↑ 0.3% from last month</div>
                <div class="quality-kpi-bar">
                    <div class="quality-kpi-fill negative" style="width: {scrap * 10}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Customer Returns
            returns = 0.8
            st.markdown(f"""
            <div class="quality-kpi-card">
                <div class="quality-kpi-title">Customer Returns</div>
                <div class="quality-kpi-value">{returns}%</div>
                <div class="quality-kpi-trend positive">↓ 0.2% from last month</div>
                <div class="quality-kpi-bar">
                    <div class="quality-kpi-fill negative" style="width: {returns * 10}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <style>
                .quality-kpi-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 15px;
                    border-left: 3px solid #4CAF50;
                }
                .quality-kpi-title {
                    font-size: 0.9rem;
                    color: #aaa;
                    margin-bottom: 5px;
                }
                .quality-kpi-value {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                }
                .quality-kpi-trend {
                    font-size: 0.8rem;
                    margin-bottom: 8px;
                }
                .quality-kpi-bar {
                    height: 6px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 3px;
                    overflow: hidden;
                }
                .quality-kpi-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #4CAF50, #8BC34A);
                }
                .quality-kpi-fill.negative {
                    background: linear-gradient(90deg, #F44336, #FF9800);
                }
            </style>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Top Quality Issues
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Top Quality Issues")
            
            # Sample data
            issues = ["Dimensional Error", "Surface Defect", "Incomplete Fill", "Material Contamination", "Alignment Issue"]
            counts = [24, 18, 15, 12, 8]
            
            # Create DataFrame
            issues_df = pd.DataFrame({"Issue": issues, "Count": counts})
            
            # Create horizontal bar chart
            fig_issues = px.bar(
                issues_df,
                y="Issue",
                x="Count",
                orientation="h",
                color="Count",
                color_continuous_scale=px.colors.sequential.Viridis,
                title="Quality Issues (Last 30 Days)"
            )
            
            fig_issues.update_layout(
                xaxis_title="Number of Occurrences",
                yaxis_title="",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_issues, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif st.session_state.dashboard_tab == "Equipment Health":
        # --- Equipment Health Dashboard ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">⚙️</span>Manufacturing Equipment Health</h3></div>', unsafe_allow_html=True)
        
        # Equipment health metrics layout
        eqp_col1, eqp_col2 = st.columns([3, 2])
        
        with eqp_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Equipment Performance Monitoring")
            
            # Create tabs for different metrics
            eqp_tabs = st.tabs(["Utilization", "Downtime", "OEE"])
            
            with eqp_tabs[0]:  # Utilization tab
                # Sample data - equipment utilization over time
                equipment_names = ["3D Printer A", "CNC Mill B", "Assembly Robot C", "Laser Cutter D", "Injection Mold E"]
                dates = pd.date_range(end=datetime.now(), periods=30).strftime("%m-%d").tolist()
                
                # Generate random utilization data with trends
                np.random.seed(42)  # for reproducible results
                base_levels = [75, 80, 65, 70, 85]  # base utilization levels
                
                utilization_data = {}
                for i, equipment in enumerate(equipment_names):
                    # Create data with realistic patterns and some noise
                    base = base_levels[i]
                    trend = np.linspace(0, 5, 30) if i % 2 == 0 else np.linspace(2, -2, 30)
                    weekly = 5 * np.sin(np.linspace(0, 2*np.pi, 30))
                    noise = np.random.normal(0, 3, 30)
                    values = np.clip(base + trend + weekly + noise, 0, 100).tolist()
                    utilization_data[equipment] = values
                
                # Create multi-line chart
                fig_utilization = go.Figure()
                
                for equipment, values in utilization_data.items():
                    fig_utilization.add_trace(
                        go.Scatter(
                            x=dates,
                            y=values,
                            mode='lines+markers',
                            name=equipment,
                            marker=dict(size=6)
                        )
                    )
                
                # Add target line
                fig_utilization.add_trace(
                    go.Scatter(
                        x=dates,
                        y=[80] * len(dates),
                        mode='lines',
                        name='Target',
                        line=dict(dash='dash', color='white', width=1)
                    )
                )
                
                # Customize layout
                fig_utilization.update_layout(
                    title='Equipment Utilization (Last 30 Days)',
                    xaxis_title='Date',
                    yaxis_title='Utilization (%)',
                    yaxis=dict(range=[40, 100]),
                    hovermode='x unified',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                st.plotly_chart(fig_utilization, use_container_width=True)
                
            with eqp_tabs[1]:  # Downtime tab
                # Sample data - equipment downtime by category
                downtime_categories = ["Scheduled Maintenance", "Unplanned Repairs", "Material Issues", "Software/Controls", "Operator Related"]
                equipment_types = ["3D Printers", "CNC Machines", "Assembly Robots", "Laser Cutters", "Injection Molds"]
                
                # Generate downtime hours matrix
                np.random.seed(43)
                downtime_matrix = np.random.randint(2, 25, size=(len(equipment_types), len(downtime_categories)))
                
                # Create heatmap
                fig_downtime = px.imshow(
                    downtime_matrix,
                    labels=dict(x="Downtime Category", y="Equipment Type", color="Hours"),
                    x=downtime_categories,
                    y=equipment_types,
                    color_continuous_scale='RdYlGn_r',
                    text_auto=True,
                    aspect='auto'
                )
                
                # Customize layout
                fig_downtime.update_layout(
                    title='Equipment Downtime by Category (Hours in Last 30 Days)',
                    xaxis_title='Downtime Category',
                    yaxis_title='Equipment Type',
                )
                
                st.plotly_chart(fig_downtime, use_container_width=True)
                
            with eqp_tabs[2]:  # OEE tab
                # Sample data - OEE components by equipment
                oee_equipment = ["3D Printer A", "3D Printer B", "CNC Mill A", "CNC Mill B", "Assembly Line"]
                
                # OEE components - Availability, Performance, Quality
                availability = [92.5, 88.7, 94.1, 90.3, 96.2]
                performance = [87.3, 85.1, 91.2, 88.5, 83.7]
                quality = [98.2, 97.5, 95.8, 96.7, 99.1]
                
                # Calculate OEE
                oee = [(a * p * q) / 10000 for a, p, q in zip(availability, performance, quality)]
                
                # Create DataFrame
                oee_df = pd.DataFrame({
                    "Equipment": oee_equipment,
                    "Availability (%)": availability,
                    "Performance (%)": performance,
                    "Quality (%)": quality,
                    "OEE (%)": oee
                })
                
                # Create grouped bar chart
                fig_oee = px.bar(
                    oee_df,
                    x="Equipment",
                    y=["Availability (%)", "Performance (%)", "Quality (%)"],
                    barmode="group",
                    color_discrete_map={
                        "Availability (%)": "#2196F3",
                        "Performance (%)": "#4CAF50",
                        "Quality (%)": "#FFC107"
                    },
                    title="OEE Components by Equipment"
                )
                
                # Add OEE markers
                fig_oee.add_trace(
                    go.Scatter(
                        x=oee_equipment,
                        y=oee,
                        mode='markers+lines+text',
                        name='OEE',
                        marker=dict(
                            color='#E91E63',
                            size=12,
                            symbol='diamond'
                        ),
                        text=[f"{x:.1f}%" for x in oee],
                        textposition="top center"
                    )
                )
                
                # Customize layout
                fig_oee.update_layout(
                    xaxis_title='Equipment',
                    yaxis_title='Percentage (%)',
                    yaxis=dict(range=[70, 100]),
                    legend_title='Metric'
                )
                
                st.plotly_chart(fig_oee, use_container_width=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display upcoming maintenance
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Upcoming Scheduled Maintenance")
            
            # Sample maintenance data
            maintenance_data = [
                {"equipment": "3D Printer A", "type": "Preventive", "date": "2023-06-03", "technician": "John Smith", "estimated_hours": 3},
                {"equipment": "Laser Cutter D", "type": "Calibration", "date": "2023-06-05", "technician": "Maria Rodriguez", "estimated_hours": 2},
                {"equipment": "CNC Mill B", "type": "Preventive", "date": "2023-06-08", "technician": "James Chen", "estimated_hours": 4},
                {"equipment": "Assembly Robot C", "type": "Software Update", "date": "2023-06-10", "technician": "Sarah Wilson", "estimated_hours": 1},
                {"equipment": "Injection Mold E", "type": "Major Overhaul", "date": "2023-06-15", "technician": "David Johnson", "estimated_hours": 8}
            ]
            
            # Convert to DataFrame for display
            maintenance_df = pd.DataFrame(maintenance_data)
            
            # Add styling for maintenance type
            def highlight_maintenance_type(val):
                color_map = {
                    "Preventive": "background-color: rgba(33, 150, 243, 0.2)",
                    "Calibration": "background-color: rgba(156, 39, 176, 0.2)",
                    "Software Update": "background-color: rgba(76, 175, 80, 0.2)",
                    "Major Overhaul": "background-color: rgba(244, 67, 54, 0.2)"
                }
                return color_map.get(val, "")
            
            # Apply styling and display
            st.dataframe(
                maintenance_df.style.applymap(
                    highlight_maintenance_type, 
                    subset=["type"]
                ),
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with eqp_col2:
            # Equipment health status cards
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Equipment Health Status")
            
            # Sample equipment status data
            equipment_status = [
                {"name": "3D Printer A", "status": "Operational", "health": 92, "last_maintenance": "15 days ago", "alert": None},
                {"name": "CNC Mill B", "status": "Operational", "health": 87, "last_maintenance": "8 days ago", "alert": "Maintenance due in 22 days"},
                {"name": "Assembly Robot C", "status": "Warning", "health": 76, "last_maintenance": "45 days ago", "alert": "Maintenance overdue by 15 days"},
                {"name": "Laser Cutter D", "status": "Operational", "health": 94, "last_maintenance": "3 days ago", "alert": None},
                {"name": "Injection Mold E", "status": "Critical", "health": 68, "last_maintenance": "60 days ago", "alert": "Performance degradation detected"}
            ]
            
            # Display equipment status cards
            for equipment in equipment_status:
                # Determine card style based on status
                card_class = "equipment-card"
                if equipment["status"] == "Warning":
                    card_class += " warning"
                elif equipment["status"] == "Critical":
                    card_class += " critical"
                
                # Create health indicator fill style
                health_fill = equipment["health"]
                
                # Determine health color
                if equipment["health"] >= 90:
                    health_color = "#4CAF50"  # Green
                elif equipment["health"] >= 75:
                    health_color = "#FFC107"  # Yellow
                else:
                    health_color = "#F44336"  # Red
                
                # Alert display
                alert_display = ""
                if equipment["alert"]:
                    alert_display = f"""<div class="equipment-alert">⚠️ {equipment["alert"]}</div>"""
                
                # Render equipment card
                st.markdown(f"""
                <div class="{card_class}">
                    <div class="equipment-header">
                        <div class="equipment-name">{equipment["name"]}</div>
                        <div class="equipment-status">{equipment["status"]}</div>
                    </div>
                    <div class="equipment-health-bar">
                        <div class="equipment-health-fill" style="width: {health_fill}%; background-color: {health_color};"></div>
                    </div>
                    <div class="equipment-health-label">Health: {equipment["health"]}%</div>
                    <div class="equipment-details">Last Maintenance: {equipment["last_maintenance"]}</div>
                    {alert_display}
                </div>
                """, unsafe_allow_html=True)
            
            # Add CSS for equipment cards
            st.markdown("""
            <style>
                .equipment-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 15px;
                    border-left: 4px solid #4CAF50;
                }
                .equipment-card.warning {
                    border-left-color: #FFC107;
                }
                .equipment-card.critical {
                    border-left-color: #F44336;
                }
                .equipment-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .equipment-name {
                    font-weight: bold;
                    font-size: 1.1rem;
                }
                .equipment-status {
                    font-size: 0.9rem;
                    padding: 3px 8px;
                    border-radius: 12px;
                    background: rgba(76, 175, 80, 0.2);
                }
                .equipment-card.warning .equipment-status {
                    background: rgba(255, 193, 7, 0.2);
                }
                .equipment-card.critical .equipment-status {
                    background: rgba(244, 67, 54, 0.2);
                }
                .equipment-health-bar {
                    height: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    overflow: hidden;
                    margin-bottom: 5px;
                }
                .equipment-health-fill {
                    height: 100%;
                }
                .equipment-health-label {
                    font-size: 0.9rem;
                    margin-bottom: 8px;
                }
                .equipment-details {
                    font-size: 0.85rem;
                    color: #aaa;
                }
                .equipment-alert {
                    margin-top: 8px;
                    font-size: 0.85rem;
                    color: #FFC107;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Parts replacement tracking
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Parts Replacement Tracking")
            
            # Create donut chart for parts lifecycle status
            part_status = ["New (<25%)", "Mid-Life (25-50%)", "Mature (50-75%)", "End-of-Life (>75%)"]
            part_counts = [12, 25, 18, 7]
            
            fig_parts = px.pie(
                names=part_status,
                values=part_counts,
                hole=0.6,
                color=part_status,
                color_discrete_map={
                    "New (<25%)": "#4CAF50",
                    "Mid-Life (25-50%)": "#2196F3",
                    "Mature (50-75%)": "#FFC107",
                    "End-of-Life (>75%)": "#F44336"
                }
            )
            
            fig_parts.update_layout(
                title="Components by Lifecycle Stage",
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="right",
                    x=1.1
                ),
                height=300,
                margin=dict(t=30, b=10, l=10, r=80)
            )
            
            fig_parts.update_traces(textposition='inside', textinfo='percent+label')
            
            # Display chart
            st.plotly_chart(fig_parts, use_container_width=True)
            
            # Critical parts replacement needed
            st.markdown("<b>Critical Parts Needing Replacement</b>", unsafe_allow_html=True)
            
            critical_parts = [
                {"part": "Extruder Nozzle", "equipment": "3D Printer B", "usage": "98%", "replacement_cost": "$120"},
                {"part": "Drive Belt", "equipment": "CNC Mill A", "usage": "92%", "replacement_cost": "$85"},
                {"part": "Laser Tube", "equipment": "Laser Cutter D", "usage": "89%", "replacement_cost": "$450"}
            ]
            
            # Create DataFrame for display
            critical_parts_df = pd.DataFrame(critical_parts)
            
            # Display table
            st.dataframe(critical_parts_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.dashboard_tab == "Materials Analysis":
        # --- Materials Analysis Dashboard ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">🧰</span>Materials Management & Analytics</h3></div>', unsafe_allow_html=True)
        
        # Materials analysis layout
        mat_col1, mat_col2 = st.columns([3, 2])
        
        with mat_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Material Consumption Trends")
            
            # Create tabs for different material views
            mat_tabs = st.tabs(["By Material Type", "By Product Line", "By Month"])
            
            with mat_tabs[0]:  # By Material Type
                # Sample data - material consumption by type
                material_types = ["PLA", "ABS", "Resin", "Metal Powder", "Nylon", "TPU", "Carbon Fiber", "PETG"]
                consumption = [285.6, 142.3, 78.9, 35.2, 67.8, 41.2, 28.6, 92.5]  # in kg
                
                # Create bar chart
                fig_mat_consumption = px.bar(
                    x=material_types,
                    y=consumption,
                    color=material_types,
                    labels={"x": "Material Type", "y": "Consumption (kg)"},
                    title="Material Consumption by Type (Last Quarter)"
                )
                
                # Customize layout
                fig_mat_consumption.update_layout(
                    xaxis_title="Material Type",
                    yaxis_title="Consumption (kg)",
                    showlegend=False
                )
                
                st.plotly_chart(fig_mat_consumption, use_container_width=True)
                
            with mat_tabs[1]:  # By Product Line
                # Sample data - material consumption by product line
                product_lines = ["Medical Devices", "Automotive Parts", "Consumer Products", "Aerospace", "Electronics"]
                material_consumption = {
                    "PLA": [45.2, 15.8, 120.3, 10.5, 93.8],
                    "ABS": [12.3, 65.7, 35.2, 8.6, 20.5],
                    "Resin": [28.6, 7.3, 15.2, 18.9, 8.9],
                    "Metal Powder": [5.3, 12.6, 0.0, 15.8, 1.5],
                }
                
                # Create stacked bar chart
                fig_mat_product = go.Figure()
                
                for material, values in material_consumption.items():
                    fig_mat_product.add_trace(
                        go.Bar(
                            name=material,
                            x=product_lines,
                            y=values
                        )
                    )
                
                # Change the bar mode
                fig_mat_product.update_layout(
                    barmode='stack',
                    title="Material Consumption by Product Line (kg)",
                    xaxis_title="Product Line",
                    yaxis_title="Consumption (kg)",
                    legend_title="Material Type"
                )
                
                st.plotly_chart(fig_mat_product, use_container_width=True)
                
            with mat_tabs[2]:  # By Month
                # Sample data - monthly material consumption
                months = list(calendar.month_abbr)[1:]
                
                # Consumption data for multiple materials
                monthly_consumption = {
                    "PLA": [22.3, 24.5, 21.8, 25.7, 28.2, 27.6, 30.5, 26.8, 24.2, 23.5, 28.4, 30.1],
                    "ABS": [12.5, 13.8, 15.2, 10.8, 11.3, 10.9, 12.2, 14.5, 15.7, 11.6, 12.8, 13.0],
                    "Resin": [8.2, 7.5, 6.9, 7.3, 8.5, 8.9, 7.2, 6.5, 7.8, 8.1, 7.8, 8.1],
                    "Metal Powder": [2.8, 3.1, 3.2, 2.7, 3.5, 3.8, 3.2, 2.9, 3.4, 2.8, 3.0, 3.3]
                }
                
                # Create multi-line chart
                fig_monthly_mat = go.Figure()
                
                for material, values in monthly_consumption.items():
                    fig_monthly_mat.add_trace(
                        go.Scatter(
                            x=months,
                            y=values,
                            mode='lines+markers',
                            name=material
                        )
                    )
                
                # Customize layout
                fig_monthly_mat.update_layout(
                    title="Monthly Material Consumption by Type",
                    xaxis_title="Month",
                    yaxis_title="Consumption (kg)",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_monthly_mat, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Material efficiency analysis
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Material Efficiency & Waste Analysis")
            
            # Sample data - material efficiency by product line
            product_efficiency = {
                "Product Line": ["Medical", "Automotive", "Aerospace", "Consumer", "Electronics", "Industrial"],
                "Material Used (kg)": [125.3, 187.6, 82.4, 215.8, 156.2, 142.7],
                "Product Weight (kg)": [98.2, 158.9, 72.5, 165.3, 132.4, 118.6],
                "Waste (kg)": [27.1, 28.7, 9.9, 50.5, 23.8, 24.1]
            }
            
            # Calculate efficiency percentages
            efficiency_df = pd.DataFrame(product_efficiency)
            efficiency_df["Efficiency (%)"] = (efficiency_df["Product Weight (kg)"] / efficiency_df["Material Used (kg)"] * 100).round(1)
            
            # Create combo chart (bar + line)
            fig_efficiency = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add bars for material used and product weight
            fig_efficiency.add_trace(
                go.Bar(
                    x=efficiency_df["Product Line"],
                    y=efficiency_df["Material Used (kg)"],
                    name="Material Used",
                    marker_color="#2196F3"
                )
            )
            
            fig_efficiency.add_trace(
                go.Bar(
                    x=efficiency_df["Product Line"],
                    y=efficiency_df["Product Weight (kg)"],
                    name="Product Weight",
                    marker_color="#4CAF50"
                )
            )
            
            fig_efficiency.add_trace(
                go.Bar(
                    x=efficiency_df["Product Line"],
                    y=efficiency_df["Waste (kg)"],
                    name="Waste",
                    marker_color="#F44336"
                )
            )
            
            # Add line for efficiency percentage
            fig_efficiency.add_trace(
                go.Scatter(
                    x=efficiency_df["Product Line"],
                    y=efficiency_df["Efficiency (%)"],
                    name="Efficiency %",
                    mode="lines+markers",
                    marker=dict(
                        size=8,
                        symbol="diamond",
                        color="#FF9800"
                    ),
                    line=dict(width=2, color="#FF9800")
                ),
                secondary_y=True
            )
            
            # Add target efficiency line
            fig_efficiency.add_trace(
                go.Scatter(
                    x=efficiency_df["Product Line"],
                    y=[90] * len(efficiency_df),
                    name="Target",
                    mode="lines",
                    line=dict(dash="dash", color="#9C27B0", width=1)
                ),
                secondary_y=True
            )
            
            # Customize layout
            fig_efficiency.update_layout(
                title="Material Efficiency Analysis by Product Line",
                barmode="group",
                xaxis_title="Product Line",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig_efficiency.update_yaxes(title_text="Weight (kg)", secondary_y=False)
            fig_efficiency.update_yaxes(
                title_text="Efficiency (%)", 
                range=[70, 100], 
                secondary_y=True
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with mat_col2:
            # Material inventory status
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Material Inventory Status")
            
            # Sample inventory data
            inventory_data = [
                {"material": "PLA Filament", "current_stock": 120.5, "min_level": 50, "reorder_level": 75, "status": "OK"},
                {"material": "ABS Filament", "current_stock": 62.8, "min_level": 50, "reorder_level": 75, "status": "OK"},
                {"material": "Clear Resin", "current_stock": 18.2, "min_level": 20, "reorder_level": 35, "status": "Low"},
                {"material": "Aluminum Powder", "current_stock": 32.5, "min_level": 15, "reorder_level": 30, "status": "Reorder"},
                {"material": "Carbon Fiber", "current_stock": 8.5, "min_level": 10, "reorder_level": 15, "status": "Low"},
                {"material": "PETG Filament", "current_stock": 45.6, "min_level": 25, "reorder_level": 40, "status": "OK"}
            ]
            
            # Convert to DataFrame
            inventory_df = pd.DataFrame(inventory_data)
            
            # Create bullet chart
            fig_inventory = go.Figure()
            
            for i, row in inventory_df.iterrows():
                # Determine color based on status
                if row["status"] == "Low":
                    color = "#F44336"  # Red for low
                elif row["status"] == "Reorder":
                    color = "#FFC107"  # Yellow for reorder
                else:
                    color = "#4CAF50"  # Green
                
                # Add bar for current stock
                fig_inventory.add_trace(
                    go.Bar(
                        y=[row["material"]],
                        x=[row["current_stock"]],
                        name=row["material"],
                        orientation="h",
                        marker=dict(color=color),
                        showlegend=False,
                        text=f"{row['current_stock']} kg",
                        textposition="inside"
                    )
                )
                
                # Add lines for min and reorder levels
                fig_inventory.add_shape(
                    type="line",
                    y0=i - 0.4,
                    y1=i + 0.4,
                    x0=row["min_level"],
                    x1=row["min_level"],
                    line=dict(color="red", width=2, dash="dash")
                )
                
                fig_inventory.add_shape(
                    type="line",
                    y0=i - 0.4,
                    y1=i + 0.4,
                    x0=row["reorder_level"],
                    x1=row["reorder_level"],
                    line=dict(color="orange", width=2, dash="dash")
                )
            
            # Customize layout
            fig_inventory.update_layout(
                title="Material Inventory Levels",
                xaxis_title="Stock Quantity (kg)",
                yaxis_title="",
                height=350,
                barmode="group",
                bargap=0.15,
                bargroupgap=0.1
            )
            
            # Set y-axis range
            fig_inventory.update_yaxes(autorange="reversed")  # Reverse axis to match table order
            
            st.plotly_chart(fig_inventory, use_container_width=True)
            
            # Legend for inventory status
            st.markdown("""
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div><span style="color: red; font-weight: bold;">●</span> Minimum Level</div>
                <div><span style="color: orange; font-weight: bold;">●</span> Reorder Level</div>
                <div><span style="color: green; font-weight: bold;">●</span> Sufficient Stock</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Material cost analysis
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Material Cost Analysis")
            
            # Sample cost data
            cost_data = {
                "Category": ["PLA", "ABS", "Resin", "Metal", "Specialty"],
                "Unit Cost ($/kg)": [25, 28, 65, 120, 85],
                "Monthly Usage (kg)": [145, 95, 48, 22, 18],
                "Monthly Cost ($)": [3625, 2660, 3120, 2640, 1530]
            }
            
            cost_df = pd.DataFrame(cost_data)
            
            # Create pie chart for cost distribution
            fig_cost = px.pie(
                cost_df,
                values="Monthly Cost ($)",
                names="Category",
                title="Material Cost Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_cost.update_traces(
                textposition="inside",
                textinfo="percent+label"
            )
            
            # Update layout
            fig_cost.update_layout(
                height=300,
                margin=dict(t=30, b=10, l=10, r=10)
            )
            
            st.plotly_chart(fig_cost, use_container_width=True)
            
            # Cost trend by month (line chart)
            months = list(calendar.month_abbr)[1:7]  # Last 6 months
            
            # Sample trend data for different material categories
            cost_trends = {
                "PLA": [3200, 3450, 3625, 3580, 3700, 3625],
                "ABS": [2400, 2550, 2480, 2660, 2720, 2660],
                "Resin": [2900, 3050, 3180, 3250, 3120, 3120],
                "Metal": [2300, 2450, 2580, 2620, 2530, 2640],
                "Specialty": [1200, 1350, 1420, 1480, 1550, 1530]
            }
            
            # Create stacked area chart
            fig_cost_trend = go.Figure()
            
            for material, costs in cost_trends.items():
                fig_cost_trend.add_trace(
                    go.Scatter(
                        x=months,
                        y=costs,
                        mode="lines",
                        stackgroup="one",
                        name=material
                    )
                )
            
            # Customize layout
            fig_cost_trend.update_layout(
                title="Monthly Material Cost Trends",
                xaxis_title="Month",
                yaxis_title="Cost ($)",
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig_cost_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif st.session_state.dashboard_tab == "Advanced Analytics":
        # --- Advanced Analytics Dashboard ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">📈</span>Manufacturing Intelligence Hub</h3></div>', unsafe_allow_html=True)
        
        # Advanced analytics layout
        analytics_col1, analytics_col2 = st.columns([2, 1])
        
        with analytics_col1:
            # Production performance correlation matrix
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Manufacturing Performance Correlation Analysis")
            
            # Sample correlation factors
            factors = ["Material Quality", "Machine Speed", "Temperature", "Humidity", "Batch Size", 
                      "Machine Age", "Operator Experience", "Setup Time"]
            
            # Create correlation matrix with realistic manufacturing relationships
            np.random.seed(42)
            corr_matrix = np.array([
                [1.0,  0.3,  0.65, -0.2,  0.15, -0.45,  0.72,  0.18],  # Material Quality
                [0.3,  1.0,  0.25, -0.05, 0.85, -0.35,  0.22,  0.42],  # Machine Speed
                [0.65, 0.25, 1.0,   0.56, 0.12, -0.18,  0.35,  0.28],  # Temperature
                [-0.2, -0.05, 0.56, 1.0, -0.08,  0.05, -0.15, -0.05],  # Humidity
                [0.15, 0.85, 0.12, -0.08, 1.0,  -0.22,  0.35,  0.62],  # Batch Size
                [-0.45, -0.35, -0.18, 0.05, -0.22, 1.0,  -0.28, -0.32], # Machine Age
                [0.72, 0.22, 0.35, -0.15,  0.35, -0.28,  1.0,   0.45],  # Operator Experience
                [0.18, 0.42, 0.28, -0.05,  0.62, -0.32,  0.45,  1.0]    # Setup Time
            ])
            
            # Create heatmap with annotations
            fig_corr = px.imshow(
                corr_matrix,
                x=factors,
                y=factors,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                color_continuous_midpoint=0,
                aspect="auto"
            )
            
            # Customize layout
            fig_corr.update_layout(
                title="Manufacturing Factor Correlation Matrix",
                height=500
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Insight cards below correlation matrix
            st.markdown("""
            <div class="insight-cards">
                <div class="insight-card">
                    <div class="insight-title">🔎 Key Insight</div>
                    <div class="insight-content">
                        <b>Material Quality</b> has the strongest positive correlation (0.72) with <b>Operator Experience</b>, 
                        suggesting skilled operators are better at detecting and resolving material issues.
                    </div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">🔎 Key Insight</div>
                    <div class="insight-content">
                        <b>Machine Speed</b> and <b>Batch Size</b> have a strong correlation (0.85), 
                        indicating optimal production efficiency is achieved with larger batch sizes.
                    </div>
                </div>
                <div class="insight-card">
                    <div class="insight-title">⚠️ Alert</div>
                    <div class="insight-content">
                        <b>Machine Age</b> negatively correlates with <b>Material Quality</b> (-0.45), 
                        suggesting older machines may be compromising output quality.
                    </div>
                </div>
            </div>
            
            <style>
                .insight-cards {
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                }
                .insight-card {
                    flex: 1;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 10px;
                    border-left: 3px solid #2196F3;
                }
                .insight-card:nth-child(2) {
                    border-left-color: #4CAF50;
                }
                .insight-card:nth-child(3) {
                    border-left-color: #FFC107;
                }
                .insight-title {
                    font-weight: bold;
                    margin-bottom: 5px;
                    font-size: 0.9rem;
                }
                .insight-content {
                    font-size: 0.85rem;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Multi-factor analysis
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Multi-Factor Production Analysis")
            
            # Sample product data for bubble chart
            products = ["Product A", "Product B", "Product C", "Product D", "Product E", 
                       "Product F", "Product G", "Product H", "Product I", "Product J"]
            
            # Production time, defect rate, production volume
            production_time = [45, 65, 80, 30, 55, 70, 25, 60, 50, 40]  # minutes
            defect_rate = [2.1, 1.8, 0.9, 3.5, 2.7, 1.2, 4.5, 1.5, 2.3, 3.0]  # percentage
            production_volume = [850, 650, 450, 1200, 580, 750, 1400, 500, 900, 1100]  # units/month
            profit_margin = [15, 28, 35, 12, 22, 25, 10, 32, 18, 20]  # percentage
            
            # Create DataFrame
            product_df = pd.DataFrame({
                "Product": products,
                "Production Time (min)": production_time,
                "Defect Rate (%)": defect_rate,
                "Production Volume": production_volume,
                "Profit Margin (%)": profit_margin
            })
            
            # Create bubble chart
            fig_products = px.scatter(
                product_df,
                x="Production Time (min)",
                y="Defect Rate (%)",
                size="Production Volume",
                color="Profit Margin (%)",
                text="Product",
                size_max=50,
                color_continuous_scale="Viridis"
            )
            
            # Add profit margin contour lines
            profit_range = np.linspace(min(profit_margin), max(profit_margin), 5)
            
            for profit in profit_range:
                fig_products.add_shape(
                    type="line",
                    line=dict(dash="dot", width=1, color="rgba(255, 255, 255, 0.5)"),
                    x0=min(production_time) - 5,
                    x1=max(production_time) + 5,
                    y0=profit / 10,  # Simplified relationship for visualization
                    y1=profit / 10
                )
            
            # Customize layout
            fig_products.update_layout(
                title="Product Portfolio Analysis",
                xaxis_title="Production Time (min)",
                yaxis_title="Defect Rate (%)",
                coloraxis_colorbar_title="Profit Margin (%)",
                height=500
            )
            
            fig_products.update_traces(
                marker=dict(line=dict(width=1, color='DarkSlateGrey')),
                selector=dict(mode='markers')
            )
            
            st.plotly_chart(fig_products, use_container_width=True)
            
            # Optimal production zone
            st.markdown("""
            <div style="background: rgba(76, 175, 80, 0.1); border-left: 3px solid #4CAF50; padding: 10px; margin: 10px 0;">
                <b>Optimal Production Zone Analysis:</b> Products in the bottom-left quadrant (low production time, low defect rate) 
                with higher profit margins (darker colors) represent the ideal production focus. 
                Products G and D show high volume but require quality improvement, while Products C and H offer 
                the best quality-to-profit ratio.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with analytics_col2:
            # Process capability analysis
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("Process Capability Analysis")
            
            # Process capability metrics
            processes = ["Extrusion", "Assembly", "Injection", "Finishing", "Testing"]
            cp_values = [1.55, 1.25, 0.95, 1.40, 1.75]  # Process capability index
            cpk_values = [1.35, 1.15, 0.85, 1.30, 1.60]  # Process capability with mean shift
            
            # Create DataFrame
            capability_df = pd.DataFrame({
                "Process": processes,
                "Cp": cp_values,
                "Cpk": cpk_values
            })
            
            
            # Create grouped bar chart
            fig_capability = px.bar(
                capability_df,
                               x="Process",
                y=["Cp", "Cpk"],
                barmode="group",
                color_discrete_map={
                    "Cp": "#2196F3",
                    "Cpk": "#FF9800"
                }
            )
            
            # Add threshold lines
            fig_capability.add_shape(
                type="line",
                line=dict(dash="dash", width=1, color="red"),
                x0=-0.5,
                x1=len(processes) - 0.5,
                y0=1.0,
                y1=1.0,
                name="Minimum Acceptable"
            )
            
            fig_capability.add_shape(
                type="line",
                line=dict(dash="dash", width=1, color="green"),
                x0=-0.5,
                x1=len(processes) - 0.5,
                y0=1.33,
                y1=1.33,
                name="Industry Target"
            )
            
            # Add annotations for threshold lines
            fig_capability.add_annotation(
                x=len(processes) - 0.5,
                y=1.0,
                text="Minimum Acceptable (1.0)",
                showarrow=False,
                yshift=10,
                xshift=20,
                font=dict(size=10, color="red")
            )
            
            fig_capability.add_annotation(
                x=len(processes) - 0.5,
                y=1.33,
                text="Industry Target (1.33)",
                showarrow=False,
                yshift=10,
                xshift=10,
                font=dict(size=10, color="green")
            )
            
            # Customize layout
            fig_capability.update_layout(
                title="Process Capability Indices by Manufacturing Process",
                xaxis_title="Process",
                yaxis_title="Capability Index",
                legend_title="Metric",
                height=350
            )
            
            st.plotly_chart(fig_capability, use_container_width=True)
            
            # Process capability interpretation
            st.markdown("""
            <div style="font-size: 0.9rem; margin: 10px 0;">
                <p><b>Cp</b>: Process capability (spread)</p>
                <p><b>Cpk</b>: Process capability accounting for mean shift</p>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><b>Cp/Cpk < 1.0:</b> Process not capable</li>
                    <li><b>1.0 ≤ Cp/Cpk < 1.33:</b> Marginally capable</li>
                    <li><b>Cp/Cpk ≥ 1.33:</b> Process is capable</li>
                    <li><b>Cp/Cpk ≥ 1.67:</b> Excellent capability</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Machine learning insights
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("AI-Driven Manufacturing Insights")
            
            # Anomaly detection tab
            with st.expander("🤖 Anomaly Detection Model", expanded=True):
                st.markdown("""
                <div class="model-container">
                    <div class="model-header">
                        <div class="model-title">Anomaly Detection Results</div>
                        <div class="model-accuracy">Model Accuracy: 94.2%</div>
                    </div>
                    
                    <div class="model-content">
                        <div class="anomaly-metrics">
                            <div class="anomaly-metric">
                                <div class="anomaly-value">15</div>
                                <div class="anomaly-label">Anomalies Detected</div>
                            </div>
                            <div class="anomaly-metric">
                                <div class="anomaly-value">8</div>
                                <div class="anomaly-label">Critical Issues</div>
                            </div>
                            <div class="anomaly-metric">
                                <div class="anomaly-value">7</div>
                                <div class="anomaly-label">Warnings</div>
                            </div>
                        </div>
                        
                        <div class="anomaly-list-header">
                            <span>Recent Anomalies:</span>
                        </div>
                        <div class="anomaly-list">
                            <div class="anomaly critical">
                                <div>CNC Mill B - Excessive Vibration</div>
                                <div>12:45 PM</div>
                            </div>
                            <div class="anomaly warning">
                                <div>Assembly Line - Cycle Time Drift</div>
                                <div>11:30 AM</div>
                            </div>
                            <div class="anomaly warning">
                                <div>Resin Tank 2 - Viscosity Deviation</div>
                                <div>9:15 AM</div>
                            </div>
                        </div>
                    </div>
                </div>
                <style>
                    .model-container {
                        background: rgba(33, 150, 243, 0.1);
                        border-radius: 8px;
                        overflow: hidden;
                        margin-bottom: 15px;
                    }
                    .model-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        background: rgba(33, 150, 243, 0.2);
                        padding: 8px 12px;
                    }
                    .model-title {
                        font-weight: bold;
                    }
                    .model-accuracy {
                        font-size: 0.8rem;
                        background: rgba(76, 175, 80, 0.2);
                        padding: 3px 8px;
                        border-radius: 12px;
                    }
                    .model-content {
                        padding: 12px;
                    }
                    .anomaly-metrics {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 15px;
                    }
                    .anomaly-metric {
                        text-align: center;
                    }
                    .anomaly-value {
                        font-size: 1.5rem;
                        font-weight: bold;
                    }
                    .anomaly-label {
                        font-size: 0.8rem;
                        color: #aaa;
                    }
                    .anomaly-list-header {
                        margin-bottom: 8px;
                        font-weight: bold;
                        font-size: 0.9rem;
                    }
                    .anomaly-list {
                        font-size: 0.85rem;
                    }
                    .anomaly {
                        display: flex;
                        justify-content: space-between;
                        padding: 5px;
                        margin-bottom: 3px;
                        border-radius: 4px;
                    }
                    .anomaly.critical {
                        background: rgba(244, 67, 54, 0.1);
                        border-left: 3px solid #F44336;
                    }
                    .anomaly.warning {
                        background: rgba(255, 193, 7, 0.1);
                        border-left: 3px solid #FFC107;
                    }
                </style>
                """, unsafe_allow_html=True)
            
            # Predictive maintenance model
            with st.expander("🔮 Predictive Maintenance", expanded=True):
                st.markdown("""
                <div class="model-container">
                    <div class="model-header">
                        <div class="model-title">Maintenance Prediction</div>
                        <div class="model-accuracy">Model Accuracy: 91.8%</div>
                    </div>
                    
                    <div class="model-content">
                        <div class="gauge-container">
                            <div class="gauge-header">Equipment Health Forecast</div>
                            <div class="gauge-row">
                                <div class="gauge">
                                    <div class="gauge-title">3D Printer A</div>
                                    <div class="gauge-visual" style="--value: 85%;"></div>
                                    <div class="gauge-label">24 days to maintenance</div>
                                </div>
                                <div class="gauge">
                                    <div class="gauge-title">CNC Mill B</div>
                                    <div class="gauge-visual" style="--value: 62%;"></div>
                                    <div class="gauge-label">12 days to maintenance</div>
                                </div>
                                <div class="gauge">
                                    <div class="gauge-title">Laser Cutter D</div>
                                    <div class="gauge-visual" style="--value: 38%;"></div>
                                    <div class="gauge-label">5 days to maintenance</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <style>
                    .gauge-container {
                        margin-bottom: 10px;
                    }
                    .gauge-header {
                        margin-bottom: 10px;
                        font-weight: bold;
                        font-size: 0.9rem;
                    }
                    .gauge-row {
                        display: flex;
                        justify-content: space-between;
                    }
                    .gauge {
                        flex: 1;
                        text-align: center;
                        padding: 0 5px;
                    }
                    .gauge-title {
                        font-size: 0.85rem;
                        margin-bottom: 5px;
                    }
                    .gauge-visual {
                        height: 5px;
                        background: linear-gradient(to right, #F44336, #FFC107, #4CAF50);
                        position: relative;
                        border-radius: 3px;
                        margin-bottom: 5px;
                    }
                    .gauge-visual::after {
                        content: "";
                        position: absolute;
                        left: var(--value);
                        top: -5px;
                        width: 2px;
                        height: 15px;
                        background: white;
                    }
                    .gauge-label {
                        font-size: 0.75rem;
                        color: #aaa;
                    }
                </style>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif st.session_state.dashboard_tab == "Predictive Insights":
        # --- Predictive Analytics Dashboard ---
        st.markdown('<div class="section-header"><h3><span class="section-icon">🔮</span>Predictive Manufacturing Intelligence</h3></div>', unsafe_allow_html=True)
        
        # Predictive analytics content goes here
        st.markdown("<p>Content for Predictive Insights dashboard will be displayed here.</p>")
    else:
        st.error("Invalid dashboard tab selected.")

# --- MAIN APP LOGIC ---
def main():
    # Check authentication status
    if st.session_state.authenticated:
        # Display the main dashboard
        main_dashboard()
    else:
        # Display the login form
        display_login_form()

# Run the main app
if __name__ == "__main__":
    main()
