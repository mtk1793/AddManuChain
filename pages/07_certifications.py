import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from src.services.certification_service import (
    get_all_certifications,
    get_certification_by_id,
    create_certification,
    update_certification,
    delete_certification,
    get_all_products
)
from src.services.material_service import get_all_materials
from src.utils.auth import check_authentication, check_authorization
from src.components.navigation import create_sidebar
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_certifications_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="Certifications | MITACS Dashboard",
    page_icon="🏆",
    layout="wide",
)

# Inject universal CSS styling
inject_universal_css()

def display_certifications():
    """Display the list of certifications with filters."""
    st.subheader("Certification Records")
    
    # Create filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            ["Active", "Expired", "Pending", "Suspended"],
            default=["Active", "Pending"],
        )
    
    with col2:
        cert_type_filter = st.multiselect(
            "Certification Type",
            ["ISO", "CE", "FDA", "UL", "CSA", "ASTM", "Other"],
        )
    
    with col3:
        product_filter = st.selectbox(
            "Product",
            ["All"] + [p["name"] for p in get_all_products()],
            index=0,
        )
        
    with col4:
        expiry_filter = st.selectbox(
            "Expiration",
            ["All", "Expired", "Expiring Soon (30 days)", "Expiring Soon (90 days)", "Valid"],
            index=0,
        )
    
    # Process filters
    product_id = None
    if product_filter != "All":
        products = get_all_products()
        for p in products:
            if p["name"] == product_filter:
                product_id = p["id"]
                break
    
    # Get certifications with filters
    today = datetime.now().date()
    expiry_date_end = None
    
    if expiry_filter == "Expired":
        expiry_date_end = today
    elif expiry_filter == "Expiring Soon (30 days)":
        expiry_date_end = today + timedelta(days=30)
    elif expiry_filter == "Expiring Soon (90 days)":
        expiry_date_end = today + timedelta(days=90)
    
    certifications = get_all_certifications(
        status=status_filter if status_filter else None,
        cert_type=cert_type_filter if cert_type_filter else None,
        product_id=product_id,
        expiry_date_end=expiry_date_end,
        expiry_filter=expiry_filter if expiry_filter != "All" else None
    )
    
    if certifications:
        # Convert to DataFrame for easy display
        certs_df = pd.DataFrame(
            [
                {
                    "ID": cert["id"],
                    "Certificate Number": cert["cert_number"],
                    "Type": cert["cert_type"],
                    "Product": cert["product_name"],
                    "Issuing Authority": cert["issuing_authority"],
                    "Issue Date": cert["issue_date"].strftime("%Y-%m-%d") if cert["issue_date"] else "Not set",
                    "Expiry Date": cert["expiry_date"].strftime("%Y-%m-%d") if cert["expiry_date"] else "Not set",
                    "Status": cert["status"],
                }
                for cert in certifications
            ]
        )
        
        # Display certifications table with color coding
        def highlight_expired_or_expiring(row):
            if row["Status"] == "Expired":
                return ["background-color: #FFCCCC"] * len(row)  # Light red
            if row["Status"] == "Active" and "Expiry Date" in row:
                try:
                    expiry_date = datetime.strptime(row["Expiry Date"], "%Y-%m-%d").date()
                    days_remaining = (expiry_date - today).days
                    if days_remaining <= 30:
                        return ["background-color: #FFFFCC"] * len(row)  # Light yellow
                except:
                    pass
            return [""] * len(row)
        
        st.dataframe(
            certs_df.style.apply(highlight_expired_or_expiring, axis=1),
            use_container_width=True,
            height=400,
        )
        
        # Add action buttons
        selected_cert_id = st.selectbox(
            "Select a certification to view details",
            options=[f"{cert['id']}: {cert['cert_number']} - {cert['product_name']}" for cert in certifications],
            format_func=lambda x: x.split(":")[1].strip(),
        )
        
        if selected_cert_id:
            cert_id = int(selected_cert_id.split(":")[0])
            display_certification_details(cert_id)
    
    else:
        st.info("No certifications found with the selected filters.")

def display_certification_details(cert_id):
    """Display detailed information about a specific certification."""
    cert = get_certification_by_id(cert_id)
    
    if cert:
        st.divider()
        st.subheader(f"Certification Details: {cert['cert_number']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Type:** {cert['cert_type']}")
            st.write(f"**Product:** {cert['product_name']}")
            st.write(f"**Issuing Authority:** {cert['issuing_authority']}")
            st.write(f"**Status:** {cert['status']}")
        
        with col2:
            st.write(f"**Issue Date:** {cert['issue_date'].strftime('%Y-%m-%d') if cert['issue_date'] else 'Not set'}")
            st.write(f"**Expiry Date:** {cert['expiry_date'].strftime('%Y-%m-%d') if cert['expiry_date'] else 'Not set'}")
            
            # Display days remaining till expiry
            if cert['expiry_date']:
                days_remaining = (cert['expiry_date'] - datetime.now().date()).days
                if days_remaining < 0:
                    st.error(f"**Expired:** {abs(days_remaining)} days ago")
                elif days_remaining <= 30:
                    st.warning(f"**Expiring Soon:** {days_remaining} days remaining")
                else:
                    st.success(f"**Valid for:** {days_remaining} days")
        
        # Display certification requirements and specifications
        if cert['requirements']:
            st.subheader("Requirements")
            st.write(cert['requirements'])
            
        # Display attached documents
        if cert['documents']:
            st.subheader("Documents")
            for doc in cert['documents']:
                st.write(f"- {doc['name']}")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏️ Edit Certification"):
                st.session_state.show_edit_cert = True
                st.session_state.edit_cert_id = cert_id
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Certification"):
                if delete_certification(cert_id):
                    st.success("Certification deleted successfully")
                    st.rerun()
                else:
                    st.error("Failed to delete certification")
        
        with col3:
            if st.button("📊 View Audit History"):
                # Display audit history for this certification
                st.info("Audit history feature coming soon")

def add_certification_form():
    """Display form to add a new certification."""
    st.subheader("Add New Certification")
    
    products = get_all_products()
    materials = get_all_materials()
    
    with st.form("add_certification_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            cert_number = st.text_input("Certificate Number*")
            
            cert_type = st.selectbox(
                "Certification Type*",
                ["ISO", "CE", "FDA", "UL", "CSA", "ASTM", "Other"]
            )
            
            item_type = st.selectbox(
                "Item Type*",
                ["Product", "Material"]
            )
            
            if item_type == "Product":
                item = st.selectbox(
                    "Product*",
                    options=products,
                    format_func=lambda x: f"{x['name']} (ID: {x['id']})",
                )
                item_id = item["id"] if item else None
                material_id = None
            else:
                item = st.selectbox(
                    "Material*",
                    options=materials,
                    format_func=lambda x: f"{x['name']} (ID: {x['id']})",
                )
                item_id = None
                material_id = item["id"] if item else None
        
        with col2:
            issuing_authority = st.text_input("Issuing Authority*")
            
            issue_date = st.date_input(
                "Issue Date*",
                value=datetime.now().date()
            )
            
            expiry_date = st.date_input(
                "Expiry Date*",
                value=datetime.now().date() + timedelta(days=365)
            )
            
            status = st.selectbox(
                "Status*",
                ["Active", "Pending", "Suspended", "Expired"]
            )
        
        requirements = st.text_area("Requirements/Specifications")
        documents = st.text_input("Documents (comma separated)")
        
        submit = st.form_submit_button("Add Certification")
        
        if submit:
            if not cert_number:
                st.error("Certificate Number is required")
                return
                
            if not issuing_authority:
                st.error("Issuing Authority is required")
                return
                
            if item_type == "Product" and not item_id:
                st.error("Please select a product")
                return
                
            if item_type == "Material" and not material_id:
                st.error("Please select a material")
                return
            
            # Process documents
            docs_list = []
            if documents:
                for doc in documents.split(","):
                    docs_list.append({"name": doc.strip()})
            
            success = create_certification(
                cert_number=cert_number,
                cert_type=cert_type,
                product_id=item_id,
                material_id=material_id,
                issuing_authority=issuing_authority,
                issue_date=issue_date,
                expiry_date=expiry_date,
                status=status,
                requirements=requirements,
                documents=docs_list
            )
            
            if success:
                st.success(f"Certification {cert_number} added successfully!")
                # Clear form by refreshing the page
                st.rerun()
            else:
                st.error("Failed to add certification. Please check your inputs.")

def generate_certification_visualizations():
    """Generate visualizations for certification statistics."""
    st.subheader("Certification Statistics")
    
    # Get all certifications for statistics
    certifications = get_all_certifications()
    
    if not certifications:
        st.info("No certifications available for statistics")
        return
    
    # Create DataFrames for visualizations
    certs_df = pd.DataFrame([
        {
            "ID": cert["id"],
            "Type": cert["cert_type"],
            "Product": cert["product_name"],
            "Status": cert["status"],
            "Issue Date": cert["issue_date"],
            "Expiry Date": cert["expiry_date"],
            "Days Remaining": (cert["expiry_date"] - datetime.now().date()).days if cert["expiry_date"] else 0
        }
        for cert in certifications
    ])
    
    col1, col2 = st.columns(2)
    
    # Certification Status Distribution
    with col1:
        status_counts = certs_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        fig1 = px.pie(
            status_counts,
            values="Count",
            names="Status",
            title="Certification Status Distribution",
            color="Status",
            color_discrete_map={
                "Active": "#28a745",
                "Pending": "#ffc107",
                "Expired": "#dc3545",
                "Suspended": "#6c757d"
            }
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    # Certification Type Distribution
    with col2:
        type_counts = certs_df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        
        fig2 = px.bar(
            type_counts,
            x="Type",
            y="Count",
            title="Certification Types Distribution",
            color="Type"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Expiring Certifications Timeline
    st.subheader("Certification Expiry Timeline")
    
    # Only show valid certifications with expiry dates
    valid_certs = certs_df[(certs_df["Status"] == "Active") & (certs_df["Days Remaining"] > 0)]
    
    if not valid_certs.empty:
        valid_certs = valid_certs.sort_values("Days Remaining")
        
        # Color based on days remaining
        valid_certs["Warning Level"] = "Safe"
        valid_certs.loc[valid_certs["Days Remaining"] <= 90, "Warning Level"] = "Warning"
        valid_certs.loc[valid_certs["Days Remaining"] <= 30, "Warning Level"] = "Critical"
        
        fig3 = px.bar(
            valid_certs,
            x="Product",
            y="Days Remaining",
            title="Days Until Certification Expiry",
            color="Warning Level",
            color_discrete_map={
                "Critical": "#dc3545",
                "Warning": "#ffc107",
                "Safe": "#28a745"
            },
            hover_data=["Type", "Expiry Date"]
        )
        
        fig3.update_layout(
            xaxis_title="Product",
            yaxis_title="Days Remaining",
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Tabular view of soon-to-expire certifications
        st.subheader("Certifications Expiring Soon")
        expiring_soon = valid_certs[valid_certs["Days Remaining"] <= 90].sort_values("Days Remaining")
        
        if not expiring_soon.empty:
            expiring_table = pd.DataFrame({
                "Product": expiring_soon["Product"],
                "Type": expiring_soon["Type"],
                "Expiry Date": expiring_soon["Expiry Date"].apply(lambda x: x.strftime("%Y-%m-%d")),
                "Days Remaining": expiring_soon["Days Remaining"]
            })
            
            st.dataframe(expiring_table, use_container_width=True)
        else:
            st.info("No certifications expiring within the next 90 days.")
    else:
        st.info("No active certifications with expiry dates available.")

def main():
    """Main function to display the Certifications page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Certifications",
        page_type="management",
        **get_certifications_page_context()
    )
    
    # Render the floating AI assistant
    render_page_ai_assistant()
    
    # Check if user is authenticated
    check_authentication()

    # Create sidebar navigation
    create_sidebar()

    # Page header with Add button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🏆 Certifications")
    with col2:
        if st.button("➕ Add New Certification", type="primary", use_container_width=True):
            # Initialize tab index if not in session state
            if "cert_active_tab" not in st.session_state:
                st.session_state.cert_active_tab = 0
            # Set tab index to show the Add New Certification tab (index 1)
            st.session_state.cert_active_tab = 1
            st.rerun()
    
    st.write("Track, manage, and monitor product and material certifications and compliance status.")

    # Initialize tab index if not in session state
    if "cert_active_tab" not in st.session_state:
        st.session_state.cert_active_tab = 0
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Certifications", "Add New Certification", "Statistics"])
    
    # Select the active tab based on session state
    if st.session_state.cert_active_tab == 1:
        tab2.active = True
    elif st.session_state.cert_active_tab == 2:
        tab3.active = True
    else:
        tab1.active = True

    with tab1:
        display_certifications()

    with tab2:
        add_certification_form()

    with tab3:
        generate_certification_visualizations()


if __name__ == "__main__":
    main()

