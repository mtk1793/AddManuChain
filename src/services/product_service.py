"""
Product service module for handling product-related operations.
"""
from typing import List, Dict, Optional, Union, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.db.models.product import Product, ProductCategory, OEM, product_certification


def get_all_products(
    db: Session, 
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    designer_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Product]:
    """
    Get all products with optional filtering
    
    Args:
        db: Database session
        status: Optional filter by product status
        category_id: Optional filter by category ID
        designer_id: Optional filter by designer ID
        min_price: Optional minimum price filter
        max_price: Optional maximum price filter
        
    Returns:
        List of Product objects matching the criteria
    """
    query = db.query(Product)
    
    # Apply filters if provided
    if status:
        query = query.filter(Product.status == status)
        
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    if designer_id:
        query = query.filter(Product.designer_id == designer_id)
        
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
        
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    return query.order_by(Product.name).all()


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """
    Get a product by its ID
    
    Args:
        db: Database session
        product_id: ID of the product to retrieve
        
    Returns:
        Product object if found, None otherwise
    """
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product_data: Dict[str, Any]) -> Optional[Product]:
    """
    Create a new product in the database
    
    Args:
        db: Database session
        product_data: Dictionary containing product data
        
    Returns:
        Newly created Product object, or None if creation failed
    """
    try:
        # Create new product object
        new_product = Product(
            name=product_data.get("name"),
            description=product_data.get("description"),
            product_code=product_data.get("product_code"),
            price=product_data.get("price"),
            status=product_data.get("status", "In Development"),
            designer_id=product_data.get("designer_id"),
            creator_id=product_data.get("creator_id"),
            category_id=product_data.get("category_id"),
            oem_id=product_data.get("oem_id"),
            blueprint_id=product_data.get("blueprint_id"),
            specifications=product_data.get("specifications", {}),
            dimensions=product_data.get("dimensions"),
            weight=product_data.get("weight"),
            materials_used=product_data.get("materials_used"),
            assembly_instructions=product_data.get("assembly_instructions"),
            image_url=product_data.get("image_url")
        )
        
        # Add to database
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {str(e)}")
        return None


def update_product(db: Session, product_id: int, product_data: Dict[str, Any]) -> Optional[Product]:
    """
    Update an existing product
    
    Args:
        db: Database session
        product_id: ID of the product to update
        product_data: Dictionary containing updated product data
        
    Returns:
        Updated Product object, or None if update failed
    """
    try:
        # Get existing product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
            
        # Update fields
        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        # Commit changes
        db.commit()
        db.refresh(product)
        
        return product
    except Exception as e:
        db.rollback()
        print(f"Error updating product: {str(e)}")
        return None


def delete_product(db: Session, product_id: int) -> bool:
    """
    Delete a product from the database
    
    Args:
        db: Database session
        product_id: ID of the product to delete
        
    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return False
            
        # Delete product
        db.delete(product)
        db.commit()
        
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {str(e)}")
        return False


def get_product_categories(db: Session) -> List[ProductCategory]:
    """
    Get all product categories
    
    Args:
        db: Database session
        
    Returns:
        List of ProductCategory objects
    """
    return db.query(ProductCategory).order_by(ProductCategory.name).all()


def get_oems(db: Session) -> List[OEM]:
    """
    Get all OEMs
    
    Args:
        db: Database session
        
    Returns:
        List of OEM objects
    """
    return db.query(OEM).order_by(OEM.name).all()