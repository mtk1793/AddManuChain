"""
Services module initialization.
This module contains business logic for interacting with the database.
"""

# Import service functions for easier importing elsewhere
from src.services.material_service import (
    get_all_materials,
    # Other material service functions...
)

from src.services.auth_service import (
    authenticate_user,
    get_all_users,
    get_user_by_id,
    # Other auth service functions...
)

from src.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    get_product_categories,
    get_oems,
)

# Add more imports as needed

# This allows imports like: from src.services import get_all_materials
__all__ = [
    'get_all_materials',
    'authenticate_user',
    'get_all_users',
    'get_user_by_id',
    'get_all_products',
    'get_product_by_id',
    'create_product',
    'update_product',
    'delete_product',
    'get_product_categories',
    'get_oems',
    # Add all other function names you want to expose
]

