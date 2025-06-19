# src/services/device_service.py
from datetime import datetime
import pandas as pd
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func # Import func
from src.db.connection import get_db_session
from src.db.models.device import Device, MaintenanceRecord
from src.db.models.print_job import PrintJob


def load_sample_devices():
    """Load sample device data from CSV file for dashboard display"""
    try:
        # Try enhanced data first, fall back to basic sample data
        enhanced_path = os.path.join(os.path.dirname(__file__), '../../data/enhanced_devices.csv')
        basic_path = os.path.join(os.path.dirname(__file__), '../../data/sample_devices.csv')
        
        if os.path.exists(enhanced_path):
            df = pd.read_csv(enhanced_path)
        elif os.path.exists(basic_path):
            df = pd.read_csv(basic_path)
        else:
            # Return default sample data if no CSV files found
            return [
                {"id": 1, "name": "3D Printer Alpha", "device_type": "FDM Printer", "model": "ProPrint X300", "status": "Active", "location": "Lab A"},
                {"id": 2, "name": "3D Printer Beta", "device_type": "SLA Printer", "model": "ResinCraft Pro", "status": "Maintenance", "location": "Lab A"},
                {"id": 3, "name": "CNC Machine Delta", "device_type": "CNC Mill", "model": "PrecisionCut 2000", "status": "Active", "location": "Workshop A"}
            ]
        
        # Convert DataFrame to list of dictionaries
        devices = df.to_dict('records')
        
        # Convert date strings to proper format if present
        for device in devices:
            if 'acquisition_date' in device and pd.notna(device['acquisition_date']):
                try:
                    device['acquisition_date'] = pd.to_datetime(device['acquisition_date']).strftime('%Y-%m-%d')
                except:
                    pass
            if 'last_maintenance_date' in device and pd.notna(device['last_maintenance_date']):
                try:
                    device['last_maintenance_date'] = pd.to_datetime(device['last_maintenance_date']).strftime('%Y-%m-%d')
                except:
                    pass
                    
        return devices
        
    except Exception as e:
        print(f"Error loading sample devices: {e}")
        # Return basic fallback data
        return [
            {"id": 1, "name": "3D Printer Alpha", "device_type": "FDM Printer", "status": "Active"},
            {"id": 2, "name": "3D Printer Beta", "device_type": "SLA Printer", "status": "Maintenance"},
            {"id": 3, "name": "CNC Machine Delta", "device_type": "CNC Mill", "status": "Active"}
        ]


def get_all_devices(db=None, status=None, device_type=None, location=None):
    """Get all devices with optional filtering"""
    # If a session was not provided, create one
    if db is None:
        with get_db_session() as session:
            query = session.query(Device)
            
            # Fix the filtering logic
            if status:
                # Check if status is a list to use the correct operator
                if isinstance(status, list):
                    query = query.filter(Device.status.in_(status))
                else:
                    query = query.filter(Device.status == status)
            
            if device_type:
                # Check if device_type is a list
                if isinstance(device_type, list):
                    query = query.filter(Device.device_type.in_(device_type))
                else:
                    query = query.filter(Device.device_type == device_type)
                
            if location:
                # Check if location is a list
                if isinstance(location, list):
                    query = query.filter(Device.location.in_(location))
                else:
                    query = query.filter(Device.location == location)
            
            # Convert to dictionaries to prevent DetachedInstanceError
            devices = query.all()
            device_list = []
            for device in devices:
                device_dict = {
                    "id": device.id,
                    "name": device.name,
                    "device_type": device.device_type,
                    "model": device.model,
                    "serial_number": device.serial_number,
                    "location": device.location,
                    "status": device.status,
                    "acquisition_date": device.acquisition_date,
                    "last_maintenance_date": device.last_maintenance_date,
                    "next_maintenance_date": device.next_maintenance_date,
                    "manager_id": device.manager_id,
                    "notes": device.notes,
                    "created_at": device.created_at,
                    "updated_at": device.updated_at
                }
                device_list.append(device_dict)
            
            return device_list
    else:
        # If a session was provided, use it directly
        query = db.query(Device)
        
        # Use the same fixed filtering logic here
        if status:
            if isinstance(status, list):
                query = query.filter(Device.status.in_(status))
            else:
                query = query.filter(Device.status == status)
        
        if device_type:
            if isinstance(device_type, list):
                query = query.filter(Device.device_type.in_(device_type))
            else:
                query = query.filter(Device.device_type == device_type)
            
        if location:
            if isinstance(location, list):
                query = query.filter(Device.location.in_(location))
            else:
                query = query.filter(Device.location == location)
        
        return query.all()


def get_device_by_id(device_id):
    """Get a device by its ID."""
    with get_db_session() as session:
        try:
            device = session.query(Device).filter(Device.id == device_id).first()
            
            if not device:
                return None
                
            # Convert to dictionary to avoid DetachedInstanceError
            device_dict = {
                "id": device.id,
                "name": device.name,
                "device_type": device.device_type,
                "model": device.model,
                "serial_number": device.serial_number,
                "location": device.location,
                "status": device.status,
                "acquisition_date": device.acquisition_date,
                "last_maintenance_date": device.last_maintenance_date,
                "next_maintenance_date": device.next_maintenance_date,
                "manager_id": device.manager_id,
                "notes": device.notes,
                "created_at": device.created_at,
                "updated_at": device.updated_at
            }
            return device_dict
        except Exception as e:
            return None


def create_device(
    name,
    device_type,
    model,
    serial_number,
    location=None,
    status="Active",
    acquisition_date=None,
    last_maintenance_date=None,
    next_maintenance_date=None,
    manager_id=None,
    notes=None,
):
    """Create a new device in the database."""
    with get_db_session() as session:
        try:
            # Create the device
            new_device = Device(
                name=name,
                device_type=device_type,
                model=model,
                serial_number=serial_number,
                location=location,
                status=status,
                acquisition_date=acquisition_date,
                last_maintenance_date=last_maintenance_date,
                next_maintenance_date=next_maintenance_date,
                manager_id=manager_id,
                notes=notes,
                created_at=datetime.utcnow(),
            )

            session.add(new_device)
            session.commit()

            return True
        except IntegrityError:
            session.rollback()
            return False
        except Exception as e:
            session.rollback()
            return False


def update_device(device_id, device_data):
    """Update an existing device in the database."""
    with get_db_session() as session:
        try:
            device = session.query(Device).filter(Device.id == device_id).first()

            if not device:
                return False

            # Update device properties
            if "name" in device_data:
                device.name = device_data["name"]
            if "device_type" in device_data:
                device.device_type = device_data["device_type"]
            if "model" in device_data:
                device.model = device_data["model"]
            if "serial_number" in device_data:
                device.serial_number = device_data["serial_number"]
            if "location" in device_data:
                device.location = device_data["location"]
            if "status" in device_data:
                device.status = device_data["status"]
            if "acquisition_date" in device_data:
                device.acquisition_date = device_data["acquisition_date"]
            if "last_maintenance_date" in device_data:
                device.last_maintenance_date = device_data["last_maintenance_date"]
            if "next_maintenance_date" in device_data:
                device.next_maintenance_date = device_data["next_maintenance_date"]
            if "manager_id" in device_data:
                device.manager_id = device_data["manager_id"]
            if "notes" in device_data:
                device.notes = device_data["notes"]

            session.commit()

            return True
        except IntegrityError:
            session.rollback()
            return False
        except Exception as e:
            session.rollback()
            return False


def delete_device(device_id):
    """Delete a device from the database."""
    with get_db_session() as session:
        try:
            device = session.query(Device).filter(Device.id == device_id).first()

            if not device:
                return False

            try:
                # First try to delete maintenance records if they exist
                if hasattr(device, 'maintenance_records'):
                    maintenance_records = session.query(MaintenanceRecord).filter(MaintenanceRecord.device_id == device_id).all()
                    for record in maintenance_records:
                        session.delete(record)
                
                # Try to delete print jobs if they exist
                if hasattr(device, 'print_jobs'):
                    print_jobs = session.query(PrintJob).filter(PrintJob.device_id == device_id).all()
                    for job in print_jobs:
                        session.delete(job)
            except Exception as inner_e:
                print(f"Warning while deleting device relationships: {inner_e}")
                # Continue with device deletion even if relationship deletion fails
                
            # Now delete the device itself
            session.delete(device)
            session.commit()

            return True
        except Exception as e:
            print(f"Error deleting device: {e}")  # Add logging for debugging
            session.rollback()
            return False

# --- ADDED FUNCTION: get_total_devices ---
def get_total_devices():
    """Get the total number of devices in the database."""
    with get_db_session() as session:
        try:
            return session.query(Device).count()
        except Exception as e:
            print(f"Error counting devices: {e}")
            return 0 # Return 0 in case of an error

def get_device_status_distribution():
    """Get the distribution of devices by status."""
    with get_db_session() as session:
        try:
            # Query the database for the count of devices in each status
            status_counts = session.query(Device.status, func.count(Device.id)).group_by(Device.status).all()
            
            # Convert the result to a dictionary
            status_distribution = {status: count for status, count in status_counts}
            
            return status_distribution
        except Exception as e:
            print(f"Error getting device status distribution: {e}")
            return {}

def get_device_type_distribution():
    """Get the distribution of devices by type."""
    with get_db_session() as session:
        try:
            # Query the database for the count of devices in each type
            type_counts = session.query(Device.device_type, func.count(Device.id)).group_by(Device.device_type).all()
            
            # Convert the result to a list of tuples for easier processing
            return [(device_type, count) for device_type, count in type_counts]
        except Exception as e:
            print(f"Error getting device type distribution: {e}")
            return []
