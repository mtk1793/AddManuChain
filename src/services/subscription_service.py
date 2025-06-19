# src/services/subscription_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from src.db.connection import get_db_session
from src.db.models.subscription import Subscription
from src.db.models.user import User
from datetime import datetime, timedelta
import pandas as pd

def get_user_subscriptions(db_session, user_id):
    """Fetches all subscriptions for a given user."""
    try:
        return db_session.query(Subscription).filter(Subscription.user_id == user_id).all()
    except Exception as e:
        print(f"Error fetching user subscriptions: {e}")
        return []

def get_all_subscriptions(db_session):
    """Fetches all subscriptions (for admin view)."""
    try:
        # Return a list of subscription objects
        # If you need user data joined, adjust the query accordingly
        return db_session.query(Subscription).all()
    except Exception as e:
        print(f"Error fetching all subscriptions: {e}")
        return []

def get_subscription_plans():
    """
    Returns a list of available subscription plans.
    For now, this is a mock. In a real app, this might come from a database table.
    """
    return [
        {"id": "basic_monthly", "name": "Basic Monthly", "price": 10.00, "currency": "USD", "interval": "month", "features": ["Feature A", "Feature B"]},
        {"id": "premium_monthly", "name": "Premium Monthly", "price": 20.00, "currency": "USD", "interval": "month", "features": ["Feature A", "Feature B", "Feature C"]},
        {"id": "basic_yearly", "name": "Basic Yearly", "price": 100.00, "currency": "USD", "interval": "year", "features": ["Feature A", "Feature B", "17% Off"]},
        {"id": "premium_yearly", "name": "Premium Yearly", "price": 200.00, "currency": "USD", "interval": "year", "features": ["Feature A", "Feature B", "Feature C", "17% Off"]},
    ]

def get_subscription_stats(db_session):
    """Calculates aggregate subscription statistics."""
    try:
        total_subscriptions = db_session.query(func.count(Subscription.id)).scalar() or 0
        active_subscriptions = db_session.query(func.count(Subscription.id)).filter(Subscription.status == "Active").scalar() or 0
        
        # Monthly Recurring Revenue (MRR) - simplified: sum of prices of active subscriptions
        mrr = db_session.query(func.sum(Subscription.price)).filter(Subscription.status == "Active").scalar() or 0
        
        # Average Revenue Per User (ARPU) - simplified
        total_revenue = db_session.query(func.sum(Subscription.price)).filter(Subscription.status == "Active").scalar() or 0
        distinct_users_with_active_subs = db_session.query(func.count(func.distinct(Subscription.user_id))).filter(
            Subscription.status == "Active"
        ).scalar() or 0
        
        arpu = (total_revenue / distinct_users_with_active_subs) if distinct_users_with_active_subs > 0 else 0

        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "mrr": mrr,
            "arpu": arpu
        }
    except Exception as e:
        print(f"Error calculating subscription stats: {e}")
        return {
            "total_subscriptions": 0,
            "active_subscriptions": 0,
            "mrr": 0,
            "arpu": 0
        }

def get_total_revenue_over_time(db_session, days_limit=90):
    """
    Calculates total revenue from new subscriptions over a specified period.
    """
    try:
        start_period = datetime.utcnow() - timedelta(days=days_limit)
        
        revenue_data = db_session.query(
            func.date(Subscription.start_date).label("date"),
            func.sum(Subscription.price).label("daily_revenue")
        ).filter(Subscription.start_date >= start_period)\
        .group_by(func.date(Subscription.start_date))\
        .order_by(func.date(Subscription.start_date))\
        .all()
        
        if not revenue_data:
            return pd.DataFrame(columns=["date", "daily_revenue", "cumulative_revenue"])

        df = pd.DataFrame(revenue_data, columns=["date", "daily_revenue"])
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure all dates in the period are present, filling missing ones with 0 revenue
        all_dates = pd.date_range(start=df['date'].min(), end=datetime.utcnow(), freq='D')
        df = df.set_index('date').reindex(all_dates, fill_value=0).reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        
        df['cumulative_revenue'] = df['daily_revenue'].cumsum()
        return df
    except Exception as e:
        print(f"Error calculating revenue over time: {e}")
        return pd.DataFrame(columns=["date", "daily_revenue", "cumulative_revenue"])

def get_active_subscriptions_trend(db_session, days_limit=90):
    """
    Calculates the trend of active subscriptions over time.
    """
    try:
        end_date = datetime.utcnow().date()
        start_date_period = (datetime.utcnow() - timedelta(days=days_limit)).date()
        
        # Create a series of dates for the requested period
        date_series = pd.date_range(start=start_date_period, end=end_date, freq='D')
        active_counts = []
        
        for current_date_dt in date_series:
            current_date = current_date_dt.date()
            # Count subscriptions active on this date
            count = db_session.query(func.count(Subscription.id)).filter(
                Subscription.start_date <= current_date,
                (Subscription.end_date.is_(None)) | (Subscription.end_date >= current_date),
                Subscription.status == "Active"
            ).scalar() or 0
            
            active_counts.append({"date": current_date_dt, "active_subscriptions": count})
        
        df = pd.DataFrame(active_counts)
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    except Exception as e:
        print(f"Error calculating active subscription trend: {e}")
        return pd.DataFrame(columns=["date", "active_subscriptions"])

def get_churn_rate_trend(db_session, days_limit=90):
    """
    Calculates churn rate trend.
    For demo, we'll return a mock trend.
    """
    try:
        # In a real implementation, this would calculate actual churn rates
        # from the database, likely using window functions to compare periods
        
        # For demonstration, return a mock decreasing churn trend
        dates = pd.date_range(
            start=datetime.utcnow() - timedelta(days=days_limit),
            end=datetime.utcnow(),
            freq='M'  # Monthly frequency
        )
        
        # Decreasing mock churn rates (percentages)
        mock_churn_rates = [(0.05 - (i * 0.001)) for i in range(len(dates))]
        
        df = pd.DataFrame({
            "date": dates,
            "churn_rate": mock_churn_rates
        })
        
        # Ensure churn rates are positive but not unreasonably high
        df['churn_rate'] = df['churn_rate'].clip(lower=0.01, upper=0.10)
        
        return df
    except Exception as e:
        print(f"Error calculating churn rate trend: {e}")
        return pd.DataFrame(columns=["date", "churn_rate"])

def create_subscription(db_session, user_id, plan_name, price, start_date=None, auto_renew=True):
    """Create a new subscription for a user."""
    try:
        if start_date is None:
            start_date = datetime.utcnow()
            
        # Create new subscription
        new_subscription = Subscription(
            user_id=user_id,
            plan_name=plan_name,
            start_date=start_date,
            price=price,
            status="Active",
            auto_renew=auto_renew,
            created_at=datetime.utcnow()
        )
        
        db_session.add(new_subscription)
        db_session.commit()
        
        return new_subscription
    except Exception as e:
        db_session.rollback()
        print(f"Error creating subscription: {e}")
        raise

def cancel_subscription(db_session, subscription_id, user_id):
    """Cancel a subscription (admin or subscription owner)."""
    try:
        # Find subscription
        subscription = db_session.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription ID {subscription_id} not found")
            
        # Check if user is authorized (subscription owner or admin)
        user = db_session.query(User).filter(User.id == user_id).first()
        is_admin = user and user.role == 'admin'
        
        if subscription.user_id != user_id and not is_admin:
            raise PermissionError("User does not have permission to cancel this subscription")
            
        # Update subscription
        subscription.status = "Cancelled"
        subscription.auto_renew = False
        subscription.end_date = datetime.utcnow()  # End immediately
        
        db_session.commit()
        return True
    except Exception as e:
        db_session.rollback()
        print(f"Error cancelling subscription: {e}")
        raise
