import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from src.db.connection import get_db_session
from src.db.models.material import Material, MaterialCategory, Supplier
from src.db.models.product import Product, ProductCategory, OEM
from src.services.material_service import get_all_materials, get_material_by_id
from src.services.product_service import get_all_products, get_product_by_id
from src.components.universal_css import inject_universal_css
from src.components.floating_ai_assistant import render_floating_ai_assistant
from src.components.ai_page_context import add_ai_page_context
from src.components.navigation import create_sidebar
from src.utils.auth import check_authentication

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

# Initialize session state variables
if 'inventory_view' not in st.session_state:
    st.session_state.inventory_view = 'overview'
if 'selected_material_id' not in st.session_state:
    st.session_state.selected_material_id = None
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None

# Inject universal CSS styling
inject_universal_css()

# Helper functions
@st.cache_data(ttl=60)
def get_inventory_overview():
    """Get overview statistics for inventory"""
    with get_db_session() as session:
        # Material stats
        total_materials = session.query(Material).filter(Material.is_active == True).count()
        low_stock_materials = session.query(Material).filter(
            Material.is_active == True,
            Material.current_stock <= Material.min_stock_level
        ).count()
        
        # Product stats
        total_products = session.query(Product).count()
        active_products = session.query(Product).filter(Product.status == 'Active').count()
        
        # Material categories
        material_categories = session.query(MaterialCategory).count()
        
        # Suppliers
        active_suppliers = session.query(Supplier).count()
        
        return {
            'total_materials': total_materials,
            'low_stock_materials': low_stock_materials,
            'total_products': total_products,
            'active_products': active_products,
            'material_categories': material_categories,
            'active_suppliers': active_suppliers
        }

@st.cache_data(ttl=60)
def get_material_inventory_data():
    """Get detailed material inventory data"""
    try:
        materials = get_all_materials()
        if not materials:
            return pd.DataFrame()
        
        # Convert to DataFrame
        material_data = []
        for material in materials:
            material_data.append({
                'ID': material.get('id'),
                'Name': material.get('name', 'Unknown'),
                'Type': material.get('type', 'Unknown'),
                'Current Stock': material.get('current_stock', 0),
                'Unit': material.get('unit', 'kg'),
                'Min Stock Level': material.get('min_stock_level', 0),
                'Price per Unit': material.get('price_per_unit', 0),
                'Status': material.get('status', 'Unknown'),
                'Location': material.get('storage_location', 'Unknown'),
                'Supplier': material.get('supplier_name', 'Unknown'),
                'Expiration Date': material.get('expiration_date')
            })
        
        return pd.DataFrame(material_data)
    except Exception as e:
        st.error(f"Error loading material data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_product_inventory_data():
    """Get detailed product inventory data"""
    try:
        with get_db_session() as session:
            products = session.query(Product).options(
                joinedload(Product.category),
                joinedload(Product.designer),
                joinedload(Product.oem)
            ).all()
            
            product_data = []
            for product in products:
                product_data.append({
                    'ID': product.id,
                    'Name': product.name,
                    'Product Code': product.product_code,
                    'Price': product.price,
                    'Status': product.status,
                    'Category': product.category.name if product.category else 'Unknown',
                    'Designer': f"{product.designer.first_name} {product.designer.last_name}" if product.designer else 'Unknown',
                    'OEM': product.oem.name if product.oem else 'Unknown',
                    'Dimensions': product.dimensions,
                    'Weight': product.weight,
                    'Materials Used': product.materials_used
                })
            
            return pd.DataFrame(product_data)
    except Exception as e:
        st.error(f"Error loading product data: {e}")
        return pd.DataFrame()

def display_overview():
    """Display inventory overview dashboard"""
    st.header("📊 Inventory Overview")
    
    # Get overview data
    overview = get_inventory_overview()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Materials",
            overview['total_materials'],
            help="Total number of active materials in inventory"
        )
        
    with col2:
        st.metric(
            "Low Stock Items",
            overview['low_stock_materials'],
            delta=-overview['low_stock_materials'] if overview['low_stock_materials'] > 0 else None,
            delta_color="inverse",
            help="Materials below minimum stock level"
        )
    
    with col3:
        st.metric(
            "Total Products",
            overview['total_products'],
            help="Total number of products in catalog"
        )
    
    with col4:
        st.metric(
            "Active Products",
            overview['active_products'],
            help="Products currently in active status"
        )
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Material Stock Status")
        material_df = get_material_inventory_data()
        if not material_df.empty:
            # Stock status distribution
            status_counts = material_df['Status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Material Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏭 Product Status Distribution")
        product_df = get_product_inventory_data()
        if not product_df.empty:
            status_counts = product_df['Status'].value_counts()
            fig = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Products by Status",
                color=status_counts.index,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def display_materials():
    """Display materials inventory"""
    st.header("🧪 Materials Inventory")
    
    material_df = get_material_inventory_data()
    
    if material_df.empty:
        st.warning("No material data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        material_types = ['All'] + sorted(material_df['Type'].unique().tolist())
        selected_type = st.selectbox("Filter by Type:", material_types)
    
    with col2:
        statuses = ['All'] + sorted(material_df['Status'].unique().tolist())
        selected_status = st.selectbox("Filter by Status:", statuses)
    
    with col3:
        suppliers = ['All'] + sorted(material_df['Supplier'].unique().tolist())
        selected_supplier = st.selectbox("Filter by Supplier:", suppliers)
    
    # Apply filters
    filtered_df = material_df.copy()
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['Type'] == selected_type]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_supplier != 'All':
        filtered_df = filtered_df[filtered_df['Supplier'] == selected_supplier]
    
    # Display summary
    st.subheader(f"📊 Summary ({len(filtered_df)} materials)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_value = (filtered_df['Current Stock'] * filtered_df['Price per Unit']).sum()
        st.metric("Total Inventory Value", f"${total_value:,.2f}")
    
    with col2:
        low_stock_count = len(filtered_df[filtered_df['Current Stock'] <= filtered_df['Min Stock Level']])
        st.metric("Low Stock Items", low_stock_count)
    
    with col3:
        avg_stock = filtered_df['Current Stock'].mean()
        st.metric("Average Stock Level", f"{avg_stock:.1f}")
    
    with col4:
        unique_locations = filtered_df['Location'].nunique()
        st.metric("Storage Locations", unique_locations)
    
    # Material table
    st.subheader("📋 Materials List")
    
    # Configure columns to display
    display_columns = [
        'Name', 'Type', 'Current Stock', 'Unit', 'Min Stock Level', 
        'Price per Unit', 'Status', 'Location', 'Supplier'
    ]
    
    # Style the dataframe
    def highlight_low_stock(row):
        if row['Current Stock'] <= row['Min Stock Level']:
            return ['background-color: #ffebee'] * len(row)
        else:
            return [''] * len(row)
    
    styled_df = filtered_df[display_columns].style.apply(highlight_low_stock, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # Material details
    if st.session_state.selected_material_id:
        display_material_details(st.session_state.selected_material_id)

def display_products():
    """Display products inventory"""
    st.header("🏭 Products Inventory")
    
    product_df = get_product_inventory_data()
    
    if product_df.empty:
        st.warning("No product data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(product_df['Category'].unique().tolist())
        selected_category = st.selectbox("Filter by Category:", categories)
    
    with col2:
        statuses = ['All'] + sorted(product_df['Status'].unique().tolist())
        selected_status = st.selectbox("Filter by Status:", statuses)
    
    with col3:
        oems = ['All'] + sorted(product_df['OEM'].unique().tolist())
        selected_oem = st.selectbox("Filter by OEM:", oems)
    
    # Apply filters
    filtered_df = product_df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_oem != 'All':
        filtered_df = filtered_df[filtered_df['OEM'] == selected_oem]
    
    # Display summary
    st.subheader(f"📊 Summary ({len(filtered_df)} products)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_value = filtered_df['Price'].sum()
        st.metric("Total Product Value", f"${total_value:,.2f}")
    
    with col2:
        avg_price = filtered_df['Price'].mean()
        st.metric("Average Price", f"${avg_price:.2f}")
    
    with col3:
        avg_weight = filtered_df['Weight'].mean()
        st.metric("Avg. Weight", f"{avg_weight:.2f} kg")
    
    with col4:
        unique_categories = filtered_df['Category'].nunique()
        st.metric("Product Categories", unique_categories)
    
    # Product table
    st.subheader("📋 Products List")
    
    # Configure columns to display
    display_columns = [
        'Name', 'Product Code', 'Price', 'Status', 'Category', 
        'OEM'
    ]
    
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # Product details
    if st.session_state.selected_product_id:
        display_product_details(st.session_state.selected_product_id)

def display_low_stock_alerts():
    """Display low stock alerts"""
    st.header("⚠️ Low Stock Alerts")
    
    material_df = get_material_inventory_data()
    
    if material_df.empty:
        st.warning("No material data available")
        return
    
    # Identify low stock items
    low_stock_df = material_df[material_df['Current Stock'] <= material_df['Min Stock Level']]
    
    if low_stock_df.empty:
        st.success("✅ No low stock items found! All materials are adequately stocked.")
        return
    
    st.warning(f"⚠️ {len(low_stock_df)} materials are below minimum stock levels")
    
    # Critical vs Low stock
    critical_df = low_stock_df[low_stock_df['Current Stock'] <= (low_stock_df['Min Stock Level'] * 0.5)]
    
    if not critical_df.empty:
        st.error(f"🚨 {len(critical_df)} materials are critically low (below 50% of minimum)")
        
        with st.expander("Critical Stock Items", expanded=True):
            critical_display = critical_df[[
                'Name', 'Current Stock', 'Min Stock Level', 'Unit', 
                'Supplier', 'Location', 'Status'
            ]].copy()
            critical_display['Stock Ratio'] = (
                critical_display['Current Stock'] / critical_display['Min Stock Level']
            ).round(2)
            st.dataframe(critical_display, use_container_width=True)
    
    # All low stock items
    st.subheader("📊 Low Stock Analysis")
    
    # Chart showing stock levels vs minimum
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current Stock',
        x=low_stock_df['Name'],
        y=low_stock_df['Current Stock'],
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        name='Min Stock Level',
        x=low_stock_df['Name'],
        y=low_stock_df['Min Stock Level'],
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title='Current Stock vs Minimum Stock Levels',
        xaxis_title='Materials',
        yaxis_title='Quantity',
        barmode='group',
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Low Stock Details")
    
    # Calculate reorder suggestions
    low_stock_display = low_stock_df.copy()
    low_stock_display['Reorder Quantity'] = (
        low_stock_display['Min Stock Level'] * 2 - low_stock_display['Current Stock']
    ).round(1)
    low_stock_display['Estimated Cost'] = (
        low_stock_display['Reorder Quantity'] * low_stock_display['Price per Unit']
    ).round(2)
    
    display_columns = [
        'Name', 'Current Stock', 'Min Stock Level', 'Unit',
        'Reorder Quantity', 'Estimated Cost', 'Supplier', 'Location'
    ]
    
    st.dataframe(low_stock_display[display_columns], use_container_width=True)
    
    # Total reorder cost
    total_reorder_cost = low_stock_display['Estimated Cost'].sum()
    st.info(f"💰 Total estimated reorder cost: ${total_reorder_cost:,.2f}")

def display_analytics():
    """Display inventory analytics"""
    st.header("📈 Inventory Analytics")
    
    material_df = get_material_inventory_data()
    product_df = get_product_inventory_data()
    
    if material_df.empty and product_df.empty:
        st.warning("No data available for analytics")
        return
    
    # Material analytics
    if not material_df.empty:
        st.subheader("🧪 Material Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Material type distribution
            type_dist = material_df.groupby('Type').agg({
                'Current Stock': 'sum',
                'Price per Unit': 'mean'
            }).reset_index()
            type_dist['Total Value'] = type_dist['Current Stock'] * type_dist['Price per Unit']
            
            fig = px.pie(
                type_dist,
                values='Total Value',
                names='Type',
                title='Material Value Distribution by Type'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stock levels by location
            location_stock = material_df.groupby('Location')['Current Stock'].sum().reset_index()
            location_stock = location_stock.sort_values('Current Stock', ascending=True)
            
            fig = px.bar(
                location_stock,
                x='Current Stock',
                y='Location',
                orientation='h',
                title='Stock Distribution by Location'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Product analytics
    if not product_df.empty:
        st.subheader("🏭 Product Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution by category
            category_price = product_df.groupby('Category').agg({
                'Price': ['mean', 'count']
            }).reset_index()
            category_price.columns = ['Category', 'Average Price', 'Count']
            
            fig = px.scatter(
                category_price,
                x='Count',
                y='Average Price',
                size='Count',
                text='Category',
                title='Product Categories: Count vs Average Price'
            )
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Manufacturing time vs quality grade
            if 'Quality Grade' in product_df.columns and 'Manufacturing Time' in product_df.columns:
                fig = px.box(
                    product_df,
                    x='Quality Grade',
                    y='Manufacturing Time',
                    title='Manufacturing Time by Quality Grade'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Combined analytics
    st.subheader("🔄 Cross-Category Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not material_df.empty:
            # Top suppliers by value
            supplier_value = material_df.copy()
            supplier_value['Total Value'] = supplier_value['Current Stock'] * supplier_value['Price per Unit']
            supplier_summary = supplier_value.groupby('Supplier')['Total Value'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=supplier_summary.values,
                y=supplier_summary.index,
                orientation='h',
                title='Top Suppliers by Inventory Value'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not product_df.empty:
            # Quality distribution if available
            if 'Quality Grade' in product_df.columns:
                quality_dist = product_df['Quality Grade'].value_counts()
                fig = px.bar(
                    x=quality_dist.index,
                    y=quality_dist.values,
                    title='Product Quality Grade Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No quality grade data available.")

def display_material_details(material_id):
    """Display detailed material information"""
    material = get_material_by_id(material_id)
    if not material:
        st.error("Material not found")
        return
    
    st.subheader(f"🧪 Material Details: {material.get('name', 'Unknown')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Information**")
        st.write(f"**ID:** {material.get('id')}")
        st.write(f"**Type:** {material.get('type', 'Unknown')}")
        st.write(f"**Description:** {material.get('description', 'N/A')}")
        st.write(f"**Status:** {material.get('status', 'Unknown')}")
        
        st.write("**Stock Information**")
        st.write(f"**Current Stock:** {material.get('current_stock', 0)} {material.get('unit', 'units')}")
        st.write(f"**Minimum Level:** {material.get('min_stock_level', 0)} {material.get('unit', 'units')}")
        st.write(f"**Reorder Level:** {material.get('reorder_level', 0)} {material.get('unit', 'units')}")
    
    with col2:
        st.write("**Supplier Information**")
        st.write(f"**Supplier:** {material.get('supplier_name', 'Unknown')}")
        st.write(f"**Location:** {material.get('storage_location', 'Unknown')}")
        
        st.write("**Pricing**")
        st.write(f"**Price per Unit:** ${material.get('price_per_unit', 0):.2f}")
        st.write(f"**Cost per Unit:** ${material.get('cost_per_unit', 0):.2f}")
        
        total_value = (material.get('current_stock', 0) * material.get('price_per_unit', 0))
        st.write(f"**Total Inventory Value:** ${total_value:.2f}")

def display_product_details(product_id):
    """Display detailed product information"""
    with get_db_session() as session:
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            st.error("Product not found")
            return
        
        st.subheader(f"🏭 Product Details: {product.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Basic Information**")
            st.write(f"**Product Code:** {product.product_code}")
            st.write(f"**Description:** {product.description or 'N/A'}")
            st.write(f"**Status:** {product.status}")
            st.write(f"**Price:** ${product.price:.2f}")
            
            st.write("**Physical Properties**")
            st.write(f"**Dimensions:** {product.dimensions or 'N/A'}")
            st.write(f"**Weight:** {product.weight or 'N/A'} kg")
        
        with col2:
            st.write("**Manufacturing Information**")
            st.write(f"**Materials Used:** {product.materials_used or 'N/A'}")
            # Manufacturing Time removed due to missing attribute
            
            st.write("**Business Information**")
            category_name = product.category.name if product.category else 'Unknown'
            st.write(f"**Category:** {category_name}")
            oem_name = product.oem.name if product.oem else 'Unknown'
            st.write(f"**OEM:** {oem_name}")

# Main content based on selected view
if st.session_state.inventory_view == 'overview':
    display_overview()
elif st.session_state.inventory_view == 'materials':
    display_materials()
elif st.session_state.inventory_view == 'products':
    display_products()
elif st.session_state.inventory_view == 'low_stock_alerts':
    display_low_stock_alerts()
elif st.session_state.inventory_view == 'analytics':
    display_analytics()

# Footer with last update info
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main function to display the Inventory Management page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Inventory Management",
        page_type="inventory",
        additional_context={
            "available_actions": [
                "View material inventory",
                "View product inventory", 
                "Check stock levels",
                "Monitor low stock items",
                "Track material usage",
                "View supplier information",
                "Analyze inventory trends"
            ],
            "key_metrics": [
                "Total materials in stock",
                "Low stock alerts",
                "Product inventory levels",
                "Material categories breakdown",
                "Supplier distribution"
            ]
        }
    )
    
    # Render the floating AI assistant
    render_floating_ai_assistant()
    
    # Check authentication
    check_authentication()
    
    # Create sidebar navigation
    create_sidebar()
    
    # Page header
    st.title("📦 Inventory Management")
    st.write("Comprehensive view of materials and products inventory")

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🧪 Materials", "🏭 Products", "⚠️ Low Stock", "📈 Analytics"])
    
    with tab1:
        st.session_state.inventory_view = 'overview'
        display_overview()
    
    with tab2:
        st.session_state.inventory_view = 'materials'
        display_materials()
    
    with tab3:
        st.session_state.inventory_view = 'products'
        display_products()
    
    with tab4:
        st.session_state.inventory_view = 'low_stock_alerts'
        display_low_stock_alerts()
    
    with tab5:
        st.session_state.inventory_view = 'analytics'
        display_analytics()

    # Footer with last update info
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()