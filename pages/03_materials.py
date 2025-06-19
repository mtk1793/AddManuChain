# pages/03_materials.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from src.services.material_service import (
    get_all_materials,
    get_material_by_id,
    create_material,
    update_material,
)
from src.utils.auth import check_authentication
from src.components.navigation import create_sidebar
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_materials_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="Material Management | MITACS Dashboard",
    page_icon="🧱",
    layout="wide",
)

# Inject universal CSS styling
inject_universal_css()

# Initialize session state for user_id if not already done
if 'user_id' not in st.session_state:
    st.session_state.user_id = None


def display_materials():
    """Display the list of materials with status indicators and filters."""
    st.subheader("Material Inventory")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "Status",
            ["Available", "Low", "Out of Stock", "Expired"],
            default=["Available", "Low"],
        )

    with col2:
        type_filter = st.multiselect(
            "Material Type",
            ["Polymer", "Metal", "Ceramic", "Composite", "Other"],
            default=[],
        )

    with col3:
        location_filter = st.multiselect(
            "Location",
            ["Main Storage", "Lab A", "Lab B", "Production Floor"],
            default=[],
        )

    # Get materials with filters - handle both development and production
    try:
        # Try direct call first
        materials = get_all_materials(
            status=status_filter if status_filter else None,
            material_type=type_filter if type_filter else None,
        )
    except AttributeError:
        # If that fails due to __enter__ error, create a session manually
        from src.db.connection import get_db_session

        session = get_db_session()  # This doesn't use context manager syntax
        try:
            # Alternative approach
            from src.db.models.material import Material

            query = session.query(Material)

            if status_filter:
                query = query.filter(Material.status.in_(status_filter))

            if type_filter:
                query = query.filter(Material.material_type.in_(type_filter))

            materials = query.all()
        except Exception as e:
            st.error(f"Error fetching materials: {str(e)}")
            materials = []
        finally:
            if hasattr(session, "close"):
                session.close()

    if materials:
        # Convert to DataFrame for easy display
        materials_df = pd.DataFrame(
            [
                {
                    "ID": material['id'],
                    "Name": material['name'],
                    "Type": material['material_type'], # Changed from material['type'] to material['material_type'] for consistency
                    "Quantity": f"{material['stock_quantity']} {material['unit']}",
                    "Location": material['storage_location'], # Changed from material['location'] to material['storage_location']
                    "Status": material['status'],
                    "Price/Unit": (
                        f"${material['price_per_unit']:.2f}"
                        if material['price_per_unit']
                        else "N/A"
                    ),
                    "Min. Stock": material['min_stock_level'],
                    "Supplier ID": material.get('supplier_id', 'N/A'), # Use .get for optional fields
                    "Category ID": material.get('category_id', 'N/A'), # Use .get for optional fields
                    "Expiration Date": (
                        material['expiration_date'].strftime('%Y-%m-%d') 
                        if material['expiration_date'] 
                        else "N/A"
                    ),
                    "Last Updated": (
                        material['updated_at'].strftime('%Y-%m-%d %H:%M')
                        if material['updated_at']
                        else "N/A"
                    ),
                }
                for material in materials
            ]
        )

        # Apply status styling
        def color_status(val):
            if val == "Available":
                return "background-color: #c6efcd"  # Green
            elif val == "Low":
                return "background-color: #ffeb9c"  # Yellow
            elif val == "Out of Stock":
                return "background-color: #f8c9c4"  # Red
            elif val == "Expired":
                return "background-color: #d9d9d9"  # Gray
            return ""

        # Style the dataframe
        styled_df = materials_df.style.applymap(color_status, subset=["Status"])

        st.dataframe(styled_df, use_container_width=True)

        # Select a material to show details
        selected_material_id = st.selectbox(
            "Select a material to view details",
            options=[f"{material['id']}: {material['name']}" for material in materials],
            format_func=lambda x: x.split(":")[1].strip(),
        )

        if selected_material_id:
            material_id = int(selected_material_id.split(":")[0])
            display_material_details(material_id)
    else:
        st.info("No materials found with the selected filters.")


def display_material_details(material_id):
    """Display detailed information about a specific material."""
    material = get_material_by_id(material_id)  # Now returns a dict

    if material:
        st.divider()
        st.subheader(f"Material Details: {material['name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Type:** {material['material_type']}")
            st.write(f"**Stock Quantity:** {material['stock_quantity']} {material['unit']}")
            st.write(f"**Minimum Stock Level:** {material['min_stock_level']} {material['unit']}")
            st.write(f"**Location:** {material['storage_location']}")
            st.write(f"**Status:** {material['status']}")

        with col2:
            st.write(
                f"**Price per Unit:** ${material['price_per_unit']:.2f}" if material['price_per_unit'] else "**Price per Unit:** N/A"
            )
            st.write(
                f"**Expiration Date:** {material['expiration_date'].strftime('%Y-%m-%d') if material['expiration_date'] else 'N/A'}"
                if material['expiration_date'] else "**Expiration Date:** N/A"
            )
            st.write(f"**Supplier ID:** {material['supplier_id'] if material['supplier_id'] else 'Unknown'}")
            st.write(f"**Manager ID:** {material['manager_id'] if material['manager_id'] else 'Unassigned'}")

        st.write(f"**Description:** {material['description'] if material['description'] else 'N/A'}")

        # Certifications - Assuming material.certifications is a list of related ORM objects
        st.subheader("Certifications")
        
        # Check if the material object has a 'certifications' attribute and if it's populated
        if hasattr(material, 'certifications') and material.certifications:
            certs_data = []
            for cert in material.certifications:
                certs_data.append({
                    "Name": cert.certification_type if hasattr(cert, 'certification_type') else cert.name, # Adjust based on actual attribute name
                    "Issuing Authority": cert.issuer if hasattr(cert, 'issuer') else cert.issuing_authority, # Adjust
                    "Issue Date": cert.issue_date.strftime("%Y-%m-%d") if cert.issue_date else "N/A",
                    "Expiry Date": cert.expiry_date.strftime("%Y-%m-%d") if cert.expiry_date else "N/A",
                    "Number": cert.certification_number if cert.certification_number else "N/A",
                    "Status": cert.status if hasattr(cert, 'status') else "N/A"
                })
            if certs_data:
                certs_df = pd.DataFrame(certs_data)
                st.dataframe(certs_df, use_container_width=True)
            else:
                st.info("No certifications linked to this material.")
        elif hasattr(material, 'material_certifications') and material.material_certifications: # Fallback for direct MaterialCertification relationship
            certs_data = []
            for cert in material.material_certifications:
                 certs_data.append({
                    "Name": cert.certification_type,
                    "Issuing Authority": cert.issuer,
                    "Issue Date": cert.issue_date.strftime("%Y-%m-%d") if cert.issue_date else "N/A",
                    "Expiry Date": cert.expiry_date.strftime("%Y-%m-%d") if cert.expiry_date else "N/A",
                    "Number": cert.certification_number if cert.certification_number else "N/A",
                    "Status": cert.status
                })
            if certs_data:
                certs_df = pd.DataFrame(certs_data)
                st.dataframe(certs_df, use_container_width=True)
            else:
                st.info("No certifications linked to this material.")
        else:
            st.info("No certification data available for this material.")

        # Stock Adjustments
        st.subheader("Stock History")
        if hasattr(material, 'stock_adjustments') and material.stock_adjustments:
            history_df = pd.DataFrame(
                [
                    {
                        "Date": adj.adjustment_date.strftime("%Y-%m-%d %H:%M"),
                        "Type": adj.adjustment_type,
                        "Quantity": adj.quantity,
                        "Unit Cost": f"${adj.unit_cost:.2f}" if adj.unit_cost else "N/A",
                        "Notes": adj.notes,
                    }
                    for adj in sorted(material.stock_adjustments, key=lambda x: x.adjustment_date, reverse=True)
                ]
            )
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No stock adjustment history for this material.")
    else:
        st.error("Material not found.")


def add_material_form():
    """Display form to add a new material."""
    st.subheader("Add New Material")

    with st.form("add_material_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            name = st.text_input("Material Name*").strip()
            material_type = st.selectbox(
                "Material Type*", ["Polymer", "Metal", "Ceramic", "Composite", "Other"]
            )
            # Ensure stock quantity is a valid number
            try:
                stock_quantity = float(
                    st.number_input(
                        "Initial Stock Quantity*", min_value=0.0, step=0.1
                    )
                )
            except:
                stock_quantity = 0.0
            unit = st.selectbox("Unit", ["kg", "g", "L", "ml", "piece", "roll"])
            min_stock_level = st.number_input(
                "Minimum Stock Level", min_value=0.0, step=0.1
            )

        with col2:
            price_per_unit = st.number_input(
                "Price per Unit ($)", min_value=0.0, step=0.01
            )
            location = st.selectbox(
                "Storage Location",
                ["Main Storage", "Lab A", "Lab B", "Production Floor", "Other"],
            )
            expiration_date = st.date_input("Expiration Date", value=None)
            # Supplier and Manager would be selected from existing entries, but for simplicity we'll use placeholders
            supplier_id = st.number_input("Supplier ID", min_value=1, step=1)
            manager_id = st.session_state.user_id

        with col3:
            status = st.selectbox("Status", ["Available", "Low", "Out of Stock"])
            description = st.text_area("Description")

        submit = st.form_submit_button("Add Material")

        if submit:
            if not name:
                st.error("Material Name is required")
                return

            # Print debug info
            print(
                f"Debug - Adding material: {name}, {material_type}, Stock: {stock_quantity}"
            )

            success = create_material(
                name=name,
                material_type=material_type,
                stock_quantity=stock_quantity,
                unit=unit,
                price_per_unit=price_per_unit,
                min_stock_level=min_stock_level,
                location=location,
                expiration_date=expiration_date,
                supplier_id=supplier_id if supplier_id else None,
                description=description,
                status=status,
            )

            if success:
                st.success(f"Material '{name}' added successfully!")
                st.rerun()
            else:
                st.error("Failed to add material.")


def generate_material_visualizations():
    """Generate visualizations for material statistics."""
    st.subheader("Material Statistics")

    # Get all materials for statistics
    materials = get_all_materials()

    if not materials:
        st.info("No materials available for statistics.")
        return

    # Create DataFrames for visualizations
    materials_df = pd.DataFrame(
        [
            {
                "ID": material['id'],
                "Name": material['name'],
                "Type": material['material_type'],
                "Status": material['status'],
                "Quantity": material['stock_quantity'],
                "Unit": material['unit'],
                "Location": material['storage_location'],
                "Price": material['price_per_unit'],
            }
            for material in materials
        ]
    )

    col1, col2 = st.columns(2)

    # Material Status Distribution
    with col1:
        status_counts = materials_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig1 = px.pie(
            status_counts,
            values="Count",
            names="Status",
            title="Material Status Distribution",
            color="Status",
            color_discrete_map={
                "Available": "#28a745",
                "Low": "#ffc107",
                "Out of Stock": "#dc3545",
                "Expired": "#6c757d",
            },
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Material Type Distribution
    with col2:
        type_counts = materials_df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]

        fig2 = px.bar(
            type_counts, x="Type", y="Count", title="Material Types", color="Type"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Create inventory value calculation
    # Convert all units to kg for visualization purposes (simplified)
    materials_df["Value"] = materials_df["Quantity"] * materials_df["Price"]
    materials_df = materials_df[
        materials_df["Price"].notna()
    ]  # Remove rows with no price

    # Inventory value by material type
    if not materials_df.empty:
        inventory_value = materials_df.groupby("Type")["Value"].sum().reset_index()

        fig3 = px.bar(
            inventory_value,
            x="Type",
            y="Value",
            title="Inventory Value by Material Type ($)",
            color="Type",
        )

        fig3.update_layout(yaxis_title="Total Value ($)")

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No pricing data available for inventory value calculation.")


def main():
    """Main function to display the Material Management page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Material Management", 
        page_type="management",
        **get_materials_page_context()
    )
    
    # Check if user is authenticated
    check_authentication()

    # Create sidebar navigation
    create_sidebar()

    # Page header
    st.title("🧱 Material Inventory Management")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Material Inventory", "Add New Material", "Statistics"])

    with tab1:
        display_materials()

    with tab2:
        add_material_form()

    with tab3:
        generate_material_visualizations()

    # Render AI assistant for this page
    render_page_ai_assistant()


if __name__ == "__main__":
    main()
