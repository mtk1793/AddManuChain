import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import time
from io import BytesIO
import base64
from sqlalchemy import desc, func, and_
import numpy as np
from src.db.models.blueprint import Blueprint
from src.db.models.certification import Certification
from src.db.models.user import User
from src.db.connection import get_db_session, Session
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_blueprints_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="MITACS Blueprints",
    page_icon="📐",
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
    page_title="Blueprints",
    page_type="management",
    **get_blueprints_page_context()
)

# Render the floating AI assistant
render_page_ai_assistant()

# Page header with icon
st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <h1 style="margin-right: 10px;">📐 Blueprints</h1>
        <span style="color: #6c757d; font-size: 1.2rem;">Design & Engineering Assets</span>
    </div>
""", unsafe_allow_html=True)

# Last updated timestamp
st.markdown(
    f"<p style='color: #6c757d; text-align: right;'>Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    unsafe_allow_html=True,
)

# Create tabs for different blueprint views
tabs = st.tabs(["Dashboard", "Browse Blueprints", "My Blueprints", "Upload Blueprint", "Analytics"])

# Blueprint Functions
def get_blueprints_from_db(page=1, limit=10, search_term=None, status_filter=None, creator_filter=None):
    """Get blueprints from database with filters"""
    with get_db_session() as session:
        query = session.query(Blueprint)
        
        # Apply filters if provided
        if search_term:
            query = query.filter(
                (Blueprint.name.ilike(f'%{search_term}%')) | 
                (Blueprint.description.ilike(f'%{search_term}%'))
            )
            
        if status_filter:
            query = query.filter(Blueprint.status == status_filter)
            
        if creator_filter:
            query = query.filter(Blueprint.creator_id == creator_filter)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        blueprints = query.order_by(desc(Blueprint.last_modified)).offset(offset).limit(limit).all()
        
        result = []
        for blueprint in blueprints:
            creator = session.query(User).filter(User.id == blueprint.creator_id).first()
            creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
            
            result.append({
                "id": blueprint.id,
                "name": blueprint.name,
                "description": blueprint.description,
                "file_path": blueprint.file_path,
                "file_type": blueprint.file_type,
                "version": blueprint.version,
                "creator_id": blueprint.creator_id,
                "creator_name": creator_name,
                "creation_date": blueprint.creation_date,
                "last_modified": blueprint.last_modified,
                "status": blueprint.status,
                "notes": blueprint.notes,
                "certifications": [cert.name for cert in blueprint.certifications],
                "product_count": len(blueprint.products)
            })
            
        return result, total_count

def get_blueprint_by_id(blueprint_id):
    """Get a single blueprint by ID"""
    with get_db_session() as session:
        blueprint = session.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
        
        if not blueprint:
            return None
            
        creator = session.query(User).filter(User.id == blueprint.creator_id).first()
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
        
        return {
            "id": blueprint.id,
            "name": blueprint.name,
            "description": blueprint.description,
            "file_path": blueprint.file_path,
            "file_type": blueprint.file_type,
            "version": blueprint.version,
            "creator_id": blueprint.creator_id,
            "creator_name": creator_name,
            "creation_date": blueprint.creation_date,
            "last_modified": blueprint.last_modified,
            "status": blueprint.status,
            "notes": blueprint.notes,
            "certifications": [
                {
                    "id": cert.id,
                    "name": cert.name,
                    "authority": cert.authority,
                    "issue_date": cert.issue_date,
                    "expiry_date": cert.expiry_date
                } 
                for cert in blueprint.certifications
            ],
            "products": [
                {
                    "id": product.id,
                    "name": product.name
                }
                for product in blueprint.products
            ]
        }

def save_uploaded_blueprint(uploaded_file, name, description, version, creator_id, status="Draft", notes=None, certification_ids=None):
    """Save uploaded blueprint file and create record in database"""
    with get_db_session() as session:
        # Create directory if it doesn't exist
        upload_dir = os.path.join("static", "uploads", "blueprints")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = "".join(c if c.isalnum() else "_" for c in name)
        filename = f"{safe_name}_{timestamp}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        try:
            # Save uploaded file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Create new blueprint record
            new_blueprint = Blueprint(
                name=name,
                description=description,
                file_path=file_path,
                file_type=file_extension.upper(),
                version=version,
                creator_id=creator_id,
                status=status,
                notes=notes,
                creation_date=datetime.datetime.utcnow(),
                last_modified=datetime.datetime.utcnow()
            )
            
            session.add(new_blueprint)
            
            # Add certifications if provided
            if certification_ids:
                certifications = session.query(Certification).filter(Certification.id.in_(certification_ids)).all()
                new_blueprint.certifications = certifications
            
            session.commit()
            return True, new_blueprint.id
        
        except Exception as e:
            return False, str(e)

def get_blueprint_stats():
    """Get statistics about blueprints"""
    with get_db_session() as session:
        # Total blueprints
        total_blueprints = session.query(func.count(Blueprint.id)).scalar()
        
        # Status distribution
        status_counts = session.query(
            Blueprint.status, func.count(Blueprint.id)
        ).group_by(Blueprint.status).all()
        
        status_distribution = {status: count for status, count in status_counts}
        
        # File type distribution
        file_type_counts = session.query(
            Blueprint.file_type, func.count(Blueprint.id)
        ).group_by(Blueprint.file_type).all()
        
        file_type_distribution = {file_type: count for file_type, count in file_type_counts}
        
        # Top creators
        top_creators = session.query(
            User.first_name, User.last_name, func.count(Blueprint.id).label("count")
        ).join(Blueprint, Blueprint.creator_id == User.id)\
         .group_by(User.id)\
         .order_by(func.count(Blueprint.id).desc())\
         .limit(5)\
         .all()
        
        top_creators_list = [
            {"name": f"{first_name} {last_name}", "count": count}
            for first_name, last_name, count in top_creators
        ]
        
        # Recent activity
        recent_blueprints = session.query(Blueprint)\
            .order_by(desc(Blueprint.last_modified))\
            .limit(10)\
            .all()
        
        recent_activity = []
        for blueprint in recent_blueprints:
            creator = session.query(User).filter(User.id == blueprint.creator_id).first()
            creator_name = f"{creator.first_name} {creator.last_name}" if creator else "Unknown"
            
            # Determine if it was created or updated
            action = "Created" if blueprint.creation_date == blueprint.last_modified else "Updated"
            
            recent_activity.append({
                "id": blueprint.id,
                "name": blueprint.name,
                "action": action,
                "date": blueprint.last_modified,
                "user": creator_name,
                "status": blueprint.status
            })
        
        return {
            "total_blueprints": total_blueprints,
            "status_distribution": status_distribution,
            "file_type_distribution": file_type_distribution,
            "top_creators": top_creators_list,
            "recent_activity": recent_activity
        }

# Define a header with custom style
def section_header(title):
    st.markdown(
        f"<div class='section-header'><h3>{title}</h3></div>",
        unsafe_allow_html=True,
    )

# Format date for display
def format_date(date):
    if isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    
    if isinstance(date, datetime.datetime):
        return date.strftime("%Y-%m-%d %H:%M")
    return str(date)

# Generate a download link for a file
def get_download_link(file_path, link_text="Download"):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        filename = os.path.basename(file_path)
        mime_type = "application/octet-stream"
        if file_path.endswith(".stl"):
            mime_type = "model/stl"
        elif file_path.endswith(".obj"):
            mime_type = "model/obj"
        
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" target="_blank">{link_text}</a>'
        return href
    except Exception as e:
        return f"Error: {str(e)}"

# Get file icon based on file type
def get_file_icon(file_type):
    file_type = file_type.lower() if file_type else ""
    icons = {
        "stl": "📦",
        "obj": "🧊",
        "step": "🔧",
        "iges": "📐",
        "dwg": "📝",
        "dxf": "📄"
    }
    return icons.get(file_type, "📄")

# Generate sample blueprint data for visualization
def generate_sample_blueprint_data():
    # Blueprint status data
    blueprint_status = pd.DataFrame({
        "Status": ["Approved", "Draft", "Review", "Deprecated"],
        "Count": [35, 24, 8, 5],
    })
    
    # Blueprint types data
    blueprint_types = pd.DataFrame({
        "File Type": ["STL", "OBJ", "STEP", "Other"],
        "Count": [42, 18, 9, 3],
    })
    
    # Recent blueprints
    current_date = datetime.datetime.now()
    dates = [(current_date - datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30, 0, -1)]
    
    blueprint_timeline = pd.DataFrame({
        "Date": dates,
        "New Blueprints": np.random.randint(0, 5, size=30),
        "Updated Blueprints": np.random.randint(0, 8, size=30),
    })
    
    # Top creators
    top_creators = pd.DataFrame({
        "Creator": ["John Smith", "Maria Garcia", "Ahmed Hassan", "Li Wei", "Sarah Johnson"],
        "Blueprints": [28, 23, 19, 16, 14],
    })
    
    # Recent activity
    recent_activity = pd.DataFrame({
        "Date": [
            current_date - datetime.timedelta(hours=2),
            current_date - datetime.timedelta(hours=5),
            current_date - datetime.timedelta(hours=12),
            current_date - datetime.timedelta(days=1),
            current_date - datetime.timedelta(days=1, hours=6),
            current_date - datetime.timedelta(days=2),
            current_date - datetime.timedelta(days=2, hours=8),
            current_date - datetime.timedelta(days=3),
        ],
        "User": [
            "Maria Garcia",
            "John Smith",
            "Ahmed Hassan",
            "Li Wei",
            "Sarah Johnson",
            "Maria Garcia",
            "Ahmed Hassan",
            "Sarah Johnson",
        ],
        "Action": [
            "Created new blueprint: 'Engine Valve v2'",
            "Updated blueprint: 'Fuel Pump Housing'",
            "Approved blueprint: 'Coolant System'",
            "Created new blueprint: 'Exhaust Manifold'",
            "Deprecated blueprint: 'Transmission v1'",
            "Created new blueprint: 'Brake Caliper'",
            "Updated blueprint: 'Oil Filter Mount'",
            "Approved blueprint: 'Intake System v3'",
        ],
        "Category": [
            "Create",
            "Update",
            "Approval",
            "Create",
            "Status Change",
            "Create",
            "Update",
            "Approval",
        ]
    })
    
    # Blueprint usage in products
    blueprint_usage = pd.DataFrame({
        "Blueprint": ["Fuel Pump Housing", "Engine Valve v2", "Exhaust Manifold", "Intake System v3", "Oil Filter Mount"],
        "Products Using": [12, 8, 6, 5, 3],
    })
    
    # Sample blueprint data for table
    blueprint_data = []
    for i in range(1, 21):
        creator_idx = np.random.randint(0, len(top_creators))
        status_idx = np.random.randint(0, len(blueprint_status))
        file_type_idx = np.random.randint(0, len(blueprint_types))
        
        days_ago = np.random.randint(0, 60)
        creation_date = current_date - datetime.timedelta(days=days_ago)
        
        # Some blueprints were modified recently
        if np.random.random() > 0.7 and days_ago > 0:
            modified_days_ago = np.random.randint(0, days_ago)
            last_modified = current_date - datetime.timedelta(days=modified_days_ago)
        else:
            last_modified = creation_date
            
        blueprint_data.append({
            "id": i,
            "name": f"Blueprint {i}: {['Engine Part', 'Chassis Component', 'Interior Element', 'Exterior Panel', 'Accessory'][i % 5]} v{i % 3 + 1}",
            "description": f"This is a detailed blueprint for manufacturing component #{i}",
            "file_path": f"/static/uploads/blueprints/blueprint_{i}.{blueprint_types['File Type'][file_type_idx].lower()}",
            "file_type": blueprint_types["File Type"][file_type_idx],
            "version": f"1.{i % 10}",
            "creator_id": creator_idx + 1,
            "creator_name": top_creators["Creator"][creator_idx],
            "creation_date": creation_date,
            "last_modified": last_modified,
            "status": blueprint_status["Status"][status_idx],
            "certifications": np.random.choice(["ISO 9001", "ASTM F3091", "CE Mark", "FDA Approval"], 
                                             size=np.random.randint(0, 3), 
                                             replace=False).tolist(),
            "product_count": np.random.randint(0, 10)
        })
    
    return blueprint_status, blueprint_types, blueprint_timeline, top_creators, recent_activity, blueprint_usage, blueprint_data

# Get sample data for now (in production, use get_blueprint_stats())
blueprint_status, blueprint_types, blueprint_timeline, top_creators, recent_activity, blueprint_usage, blueprint_data = generate_sample_blueprint_data()

# TAB 1: DASHBOARD
with tabs[0]:
    st.subheader("📊 Blueprint Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Blueprints",
            value="72",
            delta="8 this month"
        )
    
    with col2:
        st.metric(
            label="Approved",
            value="35",
            delta="3 this week"
        )
    
    with col3:
        st.metric(
            label="In Review",
            value="8",
            delta="-2 from last week"
        )
    
    with col4:
        st.metric(
            label="Active Users",
            value="15",
            delta="2 new this month"
        )
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Blueprint status distribution
        fig_status = px.pie(
            blueprint_status,
            values="Count",
            names="Status",
            title="Blueprint Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # File type distribution
        fig_types = px.bar(
            blueprint_types,
            x="File Type",
            y="Count",
            title="Blueprint File Types",
            color="File Type",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_types.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_types, use_container_width=True)
    
    # Timeline chart
    st.subheader("📈 Blueprint Activity Timeline")
    
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=blueprint_timeline["Date"],
        y=blueprint_timeline["New Blueprints"],
        mode='lines+markers',
        name='New Blueprints',
        line=dict(color='#1f77b4', width=2)
    ))
    fig_timeline.add_trace(go.Scatter(
        x=blueprint_timeline["Date"],
        y=blueprint_timeline["Updated Blueprints"],
        mode='lines+markers',
        name='Updated Blueprints',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig_timeline.update_layout(
        title="Blueprint Activity Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Blueprints",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Recent activity and top creators
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top Contributors")
        for idx, (_, row) in enumerate(top_creators.iterrows()):
            st.markdown(f"**{idx + 1}. {row['Creator']}** - {row['Blueprints']} blueprints")
    
    with col2:
        st.subheader("📋 Recent Activity")
        for _, activity in recent_activity.head(5).iterrows():
            time_ago = (datetime.datetime.now() - activity['Date']).total_seconds() / 3600
            if time_ago < 1:
                time_str = f"{int(time_ago * 60)}m ago"
            elif time_ago < 24:
                time_str = f"{int(time_ago)}h ago"
            else:
                time_str = f"{int(time_ago / 24)}d ago"
            
            st.markdown(f"**{activity['User']}** {activity['Action']} *({time_str})*")

# TAB 2: BROWSE BLUEPRINTS
with tabs[1]:
    st.subheader("🗂️ Browse All Blueprints")
    
    # Search and filter controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search blueprints...", placeholder="Enter name or description")
    
    with col2:
        status_filter = st.selectbox(
            "Status Filter",
            options=["All"] + blueprint_status["Status"].tolist(),
            index=0
        )
    
    with col3:
        file_type_filter = st.selectbox(
            "File Type Filter",
            options=["All"] + blueprint_types["File Type"].tolist(),
            index=0
        )
    
    # Filter blueprint data based on selections
    filtered_blueprints = blueprint_data.copy()
    
    if search_term:
        filtered_blueprints = [
            bp for bp in filtered_blueprints 
            if search_term.lower() in bp["name"].lower() or search_term.lower() in bp["description"].lower()
        ]
    
    if status_filter != "All":
        filtered_blueprints = [bp for bp in filtered_blueprints if bp["status"] == status_filter]
    
    if file_type_filter != "All":
        filtered_blueprints = [bp for bp in filtered_blueprints if bp["file_type"] == file_type_filter]
    
    st.markdown(f"**Found {len(filtered_blueprints)} blueprints**")
    
    # Display blueprints in a grid
    if filtered_blueprints:
        # Pagination
        items_per_page = 6
        total_pages = (len(filtered_blueprints) + items_per_page - 1) // items_per_page
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
        else:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_blueprints = filtered_blueprints[start_idx:end_idx]
        
        # Display blueprints in cards
        for i in range(0, len(page_blueprints), 2):
            col1, col2 = st.columns(2)
            
            for j, col in enumerate([col1, col2]):
                if i + j < len(page_blueprints):
                    bp = page_blueprints[i + j]
                    
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: white;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <span style="font-size: 1.5em; margin-right: 8px;">{get_file_icon(bp['file_type'])}</span>
                                    <h4 style="margin: 0;">{bp['name']}</h4>
                                </div>
                                <p style="color: #666; margin: 8px 0;">{bp['description'][:100]}...</p>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
                                    <span style="background: {'#28a745' if bp['status'] == 'Approved' else '#ffc107' if bp['status'] == 'Review' else '#6c757d'}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{bp['status']}</span>
                                    <small style="color: #666;">v{bp['version']}</small>
                                </div>
                                <div style="margin-top: 8px;">
                                    <small style="color: #666;">By {bp['creator_name']} • {format_date(bp['last_modified'])}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"View Details", key=f"view_{bp['id']}"):
                                st.session_state.selected_blueprint = bp['id']
                                st.rerun()
    else:
        st.info("No blueprints found matching your search criteria.")

# TAB 3: MY BLUEPRINTS
with tabs[2]:
    st.subheader("👤 My Blueprints")
    
    # Inline upload form triggered by Create Your First Blueprint button
    if st.session_state.get("show_upload_form", False):
        st.subheader("📤 Upload New Blueprint")
        with st.form("upload_blueprint_form_inline"):  
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Blueprint Name *", placeholder="Enter blueprint name")
                version = st.text_input("Version *", placeholder="e.g., 1.0", value="1.0")
                status = st.selectbox("Status", ["Draft", "Review", "Approved"], index=0)
            with col2:
                description = st.text_area("Description", placeholder="Describe your blueprint...")
                notes = st.text_area("Notes", placeholder="Additional notes or comments...")
            uploaded_file = st.file_uploader(
                "Choose blueprint file",
                type=['stl','obj','step','iges','dwg','dxf'],
                help="Supported formats: STL, OBJ, STEP, IGES, DWG, DXF"
            )
            st.multiselect(
                "Related Certifications",
                options=["ISO 9001", "ASTM F3091", "CE Mark", "FDA Approval"],
                help="Select applicable certifications"
            )
            submit_inline = st.form_submit_button("🚀 Upload Blueprint", use_container_width=True)
            if submit_inline:
                if not name or not uploaded_file or not version:
                    st.error("Please fill in all required fields marked with *")
                else:
                    with st.spinner("Uploading blueprint..."):
                        time.sleep(2)
                    st.success(f"✅ Blueprint '{name}' uploaded successfully!")
                    st.info("Your blueprint is now available in the system.")
                    st.session_state.show_upload_form = False
        st.stop()

    # Filter blueprints for current user
    user_blueprints = [bp for bp in blueprint_data if bp['creator_id'] == st.session_state.get('user_id', 1)]
    
    if user_blueprints:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**You have created {len(user_blueprints)} blueprints**")
        
        with col2:
            if st.button("➕ Create New Blueprint", use_container_width=True):
                st.session_state.show_upload_form = True
                st.rerun()
        
        # Display user's blueprints in a table
        df_user_blueprints = pd.DataFrame(user_blueprints)
        df_display = df_user_blueprints[['name', 'status', 'version', 'file_type', 'last_modified', 'product_count']].copy()
        df_display['last_modified'] = df_display['last_modified'].apply(format_date)
        df_display.columns = ['Name', 'Status', 'Version', 'File Type', 'Last Modified', 'Products Using']
        
        st.dataframe(df_display, use_container_width=True)
        
        # Blueprint actions
        st.subheader("📊 Your Blueprint Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_status_counts = pd.Series([bp['status'] for bp in user_blueprints]).value_counts()
            fig_user_status = px.pie(
                values=user_status_counts.values,
                names=user_status_counts.index,
                title="Your Blueprint Status"
            )
            fig_user_status.update_layout(height=300)
            st.plotly_chart(fig_user_status, use_container_width=True)
        
        with col2:
            user_type_counts = pd.Series([bp['file_type'] for bp in user_blueprints]).value_counts()
            fig_user_types = px.bar(
                x=user_type_counts.index,
                y=user_type_counts.values,
                title="Your File Types"
            )
            fig_user_types.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_user_types, use_container_width=True)
        
        with col3:
            total_products = sum(bp['product_count'] for bp in user_blueprints)
            avg_products = total_products / len(user_blueprints) if user_blueprints else 0
            
            st.metric("Total Products Using Your Blueprints", total_products)
            st.metric("Average Products per Blueprint", f"{avg_products:.1f}")
            
    else:
        st.info("You haven't created any blueprints yet.")
        if st.button("🚀 Create Your First Blueprint", use_container_width=True):
            st.session_state.show_upload_form = True
            st.rerun()

# TAB 4: UPLOAD BLUEPRINT
with tabs[3]:
    st.subheader("📤 Upload New Blueprint")
    
    with st.form("upload_blueprint_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Blueprint Name *", placeholder="Enter blueprint name")
            version = st.text_input("Version *", placeholder="e.g., 1.0", value="1.0")
            status = st.selectbox("Status", ["Draft", "Review", "Approved"], index=0)
        
        with col2:
            description = st.text_area("Description", placeholder="Describe your blueprint...")
            notes = st.text_area("Notes", placeholder="Additional notes or comments...")
        
        uploaded_file = st.file_uploader(
            "Choose blueprint file",
            type=['stl', 'obj', 'step', 'iges', 'dwg', 'dxf'],
            help="Supported formats: STL, OBJ, STEP, IGES, DWG, DXF"
        )
        
        # Certification selection (placeholder)
        st.multiselect(
            "Related Certifications",
            options=["ISO 9001", "ASTM F3091", "CE Mark", "FDA Approval"],
            help="Select applicable certifications"
        )
        
        submit_button = st.form_submit_button("🚀 Upload Blueprint", use_container_width=True)
        
        if submit_button:
            if not name or not uploaded_file or not version:
                st.error("Please fill in all required fields marked with *")
            else:
                # Simulate upload (in production, use save_uploaded_blueprint function)
                with st.spinner("Uploading blueprint..."):
                    time.sleep(2)  # Simulate processing time
                
                st.success(f"✅ Blueprint '{name}' uploaded successfully!")
                st.info("Your blueprint is now available in the system.")
                
                # Show upload details
                st.markdown("### Upload Summary")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Name:** {name}")
                    st.markdown(f"**Version:** {version}")
                    st.markdown(f"**Status:** {status}")
                
                with col2:
                    st.markdown(f"**File:** {uploaded_file.name}")
                    st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
                    st.markdown(f"**Type:** {uploaded_file.type}")

# TAB 5: ANALYTICS
with tabs[4]:
    st.subheader("📊 Blueprint Analytics")
    
    # Time period selector
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        time_period = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 3 months", "Last year"])
    
    with col2:
        chart_type = st.selectbox("Chart Type", ["Line Chart", "Bar Chart", "Area Chart"])
    
    # Analytics sections
    st.divider()
    
    # Blueprint usage in products
    st.subheader("🔗 Blueprint Usage in Products")
    fig_usage = px.bar(
        blueprint_usage,
        x="Products Using",
        y="Blueprint",
        orientation='h',
        title="Top Blueprints by Product Usage",
        color="Products Using",
        color_continuous_scale="viridis"
    )
    fig_usage.update_layout(height=400)
    st.plotly_chart(fig_usage, use_container_width=True)
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Creation Trends")
        
        # Simulate monthly creation data
        months = ["Jan", "Feb", "Mar", "Apr", "May"]
        created_counts = [12, 15, 18, 14, 22]
        
        fig_trends = px.line(
            x=months,
            y=created_counts,
            title="Blueprints Created Per Month",
            markers=True
        )
        fig_trends.update_layout(height=300)
        st.plotly_chart(fig_trends, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ Review Time Analysis")
        
        # Simulate review time data
        review_times = ["< 1 day", "1-3 days", "3-7 days", "> 7 days"]
        review_counts = [15, 25, 18, 8]
        
        fig_review = px.pie(
            values=review_counts,
            names=review_times,
            title="Blueprint Review Times"
        )
        fig_review.update_layout(height=300)
        st.plotly_chart(fig_review, use_container_width=True)
    
    # Quality metrics
    st.subheader("🏆 Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Approval Rate", "87.5%", "2.3%")
    
    with col2:
        st.metric("Avg Review Time", "2.4 days", "-0.5 days")
    
    with col3:
        st.metric("Reuse Rate", "65%", "5%")
    
    with col4:
        st.metric("User Satisfaction", "4.3/5", "0.2")
    
    # Download analytics report
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📊 Download Analytics Report", use_container_width=True):
            st.success("Analytics report downloaded!")

# Handle blueprint detail view
if 'selected_blueprint' in st.session_state and st.session_state.selected_blueprint:
    blueprint_id = st.session_state.selected_blueprint
    selected_bp = next((bp for bp in blueprint_data if bp['id'] == blueprint_id), None)
    
    if selected_bp:
        with st.expander(f"📋 Blueprint Details: {selected_bp['name']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {selected_bp['description']}")
                st.markdown(f"**Version:** {selected_bp['version']}")
                st.markdown(f"**Status:** {selected_bp['status']}")
                st.markdown(f"**File Type:** {selected_bp['file_type']}")
                st.markdown(f"**Creator:** {selected_bp['creator_name']}")
                st.markdown(f"**Created:** {format_date(selected_bp['creation_date'])}")
                st.markdown(f"**Last Modified:** {format_date(selected_bp['last_modified'])}")
                
                if selected_bp['certifications']:
                    st.markdown(f"**Certifications:** {', '.join(selected_bp['certifications'])}")
                
                st.markdown(f"**Products Using This Blueprint:** {selected_bp['product_count']}")
            
            with col2:
                st.markdown("### Actions")
                if st.button("📥 Download", use_container_width=True):
                    st.success("Download started!")
                
                if st.button("📝 Edit", use_container_width=True):
                    st.info("Edit functionality would open here")
                
                if st.button("🔄 Create Version", use_container_width=True):
                    st.info("Version creation would start here")
                
                if st.button("❌ Close", use_container_width=True):
                    del st.session_state.selected_blueprint
                    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6c757d; padding: 1rem;">
        <p>MITACS Blueprint Management System | 
        <a href="#" style="color: #0066cc;">Documentation</a> | 
        <a href="#" style="color: #0066cc;">Support</a> | 
        <a href="#" style="color: #0066cc;">API</a></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Add AI assistant context for this page
add_ai_page_context(
    page_title="Blueprints Management",
    page_type="management",
    **get_blueprints_page_context()
)

# Render the floating AI assistant
render_page_ai_assistant()

