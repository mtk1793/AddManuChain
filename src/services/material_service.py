"""
Material Service - Handles all operations related to materials in the database.
This module provides functions for creating, retrieving, updating, and deleting
materials, as well as managing inventory levels and material certifications.
"""

from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, asc, func, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
import pandas as pd
import os

from src.db.connection import get_db_session
from src.db.models.material import Material, MaterialCategory, MaterialCertification, StockAdjustment

def get_all_materials(status=None, material_type=None, location=None, supplier_id=None):
    """Get all materials with optional filtering"""
    with get_db_session() as session:
        query = session.query(Material)
        
        # Fix the filtering logic for lists
        if status:
            if isinstance(status, list):
                query = query.filter(Material.status.in_(status))
            else:
                query = query.filter(Material.status == status)
        
        if material_type:
            if isinstance(material_type, list):
                query = query.filter(Material.material_type.in_(material_type))
            else:
                query = query.filter(Material.material_type == material_type)
            
        if location:
            if isinstance(location, list):
                query = query.filter(Material.storage_location.in_(location))
            else:
                query = query.filter(Material.storage_location == location)
                
        if supplier_id:
            query = query.filter(Material.supplier_id == supplier_id)

        # Convert to dictionaries to prevent DetachedInstanceError
        materials = query.all()
        material_list = []
        for material in materials:
            material_dict = {
                "id": material.id,
                "name": material.name,
                "description": material.description,
                "type": getattr(material, "type", None),
                "material_type": material.material_type,
                "supplier_id": material.supplier_id,
                "category_id": material.category_id,
                "stock_quantity": material.stock_quantity,
                "current_stock": getattr(material, "current_stock", None),
                "unit": material.unit,
                "unit_of_measure": getattr(material, "unit_of_measure", None),
                "price_per_unit": material.price_per_unit,
                "cost_per_unit": getattr(material, "cost_per_unit", None),
                "min_stock_level": material.min_stock_level,
                "reorder_level": getattr(material, "reorder_level", None),
                "location": getattr(material, "location", None),
                "storage_location": material.storage_location,
                "expiration_date": material.expiration_date,
                "manager_id": material.manager_id,
                "status": material.status,
                "is_active": material.is_active,
                "properties": material.properties,
                "created_at": material.created_at,
                "updated_at": material.updated_at
            }
            material_list.append(material_dict)
            
        return material_list

def get_material_by_id(material_id: int) -> dict:
    """
    Retrieve a specific material by its ID and return as a dictionary.
    
    Args:
        material_id: The ID of the material to retrieve
        
    Returns:
        dict: Material data if found, None otherwise
    """
    try:
        with get_db_session() as session:
            material = session.query(Material).filter(Material.id == material_id).first()
            if material:
                return {
                    "id": material.id,
                    "name": material.name,
                    "material_type": material.material_type,
                    "supplier_id": material.supplier_id,
                    "category_id": material.category_id,
                    "stock_quantity": material.stock_quantity,
                    "unit": material.unit,
                    "price_per_unit": material.price_per_unit,
                    "min_stock_level": material.min_stock_level,
                    "storage_location": material.storage_location,
                    "location": material.location,
                    "expiration_date": material.expiration_date,
                    "manager_id": material.manager_id,
                    "status": material.status,
                    "description": material.description,
                    "properties": material.properties,
                    "created_at": material.created_at,
                    "updated_at": material.updated_at,
                }
            return None
    except Exception as e:
        print(f"Error retrieving material with ID {material_id}: {e}")
        return None

def create_material(
    name,
    material_type,
    supplier_id=None,
    category_id=None,
    stock_quantity=0,
    unit=None,
    price_per_unit=None,
    min_stock_level=None,
    storage_location=None,
    location=None,
    expiration_date=None,
    manager_id=None,
    status="Available",
    description=None,
    properties=None,
    type=None,
):
    """Create a new material in the database."""
    if not name or name.strip() == "":
        print("Error: Material name is required")
        return False

    if location and not storage_location:
        storage_location = location
        
    if type is None:
        type = material_type
        
    with get_db_session() as session:
        try:
            # Create the material
            new_material = Material(
                name=name,
                description=description,
                type=type,
                material_type=material_type,
                supplier_id=supplier_id,
                category_id=category_id,
                stock_quantity=float(stock_quantity) if stock_quantity else 0.0,
                current_stock=float(stock_quantity) if stock_quantity else 0.0,  # Set current_stock to initial stock_quantity
                unit=unit,
                unit_of_measure=unit,
                price_per_unit=float(price_per_unit) if price_per_unit else 0.0,
                min_stock_level=float(min_stock_level) if min_stock_level else 0.0,
                reorder_level=float(min_stock_level) * 2 if min_stock_level else 10.0,  # Set reorder level based on min_stock_level
                storage_location=storage_location,
                expiration_date=expiration_date,
                manager_id=manager_id,
                status=status,
                is_active=True,
                properties={} if not properties else properties,  # Use empty dict instead of None
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),  # Add updated_at
            )

            session.add(new_material)
            session.commit()

            return True
        except IntegrityError as e:
            session.rollback()
            print(f"IntegrityError creating material: {str(e)}")
            if hasattr(e, 'orig') and hasattr(e.orig, 'diag'):
                print(f"Detail: {e.orig.diag.message_detail}")
            return False
        except Exception as e:
            session.rollback()
            print(f"Error creating material: {str(e)}")
            # Print traceback for debugging
            import traceback
            traceback.print_exc()
            return False
def update_material(material_id: int, data: Dict) -> bool:
    """
    Update an existing material in the database.
    
    Args:
        material_id: ID of the material to update
        data: Dictionary of fields to update
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        with get_db_session() as session:
            material = session.query(Material).filter(Material.id == material_id).first()
            if not material:
                return False
            
            # Track if stock changed to create adjustment record
            old_stock = material.current_stock
            
            # Update fields from data dictionary
            for key, value in data.items():
                if hasattr(material, key):
                    setattr(material, key, value)
            
            # Create stock adjustment record if stock changed
            if 'current_stock' in data and data['current_stock'] != old_stock:
                adjustment = StockAdjustment(
                    material_id=material_id,
                    adjustment_date=datetime.now(),
                    quantity=data['current_stock'] - old_stock,
                    adjustment_type="Manual Adjustment",
                    notes=data.get('adjustment_notes', 'Stock updated through admin interface'),
                    unit_cost=material.cost_per_unit
                )
                session.add(adjustment)
            
            material.updated_at = datetime.now()
            session.commit()
            return True
    except Exception as e:
        print(f"Error updating material {material_id}: {e}")
        return False

def delete_material(material_id: int) -> bool:
    """
    Delete a material from the database (soft delete).
    
    Args:
        material_id: ID of the material to delete
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        with get_db_session() as session:
            material = session.query(Material).filter(Material.id == material_id).first()
            if not material:
                return False
            
            # Soft delete by setting is_active to False
            material.is_active = False
            material.updated_at = datetime.now()
            session.commit()
            return True
    except Exception as e:
        print(f"Error deleting material {material_id}: {e}")
        return False

def adjust_material_stock(
    material_id: int, 
    quantity: float,
    adjustment_type: str, 
    notes: Optional[str] = None,
    unit_cost: Optional[float] = None
) -> bool:
    """
    Adjust the stock level of a material.
    
    Args:
        material_id: ID of the material
        quantity: Amount to adjust (positive for additions, negative for removals)
        adjustment_type: Type of adjustment (e.g., "Purchase", "Usage", "Write-off")
        notes: Optional notes about the adjustment
        unit_cost: Cost per unit for this adjustment (for inventory valuation)
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        with get_db_session() as session:
            material = session.query(Material).filter(Material.id == material_id).first()
            if not material:
                return False
            
            # Update the stock level
            material.current_stock += quantity
            
            # Create a stock adjustment record
            adjustment = StockAdjustment(
                material_id=material_id,
                adjustment_date=datetime.now(),
                quantity=quantity,
                adjustment_type=adjustment_type,
                notes=notes,
                unit_cost=unit_cost if unit_cost is not None else material.cost_per_unit
            )
            session.add(adjustment)
            
            material.updated_at = datetime.now()
            session.commit()
            return True
    except Exception as e:
        print(f"Error adjusting stock for material {material_id}: {e}")
        return False

def get_low_stock_materials() -> List[Material]:
    """
    Get all materials that are at or below their reorder level.
    
    Returns:
        List of material objects that need reordering
    """
    try:
        with get_db_session() as session:
            low_stock_materials = (
                session.query(Material)
                .filter(Material.current_stock <= Material.reorder_level)
                .filter(Material.is_active == True)
                .order_by(asc(Material.current_stock / Material.reorder_level))
                .all()
            )
            return low_stock_materials
    except Exception as e:
        print(f"Error retrieving low stock materials: {e}")
        return []

def search_materials(search_term: str) -> List[Material]:
    """
    Search for materials by name, type, or description.
    
    Args:
        search_term: The term to search for
        
    Returns:
        List of material objects matching the search criteria
    """
    try:
        with get_db_session() as session:
            search_pattern = f"%{search_term}%"
            materials = (
                session.query(Material)
                .filter(
                    or_(
                        Material.name.ilike(search_pattern),
                        Material.material_type.ilike(search_pattern),
                        Material.description.ilike(search_pattern)
                    )
                )
                .order_by(Material.name)
                .all()
            )
            return materials
    except Exception as e:
        print(f"Error searching materials: {e}")
        return []

def get_material_history(material_id: int) -> List[StockAdjustment]:
    """
    Get the stock adjustment history for a material.
    
    Args:
        material_id: ID of the material
        
    Returns:
        List of stock adjustment records ordered by date (newest first)
    """
    try:
        with get_db_session() as session:
            history = (
                session.query(StockAdjustment)
                .filter(StockAdjustment.material_id == material_id)
                .order_by(desc(StockAdjustment.adjustment_date))
                .all()
            )
            return history
    except Exception as e:
        print(f"Error retrieving history for material {material_id}: {e}")
        return []

def get_materials_by_category(category_id: int) -> List[Material]:
    """
    Get all materials in a specific category.
    
    Args:
        category_id: ID of the category
        
    Returns:
        List of material objects in that category
    """
    try:
        with get_db_session() as session:
            materials = (
                session.query(Material)
                .filter(Material.category_id == category_id)
                .filter(Material.is_active == True)
                .order_by(Material.name)
                .all()
            )
            return materials
    except Exception as e:
        print(f"Error retrieving materials for category {category_id}: {e}")
        return []

def get_all_categories() -> List[MaterialCategory]:
    """
    Get all material categories.
    
    Returns:
        List of all material category objects
    """
    try:
        with get_db_session() as session:
            categories = (
                session.query(MaterialCategory)
                .order_by(MaterialCategory.name)
                .all()
            )
            return categories
    except Exception as e:
        print(f"Error retrieving material categories: {e}")
        return []

def create_category(name: str, description: Optional[str] = None) -> Tuple[bool, Optional[int]]:
    """
    Create a new material category.
    
    Args:
        name: Name of the category
        description: Optional description
        
    Returns:
        Tuple of (success_boolean, category_id_if_successful)
    """
    try:
        with get_db_session() as session:
            # Check if category already exists
            existing = session.query(MaterialCategory).filter(
                func.lower(MaterialCategory.name) == func.lower(name)
            ).first()
            
            if existing:
                return False, None
            
            new_category = MaterialCategory(
                name=name,
                description=description
            )
            session.add(new_category)
            session.commit()
            return True, new_category.id
    except Exception as e:
        print(f"Error creating category: {e}")
        return False, None

def add_material_certification(
    material_id: int,
    certification_type: str,
    issuer: str,
    issue_date: datetime,
    expiry_date: Optional[datetime] = None,
    certification_number: Optional[str] = None,
    notes: Optional[str] = None,
    document_url: Optional[str] = None
) -> bool:
    """
    Add a certification to a material.
    
    Args:
        material_id: ID of the material
        certification_type: Type of certification
        issuer: Organization issuing the certification
        issue_date: Date when certification was issued
        expiry_date: Date when certification expires (if applicable)
        certification_number: Unique number for the certification
        notes: Additional notes about the certification
        document_url: URL to the certification document
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        with get_db_session() as session:
            # Check if material exists
            material = session.query(Material).get(material_id)
            if not material:
                return False
                
            certification = MaterialCertification(
                material_id=material_id,
                certification_type=certification_type,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=expiry_date,
                certification_number=certification_number,
                notes=notes,
                document_url=document_url,
                status="Active"
            )
            
            session.add(certification)
            session.commit()
            return True
    except Exception as e:
        print(f"Error adding certification for material {material_id}: {e}")
        return False

def get_material_certifications(material_id: int) -> List[MaterialCertification]:
    """
    Get all certifications for a specific material.
    
    Args:
        material_id: ID of the material
        
    Returns:
        List of certification objects for the material
    """
    try:
        with get_db_session() as session:
            certifications = (
                session.query(MaterialCertification)
                .filter(MaterialCertification.material_id == material_id)
                .order_by(desc(MaterialCertification.issue_date))
                .all()
            )
            return certifications
    except Exception as e:
        print(f"Error retrieving certifications for material {material_id}: {e}")
        return []

def get_expiring_certifications(days: int = 30) -> List[Dict]:
    """
    Get certifications that will expire within the specified number of days.
    
    Args:
        days: Number of days to look ahead
        
    Returns:
        List of certification objects that are expiring soon
    """
    try:
        with get_db_session() as session:
            today = datetime.now().date()
            expiry_cutoff = today + timedelta(days=days)
            
            result = (
                session.query(
                    MaterialCertification, 
                    Material.name.label("material_name")
                )
                .join(Material, MaterialCertification.material_id == Material.id)
                .filter(
                    MaterialCertification.expiry_date <= expiry_cutoff,
                    MaterialCertification.expiry_date >= today,
                    MaterialCertification.status == "Active"
                )
                .order_by(asc(MaterialCertification.expiry_date))
                .all()
            )
            
            # Format the results
            expiring_certs = []
            for cert, material_name in result:
                expiring_certs.append({
                    "id": cert.id,
                    "material_id": cert.material_id,
                    "material_name": material_name,
                    "certification_type": cert.certification_type,
                    "issuer": cert.issuer,
                    "expiry_date": cert.expiry_date,
                    "days_remaining": (cert.expiry_date - today).days
                })
                
            return expiring_certs
    except Exception as e:
        print(f"Error retrieving expiring certifications: {e}")
        return []

def get_material_usage_stats(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
    """
    Get statistics on material usage during the specified period.
    
    Args:
        start_date: Starting date for the statistics (optional)
        end_date: Ending date for the statistics (optional)
        
    Returns:
        List of dictionaries with material usage statistics
    """
    try:
        with get_db_session() as session:
            # Set default dates if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
                
            # Query for usage (negative adjustments)
            usage_query = (
                session.query(
                    StockAdjustment.material_id,
                    func.sum(StockAdjustment.quantity * -1).label("usage_amount"),
                    func.sum(StockAdjustment.quantity * StockAdjustment.unit_cost * -1).label("usage_cost")
                )
                .filter(
                    StockAdjustment.adjustment_date.between(start_date, end_date),
                    StockAdjustment.quantity < 0,  # Only count usage (negative adjustments)
                    StockAdjustment.adjustment_type != "Write-off"  # Don't count write-offs as usage
                )
                .group_by(StockAdjustment.material_id)
            )
            
            # Join with materials table to get names
            results = (
                session.query(
                    Material.id,
                    Material.name,
                    Material.material_type,
                    Material.unit_of_measure,
                    Material.current_stock,
                    usage_query.c.usage_amount,
                    usage_query.c.usage_cost
                )
                .join(
                    usage_query, 
                    Material.id == usage_query.c.material_id
                )
                .order_by(desc(usage_query.c.usage_amount))
                .all()
            )
            
            # Format the results
            usage_stats = []
            for row in results:
                usage_stats.append({
                    "material_id": row.id,
                    "material_name": row.name,
                    "material_type": row.material_type,
                    "unit": row.unit_of_measure,
                    "current_stock": row.current_stock,
                    "usage_amount": abs(row.usage_amount) if row.usage_amount else 0,
                    "usage_cost": abs(row.usage_cost) if row.usage_cost else 0
                })
                
            return usage_stats
    except Exception as e:
        print(f"Error retrieving material usage statistics: {e}")
        return []

def load_sample_materials():
    """Load sample material data from CSV file for dashboard display"""
    try:
        # Try enhanced data first, fall back to basic sample data
        enhanced_path = os.path.join(os.path.dirname(__file__), '../../data/enhanced_materials.csv')
        basic_path = os.path.join(os.path.dirname(__file__), '../../data/sample_materials.csv')
        
        if os.path.exists(enhanced_path):
            df = pd.read_csv(enhanced_path)
        elif os.path.exists(basic_path):
            df = pd.read_csv(basic_path)
        else:
            # Return default sample data if no CSV files found
            return [
                {"id": 1, "name": "PLA Natural", "type": "Polymer", "stock_quantity": 50.5, "status": "Available"},
                {"id": 2, "name": "ABS Black", "type": "Polymer", "stock_quantity": 30.2, "status": "Available"},
                {"id": 3, "name": "Standard Resin Clear", "type": "Photopolymer", "stock_quantity": 15.3, "status": "Available"}
            ]
        
        # Convert DataFrame to list of dictionaries
        materials = df.to_dict('records')
        
        # Convert date strings to proper format if present
        for material in materials:
            if 'expiration_date' in material and pd.notna(material['expiration_date']):
                try:
                    material['expiration_date'] = pd.to_datetime(material['expiration_date']).strftime('%Y-%m-%d')
                except:
                    pass
                    
        return materials
        
    except Exception as e:
        print(f"Error loading sample materials: {e}")
        # Return basic fallback data
        return [
            {"id": 1, "name": "PLA Natural", "type": "Polymer", "stock_quantity": 50.5},
            {"id": 2, "name": "ABS Black", "type": "Polymer", "stock_quantity": 30.2},
            {"id": 3, "name": "Standard Resin Clear", "type": "Photopolymer", "stock_quantity": 15.3}
        ]

# Dashboard-specific functions for app.py

def get_active_materials_count() -> int:
    """Get count of active materials for dashboard metrics"""
    try:
        with get_db_session() as session:
            count = session.query(Material).filter(
                Material.is_active == True,
                Material.status.in_(['Available', 'Low'])
            ).count()
            return count
    except Exception as e:
        print(f"Error getting active materials count: {e}")
        return 0

def get_material_availability() -> List[Tuple[str, float]]:
    """Get material availability data for dashboard charts"""
    try:
        with get_db_session() as session:
            results = session.query(
                Material.name,
                Material.stock_quantity
            ).filter(
                Material.is_active == True,
                Material.stock_quantity > 0
            ).order_by(desc(Material.stock_quantity)).limit(10).all()
            
            return [(name, quantity) for name, quantity in results]
    except Exception as e:
        print(f"Error getting material availability: {e}")
        return []

def get_materials_by_category() -> List[Tuple[str, int]]:
    """Get materials count by category for dashboard charts"""
    try:
        with get_db_session() as session:
            # First try with MaterialCategory if it exists
            try:
                results = session.query(
                    MaterialCategory.name,
                    func.count(Material.id)
                ).join(
                    Material, Material.category_id == MaterialCategory.id
                ).filter(
                    Material.is_active == True
                ).group_by(MaterialCategory.name).all()
                
                if results:
                    return [(category, count) for category, count in results]
            except:
                pass
            
            # Fallback to material_type if categories don't exist
            results = session.query(
                Material.material_type,
                func.count(Material.id)
            ).filter(
                Material.is_active == True,
                Material.material_type.isnot(None)
            ).group_by(Material.material_type).all()
            
            return [(material_type or 'Uncategorized', count) for material_type, count in results]
    except Exception as e:
        print(f"Error getting materials by category: {e}")
        return []

