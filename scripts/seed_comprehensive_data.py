#!/usr/bin/env python3
"""
Database Seeding Script for MITACS Dashboard
This script populates the database with comprehensive sample data from CSV files.
"""

import pandas as pd
import os
import json
from datetime import datetime, date
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.connection import get_db_session
from src.db.models.user import User
from src.db.models.device import Device, MaintenanceRecord
from src.db.models.material import Material
from src.db.models.product import Product
from src.db.models.print_job import PrintJob
from src.db.models.certification import Certification
from src.db.models.quality import QualityInspection
from src.db.models.blueprint import Blueprint
from sqlalchemy.exc import IntegrityError

def load_csv_data(filename):
    """Load data from CSV file in the data directory"""
    csv_path = os.path.join("data", filename)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return []
    else:
        print(f"CSV file not found: {filename}")
        return []

def parse_date(date_str):
    """Parse date string into date object"""
    if pd.isna(date_str) or not date_str:
        return None
    try:
        return datetime.strptime(str(date_str), '%Y-%m-%d').date()
    except:
        try:
            return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S').date()
        except:
            return None

def parse_datetime(datetime_str):
    """Parse datetime string into datetime object"""
    if pd.isna(datetime_str) or not datetime_str:
        return None
    try:
        return datetime.strptime(str(datetime_str), '%Y-%m-%d %H:%M:%S')
    except:
        try:
            return datetime.strptime(str(datetime_str), '%Y-%m-%d')
        except:
            return None

def seed_users():
    """Seed user data"""
    print("Seeding users...")
    users_data = load_csv_data("sample_users.csv")
    
    with get_db_session() as session:
        for user_data in users_data:
            try:
                # Parse preferences JSON
                preferences = {}
                if user_data.get('preferences'):
                    try:
                        preferences = json.loads(user_data['preferences'])
                    except:
                        preferences = {}
                
                user = User(
                    id=user_data.get('id'),
                    username=user_data.get('username'),
                    email=user_data.get('email'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    role=user_data.get('role', 'User'),
                    department=user_data.get('department'),
                    phone=user_data.get('phone'),
                    hire_date=parse_date(user_data.get('hire_date')),
                    status=user_data.get('status', 'Active'),
                    last_login=parse_datetime(user_data.get('last_login')),
                    preferences=preferences,
                    profile_picture=user_data.get('profile_picture')
                )
                session.merge(user)  # Use merge to handle existing records
                
            except Exception as e:
                print(f"Error seeding user {user_data.get('username', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(users_data)} users")
        except Exception as e:
            session.rollback()
            print(f"Error committing users: {e}")

def seed_devices():
    """Seed device data"""
    print("Seeding devices...")
    devices_data = load_csv_data("enhanced_devices.csv")
    
    with get_db_session() as session:
        for device_data in devices_data:
            try:
                device = Device(
                    id=device_data.get('id'),
                    name=device_data.get('name'),
                    device_type=device_data.get('device_type'),
                    model=device_data.get('model'),
                    serial_number=device_data.get('serial_number'),
                    location=device_data.get('location'),
                    status=device_data.get('status', 'Active'),
                    acquisition_date=parse_date(device_data.get('acquisition_date')),
                    last_maintenance_date=parse_date(device_data.get('last_maintenance_date')),
                    next_maintenance_date=parse_date(device_data.get('next_maintenance_date')),
                    manager_id=device_data.get('manager_id'),
                    notes=device_data.get('notes')
                )
                session.merge(device)
                
            except Exception as e:
                print(f"Error seeding device {device_data.get('name', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(devices_data)} devices")
        except Exception as e:
            session.rollback()
            print(f"Error committing devices: {e}")

def seed_materials():
    """Seed material data"""
    print("Seeding materials...")
    materials_data = load_csv_data("enhanced_materials.csv")
    
    with get_db_session() as session:
        for material_data in materials_data:
            try:
                material = Material(
                    id=material_data.get('id'),
                    name=material_data.get('name'),
                    description=material_data.get('description'),
                    type=material_data.get('type'),
                    material_type=material_data.get('material_type'),
                    supplier_id=material_data.get('supplier_id'),
                    category_id=material_data.get('category_id'),
                    stock_quantity=float(material_data.get('stock_quantity', 0)),
                    current_stock=float(material_data.get('current_stock', 0)),
                    unit=material_data.get('unit', 'kg'),
                    unit_of_measure=material_data.get('unit_of_measure', 'kg'),
                    price_per_unit=float(material_data.get('price_per_unit', 0)) if material_data.get('price_per_unit') else None,
                    cost_per_unit=float(material_data.get('cost_per_unit', 0)) if material_data.get('cost_per_unit') else None,
                    min_stock_level=float(material_data.get('min_stock_level', 0)) if material_data.get('min_stock_level') else None,
                    reorder_level=float(material_data.get('reorder_level', 10)),
                    location=material_data.get('location'),
                    storage_location=material_data.get('storage_location'),
                    expiration_date=parse_datetime(material_data.get('expiration_date')),
                    status=material_data.get('status', 'Available')
                )
                session.merge(material)
                
            except Exception as e:
                print(f"Error seeding material {material_data.get('name', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(materials_data)} materials")
        except Exception as e:
            session.rollback()
            print(f"Error committing materials: {e}")

def seed_products():
    """Seed product data"""
    print("Seeding products...")
    products_data = load_csv_data("sample_products.csv")
    
    with get_db_session() as session:
        for product_data in products_data:
            try:
                # Parse specifications if it's a JSON string
                specifications = {}
                if product_data.get('specifications'):
                    try:
                        specifications = json.loads(product_data['specifications'])
                    except:
                        specifications = {}
                
                product = Product(
                    id=product_data.get('id'),
                    name=product_data.get('name'),
                    description=product_data.get('description'),
                    product_code=product_data.get('product_code'),
                    price=float(product_data.get('price', 0)) if product_data.get('price') else None,
                    status=product_data.get('status', 'Active'),
                    designer_id=product_data.get('designer_id'),
                    creator_id=product_data.get('creator_id'),
                    category_id=product_data.get('category_id'),
                    oem_id=product_data.get('oem_id'),
                    blueprint_id=product_data.get('blueprint_id'),
                    specifications=specifications,
                    dimensions=product_data.get('dimensions'),
                    weight=float(product_data.get('weight', 0)) if product_data.get('weight') else None,
                    material_requirements=product_data.get('material_requirements'),
                    manufacturing_time=int(product_data.get('manufacturing_time', 0)) if product_data.get('manufacturing_time') else None,
                    quality_grade=product_data.get('quality_grade')
                )
                session.merge(product)
                
            except Exception as e:
                print(f"Error seeding product {product_data.get('name', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(products_data)} products")
        except Exception as e:
            session.rollback()
            print(f"Error committing products: {e}")

def seed_print_jobs():
    """Seed print job data"""
    print("Seeding print jobs...")
    jobs_data = load_csv_data("sample_print_jobs.csv")
    
    with get_db_session() as session:
        for job_data in jobs_data:
            try:
                print_job = PrintJob(
                    id=job_data.get('id'),
                    name=job_data.get('name'),
                    description=job_data.get('description'),
                    status=job_data.get('status', 'Pending'),
                    user_id=job_data.get('user_id'),
                    device_id=job_data.get('device_id'),
                    material_id=job_data.get('material_id'),
                    file_path=job_data.get('file_path'),
                    start_time=parse_datetime(job_data.get('start_time')),
                    end_time=parse_datetime(job_data.get('end_time')),
                    estimated_duration=float(job_data.get('estimated_duration', 0)) if job_data.get('estimated_duration') else None,
                    actual_duration=float(job_data.get('actual_duration', 0)) if job_data.get('actual_duration') else None,
                    material_used=float(job_data.get('material_used', 0)) if job_data.get('material_used') else None,
                    success=bool(job_data.get('success', False)) if job_data.get('success') != '' else None,
                    failure_reason=job_data.get('failure_reason'),
                    notes=job_data.get('notes'),
                    created_at=parse_datetime(job_data.get('created_at')) or datetime.now(),
                    updated_at=parse_datetime(job_data.get('updated_at')) or datetime.now()
                )
                session.merge(print_job)
                
            except Exception as e:
                print(f"Error seeding print job {job_data.get('name', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(jobs_data)} print jobs")
        except Exception as e:
            session.rollback()
            print(f"Error committing print jobs: {e}")

def seed_certifications():
    """Seed certification data"""
    print("Seeding certifications...")
    certs_data = load_csv_data("sample_certifications.csv")
    
    with get_db_session() as session:
        for cert_data in certs_data:
            try:
                # Parse documents JSON
                documents = {}
                if cert_data.get('documents'):
                    try:
                        documents = json.loads(cert_data['documents'])
                    except:
                        documents = {}
                
                certification = Certification(
                    id=cert_data.get('id'),
                    cert_number=cert_data.get('cert_number'),
                    cert_type=cert_data.get('cert_type'),
                    product_id=cert_data.get('product_id') if cert_data.get('product_id') else None,
                    material_id=cert_data.get('material_id') if cert_data.get('material_id') else None,
                    issuing_authority=cert_data.get('issuing_authority'),
                    issue_date=parse_date(cert_data.get('issue_date')),
                    expiry_date=parse_date(cert_data.get('expiry_date')),
                    status=cert_data.get('status', 'Active'),
                    requirements=cert_data.get('requirements'),
                    documents=documents
                )
                session.merge(certification)
                
            except Exception as e:
                print(f"Error seeding certification {cert_data.get('cert_number', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            print(f"Successfully seeded {len(certs_data)} certifications")
        except Exception as e:
            session.rollback()
            print(f"Error committing certifications: {e}")

def main():
    """Main seeding function"""
    print("Starting database seeding with comprehensive sample data...")
    print("=" * 60)
    
    # Seed data in order of dependencies
    seed_users()
    seed_devices()
    seed_materials()
    seed_products()
    seed_print_jobs()
    seed_certifications()
    
    print("=" * 60)
    print("Database seeding completed!")
    print("\nSample data has been loaded for:")
    print("✓ Users (10 sample users)")
    print("✓ Devices (10 manufacturing devices)")
    print("✓ Materials (15 various materials)")
    print("✓ Products (15 product designs)")
    print("✓ Print Jobs (15 print job records)")
    print("✓ Certifications (15 certifications)")
    print("\nYou can now explore the dashboard with realistic sample data!")

if __name__ == "__main__":
    main()
