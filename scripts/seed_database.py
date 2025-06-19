#!/usr/bin/env python3
# scripts/seed_payment_data.py
import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.connection import get_db_session
from src.db.models.subscription import Subscription, Payment
from src.db.models.user import User
from src.services.subscription_service import get_subscription_plans

# Load environment variables
load_dotenv()

# Payment methods
PAYMENT_METHODS = ["Credit Card", "PayPal", "Bank Transfer", "Debit Card", "Crypto"]

# Payment statuses with weighted probabilities
PAYMENT_STATUSES = {
    "Completed": 0.9,  # 90% completed
    "Failed": 0.08,    # 8% failed
    "Refunded": 0.02,  # 2% refunded
}

def generate_transaction_id():
    """Generate a random transaction ID."""
    return f"TRANS-{uuid.uuid4().hex[:12].upper()}"

def get_payment_status():
    """Return a payment status based on weighted probabilities."""
    rand = random.random()
    cumulative = 0
    for status, probability in PAYMENT_STATUSES.items():
        cumulative += probability
        if rand <= cumulative:
            return status
    return "Completed"  # Default fallback

def create_subscription(db_session, user_id, months_ago, plan=None):
    """Create a subscription for a user that started X months ago."""
    if plan is None:
        # Get random plan from available plans
        all_plans = get_subscription_plans()
        plan = random.choice(all_plans)
    
    start_date = datetime.utcnow() - timedelta(days=30 * months_ago)
    
    # Determine if subscription is active, expired, or cancelled
    subscription_status_options = ["Active", "Expired", "Cancelled"]
    weights = [0.7, 0.2, 0.1]  # 70% active, 20% expired, 10% cancelled
    status = random.choices(subscription_status_options, weights=weights)[0]
    
    if status == "Active":
        end_date = None if plan["interval"] == "month" else start_date + timedelta(days=365)
    elif status == "Expired":
        if plan["interval"] == "month":
            end_date = start_date + timedelta(days=30)
        else:
            end_date = start_date + timedelta(days=365)
    else:  # Cancelled
        days_until_cancelled = random.randint(5, 25) if plan["interval"] == "month" else random.randint(30, 300)
        end_date = start_date + timedelta(days=days_until_cancelled)
    
    subscription = Subscription(
        user_id=user_id,
        plan_name=plan["name"],
        start_date=start_date,
        end_date=end_date,
        price=plan["price"],
        status=status,
        auto_renew=(status == "Active")
    )
    
    db_session.add(subscription)
    db_session.flush()  # This populates the ID field
    
    return subscription

def create_payment_history(db_session, subscription, months_ago):
    """Create payment history for a subscription."""
    plan_interval = "month" if "Monthly" in subscription.plan_name else "year"
    payment_cycle = 1 if plan_interval == "month" else 12  # Months between payments
    
    # Calculate how many payments should have been made since subscription start
    if subscription.status == "Active":
        num_payments = months_ago // payment_cycle + 1
    elif subscription.status == "Expired":
        num_payments = 1  # One payment for expired subscription
    else:  # Cancelled
        # For cancelled subscriptions, calculate payments until cancellation date
        if subscription.end_date:
            months_until_cancelled = (subscription.end_date - subscription.start_date).days / 30
            num_payments = int(months_until_cancelled // payment_cycle) + 1
        else:
            num_payments = months_ago // payment_cycle + 1
    
    payments = []
    for i in range(min(int(num_payments), 24)):  # Limit to 24 payments max for performance
        payment_date = subscription.start_date + timedelta(days=30 * i * payment_cycle)
        
        # Don't create payments in the future
        if payment_date > datetime.utcnow():
            continue
            
        # Most recent payment for failed/cancelled subscriptions should show the failure
        if i == num_payments - 1 and subscription.status in ["Expired", "Cancelled"]:
            status = "Failed" if random.random() < 0.8 else "Refunded"
            notes = "Payment failed - subscription expired" if status == "Failed" else "Payment refunded - subscription cancelled"
        else:
            status = get_payment_status()
            notes = ""
            
            if status == "Failed":
                notes = random.choice([
                    "Credit card declined",
                    "Insufficient funds",
                    "Payment gateway error",
                    "Card expired",
                ])
            elif status == "Refunded":
                notes = random.choice([
                    "Customer request",
                    "Service issue",
                    "Billing error",
                    "Plan downgrade"
                ])
                
        payment = Payment(
            subscription_id=subscription.id,
            amount=subscription.price,
            payment_date=payment_date,
            payment_method=random.choice(PAYMENT_METHODS),
            transaction_id=generate_transaction_id(),
            status=status,
            notes=notes
        )
        
        payments.append(payment)
    
    db_session.add_all(payments)
    
def seed_payment_data():
    """Main function to seed payment and subscription data."""
    try:
        with get_db_session() as session:
            # Get all users
            users = session.query(User).all()
            
            if not users:
                print("No users found in database. Make sure to run seed_database.py first.")
                return
            
            print(f"Found {len(users)} users. Creating subscriptions and payment data...")
            
            # For each user, create 1-2 subscriptions with payment history
            all_plans = get_subscription_plans()
            
            for user in users:
                # Skip some users randomly to have some without subscriptions
                if random.random() < 0.1:
                    continue
                    
                # How many subscriptions for this user?
                num_subscriptions = random.choices([1, 2], weights=[0.7, 0.3])[0]
                
                for sub_idx in range(num_subscriptions):
                    # Pick a random time in the past (0-12 months ago)
                    months_ago = random.randint(1, 12)
                    
                    # For users with multiple subscriptions, make one active and one cancelled
                    if num_subscriptions > 1 and sub_idx == 0:
                        # Get a yearly plan for first subscription
                        yearly_plans = [p for p in all_plans if "Yearly" in p["name"]]
                        plan = random.choice(yearly_plans)
                        subscription = create_subscription(session, user.id, months_ago, plan)
                    else:
                        subscription = create_subscription(session, user.id, months_ago)
                    
                    create_payment_history(session, subscription, months_ago)
                    
            print("Successfully created subscription and payment data!")
            
            # Print out some stats
            subscription_count = session.query(Subscription).count()
            payment_count = session.query(Payment).count()
            
            print(f"Created {subscription_count} subscriptions")
            print(f"Created {payment_count} payments")
            
    except Exception as e:
        print(f"Error seeding payment data: {e}")
        raise

if __name__ == "__main__":
    seed_payment_data()
