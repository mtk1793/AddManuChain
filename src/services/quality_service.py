from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import desc, asc

from src.db.connection import get_db_session
from src.db.models.quality import QualityTest
from src.db.models.product import Product  # Assuming Product model is in src.db.models.product

def get_all_quality_tests(status=None, product_id=None, test_type=None, result=None, start_date=None, end_date=None):
    """Get all quality tests with optional filtering"""
    with get_db_session() as session:
        query = session.query(QualityTest)
        
        # Fix the filtering logic for lists
        if status:
            if isinstance(status, list):
                query = query.filter(QualityTest.status.in_(status))
            else:
                query = query.filter(QualityTest.status == status)
        
        if test_type:
            if isinstance(test_type, list):
                query = query.filter(QualityTest.test_type.in_(test_type))
            else:
                query = query.filter(QualityTest.test_type == test_type)
            
        if product_id:
            query = query.filter(QualityTest.product_id == product_id)
            
        if result:
            if isinstance(result, list):
                query = query.filter(QualityTest.result.in_(result))
            else:
                query = query.filter(QualityTest.result == result)
                  # Add date range filtering
        if start_date:
            query = query.filter(QualityTest.test_date >= start_date)
            
        if end_date:
            query = query.filter(QualityTest.test_date <= end_date)        # Convert to dictionaries to prevent DetachedInstanceError
        tests = query.all()
        test_list = []
        for test in tests:
            # Get product and tester info safely
            product_name = "Unknown"
            if test.product:
                product_name = getattr(test.product, "name", "Unknown")
            
            tester_name = "Unknown"
            if test.tester:
                first_name = getattr(test.tester, "first_name", "")
                last_name = getattr(test.tester, "last_name", "")
                if first_name or last_name:
                    tester_name = f"{first_name} {last_name}".strip()
            
            test_dict = {
                "id": test.id,
                "test_type": test.test_type,
                "product_id": test.product_id,
                "product_name": product_name,
                "result": test.result,
                "tester_id": test.tester_id,
                "tester_name": tester_name,
                "test_date": test.test_date,
                "measurements": test.measurements,
                "notes": test.notes,
                "created_at": test.created_at,
            }
            test_list.append(test_dict)
            
        return test_list

def get_quality_test_by_id(test_id: int) -> Optional[Dict[str, Any]]:
    """Get a quality test by its ID."""
    with get_db_session() as session:
        try:
            test = session.query(QualityTest).filter(QualityTest.id == test_id).first()
            if not test:
                return None
                
            # Get product and tester info safely
            product_name = "Unknown"
            if test.product:
                product_name = getattr(test.product, "name", "Unknown")
            
            tester_name = "Unknown"
            if test.tester:
                first_name = getattr(test.tester, "first_name", "")
                last_name = getattr(test.tester, "last_name", "")
                if first_name or last_name:
                    tester_name = f"{first_name} {last_name}".strip()
                
            # Convert to dictionary to avoid DetachedInstanceError
            test_dict = {
                "id": test.id,
                "test_type": test.test_type,
                "product_id": test.product_id,
                "product_name": product_name,
                "result": test.result,
                "tester_id": test.tester_id,
                "tester_name": tester_name,
                "test_date": test.test_date,
                "measurements": test.measurements,
                "notes": test.notes,
                "created_at": test.created_at,
            }
            return test_dict
        except Exception as e:
            print(f"Error retrieving quality test with ID {test_id}: {e}")
            return None

def create_quality_test(
    test_type=None,
    product_id=None,
    tester_id=None,
    test_date=None,
    result=None,
    measurements=None,
    notes=None,
):
    """Create a new quality test in the database."""
    with get_db_session() as session:
        try:
            # Create the quality test
            new_test = QualityTest(
                test_type=test_type,
                product_id=product_id,
                tester_id=tester_id,
                test_date=test_date or datetime.utcnow(),
                result=result,
                measurements=measurements,
                notes=notes,
            )

            # These two lines were missing or incomplete:
            session.add(new_test)
            session.commit()

            return True
        except IntegrityError as e:
            session.rollback()
            print(f"IntegrityError creating quality test: {str(e)}")
            return False
        except Exception as e:
            session.rollback()
            print(f"Error creating quality test: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full stack trace
            return False

def update_quality_test(test_id, test_data):
    """Update an existing quality test in the database."""
    with get_db_session() as session:
        try:
            test = session.query(QualityTest).filter(QualityTest.id == test_id).first()
            
            if not test:
                return False
                
            # Only update fields that exist in the model
            if "test_type" in test_data:
                test.test_type = test_data["test_type"]
            if "product_id" in test_data:
                test.product_id = test_data["product_id"]
            if "tester_id" in test_data:
                test.tester_id = test_data["tester_id"]
            if "test_date" in test_data:
                test.test_date = test_data["test_date"]
            if "result" in test_data:
                test.result = test_data["result"]
            if "measurements" in test_data:
                test.measurements = test_data["measurements"]
            if "notes" in test_data:
                test.notes = test_data["notes"]

            session.commit()

            return True
        except IntegrityError:
            session.rollback()
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating quality test: {str(e)}")
            return False

def delete_quality_test(test_id):
    """Delete a quality test from the database."""
    with get_db_session() as session:
        try:
            test = session.query(QualityTest).filter(QualityTest.id == test_id).first()

            if not test:
                return False

            session.delete(test)
            session.commit()

            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting quality test: {str(e)}")
            return False

def get_all_products(status=None):
    """Get all products with optional filtering"""
    with get_db_session() as session:
        query = session.query(Product)
        
        if status:
            if isinstance(status, list):
                query = query.filter(Product.status.in_(status))
            else:
                query = query.filter(Product.status == status)
                
        products = query.all()
        
        # Create a list of dictionaries for each product
        product_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                # Use getattr with a default value to handle missing attributes
                "type": getattr(product, "type", None),
                # Use getattr for product_type if it might not exist
                "product_type": getattr(product, "type", None),  # Use type instead of product_type
                "description": getattr(product, "description", None),
                "status": getattr(product, "status", "Active")
                # Add other product attributes as needed
            }
            product_list.append(product_dict)
            
        return product_list