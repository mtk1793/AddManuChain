# src/services/payment_service.py
from datetime import datetime, timedelta
from sqlalchemy import func
from src.db.connection import get_db_session
from src.db.models.subscription import Payment, Subscription
from src.db.models.user import User
import pandas as pd

def get_user_payments(db_session, user_id):
    """Fetches all payments for a given user, joining with subscription for plan name."""
    try:
        results = db_session.query(
            Payment.id,
            Payment.amount,
            Payment.payment_date,
            Payment.payment_method,
            Payment.transaction_id,
            Payment.status,
            Payment.notes,
            Subscription.plan_name
        ).join(Subscription, Payment.subscription_id == Subscription.id)\
        .filter(Subscription.user_id == user_id)\
        .order_by(Payment.payment_date.desc())\
        .all()
        
        # Convert tuple results to objects with named attributes for easy access
        class PaymentResult:
            def __init__(self, id, amount, payment_date, payment_method, transaction_id, status, notes, plan_name):
                self.id = id
                self.amount = amount
                self.payment_date = payment_date
                self.payment_method = payment_method
                self.transaction_id = transaction_id
                self.status = status
                self.notes = notes
                self.plan_name = plan_name
        
        return [PaymentResult(*row) for row in results]
    except Exception as e:
        print(f"Error fetching user payments: {e}")
        return []

def get_all_payments(db_session):
    """Fetches all payments, joining with User and Subscription for more details (admin view)."""
    try:
        results = db_session.query(
            Payment.id,
            User.username.label("user_name"),
            Subscription.plan_name,
            Payment.amount,
            Payment.payment_date,
            Payment.payment_method,
            Payment.transaction_id,
            Payment.status
        ).join(Subscription, Payment.subscription_id == Subscription.id)\
        .join(User, Subscription.user_id == User.id)\
        .order_by(Payment.payment_date.desc())\
        .all()
        
        # Convert tuple results to objects with named attributes
        class PaymentAdminResult:
            def __init__(self, id, user_name, plan_name, amount, payment_date, payment_method, transaction_id, status):
                self.id = id
                self.user_name = user_name
                self.plan_name = plan_name
                self.amount = amount
                self.payment_date = payment_date
                self.payment_method = payment_method
                self.transaction_id = transaction_id
                self.status = status
        
        return [PaymentAdminResult(*row) for row in results]
    except Exception as e:
        print(f"Error fetching all payments: {e}")
        return []

def get_payment_stats(db_session):
    """Calculates aggregate payment statistics."""
    try:
        total_payments = db_session.query(func.count(Payment.id)).scalar() or 0
        successful_payments = db_session.query(func.count(Payment.id)).filter(Payment.status == "Completed").scalar() or 0
        total_revenue = db_session.query(func.sum(Payment.amount)).filter(Payment.status == "Completed").scalar() or 0
        
        # Average Payment Value
        avg_payment_value = (total_revenue / successful_payments) if successful_payments else 0
        
        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "total_revenue": total_revenue,
            "average_payment_value": avg_payment_value,
        }
    except Exception as e:
        print(f"Error calculating payment stats: {e}")
        return {
            "total_payments": 0,
            "successful_payments": 0,
            "total_revenue": 0,
            "average_payment_value": 0,
        }

def get_payment_volume_over_time(db_session, days_limit=90):
    """
    Calculates total payment volume from successful payments over a specified period.
    """
    try:
        start_period = datetime.utcnow() - timedelta(days=days_limit)
        
        volume_data = db_session.query(
            func.date(Payment.payment_date).label("date"),
            func.sum(Payment.amount).label("daily_volume")
        ).filter(Payment.status == "Completed", Payment.payment_date >= start_period)\
        .group_by(func.date(Payment.payment_date))\
        .order_by(func.date(Payment.payment_date))\
        .all()

        if not volume_data:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=["date", "daily_volume", "cumulative_volume"])

        # Create DataFrame from query results
        df = pd.DataFrame(volume_data, columns=["date", "daily_volume"])
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure all dates in the period are present, filling missing ones with 0 volume
        date_range = pd.date_range(start=df['date'].min(), end=datetime.utcnow(), freq='D')
        df = df.set_index('date').reindex(date_range, fill_value=0).reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        
        # Calculate cumulative sum
        df['cumulative_volume'] = df['daily_volume'].cumsum()
        
        return df
    except Exception as e:
        print(f"Error calculating payment volume: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=["date", "daily_volume", "cumulative_volume"])

def process_refund(db_session, payment_id, user_id, reason="User requested refund"):
    """Processes a refund for a given payment."""
    try:
        # Find the payment
        payment = db_session.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment with ID {payment_id} not found.")
        
        # Find the subscription to check ownership
        subscription = db_session.query(Subscription).filter(Subscription.id == payment.subscription_id).first()
        if not subscription:
            raise ValueError(f"Subscription for payment ID {payment_id} not found.")
        
        # Get the user role (admin check would be here in a real implementation)
        user = db_session.query(User).filter(User.id == user_id).first()
        is_admin = user and user.role == 'admin'
        
        # Check if user has permission (either owns the subscription or is an admin)
        if subscription.user_id != user_id and not is_admin:
            raise PermissionError("User does not have permission to refund this payment.")

        # Check if payment is in a refundable state
        if payment.status != "Completed":
            raise ValueError(f"Payment ID {payment_id} is not in a refundable state (current status: {payment.status}).")

        # Process the refund
        payment.status = "Refunded"
        
        # Add refund note
        refund_note = f"Refund processed on {datetime.utcnow().strftime('%Y-%m-%d')}: {reason}"
        if payment.notes:
            payment.notes = f"{payment.notes}; {refund_note}"
        else:
            payment.notes = refund_note
        
        db_session.commit()
        return True
        
    except Exception as e:
        db_session.rollback()
        print(f"Error processing refund: {e}")
        raise
