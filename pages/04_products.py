import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import joinedload

from src.db.connection import get_db_session
from src.db.models.product import Product, ProductCategory, OEM
from src.db.models.user import User
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_products_page_context
from src.components.universal_css import inject_universal_css
from src.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)

st.set_page_config(page_title="Products Management", layout="wide")

# Inject universal CSS styling
inject_universal_css()


# Utility functions
def load_product_categories():
    with get_db_session() as session:
        categories = session.query(ProductCategory).all()
        return [(c.id, c.name) for c in categories]


def load_oems():
    with get_db_session() as session:
        oems = session.query(OEM).all()
        return [(o.id, o.name) for o in oems]


def load_designers():
    with get_db_session() as session:
        designers = (
            session.query(User).filter(User.role.in_(["Designer", "Admin"])).all()
        )
        return [(d.id, f"{d.first_name} {d.last_name}") for d in designers]


def format_currency(amount):
    if amount is None:
        return "N/A"
    return f"${amount:.2f}"


def display_product_details(product):
    col1, col2 = st.columns([1, 2])

    with col1:
        if product.image_url:
            st.image(product.image_url, width=300)
        else:
            st.image("https://via.placeholder.com/300x300?text=No+Image", width=300)

    with col2:
        st.subheader(product.name)
        st.caption(f"Product Code: {product.product_code}")
        st.write(f"**Status:** {product.status}")
        st.write(f"**Price:** {format_currency(product.price)}")
        st.write(
            f"**Category:** {product.category.name if product.category else 'Uncategorized'}"
        )
        st.write(f"**OEM:** {product.oem.name if product.oem else 'N/A'}")
        st.write(
            f"**Designer:** {product.designer.first_name} {product.designer.last_name if product.designer else 'N/A'}"
        )

    st.write("### Description")
    st.write(product.description)

    # Product details in tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Specifications", "Materials & Assembly", "Quality Tests", "Certifications"]
    )

    with tab1:
        if product.specifications:
            specs = product.specifications
            if isinstance(specs, str):
                try:
                    specs = json.loads(specs)
                except:
                    pass

            if isinstance(specs, dict):
                for key, value in specs.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write(specs)
        else:
            st.info("No specifications available")

        st.write(
            f"**Dimensions:** {product.dimensions if product.dimensions else 'N/A'}"
        )
        st.write(f"**Weight:** {product.weight if product.weight else 'N/A'} kg")

    with tab2:
        st.write("#### Materials Used")
        st.write(product.materials_used or "No materials information available")

        st.write("#### Assembly Instructions")
        st.write(product.assembly_instructions or "No assembly instructions available")

    with tab3:
        if product.quality_tests and len(product.quality_tests) > 0:
            test_data = []
            for test in product.quality_tests:
                test_data.append(
                    {
                        "Test Name": test.name,
                        "Date": (
                            test.test_date.strftime("%Y-%m-%d")
                            if test.test_date
                            else "N/A"
                        ),
                        "Result": "PASS" if test.passed else "FAIL",
                        "Conducted By": (
                            f"{test.tester.first_name} {test.tester.last_name}"
                            if test.tester
                            else "N/A"
                        ),
                    }
                )

            st.dataframe(pd.DataFrame(test_data), use_container_width=True)
        else:
            st.info("No quality tests have been performed for this product")

    with tab4:
        if product.certifications and len(product.certifications) > 0:
            cert_data = []
            for cert in product.certifications:
                cert_data.append(
                    {
                        "Certification": cert.name,
                        "Issuer": cert.issuer,
                        "Issue Date": (
                            cert.issue_date.strftime("%Y-%m-%d")
                            if cert.issue_date
                            else "N/A"
                        ),
                        "Expiry Date": (
                            cert.expiry_date.strftime("%Y-%m-%d")
                            if cert.expiry_date
                            else "N/A"
                        ),
                    }
                )

            st.dataframe(pd.DataFrame(cert_data), use_container_width=True)
        else:
            st.info("No certifications found for this product")


def display_products():
    # Filters
    st.sidebar.header("Filters")

    # Load filter options
    categories = [("all", "All Categories")] + load_product_categories()
    statuses = [
        ("all", "All Statuses"),
        ("Active", "Active"),
        ("Discontinued", "Discontinued"),
        ("In Development", "In Development"),
    ]
    designers = [("all", "All Designers")] + load_designers()

    # Filter selection
    selected_category_id = st.sidebar.selectbox(
        "Category",
        options=[c[0] for c in categories],
        format_func=lambda x: dict(categories).get(x, x),
        index=0,
    )

    selected_status = st.sidebar.selectbox(
        "Status",
        options=[s[0] for s in statuses],
        format_func=lambda x: dict(statuses).get(x, x),
        index=0,
    )

    selected_designer_id = st.sidebar.selectbox(
        "Designer",
        options=[d[0] for d in designers],
        format_func=lambda x: dict(designers).get(x, x),
        index=0,
    )

    price_range = st.sidebar.slider("Price Range ($)", 0, 10000, (0, 10000), 100)

    # Get filtered products with eager loading
    with get_db_session() as session:
        query = session.query(Product).options(
            # Eager load the relationships you need
            joinedload(Product.category),
            joinedload(Product.designer),
            joinedload(Product.oem)
        )
        
        if selected_category_id != "all":
            query = query.filter(Product.category_id == selected_category_id)

        if selected_status != "all":
            query = query.filter(Product.status == selected_status)

        if selected_designer_id != "all":
            query = query.filter(Product.designer_id == selected_designer_id)

        query = query.filter(
            (Product.price >= price_range[0]) & (Product.price <= price_range[1])
        )

        # Execute query and get all data at once
        products = query.all()
        
        # Convert to dictionaries to detach from session
        product_dicts = []
        for p in products:
            product_dict = {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "price": p.price,
                "product_code": p.product_code,
                "category_name": p.category.name if p.category else "Uncategorized",
                "designer_name": f"{p.designer.first_name} {p.designer.last_name}" if p.designer else "N/A",
                "created_at": p.created_at,
                # Add these missing attributes:
                "weight": p.weight,
                "dimensions": p.dimensions,
                "specifications": p.specifications,
                "description": p.description,
                "image_url": p.image_url,
            }
            product_dicts.append(product_dict)
    
    # Now use product_dicts outside the session
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products", len(product_dicts))
    with col2:
        active_count = len([p for p in product_dicts if p["status"] == "Active"])
        st.metric("Active Products", active_count)
    with col3:
        avg_price = (
            sum([p["price"] for p in product_dicts if p["price"] is not None])
            / len([p for p in product_dicts if p["price"] is not None])
            if any(p["price"] is not None for p in product_dicts)
            else 0
        )
        st.metric("Average Price", f"${avg_price:.2f}")
    with col4:
        new_count = len(
            [
                p for p in product_dicts
                if p["created_at"] and p["created_at"] > datetime.now() - timedelta(days=30)
            ]
        )

    # Charts
    with st.expander("Product Analytics", expanded=True):
        tab1, tab2 = st.tabs(["Price Distribution", "Status Breakdown"])

        with tab1:
            if not all(p["price"] is None for p in product_dicts):
                price_data = [
                    {
                        "name": p["name"],
                        "price": p["price"] or 0,
                        "category": p["category_name"],
                    }
                    for p in product_dicts
                ]
                price_df = pd.DataFrame(price_data)

                fig = px.histogram(
                    price_df,
                    x="price",
                    color="category",
                    title="Product Price Distribution",
                    labels={"price": "Price ($)", "count": "Number of Products"},
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No price data available for visualization")

        with tab2:
            status_counts = {}
            for p in product_dicts:
                status_counts[p["status"]] = status_counts.get(p["status"], 0) + 1

            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Product Status Breakdown",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Product cards in grid view
    st.subheader(f"Showing {len(product_dicts)} Products")

    # Display products in a grid with 3 columns
    cols = st.columns(3)
    for i, product_dict in enumerate(product_dicts):  # Use product_dicts instead of products
        with cols[i % 3]:
            with st.container():
                st.markdown(
                    f"""
                <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 15px">
                    <h3>{product_dict["name"]}</h3>
                    <p><strong>Code:</strong> {product_dict["product_code"]}</p>
                    <p><strong>Price:</strong> {format_currency(product_dict["price"])}</p>
                    <p><strong>Status:</strong> {product_dict["status"]}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Details", key=f"view_{product_dict['id']}"):  # Use product_dict['id']
                        st.session_state.selected_product_id = product_dict["id"]
                        st.session_state.show_product_details = True

                with col2:
                    if st.button("Edit", key=f"edit_{product_dict['id']}"):  # Use product_dict['id']
                        st.session_state.selected_product_id = product_dict["id"]
                        st.session_state.show_edit_product = True

    # Product details view
    if st.session_state.get("show_product_details", False) and st.session_state.get(
        "selected_product_id"
    ):
        with st.container():
            st.divider()
            with get_db_session() as session:
                product = (
                    session.query(Product)
                    .filter(Product.id == st.session_state.selected_product_id)
                    .first()
                )
                if product:
                    display_product_details(product)
                    if st.button("Close Details"):
                        st.session_state.show_product_details = False
                        st.session_state.selected_product_id = None
                else:
                    st.error("Product not found")


def create_new_product():
    st.subheader("Create New Product")

    # Load necessary data
    categories = load_product_categories()
    oems = load_oems()
    designers = load_designers()

    # Form inputs
    with st.form("product_form"):
        name = st.text_input("Product Name*", help="Required")
        description = st.text_area("Description")
        product_code = st.text_input("Product Code*", help="Must be unique")
        price = st.number_input("Price ($)", min_value=0.0, step=10.0)
        status = st.selectbox(
            "Status", options=["In Development", "Active", "Discontinued"], index=0
        )

        col1, col2 = st.columns(2)
        with col1:
            category_id = st.selectbox(
                "Category",
                options=[c[0] for c in categories],
                format_func=lambda x: dict(categories).get(x, "Select..."),
            )
            dimensions = st.text_input("Dimensions")

        with col2:
            oem_id = st.selectbox(
                "OEM",
                options=[o[0] for o in oems],
                format_func=lambda x: dict(oems).get(x, "Select..."),
            )
            weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)

        designer_id = st.selectbox(
            "Designer",
            options=[d[0] for d in designers],
            format_func=lambda x: dict(designers).get(x, "Select..."),
        )

        materials_used = st.text_area("Materials Used")
        assembly_instructions = st.text_area("Assembly Instructions")
        image_url = st.text_input("Image URL")

        submitted = st.form_submit_button("Create Product")

        if submitted:
            if not name or not product_code:
                st.error("Name and product code are required!")
            else:
                # Create product object
                new_product = {
                    "name": name,
                    "description": description,
                    "product_code": product_code,
                    "price": price,
                    "status": status,
                    "designer_id": designer_id,
                    "category_id": category_id,
                    "oem_id": oem_id,
                    "dimensions": dimensions,
                    "weight": weight,
                    "materials_used": materials_used,
                    "assembly_instructions": assembly_instructions,
                    "image_url": image_url,
                    "specifications": {},  # Empty dict for now
                }

                # Call service to create product
                try:
                    with get_db_session() as session:
                        created = create_product(session, new_product)
                        if created:
                            st.success(f"Product '{name}' created successfully!")
                            st.session_state.show_add_product = False
                        else:
                            st.error("Failed to create product")
                except Exception as e:
                    st.error(f"Error creating product: {str(e)}")


def main():
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Products Management",
        page_type="management",
        **get_products_page_context()
    )
    
    # Render the floating AI assistant
    render_page_ai_assistant()
    
    st.title("Products Management")
    
    # Add this code right after the title
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add New Product", type="primary", use_container_width=True):
            st.session_state.show_add_product = True
            st.session_state.show_product_details = False
            st.session_state.show_edit_product = False
    
    # Initialize session state
    if "show_product_details" not in st.session_state:
        st.session_state.show_product_details = False

    if "selected_product_id" not in st.session_state:
        st.session_state.selected_product_id = None

    if "show_add_product" not in st.session_state:
        st.session_state.show_add_product = False

    if "show_edit_product" not in st.session_state:
        st.session_state.show_edit_product = False

    # Display based on state
    if st.session_state.show_add_product:
        create_new_product()
    else:
        display_products()


if __name__ == "__main__":
    main()
