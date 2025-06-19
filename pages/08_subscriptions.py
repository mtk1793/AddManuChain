import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- Database and Service Imports ---
from src.db.connection import get_db_session # Changed from get_session
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_subscriptions_page_context
from src.components.universal_css import inject_universal_css
from src.services.subscription_service import (
    get_user_subscriptions,
    get_all_subscriptions,
    get_subscription_plans,
    get_subscription_stats,
    get_total_revenue_over_time,
    get_active_subscriptions_trend,
    get_churn_rate_trend 
)
from src.services.auth_service import get_current_user_id, get_user_by_id # Assuming you have these

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Subscription Management", layout="wide", page_icon="💳")

# Inject universal CSS styling
inject_universal_css()

def main():
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Subscription Management",
        page_type="management",
        **get_subscriptions_page_context()
    )
    
    # Render the floating AI assistant
    render_page_ai_assistant()
    
    # --- Page Title ---
    st.title("👑 Subscription Management")
    st.markdown("Manage your subscriptions or view overall platform subscription metrics.")

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
            st.warning("Please log in to manage subscriptions.")
            st.stop()


        # --- Main Page Sections ---
        tab_titles = ["My Subscriptions", "Subscription Plans"]
        if is_admin:
            tab_titles.append("Admin Dashboard")

        tabs = st.tabs(tab_titles)

    with tabs[0]: # My Subscriptions
        st.header("My Current Subscriptions")
        if current_user_id:
            # user_subs_df = get_mock_user_subscriptions(current_user_id) # Old mock
            user_subs_list = get_user_subscriptions(db_session, current_user_id)
            if user_subs_list:
                user_subs_data = [{
                    "id": sub.id,
                    "plan_name": sub.plan_name,
                    "start_date": sub.start_date.strftime("%Y-%m-%d"),
                    "end_date": sub.end_date.strftime("%Y-%m-%d") if sub.end_date else "N/A",
                    "price": f"${sub.price:.2f}",
                    "status": sub.status,
                    "auto_renew": "Yes" if sub.auto_renew else "No"
                } for sub in user_subs_list]
                user_subs_df = pd.DataFrame(user_subs_data)
                st.dataframe(user_subs_df, use_container_width=True, hide_index=True)
            else:
                st.info("You currently have no active subscriptions.")
        else:
            st.warning("Could not identify user.")


    with tabs[1]: # Subscription Plans
        st.header("Available Subscription Plans")
        # plans = get_mock_subscription_plans() # Old mock
        plans = get_subscription_plans() # Service call
        if plans:
            for plan in plans:
                with st.container(border=True):
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.subheader(plan["name"])
                        st.caption(f"Price: ${plan['price']:.2f} per {plan['interval']}")
                        st.markdown("**Features:**")
                        for feature in plan["features"]:
                            st.markdown(f"- {feature}")
                    with col2:
                        if st.button(f"Choose {plan['name']}", key=f"choose_{plan['id']}", use_container_width=True):
                            st.success(f"Mock: You've selected the {plan['name']} plan. Checkout not implemented.")
                            # Here you would typically redirect to a payment page or handle plan activation
        else:
            st.error("Could not load subscription plans at this time.")

    if is_admin and len(tabs) > 2:
        with tabs[2]: # Admin Dashboard
            st.header("Admin Dashboard: Subscription Metrics")
            
            # stats = get_mock_subscription_stats() # Old mock
            stats = get_subscription_stats(db_session) # Service call

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Subscriptions", stats.get("total_subscriptions", 0))
            col2.metric("Active Subscriptions", stats.get("active_subscriptions", 0))
            col3.metric("Monthly Recurring Revenue (MRR)", f"${stats.get('mrr', 0):.2f}")
            col4.metric("Avg. Revenue Per User (ARPU)", f"${stats.get('arpu', 0):.2f}")

            st.divider()
            
            st.subheader("Revenue Trend (Last 90 Days)")
            # revenue_df = get_mock_total_revenue_over_time() # Old mock
            revenue_df = get_total_revenue_over_time(db_session) # Service call
            if not revenue_df.empty:
                revenue_chart = alt.Chart(revenue_df).mark_line(point=True).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('cumulative_revenue:Q', title='Cumulative Revenue (USD)'),
                    tooltip=['date:T', 'daily_revenue:Q', 'cumulative_revenue:Q']
                ).properties(
                    title="Cumulative Subscription Revenue Over Time"
                )
                st.altair_chart(revenue_chart, use_container_width=True)
            else:
                st.info("Not enough data to display revenue trend.")

            st.divider()

            col_active, col_churn = st.columns(2)

            with col_active:
                st.subheader("Active Subscriptions Trend (Last 90 Days)")
                # active_trend_df = get_mock_active_subscriptions_trend() # Old mock
                active_trend_df = get_active_subscriptions_trend(db_session) # Service call
                if not active_trend_df.empty:
                    active_chart = alt.Chart(active_trend_df).mark_area(
                        line={'color':'darkgreen'},
                        color=alt.Gradient(
                            gradient='linear',
                            stops=[alt.GradientStop(color='white', offset=0),
                                   alt.GradientStop(color='lightgreen', offset=1)],
                            x1=1,
                            x2=1,
                            y1=1,
                            y2=0
                        )
                    ).encode(
                        x=alt.X('date:T', title='Date'),
                        y=alt.Y('active_subscriptions:Q', title='Number of Active Subscriptions'),
                        tooltip=['date:T', 'active_subscriptions:Q']
                    ).properties(
                        title="Active Subscriptions Over Time"
                    )
                    st.altair_chart(active_chart, use_container_width=True)
                else:
                    st.info("Not enough data to display active subscriptions trend.")

            with col_churn:
                st.subheader("Churn Rate Trend (Monthly - Mock)")
                # churn_df = get_mock_churn_rate_trend() # Old mock
                churn_df = get_churn_rate_trend(db_session) # Service call (currently mock in service)
                if not churn_df.empty:
                    churn_chart = alt.Chart(churn_df).mark_line(point=True, color='orange').encode(
                        x=alt.X('date:T', title='Month'),
                        y=alt.Y('churn_rate:Q', title='Churn Rate', axis=alt.Axis(format='%')),
                        tooltip=['date:T', alt.Tooltip('churn_rate:Q', format='.2%')]
                    ).properties(
                        title="Monthly Churn Rate (Mock Data)"
                    )
                    st.altair_chart(churn_chart, use_container_width=True)
                else:
                    st.info("Not enough data to display churn rate trend.")
            
            st.divider()
            st.subheader("All User Subscriptions (Admin View)")
            # all_subs_df = get_mock_all_subscriptions() # Old mock
            all_subs_list = get_all_subscriptions(db_session)
            if all_subs_list:
                # Now we're getting just a list of Subscription objects
                all_subs_data = []
                for sub in all_subs_list:
                    # Get the username if needed (could be done in the service instead)
                    user = get_user_by_id(db_session, sub.user_id) if sub.user_id else None
                    all_subs_data.append({
                        "user_id": sub.user_id,
                        "user_name": user.username if user else "N/A",
                        "plan_name": sub.plan_name,
                        "start_date": sub.start_date.strftime("%Y-%m-%d"),
                        "end_date": sub.end_date.strftime("%Y-%m-%d") if sub.end_date else "N/A",
                        "price": f"${sub.price:.2f}",
                        "status": sub.status,
                        "auto_renew": "Yes" if sub.auto_renew else "No"
                    })
                all_subs_df_final = pd.DataFrame(all_subs_data)
                st.dataframe(all_subs_df_final, use_container_width=True, hide_index=True)
            else:
                st.info("No subscription data found.")

if __name__ == "__main__":
    main()

# The session is automatically closed when exiting the with-block
# To run this page: streamlit run pages/08_subscriptions.py
# Remember to create the actual service functions and connect to your database.

