import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import time
from io import BytesIO
import base64
import numpy as np
from src.db.connection import get_db_session, Session
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_notifications_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="MITACS Notifications",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject universal CSS styling
inject_universal_css()

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page.")
    st.stop()

# Add AI assistant context for this page
add_ai_page_context(
    page_title="Notifications",
    page_type="management",
    **get_notifications_page_context()
)

# Render the floating AI assistant
render_page_ai_assistant()

# Page header with icon
st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <h1 style="margin-right: 10px;">🔔 Notifications</h1>
        <span style="color: #6c757d; font-size: 1.2rem;">System Alerts & Messages</span>
    </div>
""", unsafe_allow_html=True)

# Last updated timestamp
st.markdown(
    f"<p style='color: #6c757d; text-align: right;'>Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    unsafe_allow_html=True,
)

# Create tabs for different notification views
tabs = st.tabs(["Dashboard", "All Notifications", "System Alerts", "User Activity", "Settings"])

# Notification Functions
def get_notification_priority_color(priority):
    """Get color based on notification priority"""
    colors = {
        "Critical": "#dc3545",  # Red
        "High": "#fd7e14",      # Orange
        "Medium": "#ffc107",    # Yellow
        "Low": "#28a745",       # Green
        "Info": "#17a2b8"       # Blue
    }
    return colors.get(priority, "#6c757d")

def get_notification_icon(notification_type):
    """Get icon based on notification type"""
    icons = {
        "system": "⚙️",
        "security": "🔒",
        "maintenance": "🔧",
        "quality": "✅",
        "user": "👤",
        "device": "🖨️",
        "material": "🧱",
        "blueprint": "📐",
        "certification": "📜",
        "subscription": "💰",
        "payment": "💳"
    }
    return icons.get(notification_type.lower(), "📢")

def format_time_ago(timestamp):
    """Format timestamp to show time ago"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        except:
            return timestamp
    
    now = datetime.datetime.now()
    diff = now - timestamp
    
    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff.days < 7:
        return f"{diff.days}d ago"
    else:
        return timestamp.strftime("%Y-%m-%d")

def generate_sample_notifications():
    """Generate sample notification data"""
    current_time = datetime.datetime.now()
    
    notification_types = ["system", "security", "maintenance", "quality", "user", "device", "material", "blueprint", "certification", "subscription"]
    priorities = ["Critical", "High", "Medium", "Low", "Info"]
    statuses = ["Unread", "Read", "Archived"]
    
    notifications = []
    
    # Generate sample notifications
    sample_notifications = [
        {
            "title": "System Maintenance Scheduled",
            "message": "Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST.",
            "type": "system",
            "priority": "Medium",
            "timestamp": current_time - datetime.timedelta(hours=2),
            "status": "Unread",
            "category": "Maintenance",
            "sender": "System Administrator"
        },
        {
            "title": "Security Alert: Failed Login Attempts",
            "message": "Multiple failed login attempts detected for user account. Please review security logs.",
            "type": "security",
            "priority": "High",
            "timestamp": current_time - datetime.timedelta(hours=1),
            "status": "Unread",
            "category": "Security",
            "sender": "Security System"
        },
        {
            "title": "Device Offline Alert",
            "message": "3D Printer #5 has gone offline and needs immediate attention.",
            "type": "device",
            "priority": "Critical",
            "timestamp": current_time - datetime.timedelta(minutes=30),
            "status": "Unread",
            "category": "Equipment",
            "sender": "Device Monitor"
        },
        {
            "title": "Material Stock Low",
            "message": "PLA filament stock is running low (15kg remaining). Consider reordering.",
            "type": "material",
            "priority": "Medium",
            "timestamp": current_time - datetime.timedelta(hours=3),
            "status": "Read",
            "category": "Inventory",
            "sender": "Inventory System"
        },
        {
            "title": "Quality Check Completed",
            "message": "Quality assessment for Batch #2024-05-24 has been completed successfully.",
            "type": "quality",
            "priority": "Info",
            "timestamp": current_time - datetime.timedelta(hours=4),
            "status": "Read",
            "category": "Quality",
            "sender": "QA System"
        },
        {
            "title": "New User Registration",
            "message": "New user 'john.smith@company.com' has registered and requires approval.",
            "type": "user",
            "priority": "Low",
            "timestamp": current_time - datetime.timedelta(hours=6),
            "status": "Read",
            "category": "User Management",
            "sender": "User Management"
        },
        {
            "title": "Blueprint Approval Required",
            "message": "Blueprint 'Engine Component v2.1' is awaiting your approval.",
            "type": "blueprint",
            "priority": "Medium",
            "timestamp": current_time - datetime.timedelta(hours=8),
            "status": "Unread",
            "category": "Approval",
            "sender": "Blueprint System"
        },
        {
            "title": "Certification Expiring Soon",
            "message": "ISO 9001 certification expires in 30 days. Renewal process should begin.",
            "type": "certification",
            "priority": "High",
            "timestamp": current_time - datetime.timedelta(days=1),
            "status": "Read",
            "category": "Compliance",
            "sender": "Certification System"
        },
        {
            "title": "Subscription Payment Due",
            "message": "Monthly subscription payment of $299.99 is due in 3 days.",
            "type": "subscription",
            "priority": "Medium",
            "timestamp": current_time - datetime.timedelta(days=2),
            "status": "Unread",
            "category": "Billing",
            "sender": "Billing System"
        },
        {
            "title": "Backup Completed Successfully",
            "message": "Daily database backup completed successfully at 2:00 AM EST.",
            "type": "system",
            "priority": "Info",
            "timestamp": current_time - datetime.timedelta(days=1),
            "status": "Read",
            "category": "System",
            "sender": "Backup System"
        }
    ]
    
    # Add more random notifications
    for i in range(15):
        notifications.append({
            "title": f"Sample Notification {i + 11}",
            "message": f"This is a sample notification message for testing purposes. ID: {i + 11}",
            "type": np.random.choice(notification_types),
            "priority": np.random.choice(priorities),
            "timestamp": current_time - datetime.timedelta(
                hours=np.random.randint(1, 72),
                minutes=np.random.randint(0, 60)
            ),
            "status": np.random.choice(statuses),
            "category": np.random.choice(["System", "User", "Equipment", "Quality", "Security"]),
            "sender": np.random.choice(["System", "Admin", "QA Team", "IT Support"])
        })
    
    # Combine all notifications
    all_notifications = sample_notifications + notifications
    
    # Add IDs and format timestamps
    for i, notif in enumerate(all_notifications):
        notif["id"] = i + 1
        notif["time_ago"] = format_time_ago(notif["timestamp"])
    
    return all_notifications

def get_notification_stats(notifications):
    """Get statistics about notifications"""
    total_notifications = len(notifications)
    unread_count = len([n for n in notifications if n["status"] == "Unread"])
    critical_count = len([n for n in notifications if n["priority"] == "Critical"])
    
    # Priority distribution
    priority_counts = {}
    for priority in ["Critical", "High", "Medium", "Low", "Info"]:
        priority_counts[priority] = len([n for n in notifications if n["priority"] == priority])
    
    # Type distribution
    type_counts = {}
    types = list(set([n["type"] for n in notifications]))
    for ntype in types:
        type_counts[ntype] = len([n for n in notifications if n["type"] == ntype])
    
    # Recent activity (last 24 hours)
    recent_notifications = [
        n for n in notifications 
        if (datetime.datetime.now() - n["timestamp"]).total_seconds() < 86400
    ]
    
    return {
        "total": total_notifications,
        "unread": unread_count,
        "critical": critical_count,
        "priority_distribution": priority_counts,
        "type_distribution": type_counts,
        "recent_count": len(recent_notifications)
    }

# Generate sample data
notifications = generate_sample_notifications()
stats = get_notification_stats(notifications)

# TAB 1: DASHBOARD
with tabs[0]:
    st.subheader("📊 Notification Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Notifications",
            value=stats["total"],
            delta=f"+{stats['recent_count']} today"
        )
    
    with col2:
        st.metric(
            label="Unread",
            value=stats["unread"],
            delta=f"{stats['unread']/stats['total']*100:.1f}% of total"
        )
    
    with col3:
        st.metric(
            label="Critical Alerts",
            value=stats["critical"],
            delta="Requires attention" if stats["critical"] > 0 else "All clear"
        )
    
    with col4:
        st.metric(
            label="Last 24 Hours",
            value=stats["recent_count"],
            delta="Recent activity"
        )
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution
        priority_df = pd.DataFrame(
            list(stats["priority_distribution"].items()),
            columns=["Priority", "Count"]
        )
        priority_df = priority_df[priority_df["Count"] > 0]  # Only show non-zero counts
        
        fig_priority = px.pie(
            priority_df,
            values="Count",
            names="Priority",
            title="Notification Priority Distribution",
            color="Priority",
            color_discrete_map={
                "Critical": "#dc3545",
                "High": "#fd7e14", 
                "Medium": "#ffc107",
                "Low": "#28a745",
                "Info": "#17a2b8"
            }
        )
        fig_priority.update_layout(height=400)
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        # Type distribution
        type_df = pd.DataFrame(
            list(stats["type_distribution"].items()),
            columns=["Type", "Count"]
        )
        type_df = type_df[type_df["Count"] > 0]  # Only show non-zero counts
        
        fig_types = px.bar(
            type_df,
            x="Type",
            y="Count",
            title="Notification Types",
            color="Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_types.update_layout(height=400, showlegend=False)
        fig_types.update_xaxes(tickangle=45)
        st.plotly_chart(fig_types, use_container_width=True)
    
    # Timeline chart
    st.subheader("📈 Notification Timeline")
    
    # Group notifications by date for timeline
    timeline_data = {}
    for notif in notifications:
        date_str = notif["timestamp"].strftime("%Y-%m-%d")
        if date_str not in timeline_data:
            timeline_data[date_str] = {"total": 0, "critical": 0, "high": 0}
        timeline_data[date_str]["total"] += 1
        if notif["priority"] == "Critical":
            timeline_data[date_str]["critical"] += 1
        elif notif["priority"] == "High":
            timeline_data[date_str]["high"] += 1
    
    # Create timeline dataframe
    timeline_df = pd.DataFrame([
        {"Date": date, **data} for date, data in timeline_data.items()
    ]).sort_values("Date")
    
    if not timeline_df.empty:
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df["Date"],
            y=timeline_df["total"],
            mode='lines+markers',
            name='Total Notifications',
            line=dict(color='#1f77b4', width=2)
        ))
        fig_timeline.add_trace(go.Scatter(
            x=timeline_df["Date"],
            y=timeline_df["critical"],
            mode='lines+markers',
            name='Critical Notifications',
            line=dict(color='#dc3545', width=2)
        ))
        
        fig_timeline.update_layout(
            title="Notification Activity Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Notifications",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Recent critical notifications
    critical_notifications = [n for n in notifications if n["priority"] == "Critical" and n["status"] == "Unread"]
    
    if critical_notifications:
        st.subheader("🚨 Critical Alerts")
        for notif in critical_notifications[:3]:  # Show top 3 critical
            st.error(f"**{notif['title']}** - {notif['message']} *({notif['time_ago']})*")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Recent Activity")
        recent_notifications = sorted(notifications, key=lambda x: x["timestamp"], reverse=True)[:5]
        
        for notif in recent_notifications:
            icon = get_notification_icon(notif["type"])
            color = get_notification_priority_color(notif["priority"])
            
            st.markdown(f"""
                <div style="padding: 10px; border-left: 4px solid {color}; margin-bottom: 10px; background-color: #f8f9fa;">
                    <strong>{icon} {notif['title']}</strong><br>
                    <small style="color: #6c757d;">{notif['time_ago']} • {notif['priority']} • {notif['sender']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📋 Quick Actions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📩 Mark All as Read", use_container_width=True):
                st.success("All notifications marked as read!")
        
        with col_b:
            if st.button("🗑️ Clear Old Notifications", use_container_width=True):
                st.success("Old notifications cleared!")
        
        if st.button("⚙️ Notification Settings", use_container_width=True):
            st.info("Redirecting to notification settings...")
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Notification report generated!")

# TAB 2: ALL NOTIFICATIONS
with tabs[1]:
    st.subheader("📋 All Notifications")
    
    # Filter controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Unread", "Read", "Archived"],
            index=0
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priority",
            options=["All", "Critical", "High", "Medium", "Low", "Info"],
            index=0
        )
    
    with col3:
        type_filter = st.selectbox(
            "Type",
            options=["All"] + list(set([n["type"] for n in notifications])),
            index=0
        )
    
    with col4:
        search_term = st.text_input("🔍 Search", placeholder="Search notifications...")
    
    # Filter notifications
    filtered_notifications = notifications.copy()
    
    if status_filter != "All":
        filtered_notifications = [n for n in filtered_notifications if n["status"] == status_filter]
    
    if priority_filter != "All":
        filtered_notifications = [n for n in filtered_notifications if n["priority"] == priority_filter]
    
    if type_filter != "All":
        filtered_notifications = [n for n in filtered_notifications if n["type"] == type_filter]
    
    if search_term:
        filtered_notifications = [
            n for n in filtered_notifications 
            if search_term.lower() in n["title"].lower() or search_term.lower() in n["message"].lower()
        ]
    
    st.markdown(f"**Showing {len(filtered_notifications)} of {len(notifications)} notifications**")
    
    # Pagination
    items_per_page = 10
    total_pages = (len(filtered_notifications) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
    else:
        page = 0
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_notifications = filtered_notifications[start_idx:end_idx]
    
    # Display notifications
    for notif in page_notifications:
        icon = get_notification_icon(notif["type"])
        color = get_notification_priority_color(notif["priority"])
        
        # Create container for each notification
        with st.container():
            col1, col2, col3 = st.columns([8, 2, 2])
            
            with col1:
                status_indicator = "🔵" if notif["status"] == "Unread" else "⚪"
                st.markdown(f"""
                    <div style="padding: 15px; border-left: 4px solid {color}; margin-bottom: 10px; background-color: {'#f8f9fa' if notif['status'] == 'Read' else '#ffffff'}; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="margin-right: 10px;">{status_indicator}</span>
                            <strong style="font-size: 16px;">{icon} {notif['title']}</strong>
                            <span style="margin-left: auto; background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{notif['priority']}</span>
                        </div>
                        <p style="margin: 10px 0; color: #333;">{notif['message']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <small style="color: #6c757d;">
                                📅 {notif['timestamp'].strftime('%Y-%m-%d %H:%M')} • 
                                📁 {notif['category']} • 
                                👤 {notif['sender']}
                            </small>
                            <small style="color: #007bff; font-weight: bold;">{notif['time_ago']}</small>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if notif["status"] == "Unread":
                    if st.button("Mark Read", key=f"read_{notif['id']}", use_container_width=True):
                        st.success("Marked as read!")
                        st.rerun()
            
            with col3:
                if st.button("Archive", key=f"archive_{notif['id']}", use_container_width=True):
                    st.success("Archived!")
                    st.rerun()

# TAB 3: SYSTEM ALERTS
with tabs[2]:
    st.subheader("⚠️ System Alerts")
    
    # Filter for system-related notifications
    system_notifications = [
        n for n in notifications 
        if n["type"] in ["system", "security", "maintenance", "device"]
    ]
    
    # Group by priority
    critical_alerts = [n for n in system_notifications if n["priority"] == "Critical"]
    high_alerts = [n for n in system_notifications if n["priority"] == "High"]
    other_alerts = [n for n in system_notifications if n["priority"] not in ["Critical", "High"]]
    
    # Critical alerts section
    if critical_alerts:
        st.error("🚨 **CRITICAL ALERTS** - Immediate Action Required")
        for alert in critical_alerts:
            icon = get_notification_icon(alert["type"])
            st.markdown(f"""
                <div style="padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{icon} {alert['title']}</strong><br>
                    {alert['message']}<br>
                    <small>🕐 {alert['time_ago']} | 📧 {alert['sender']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    # High priority alerts
    if high_alerts:
        st.warning("🔶 **HIGH PRIORITY ALERTS**")
        for alert in high_alerts:
            icon = get_notification_icon(alert["type"])
            st.markdown(f"""
                <div style="padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{icon} {alert['title']}</strong><br>
                    {alert['message']}<br>
                    <small>🕐 {alert['time_ago']} | 📧 {alert['sender']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Other alerts
    if other_alerts:
        st.info("📢 **OTHER SYSTEM NOTIFICATIONS**")
        for alert in other_alerts[:5]:  # Limit to 5 for space
            icon = get_notification_icon(alert["type"])
            st.markdown(f"• {icon} **{alert['title']}** - {alert['message']} *({alert['time_ago']})*")
    
    # System status overview
    st.divider()
    st.subheader("🖥️ System Status Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Health", "98.5%", "↑ 0.2%")
        st.metric("Active Devices", "23/25", "2 offline")
    
    with col2:
        st.metric("Security Status", "Secure", "No threats")
        st.metric("Last Backup", "2 hours ago", "Successful")
    
    with col3:
        st.metric("System Load", "45%", "Normal")
        st.metric("Storage Used", "67%", "33% free")

# TAB 4: USER ACTIVITY
with tabs[3]:
    st.subheader("👥 User Activity Notifications")
    
    # Filter for user-related notifications
    user_notifications = [
        n for n in notifications 
        if n["type"] in ["user", "blueprint", "quality", "certification"]
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent User Actions")
        for notif in user_notifications[:8]:
            icon = get_notification_icon(notif["type"])
            color = get_notification_priority_color(notif["priority"])
            
            st.markdown(f"""
                <div style="padding: 10px; border-left: 3px solid {color}; margin-bottom: 8px; background-color: #f8f9fa;">
                    <strong>{icon} {notif['title']}</strong><br>
                    <small style="color: #6c757d;">{notif['time_ago']} • {notif['sender']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Activity Summary")
        
        # Activity metrics
        st.metric("New Registrations", "3", "This week")
        st.metric("Blueprint Uploads", "12", "+5 from last week")
        st.metric("Quality Checks", "45", "This month")
        st.metric("Certifications", "2", "Expiring soon")
        
        # Activity chart
        activity_data = pd.DataFrame({
            "Activity": ["Logins", "Uploads", "Reviews", "Approvals"],
            "Count": [45, 12, 8, 6]
        })
        
        fig_activity = px.bar(
            activity_data,
            x="Activity",
            y="Count",
            title="User Activity This Week",
            color="Activity",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_activity.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_activity, use_container_width=True)

# TAB 5: SETTINGS
with tabs[4]:
    st.subheader("⚙️ Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### General Settings")
        
        st.checkbox("Enable email notifications", value=True)
        st.checkbox("Enable browser notifications", value=True)
        st.checkbox("Enable mobile notifications", value=False)
        
        st.selectbox(
            "Notification frequency",
            options=["Real-time", "Hourly", "Daily", "Weekly"],
            index=0
        )
        
        st.selectbox(
            "Default priority filter",
            options=["All", "Critical and High", "Critical only"],
            index=1
        )
        
        st.markdown("### Quiet Hours")
        start_time = st.time_input("Start time", datetime.time(22, 0))
        end_time = st.time_input("End time", datetime.time(8, 0))
        
        if st.button("Save General Settings", use_container_width=True):
            st.success("General settings saved!")
    
    with col2:
        st.markdown("### Notification Types")
        
        notification_types = [
            ("System alerts", True),
            ("Security notifications", True),
            ("Device status", True),
            ("Material inventory", True),
            ("Quality assurance", True),
            ("User management", False),
            ("Blueprint updates", True),
            ("Certification reminders", True),
            ("Billing notifications", True),
            ("Maintenance schedules", True)
        ]
        
        for notif_type, default_value in notification_types:
            st.checkbox(notif_type, value=default_value)
        
        if st.button("Save Notification Types", use_container_width=True):
            st.success("Notification type preferences saved!")
        
        st.markdown("### Advanced Settings")
        
        st.number_input("Notification retention (days)", min_value=1, max_value=365, value=30)
        st.number_input("Auto-archive after (days)", min_value=1, max_value=180, value=7)
        
        if st.button("Reset to Defaults", use_container_width=True):
            st.warning("Settings reset to default values!")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #6c757d; font-size: 0.9rem; margin-top: 2rem;'>
        MITACS Dashboard - Notification Center | 
        <a href='#' style='color: #007bff;'>Documentation</a> | 
        <a href='#' style='color: #007bff;'>Support</a> | 
        <a href='#' style='color: #007bff;'>Privacy Policy</a>
    </div>
    """,
    unsafe_allow_html=True,
)

