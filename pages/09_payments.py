import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- Database and Service Imports ---
from src.db.connection import get_db_session
from src.services.payment_service import (
    get_user_payments,
    get_all_payments,
    get_payment_stats,
    get_payment_volume_over_time
    # process_refund # Example, if you implement refund processing
)
from src.services.auth_service import get_current_user_id, get_user_by_id # Assuming you have these
from src.components.universal_css import inject_universal_css

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Payment Management", layout="wide", page_icon="💰")

# Inject universal CSS styling
inject_universal_css()

# --- Page Title ---
st.title("💰 Payment Management")
st.markdown("View your payment history or overall payment metrics.")

# --- Database Session and User Authentication ---
# db_session = next(get_session()) # Old way
with get_db_session() as db_session: # New context managed way
    current_user_id = get_current_user_id(db_session) # Placeholder, replace with actual auth
    current_user = None
    is_admin = False

    if current_user_id:
        current_user = get_user_by_id(db_session, current_user_id) # Fetch user details
        if current_user:
            is_admin = current_user.role == "admin" # Check if user is admin
    else:
        st.warning("Please log in to view payment information.")
        st.stop()

    # --- Main Page Sections ---
    tab_titles = ["My Payment History"]
    if is_admin:
        tab_titles.append("Admin Dashboard")

    tabs = st.tabs(tab_titles)

    with tabs[0]: # My Payment History
        st.header("My Payment History")
        if current_user_id:
            user_payments_list = get_user_payments(db_session, current_user_id)
            
            if user_payments_list:
                # Convert list of tuples/objects to DataFrame
                user_payments_data = [{
                    "id": p.id, # Assuming 'id' is part of the returned payment object/tuple
                    "amount": p.amount,
                    "payment_date": p.payment_date, # Already datetime
                    "status": p.status,
                    "transaction_id": p.transaction_id,
                    "plan_name": p.plan_name, # From joined Subscription
                    "payment_method": p.payment_method,
                    "notes": p.notes
                } for p in user_payments_list]
                user_payments_df = pd.DataFrame(user_payments_data)
                user_payments_df['payment_date'] = pd.to_datetime(user_payments_df['payment_date'])


                if not user_payments_df.empty:
                    for index, row in user_payments_df.iterrows():
                        expander_title = f"Payment: ${row['amount']:.2f} on {row['payment_date'].strftime('%Y-%m-%d')} ({row['status']})"
                        with st.expander(expander_title):
                            st.markdown(f"**Transaction ID:** {row['transaction_id']}")
                            st.markdown(f"**Plan:** {row['plan_name']}")
                            st.markdown(f"**Payment Method:** {row['payment_method']}")
                            st.markdown(f"**Status:** {row['status']}")
                            if pd.notna(row['notes']) and row['notes']:
                                st.markdown(f"**Notes:** {row['notes']}")
                            
                            if row['status'] == 'Completed':
                                if st.button("Request Refund", key=f"refund_{row['id']}_{index}"): # Ensure unique key
                                    # try:
                                    #     process_refund(db_session, row['id'], current_user_id)
                                    #     st.success(f"Refund processed for payment ID {row['id']}.")
                                    #     st.rerun() # To refresh the payment list
                                    # except Exception as e:
                                    #     st.error(f"Refund failed: {e}")
                                    st.info(f"Mock: Refund requested for payment ID {row['id']}. (Actual refund processing not implemented in this step)")
                else:
                    st.info("No payment history found.")
            else:
                st.info("No payment history found.")
        else:
            st.warning("Could not identify user.")


    if is_admin and len(tabs) > 1:
        with tabs[1]: # Admin Dashboard
            st.header("Admin Dashboard: Payment Metrics")

            stats = get_payment_stats(db_session) # Service call

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Payments Logged", stats.get("total_payments",0))
            col2.metric("Successful Payments", stats.get("successful_payments",0))
            col3.metric("Total Revenue", f"${stats.get('total_revenue',0):.2f}")
            col4.metric("Avg. Payment Value", f"${stats.get('average_payment_value',0):.2f}")
            # col4.metric("Refund Rate", f"{stats.get('refund_rate',0)*100:.1f}%") # If refund_rate is implemented

            st.divider()

            st.subheader("Payment Volume Over Time (Last 90 Days)")
            volume_df = get_payment_volume_over_time(db_session) # Service call
            
            if not volume_df.empty:
                volume_chart = alt.Chart(volume_df).mark_bar().encode(
                    x=alt.X('date:T', title='Date', timeUnit='yearmonthdate'),
                    y=alt.Y('daily_volume:Q', title='Daily Payment Volume (USD)'),
                    tooltip=['date:T', 'daily_volume:Q', 'cumulative_volume:Q']
                ).properties(
                    title="Daily Payment Volume"
                )
                
                cumulative_line = alt.Chart(volume_df).mark_line(color='red', point=True).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('cumulative_volume:Q', title='Cumulative Volume (USD)'),
                     tooltip=['date:T', 'cumulative_volume:Q']
                ).properties(
                    title="Cumulative Payment Volume"
                )
                
                st.altair_chart(volume_chart, use_container_width=True)
                st.altair_chart(cumulative_line, use_container_width=True)
                
            else:
                st.info("Not enough data to display payment volume trend.")

            st.divider()

            st.subheader("All User Payments (Admin View)")
            all_payments_list = get_all_payments(db_session) # Service call

            if all_payments_list:
                # Convert list of tuples/objects to DataFrame
                all_payments_data = [{
                    "user_name": p.user_name, # From joined User
                    "plan_name": p.plan_name, # From joined Subscription
                    "amount": p.amount,
                    "payment_date": p.payment_date, # Already datetime
                    "payment_method": p.payment_method,
                    "transaction_id": p.transaction_id,
                    "status": p.status
                } for p in all_payments_list]
                all_payments_df = pd.DataFrame(all_payments_data)
                all_payments_df['payment_date'] = pd.to_datetime(all_payments_df['payment_date'])


                if not all_payments_df.empty:
                    # Filtering options
                    status_options = ['All'] + sorted(list(all_payments_df['status'].unique()))
                    selected_status = st.selectbox("Filter by Status:", options=status_options)

                    payment_method_options = ['All'] + sorted(list(all_payments_df['payment_method'].unique()))
                    selected_methods = st.selectbox("Filter by Payment Method:", options=payment_method_options)
                    
                    filtered_df = all_payments_df.copy()
                    if selected_status != 'All':
                        filtered_df = filtered_df[filtered_df['status'] == selected_status]
                    if selected_methods != 'All':
                        filtered_df = filtered_df[filtered_df['payment_method'] == selected_methods]
                    
                    st.dataframe(
                        filtered_df[['user_name', 'plan_name', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'status']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "payment_date": st.column_config.DatetimeColumn("Payment Date", format="YYYY-MM-DD HH:mm"),
                            "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
                        }
                    )
                else:
                    st.info("No payment data found.")
            else:
                st.info("No payment data found.")

# Close the session when done
# db_session.close() # No longer needed with context manager

# To run this page: streamlit run pages/09_payments.py
# Remember to create the actual service functions (e.g., in src/services/payment_service.py) 
# and connect to your database.

