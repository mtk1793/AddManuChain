# src/services/maintenance_service.py
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.db.connection import get_db_session
from src.db.models.device import MaintenanceRecord, Device


def get_maintenance_records(
    device_id=None, technician_id=None, status=None, start_date=None, end_date=None
):
    """
    Get maintenance records with optional filters.

    Args:
        device_id (int): Filter by device ID
        technician_id (int): Filter by technician ID
        status (list): Filter by status (Scheduled, In Progress, Completed)
        start_date (date): Filter records from this date
        end_date (date): Filter records to this date

    Returns:
        list: List of MaintenanceRecord objects
    """
    with get_db_session() as session:
        try:
            query = session.query(MaintenanceRecord)

            if device_id:
                query = query.filter(MaintenanceRecord.device_id == device_id)

            if technician_id:
                query = query.filter(MaintenanceRecord.technician_id == technician_id)

            if status:
                query = query.filter(MaintenanceRecord.status.in_(status))

            if start_date:
                query = query.filter(MaintenanceRecord.maintenance_date >= start_date)

            if end_date:
                query = query.filter(MaintenanceRecord.maintenance_date <= end_date)

            records = query.order_by(MaintenanceRecord.maintenance_date.desc()).all()
            # Convert records to dictionaries to avoid DetachedInstanceError
            result = []
            for record in records:
                result.append({
                    "id": record.id,
                    "device_id": record.device_id,
                    "technician_id": record.technician_id,
                    "maintenance_date": record.maintenance_date,
                    "maintenance_type": record.maintenance_type,
                    "description": record.description,
                    "status": record.status,
                    "cost": record.cost,
                    # Add other relevant fields from MaintenanceRecord model here
                })
            return result
        except Exception as e:
            return []


def get_maintenance_record_by_id(record_id):
    """Get a maintenance record by its ID."""
    with get_db_session() as session:
        try:
            record = (
                session.query(MaintenanceRecord)
                .filter(MaintenanceRecord.id == record_id)
                .first()
            )
            
            if not record:
                return None
                
            # Convert to dictionary
            record_dict = {
                "id": record.id,
                "device_id": record.device_id,
                "technician_id": record.technician_id,
                "maintenance_date": record.maintenance_date,
                "maintenance_type": record.maintenance_type,
                "description": record.description,
                "status": record.status,
                "cost": record.cost,
                # Add other fields as needed
            }
            return record_dict
        except Exception as e:
            return None


def schedule_maintenance(
    device_id, technician_id, maintenance_date, maintenance_type, description, status="Scheduled", cost=None
):
    """Schedule a maintenance record for a device."""
    with get_db_session() as session:
        try:
            # Create maintenance record
            new_record = MaintenanceRecord(
                device_id=device_id,
                technician_id=technician_id,
                maintenance_date=maintenance_date,
                maintenance_type=maintenance_type,
                description=description,
                status=status,
                cost=cost,
            )
            
            session.add(new_record)
            
            # Update device's next maintenance date if this is a future maintenance
            if maintenance_date > datetime.now().date():
                device = session.query(Device).filter(Device.id == device_id).first()
                if device:
                    device.next_maintenance_date = maintenance_date
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False


def update_maintenance_record(record_id, record_data):
    """Update an existing maintenance record."""
    with get_db_session() as session:
        try:
            record = (
                session.query(MaintenanceRecord)
                .filter(MaintenanceRecord.id == record_id)
                .first()
            )

            if not record:
                return False

            # Update record properties
            if "maintenance_date" in record_data:
                record.maintenance_date = record_data["maintenance_date"]
            if "maintenance_type" in record_data:
                record.maintenance_type = record_data["maintenance_type"]
            if "description" in record_data:
                record.description = record_data["description"]
            if "parts_replaced" in record_data:
                record.parts_replaced = record_data["parts_replaced"]
            if "cost" in record_data:
                record.cost = record_data["cost"]
            if "status" in record_data:
                record.status = record_data["status"]

                # If the maintenance is completed, update the device's last maintenance date
                if record_data["status"] == "Completed":
                    device = (
                        session.query(Device)
                        .filter(Device.id == record.device_id)
                        .first()
                    )
                    if device:
                        device.last_maintenance_date = record.maintenance_date

                        # Schedule next maintenance in 3 months (as an example)
                        from datetime import timedelta

                        next_maintenance = record.maintenance_date + timedelta(days=90)
                        device.next_maintenance_date = next_maintenance

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False


def delete_maintenance_record(record_id):
    """Delete a maintenance record."""
    with get_db_session() as session:
        try:
            record = (
                session.query(MaintenanceRecord)
                .filter(MaintenanceRecord.id == record_id)
                .first()
            )

            if not record:
                return False

            session.delete(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
