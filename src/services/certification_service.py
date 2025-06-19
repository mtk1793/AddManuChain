from datetime import datetime, timedelta  # Add timedelta import
from typing import Optional, List, Dict, Any
import pandas as pd
import os
import json
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import desc, asc

from src.db.connection import get_db_session
from src.db.models.certification import Certification
from src.db.models.product import Product
from src.db.models.material import Material

def get_all_certifications(status=None, cert_type=None, product_id=None, material_id=None, 
                          expiry_date_start=None, expiry_date_end=None, expiry_filter=None):
    """Get all certifications with optional filtering"""
    with get_db_session() as session:
        query = session.query(
            Certification, 
            Product.name.label("product_name"),
            Material.name.label("material_name")
        ).outerjoin(
            Product, Certification.product_id == Product.id
        ).outerjoin(
            Material, Certification.material_id == Material.id
        )
        
        # Filter by status
        if status:
            if isinstance(status, list):
                query = query.filter(Certification.status.in_(status))
            else:
                query = query.filter(Certification.status == status)
        
        # Filter by certification type
        if cert_type:
            if isinstance(cert_type, list):
                query = query.filter(Certification.cert_type.in_(cert_type))
            else:
                query = query.filter(Certification.cert_type == cert_type)
        
        # Filter by product or material
        if product_id:
            query = query.filter(Certification.product_id == product_id)
            
        if material_id:
            query = query.filter(Certification.material_id == material_id)
        
        # Filter by expiry date range
        if expiry_date_start:
            query = query.filter(Certification.expiry_date >= expiry_date_start)
            
        if expiry_date_end:
            query = query.filter(Certification.expiry_date <= expiry_date_end)
            
        # Special expiry filters
        today = datetime.now().date()
        if expiry_filter == "Expired":
            query = query.filter(Certification.expiry_date < today)
        elif expiry_filter == "Valid":
            query = query.filter(Certification.expiry_date >= today)
        elif expiry_filter == "Expiring Soon (30 days)":
            query = query.filter(Certification.expiry_date >= today)
            query = query.filter(Certification.expiry_date <= today + timedelta(days=30))
        elif expiry_filter == "Expiring Soon (90 days)":
            query = query.filter(Certification.expiry_date >= today)
            query = query.filter(Certification.expiry_date <= today + timedelta(days=90))

        # Get results
        results = query.all()
        
        # Convert to dictionaries to prevent DetachedInstanceError
        cert_list = []
        for cert, product_name, material_name in results:
            cert_dict = {
                "id": cert.id,
                "cert_number": cert.cert_number,
                "cert_type": cert.cert_type,
                "product_id": cert.product_id,
                "material_id": cert.material_id,
                "product_name": product_name,
                "material_name": material_name,
                "issuing_authority": cert.issuing_authority,
                "issue_date": cert.issue_date,
                "expiry_date": cert.expiry_date,
                "status": cert.status,
                "requirements": cert.requirements,
                "documents": cert.documents,
                "created_at": cert.created_at,
                "updated_at": cert.updated_at
            }
            cert_list.append(cert_dict)
            
        return cert_list

def get_certification_by_id(cert_id: int) -> Optional[Dict[str, Any]]:
    """Get a certification by its ID."""
    with get_db_session() as session:
        try:
            result = session.query(
                Certification, 
                Product.name.label("product_name"),
                Material.name.label("material_name")
            ).outerjoin(
                Product, Certification.product_id == Product.id
            ).outerjoin(
                Material, Certification.material_id == Material.id
            ).filter(
                Certification.id == cert_id
            ).first()
            
            if not result:
                return None
                
            cert, product_name, material_name = result
            
            # Convert to dictionary to avoid DetachedInstanceError
            cert_dict = {
                "id": cert.id,
                "cert_number": cert.cert_number,
                "cert_type": cert.cert_type,
                "product_id": cert.product_id,
                "material_id": cert.material_id,
                "product_name": product_name,
                "material_name": material_name,
                "issuing_authority": cert.issuing_authority,
                "issue_date": cert.issue_date,
                "expiry_date": cert.expiry_date,
                "status": cert.status,
                "requirements": cert.requirements,
                "documents": cert.documents,
                "created_at": cert.created_at,
                "updated_at": cert.updated_at
            }
            return cert_dict
        except Exception as e:
            print(f"Error retrieving certification with ID {cert_id}: {e}")
            return None

def create_certification(
    cert_number,
    cert_type,
    issuing_authority,
    issue_date,
    expiry_date,
    status="Active",
    product_id=None,
    material_id=None,
    requirements=None,
    documents=None
):
    """Create a new certification in the database."""
    with get_db_session() as session:
        try:
            # Create the certification
            new_cert = Certification(
                cert_number=cert_number,
                cert_type=cert_type,
                product_id=product_id,
                material_id=material_id,
                issuing_authority=issuing_authority,
                issue_date=issue_date,
                expiry_date=expiry_date,
                status=status,
                requirements=requirements,
                documents=documents or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(new_cert)
            session.commit()

            return True
        except IntegrityError as e:
            session.rollback()
            print(f"IntegrityError creating certification: {str(e)}")
            return False
        except Exception as e:
            session.rollback()
            print(f"Error creating certification: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def update_certification(cert_id, cert_data):
    """Update an existing certification in the database."""
    with get_db_session() as session:
        try:
            cert = session.query(Certification).filter(Certification.id == cert_id).first()

            if not cert:
                return False

            # Update certification properties
            if "cert_number" in cert_data:
                cert.cert_number = cert_data["cert_number"]
            if "cert_type" in cert_data:
                cert.cert_type = cert_data["cert_type"]
            if "product_id" in cert_data:
                cert.product_id = cert_data["product_id"]
            if "material_id" in cert_data:
                cert.material_id = cert_data["material_id"]
            if "issuing_authority" in cert_data:
                cert.issuing_authority = cert_data["issuing_authority"]
            if "issue_date" in cert_data:
                cert.issue_date = cert_data["issue_date"]
            if "expiry_date" in cert_data:
                cert.expiry_date = cert_data["expiry_date"]
            if "status" in cert_data:
                cert.status = cert_data["status"]
            if "requirements" in cert_data:
                cert.requirements = cert_data["requirements"]
            if "documents" in cert_data:
                cert.documents = cert_data["documents"]
            
            # Always update the updated_at timestamp
            cert.updated_at = datetime.utcnow()

            session.commit()

            return True
        except IntegrityError:
            session.rollback()
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating certification: {str(e)}")
            return False

def delete_certification(cert_id):
    """Delete a certification from the database."""
    with get_db_session() as session:
        try:
            cert = session.query(Certification).filter(Certification.id == cert_id).first()

            if not cert:
                return False

            session.delete(cert)
            session.commit()

            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting certification: {str(e)}")
            return False

# Add this function to certification_service.py
def get_all_products(status=None):
    """Get all products with optional filtering specifically for certification page"""
    with get_db_session() as session:
        query = session.query(Product)
        
        if status:
            if isinstance(status, list):
                query = query.filter(Product.status.in_(status))
            else:
                query = query.filter(Product.status == status)
                
        products = query.all()
        product_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "name": getattr(product, "name", f"Product {product.id}"),
                "status": getattr(product, "status", "Active")
            }
            product_list.append(product_dict)
            
        return product_list

def load_sample_certifications():
    """Load sample certification data from CSV file for dashboard display"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '../../data/sample_certifications.csv')
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            # Return default sample data if no CSV file found
            return [
                {"id": 1, "cert_number": "ISO9001-2024-001", "cert_type": "ISO 9001:2015", "status": "Active", "issuing_authority": "ISO International"},
                {"id": 2, "cert_number": "FDA-510K-2024-002", "cert_type": "FDA 510(k)", "status": "Active", "issuing_authority": "U.S. Food and Drug Administration"},
                {"id": 3, "cert_number": "AS9100D-2024-003", "cert_type": "AS9100 Rev D", "status": "Active", "issuing_authority": "SAE International"}
            ]
        
        # Convert DataFrame to list of dictionaries
        certifications = df.to_dict('records')
        
        # Convert date strings to proper format if present
        for cert in certifications:
            if 'issue_date' in cert and pd.notna(cert['issue_date']):
                try:
                    cert['issue_date'] = pd.to_datetime(cert['issue_date']).strftime('%Y-%m-%d')
                except:
                    pass
            if 'expiry_date' in cert and pd.notna(cert['expiry_date']):
                try:
                    cert['expiry_date'] = pd.to_datetime(cert['expiry_date']).strftime('%Y-%m-%d')
                except:
                    pass
            # Parse JSON documents if present
            if 'documents' in cert and pd.notna(cert['documents']):
                try:
                    cert['documents'] = json.loads(cert['documents'])
                except:
                    cert['documents'] = {}
                    
        return certifications
        
    except Exception as e:
        print(f"Error loading sample certifications: {e}")
        # Return basic fallback data
        return [
            {"id": 1, "cert_number": "ISO9001-2024-001", "cert_type": "ISO 9001:2015", "status": "Active"},
            {"id": 2, "cert_number": "FDA-510K-2024-002", "cert_type": "FDA 510(k)", "status": "Active"},
            {"id": 3, "cert_number": "AS9100D-2024-003", "cert_type": "AS9100 Rev D", "status": "Active"}
        ]

# Dashboard-specific functions for app.py

def get_pending_certifications_count() -> int:
    """Get count of pending certifications for dashboard metrics"""
    try:
        with get_db_session() as session:
            count = session.query(Certification).filter(
                Certification.status.in_(['Pending', 'In Review', 'Submitted'])
            ).count()
            return count
    except Exception as e:
        print(f"Error getting pending certifications count: {e}")
        return 0