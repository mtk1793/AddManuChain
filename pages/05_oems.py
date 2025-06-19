import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from src.db.connection import get_db_session
from src.db.models.product import OEM, Product
from src.utils.auth import check_authentication, check_authorization
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_oems_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="OEM Management",
    page_icon="🏭",
    layout="wide"
)

# Inject universal CSS styling
inject_universal_css()

# Check authentication
check_authentication()

# Check authorization (allow managers and admins)
check_authorization(["Admin", "Manager"])

# Initialize session state variables
if "show_oem_details" not in st.session_state:
    st.session_state.show_oem_details = False
    
if "selected_oem_id" not in st.session_state:
    st.session_state.selected_oem_id = None
    
if "show_add_oem" not in st.session_state:
    st.session_state.show_add_oem = False
    
if "show_edit_oem" not in st.session_state:
    st.session_state.show_edit_oem = False


def format_currency(value):
    """Format a value as currency"""
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"


def get_all_oems(status=None, location=None, partnership_type=None):
    """Get all OEMs with filtering done in Python rather than SQL"""
    with get_db_session() as session:
        # Only select columns that definitely exist in the database
        query = session.query(OEM).options(
            joinedload(OEM.products)
        )
        
        # Get all OEMs without any SQL filtering
        oems = query.order_by(OEM.name).all()
        
        # Create dictionaries with safe defaults for missing attributes
        oem_list = []
        for oem in oems:
            # Set defaults for any attributes that might not exist
            oem_dict = {
                "id": getattr(oem, "id", None),
                "name": getattr(oem, "name", "Unknown"),
                "contact_name": getattr(oem, "contact_name", "Not specified"),
                "email": getattr(oem, "email", "Not specified"),
                "phone": getattr(oem, "phone", "Not specified"),
                "location": getattr(oem, "location", "Not specified"),
                "partnership_type": getattr(oem, "partnership_type", "Standard"),
                "contract_start_date": getattr(oem, "contract_start_date", None),
                "contract_end_date": getattr(oem, "contract_end_date", None),
                "status": getattr(oem, "status", "Active"),  # Default to Active
                "description": getattr(oem, "description", ""),
                "website": getattr(oem, "website", ""),
                "logo_url": getattr(oem, "logo_url", ""),
                "created_at": getattr(oem, "created_at", datetime.now()),
                "products": [{"id": p.id, "name": p.name, "price": p.price} for p in oem.products] if oem.products else []
            }
            oem_list.append(oem_dict)
        
        # Filter in Python instead of SQL
        filtered_oems = oem_list
        if status:
            filtered_oems = [o for o in filtered_oems if o["status"] in status]
        if location and location.strip():
            filtered_oems = [o for o in filtered_oems if location.lower() in o["location"].lower()]
        if partnership_type:
            filtered_oems = [o for o in filtered_oems if o["partnership_type"] in partnership_type]
            
        return filtered_oems


def get_oem_by_id(oem_id):
    """Get OEM by ID"""
    with get_db_session() as session:
        oem = session.query(OEM).options(
            joinedload(OEM.products)
        ).filter(OEM.id == oem_id).first()
        
        if not oem:
            return None
            
        # Create dictionary with safe defaults
        oem_dict = {
            "id": getattr(oem, "id", None),
            "name": getattr(oem, "name", "Unknown"),
            "contact_name": getattr(oem, "contact_name", "Not specified"),
            "email": getattr(oem, "email", "Not specified"),
            "phone": getattr(oem, "phone", "Not specified"),
            "location": getattr(oem, "location", "Not specified"),
            "partnership_type": getattr(oem, "partnership_type", "Standard"),
            "contract_start_date": getattr(oem, "contract_start_date", None),
            "contract_end_date": getattr(oem, "contract_end_date", None),
            "status": getattr(oem, "status", "Active"),
            "description": getattr(oem, "description", ""),
            "website": getattr(oem, "website", ""),
            "logo_url": getattr(oem, "logo_url", ""),
            "created_at": getattr(oem, "created_at", datetime.now()),
            "products": [{"id": p.id, "name": p.name, "price": p.price, "status": p.status} 
                       for p in oem.products] if oem.products else []
        }
        return oem_dict


def display_oems():
    """Display OEMs with filtering and details"""
    st.title("OEM Management Dashboard")
    
    # Add new OEM button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("➕ Add OEM", use_container_width=True):
            st.session_state.show_add_oem = True
            st.session_state.show_oem_details = False
            st.session_state.show_edit_oem = False
    
    # Filters section
    st.markdown("### Filters")
    filter_cols = st.columns(4)
    
    with filter_cols[0]:
        status_filter = st.multiselect(
            "Status",
            ["Active", "Inactive", "Pending", "Suspended"],
            default=["Active"]
        )
    
    with filter_cols[1]:
        location_filter = st.text_input("Location", "")
    
    with filter_cols[2]:
        partnership_filter = st.multiselect(
            "Partnership Type",
            ["Strategic", "Preferred", "Standard", "Probationary"],
            default=[]
        )
    
    with filter_cols[3]:
        sort_by = st.selectbox(
            "Sort By",
            ["Name (A-Z)", "Name (Z-A)", "Products (High-Low)", "Partnership Level"]
        )
    
    # Get OEMs with filters
    oems = get_all_oems(
        status=status_filter if status_filter else None,
        location=location_filter if location_filter else None,
        partnership_type=partnership_filter if partnership_filter else None
    )
    
    # Convert OEM objects to dictionaries to avoid detached instance errors
    oem_dicts = []
    for oem in oems: # oem is already a dictionary here due to changes in get_all_oems
        products = [{"id": p['id'], "name": p['name'], "price": p['price']} for p in oem['products']] if oem['products'] else []
        
        oem_dict = {
            "id": oem['id'],
            "name": oem['name'],
            "contact_name": oem['contact_name'],
            "email": oem['email'],
            "phone": oem['phone'],
            "location": oem['location'],
            "partnership_type": oem['partnership_type'],
            "contract_start_date": oem['contract_start_date'],
            "contract_end_date": oem['contract_end_date'],
            "status": oem['status'],
            "description": oem['description'],
            "website": oem['website'],
            "logo_url": oem['logo_url'],
            "products": products,
            "product_count": len(products),
            "created_at": oem['created_at']
        }
        oem_dicts.append(oem_dict)
    
    # Apply sorting
    if sort_by == "Name (A-Z)":
        oem_dicts.sort(key=lambda x: x["name"])
    elif sort_by == "Name (Z-A)":
        oem_dicts.sort(key=lambda x: x["name"], reverse=True)
    elif sort_by == "Products (High-Low)":
        oem_dicts.sort(key=lambda x: x["product_count"], reverse=True)
    elif sort_by == "Partnership Level":
        # Define partnership level order
        level_order = {"Strategic": 1, "Preferred": 2, "Standard": 3, "Probationary": 4}
        oem_dicts.sort(key=lambda x: level_order.get(x["partnership_type"], 5))
    
    # Display metrics
    st.markdown("### Key Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric(
            "Total OEMs",
            len(oem_dicts),
            delta=None
        )
    
    with metric_cols[1]:
        active_count = len([o for o in oem_dicts if o["status"] == "Active"])
        st.metric(
            "Active Partnerships",
            active_count,
            delta=f"{int(active_count/len(oem_dicts)*100)}%" if oem_dicts else "0%"
        )
    
    with metric_cols[2]:
        strategic_count = len([o for o in oem_dicts if o["partnership_type"] == "Strategic"])
        st.metric(
            "Strategic Partners",
            strategic_count,
            delta=None
        )
    
    with metric_cols[3]:
        total_products = sum(o["product_count"] for o in oem_dicts)
        avg_products = round(total_products / len(oem_dicts), 1) if oem_dicts else 0
        st.metric(
            "Avg Products per OEM",
            avg_products,
            delta=None
        )
    
    # Visualizations
    st.markdown("### OEM Analytics")
    chart_tabs = st.tabs(["Partnership Distribution", "Product Distribution", "Status Breakdown"])
    
    with chart_tabs[0]:
        if oem_dicts:
            partnership_counts = {}
            for oem in oem_dicts:
                partnership_type = oem["partnership_type"] or "Unspecified"
                partnership_counts[partnership_type] = partnership_counts.get(partnership_type, 0) + 1
            
            fig = px.pie(
                values=list(partnership_counts.values()),
                names=list(partnership_counts.keys()),
                title="OEM Partnership Types",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No OEM data available for visualization")
    
    with chart_tabs[1]:
        if oem_dicts:
            # Create data for horizontal bar chart of product counts
            sorted_oems = sorted(oem_dicts, key=lambda x: x["product_count"], reverse=True)[:10]
            
            fig = px.bar(
                x=[o["product_count"] for o in sorted_oems],
                y=[o["name"] for o in sorted_oems],
                orientation='h',
                labels={"x": "Number of Products", "y": "OEM"},
                title="Top OEMs by Product Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No OEM data available for visualization")
    
    with chart_tabs[2]:
        if oem_dicts:
            status_counts = {}
            for oem in oem_dicts:
                status = oem["status"] or "Unknown"
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = px.bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                labels={"x": "Status", "y": "Count"},
                title="OEM Status Distribution",
                color=list(status_counts.keys()),
                color_discrete_map={
                    "Active": "#2ecc71",
                    "Inactive": "#e74c3c",
                    "Pending": "#f39c12",
                    "Suspended": "#95a5a6"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No OEM data available for visualization")
    
    # Display OEM List
    st.markdown("### OEM Directory")
    st.markdown(f"Showing {len(oem_dicts)} OEMs")
    
    # Display as cards in a grid
    columns = st.columns(3)
    for i, oem in enumerate(oem_dicts):
        with columns[i % 3]:
            with st.container():
                # Card styling
                st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                    <h3>{oem["name"]}</h3>
                    <p><strong>Status:</strong> <span style="color: {'green' if oem['status'] == 'Active' else 'red'};">{oem["status"]}</span></p>
                    <p><strong>Partnership:</strong> {oem["partnership_type"] or "Not specified"}</p>
                    <p><strong>Products:</strong> {oem["product_count"]}</p>
                    <p><strong>Location:</strong> {oem["location"] or "Not specified"}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Details", key=f"view_{oem['id']}"):
                        st.session_state.selected_oem_id = oem["id"]
                        st.session_state.show_oem_details = True
                        st.session_state.show_add_oem = False
                        st.session_state.show_edit_oem = False
                
                with col2:
                    if st.button("Edit", key=f"edit_{oem['id']}"):
                        st.session_state.selected_oem_id = oem["id"]
                        st.session_state.show_edit_oem = True
                        st.session_state.show_oem_details = False
                        st.session_state.show_add_oem = False


def display_oem_details():
    """Display details for a specific OEM"""
    oem_id = st.session_state.selected_oem_id
    
    # Use context manager to query OEM
    with get_db_session() as session:
        oem = session.query(OEM).options(
            joinedload(OEM.products)
        ).filter(OEM.id == oem_id).first()
        
        if not oem:
            st.error("OEM not found")
            st.session_state.show_oem_details = False
            return
        
        # Create dictionary from OEM to avoid detached instance errors
        products = [{"id": p.id, "name": p.name, "price": p.price, "status": p.status} 
                   for p in oem.products] if oem.products else []
        
        oem_dict = {
            "id": oem.id,
            "name": oem.name,
            "contact_name": oem.contact_name,
            "email": oem.email,
            "phone": oem.phone,
            "location": oem.location,
            "partnership_type": oem.partnership_type,
            "contract_start_date": oem.contract_start_date,
            "contract_end_date": oem.contract_end_date,
            "status": oem.status,
            "description": oem.description,
            "website": oem.website,
            "logo_url": oem.logo_url,
            "products": products,
            "created_at": oem.created_at
        }
    
    # Back button
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("← Back"):
            st.session_state.show_oem_details = False
            st.session_state.selected_oem_id = None
    
    # OEM details header
    st.title(oem_dict["name"])
    
    status_color = {
        "Active": "green",
        "Inactive": "red",
        "Pending": "orange",
        "Suspended": "gray"
    }.get(oem_dict["status"], "gray")
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <span style="background-color: {status_color}; 
                    color: white; 
                    padding: 5px 10px; 
                    border-radius: 15px; 
                    font-size: 0.8em; 
                    margin-right: 10px;">
            {oem_dict["status"]}
        </span>
        <span style="background-color: #3498db; 
                    color: white; 
                    padding: 5px 10px; 
                    border-radius: 15px; 
                    font-size: 0.8em;">
            {oem_dict["partnership_type"] or "No partnership type"}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic info and contact section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        st.markdown(f"""
        * **ID:** {oem_dict["id"]}
        * **Location:** {oem_dict["location"] or "Not specified"}
        * **Website:** {oem_dict["website"] or "Not available"}
        * **Onboarded:** {oem_dict["created_at"].strftime('%Y-%m-%d') if oem_dict["created_at"] else "Unknown"}
        """)
        
        # Contract information
        st.subheader("Contract Information")
        contract_start = oem_dict["contract_start_date"].strftime('%Y-%m-%d') if oem_dict["contract_start_date"] else "Not set"
        contract_end = oem_dict["contract_end_date"].strftime('%Y-%m-%d') if oem_dict["contract_end_date"] else "Not set"
        
        # Check if contract is expired
        contract_status = "Active"
        status_color = "green"
        if oem_dict["contract_end_date"] and oem_dict["contract_end_date"] < datetime.now():
            contract_status = "Expired"
            status_color = "red"
        elif oem_dict["contract_end_date"] and oem_dict["contract_end_date"] < datetime.now() + timedelta(days=30):
            contract_status = "Expiring Soon"
            status_color = "orange"
        
        st.markdown(f"""
        * **Start Date:** {contract_start}
        * **End Date:** {contract_end}
        * **Status:** <span style="color: {status_color};">{contract_status}</span>
        * **Partnership Type:** {oem_dict["partnership_type"] or "Not specified"}
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Contact Information")
        st.markdown(f"""
        * **Contact Name:** {oem_dict["contact_name"] or "Not specified"}
        * **Email:** {oem_dict["email"] or "Not specified"}
        * **Phone:** {oem_dict["phone"] or "Not specified"}
        """)
        
        # Description
        st.subheader("Description")
        st.write(oem_dict["description"] or "No description available")
    
    # Products section
    st.subheader(f"Products ({len(oem_dict['products'])})")
    
    if not oem_dict["products"]:
        st.info("No products associated with this OEM")
    else:
        # Create a DataFrame for better display
        df = pd.DataFrame(oem_dict["products"])
        st.dataframe(
            df,
            column_config={
                "id": "ID",
                "name": "Product Name",
                "price": st.column_config.NumberColumn(
                    "Price ($)",
                    format="$%.2f"
                ),
                "status": "Status"
            },
            use_container_width=True
        )
    
    # Actions
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edit OEM", use_container_width=True):
            st.session_state.show_edit_oem = True
            st.session_state.show_oem_details = False
    
    with col2:
        if oem_dict["status"] == "Active":
            if st.button("Deactivate OEM", use_container_width=True):
                with get_db_session() as session:
                    oem = session.query(OEM).filter(OEM.id == oem_dict["id"]).first()
                    if oem:
                        oem.status = "Inactive"
                        session.commit()
                        st.success("OEM deactivated successfully")
                        st.session_state.show_oem_details = False
        else:
            if st.button("Activate OEM", use_container_width=True):
                with get_db_session() as session:
                    oem = session.query(OEM).filter(OEM.id == oem_dict["id"]).first()
                    if oem:
                        oem.status = "Active"
                        session.commit()
                        st.success("OEM activated successfully")
                        st.session_state.show_oem_details = False
    
    with col3:
        if st.button("Delete OEM", use_container_width=True, type="primary"):
            st.warning("Are you sure you want to delete this OEM?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete", key="confirm_delete"):
                    with get_db_session() as session:
                        oem = session.query(OEM).filter(OEM.id == oem_dict["id"]).first()
                        if oem:
                            session.delete(oem)
                            session.commit()
                            st.success("OEM deleted successfully")
                            st.session_state.show_oem_details = False
            with col2:
                if st.button("Cancel"):
                    pass


def add_oem_form():
    """Form for adding a new OEM"""
    st.title("Add New OEM")
    
    # Back button
    if st.button("← Back"):
        st.session_state.show_add_oem = False
    
    with st.form("add_oem_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("OEM Name*", placeholder="Enter OEM name")
            contact_name = st.text_input("Contact Person", placeholder="Enter contact name")
            email = st.text_input("Email", placeholder="Enter email address")
            phone = st.text_input("Phone", placeholder="Enter phone number")
            location = st.text_input("Location", placeholder="City, Country")
            
        with col2:
            partnership_type = st.selectbox(
                "Partnership Type",
                ["Strategic", "Preferred", "Standard", "Probationary", ""]
            )
            
            contract_start = st.date_input("Contract Start Date", datetime.now())
            contract_end = st.date_input("Contract End Date", datetime.now() + timedelta(days=365))
            website = st.text_input("Website", placeholder="https://")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive", "Pending"]
            )
        
        description = st.text_area("Description", placeholder="Enter description or notes about this OEM")
        logo_url = st.text_input("Logo URL", placeholder="https://example.com/logo.png")
        
        submitted = st.form_submit_button("Create OEM")
        
        if submitted:
            if not name:
                st.error("OEM name is required")
            else:
                try:
                    with get_db_session() as session:
                        # Only set the fields that actually exist in your database
                        new_oem = OEM(
                            name=name
                            # Add other fields only if they exist in your database
                            # contact_name=contact_name,
                            # email=email,
                            # etc.
                        )
                        session.add(new_oem)
                        session.commit()
                        st.success(f"OEM '{name}' created successfully!")
                        st.session_state.show_add_oem = False
                except Exception as e:
                    st.error(f"Error creating OEM: {str(e)}")


def edit_oem_form():
    """Form for editing an existing OEM"""
    oem_id = st.session_state.selected_oem_id
    
    # Query the OEM
    with get_db_session() as session:
        oem = session.query(OEM).filter(OEM.id == oem_id).first()
        
        if not oem:
            st.error("OEM not found")
            st.session_state.show_edit_oem = False
            return
        
        # Create a copy of the OEM data
        oem_data = {
            "id": oem.id,
            "name": oem.name,
            "contact_name": oem.contact_name,
            "email": oem.email,
            "phone": oem.phone,
            "location": oem.location,
            "partnership_type": oem.partnership_type,
            "contract_start_date": oem.contract_start_date,
            "contract_end_date": oem.contract_end_date,
            "status": oem.status,
            "description": oem.description,
            "website": oem.website,
            "logo_url": oem.logo_url
        }
    
    st.title(f"Edit OEM: {oem_data['name']}")
    
    # Back button
    if st.button("← Back"):
        st.session_state.show_edit_oem = False
    
    with st.form("edit_oem_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("OEM Name*", value=oem_data["name"])
            contact_name = st.text_input("Contact Person", value=oem_data["contact_name"] or "")
            email = st.text_input("Email", value=oem_data["email"] or "")
            phone = st.text_input("Phone", value=oem_data["phone"] or "")
            location = st.text_input("Location", value=oem_data["location"] or "")
            
        with col2:
            partnership_options = ["Strategic", "Preferred", "Standard", "Probationary", ""]
            selected_partnership = oem_data["partnership_type"] if oem_data["partnership_type"] in partnership_options else ""
            
            partnership_type = st.selectbox(
                "Partnership Type",
                options=partnership_options,
                index=partnership_options.index(selected_partnership) if selected_partnership in partnership_options else 0
            )
            
            contract_start = st.date_input(
                "Contract Start Date", 
                oem_data["contract_start_date"] if oem_data["contract_start_date"] else datetime.now()
            )
            
            contract_end = st.date_input(
                "Contract End Date", 
                oem_data["contract_end_date"] if oem_data["contract_end_date"] else datetime.now() + timedelta(days=365)
            )
            
            website = st.text_input("Website", value=oem_data["website"] or "")
            
            status_options = ["Active", "Inactive", "Pending", "Suspended"]
            selected_status = oem_data["status"] if oem_data["status"] in status_options else "Active"
            
            status = st.selectbox(
                "Status",
                options=status_options,
                index=status_options.index(selected_status)
            )
        
        description = st.text_area("Description", value=oem_data["description"] or "")
        logo_url = st.text_input("Logo URL", value=oem_data["logo_url"] or "")
        
        submitted = st.form_submit_button("Update OEM")
        
        if submitted:
            if not name:
                st.error("OEM name is required")
            else:
                # Update OEM in database
                try:
                    with get_db_session() as session:
                        oem = session.query(OEM).filter(OEM.id == oem_id).first()
                        if oem:
                            oem.name = name
                            oem.contact_name = contact_name
                            oem.email = email
                            oem.phone = phone
                            oem.location = location
                            oem.partnership_type = partnership_type if partnership_type else None
                            oem.contract_start_date = contract_start
                            oem.contract_end_date = contract_end
                            oem.website = website
                            oem.status = status
                            oem.description = description
                            oem.logo_url = logo_url
                            
                            session.commit()
                            
                            st.success(f"OEM '{name}' updated successfully!")
                            st.session_state.show_edit_oem = False
                except Exception as e:
                    st.error(f"Error updating OEM: {str(e)}")


def main():
    """Main function to control the flow of the application"""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="OEM Management",
        page_type="management",
        **get_oems_page_context()
    )
    
    # Render the floating AI assistant
    render_page_ai_assistant()
    
    # Show different views based on session state
    if st.session_state.show_oem_details:
        display_oem_details()
    elif st.session_state.show_add_oem:
        add_oem_form()
    elif st.session_state.show_edit_oem:
        edit_oem_form()
    else:
        display_oems()


if __name__ == "__main__":
    main()

