# pages/06_quality_assurance.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.services.quality_service import (
    get_all_quality_tests,
    get_quality_test_by_id,
    create_quality_test,
    update_quality_test,
    get_all_products,
)
from src.utils.auth import check_authentication
from src.components.navigation import create_sidebar
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_quality_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="Quality Assurance | MITACS Dashboard",
    page_icon="🔬",
    layout="wide",
)

# Inject universal CSS styling
inject_universal_css()


def display_quality_tests():
    """Display the list of quality tests with filters."""
    st.subheader("Quality Tests")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        result_filter = st.multiselect(
            "Result",
            ["Pass", "Fail", "Pending"],
            default=["Pass", "Fail", "Pending"],  # Show all by default
        )

    with col2:
        test_type_filter = st.multiselect(
            "Test Type",
            ["Visual", "Mechanical", "Chemical", "Dimensional", "Other"],
            default=["Visual", "Mechanical", "Chemical", "Dimensional", "Other"],  # Show all by default
        )

    with col3:
        date_range = st.date_input(
            "Test Date Range",
            value=[datetime(2000, 1, 1).date(), datetime.now().date()],  # Wide range by default
        )

    # Get quality tests with filters
    start_date = date_range[0] if len(date_range) > 0 else None
    end_date = date_range[1] if len(date_range) > 1 else None

    quality_tests = get_all_quality_tests(
        result=result_filter if result_filter else None,
        test_type=test_type_filter if test_type_filter else None,
        start_date=start_date,
        end_date=end_date,
    )

    if quality_tests:
        # Convert to DataFrame for easy display
        tests_df = pd.DataFrame(
            [
                {
                    "ID": test["id"],
                    "Product": test["product_name"],
                    "Test Type": test["test_type"],
                    "Test Date": test["test_date"].strftime("%Y-%m-%d") if test["test_date"] else "Unknown",
                    "Result": test["result"],
                    "Tester": test["tester_name"],
                }
                for test in quality_tests
            ]
        )

        # Apply result styling
        def color_result(val):
            if val == "Pass":
                return "background-color: #c6efcd"  # Green
            elif val == "Fail":
                return "background-color: #f8c9c4"  # Red
            elif val == "Pending":
                return "background-color: #ffeb9c"  # Yellow
            return ""

        # Style the dataframe
        styled_df = tests_df.style.applymap(color_result, subset=["Result"])

        st.dataframe(styled_df, use_container_width=True)

        # Select a test to show details
        selected_test_id = st.selectbox(
            "Select a test to view details",
            options=[f"{test['id']}: {test['product_name']} - {test['test_type']}" for test in quality_tests],
            format_func=lambda x: x.split(":", 1)[1].strip(),
        )

        if selected_test_id:
            test_id = int(selected_test_id.split(":", 1)[0])
            display_test_details(test_id)
    else:
        st.info("No quality tests found with the selected filters.")


def display_test_details(test_id):
    """Display detailed information about a specific quality test."""
    test = get_quality_test_by_id(test_id)

    if test:
        st.divider()
        st.subheader(
            f"Test Details: {test['product_name']} - {test['test_type']}"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Product:** {test['product_name']}")
            st.write(f"**Test Type:** {test['test_type']}")
            st.write(f"**Test Date:** {test['test_date'].strftime('%Y-%m-%d') if test['test_date'] else 'Unknown'}")
            st.write(f"**Result:** {test['result']}")

        with col2:
            st.write(f"**Tester:** {test['tester_name']}")
            st.write(f"**Created At:** {test['created_at'].strftime('%Y-%m-%d %H:%M') if test['created_at'] else 'Unknown'}")

        st.write(f"**Measurements:** {test['measurements'] or 'None'}")
        st.write(f"**Notes:** {test['notes'] or 'None'}")

        # Update test result
        st.subheader("Update Test Result")

        new_result = st.selectbox(
            "Result",
            ["Pass", "Fail", "Pending"],
            index=["Pass", "Fail", "Pending"].index(test['result']),
        )

        new_notes = st.text_area(
            "Additional Notes", value=test['notes'] if test['notes'] else ""
        )

        if st.button("Update Result"):
            success = update_quality_test(
                test_id=test_id, test_data={"result": new_result, "notes": new_notes}
            )

            if success:
                st.success(f"Test result updated to {new_result}")
                st.rerun()
            else:
                st.error("Failed to update test result.")


def add_quality_test_form():
    """Display form to add a new quality test."""
    st.subheader("Add New Quality Test")

    # Get all products for selection
    products = get_all_products()

    if products:
        with st.form("add_quality_test_form"):
            col1, col2 = st.columns(2)

            with col1:
                product = st.selectbox(
                    "Product*",
                    options=products,
                    format_func=lambda x: f"{x['name']} (ID: {x['id']})",
                )
                
                test_type = st.selectbox(
                    "Test Type*",
                    ["Visual", "Mechanical", "Chemical", "Dimensional", "Other"],
                )
                
                test_date = st.date_input(
                    "Test Date*",
                    value=datetime.now().date(),
                )

            with col2:
                result = st.selectbox(
                    "Result*",
                    ["Pass", "Fail", "Inconclusive", "Not Tested", "Pending"],
                )
                
            measurements = st.text_area("Measurements")
            notes = st.text_area("Notes")

            submit = st.form_submit_button("Add Test")

            if submit:
                # Add debug print to see what's being passed
                print(f"Adding test: {product['id']}, {test_type}, {test_date}, {result}")
                
                # Convert date to datetime.date if it's not already
                if isinstance(test_date, (str, datetime)):
                    if isinstance(test_date, str):
                        try:
                            test_date = datetime.strptime(test_date, "%Y-%m-%d").date()
                        except ValueError:
                            st.error("Invalid date format. Please use YYYY-MM-DD.")
                            return
                
                try:
                    success = create_quality_test(
                        product_id=product['id'],
                        test_type=test_type,
                        test_date=test_date,
                        result=result,
                        measurements=measurements if measurements else None,
                        notes=notes if notes else None,
                        # Add tester_id if you've added that field
                    )

                    if success:
                        st.success("Quality test added successfully.")
                        st.experimental_rerun()  # Force rerun to update visualizations
                    else:
                        st.error("Failed to add quality test. Please check the entered data.")
                except Exception as e:
                    st.error(f"Error adding quality test: {str(e)}")
                    print(f"Exception details: {e}")
    else:
        st.warning("No products available. Please add a product first.")


def generate_qa_visualizations():
    """Generate visualizations for quality assurance statistics."""
    st.subheader("Quality Assurance Statistics")

    # Get all quality tests for statistics
    quality_tests = get_all_quality_tests()

    if not quality_tests:
        st.info("No quality tests available for statistics.")
        return

    # Create DataFrames for visualizations
    tests_df = pd.DataFrame(
        [
            {
                "ID": test["id"],
                "Product": test["product_name"],
                "Test Type": test["test_type"],
                "Test Date": test["test_date"],
                "Result": test["result"],
                "Tester": test["tester_name"],
            }
            for test in quality_tests
        ]
    )

    col1, col2 = st.columns(2)

    # Test Results Distribution
    with col1:
        result_counts = tests_df["Result"].value_counts().reset_index()
        result_counts.columns = ["Result", "Count"]

        fig1 = px.pie(
            result_counts,
            values="Count",
            names="Result",
            title="Test Results Distribution",
            color="Result",
            color_discrete_map={
                "Pass": "#28a745",
                "Fail": "#dc3545",
                "Pending": "#ffc107",
            },
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Test Types Distribution
    with col2:
        type_counts = tests_df["Test Type"].value_counts().reset_index()
        type_counts.columns = ["Test Type", "Count"]

        fig2 = px.bar(
            type_counts, x="Test Type", y="Count", title="Test Types", color="Test Type"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Results Over Time
    # Group by week and count results
    tests_df["Week"] = tests_df["Test Date"].dt.to_period("W").astype(str)

    result_by_week = (
        tests_df.groupby(["Week", "Result"]).size().reset_index(name="Count")
    )
    result_by_week_pivot = result_by_week.pivot(
        index="Week", columns="Result", values="Count"
    ).reset_index()
    result_by_week_pivot = result_by_week_pivot.fillna(0)

    # Ensure all result columns exist
    for result in ["Pass", "Fail", "Pending"]:
        if result not in result_by_week_pivot:
            result_by_week_pivot[result] = 0

    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=result_by_week_pivot["Week"],
            y=result_by_week_pivot["Pass"],
            name="Pass",
            mode="lines+markers",
            line=dict(color="#28a745", width=2),
            marker=dict(color="#28a745", size=8),
        )
    )

    fig3.add_trace(
        go.Scatter(
            x=result_by_week_pivot["Week"],
            y=result_by_week_pivot["Fail"],
            name="Fail",
            mode="lines+markers",
            line=dict(color="#dc3545", width=2),
            marker=dict(color="#dc3545", size=8),
        )
    )

    fig3.add_trace(
        go.Scatter(
            x=result_by_week_pivot["Week"],
            y=result_by_week_pivot["Pending"],
            name="Pending",
            mode="lines+markers",
            line=dict(color="#ffc107", width=2),
            marker=dict(color="#ffc107", size=8),
        )
    )

    fig3.update_layout(
        title="Test Results Over Time",
        xaxis_title="Week",
        yaxis_title="Number of Tests",
        legend_title="Result",
        hovermode="x unified",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Calculate Pass Rate by Product
    pass_rate_by_product = tests_df[tests_df["Result"].isin(["Pass", "Fail"])]

    if not pass_rate_by_product.empty:
        pass_rate = (
            pass_rate_by_product.groupby("Product")
            .apply(lambda x: (x["Result"] == "Pass").sum() / len(x))
            .reset_index()
        )
        pass_rate.columns = ["Product", "Pass Rate"]
        pass_rate["Pass Rate"] = pass_rate["Pass Rate"] * 100  # Convert to percentage

        fig4 = px.bar(
            pass_rate,
            x="Product",
            y="Pass Rate",
            title="Pass Rate by Product (%)",
            color="Pass Rate",
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[0, 100],
        )

        fig4.update_layout(yaxis_title="Pass Rate (%)")

        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No pass/fail data available for pass rate calculation.")


def main():
    """Main function to display the Quality Assurance page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Quality Assurance",
        page_type="management",
        **get_quality_page_context()
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
        st.title("✅ Quality Assurance")
    with col2:
        if st.button("➕ Add New Test", type="primary", use_container_width=True):
            # Initialize tab index if not in session state
            if "qa_active_tab" not in st.session_state:
                st.session_state.qa_active_tab = 0
            # Set tab index to show the Add New Test tab (index 1)
            st.session_state.qa_active_tab = 1
            st.rerun()

    # Initialize tab index if not in session state
    if "qa_active_tab" not in st.session_state:
        st.session_state.qa_active_tab = 0
        
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Quality Tests", "Add New Test", "Statistics"])
    
    # Select the active tab based on session state
    if st.session_state.qa_active_tab == 1:
        tab2.active = True
    elif st.session_state.qa_active_tab == 2:
        tab3.active = True
    else:
        tab1.active = True

    with tab1:
        display_quality_tests()

    with tab2:
        add_quality_test_form()

    with tab3:
        generate_qa_visualizations()


if __name__ == "__main__":
    main()
