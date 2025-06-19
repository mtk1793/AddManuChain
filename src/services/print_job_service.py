# src/services/print_job_service.py
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import os
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import desc, asc

from src.db.connection import get_db_session
from src.db.models.print_job import PrintJob
from src.db.models.user import User
from src.db.models.device import Device
from src.db.models.material import Material

def load_sample_print_jobs():
    """Load sample print job data from CSV file for dashboard display"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '../../data/sample_print_jobs.csv')
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            # Return default sample data if no CSV file found
            return [
                {"id": 1, "name": "Prototype Bracket", "status": "Completed", "user_id": 1, "device_id": 1, "material_used": 125.5},
                {"id": 2, "name": "Medical Housing", "status": "Completed", "user_id": 2, "device_id": 2, "material_used": 89.3},
                {"id": 3, "name": "Gear Assembly", "status": "In Progress", "user_id": 3, "device_id": 3, "material_used": 67.8}
            ]
        
        # Convert DataFrame to list of dictionaries
        print_jobs = df.to_dict('records')
        
        # Convert date strings to proper format if present
        for job in print_jobs:
            if 'start_time' in job and pd.notna(job['start_time']):
                try:
                    job['start_time'] = pd.to_datetime(job['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            if 'end_time' in job and pd.notna(job['end_time']):
                try:
                    job['end_time'] = pd.to_datetime(job['end_time']).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            if 'created_at' in job and pd.notna(job['created_at']):
                try:
                    job['created_at'] = pd.to_datetime(job['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
                    
        return print_jobs
        
    except Exception as e:
        print(f"Error loading sample print jobs: {e}")
        # Return basic fallback data
        return [
            {"id": 1, "name": "Prototype Bracket", "status": "Completed", "material_used": 125.5},
            {"id": 2, "name": "Medical Housing", "status": "Completed", "material_used": 89.3},
            {"id": 3, "name": "Gear Assembly", "status": "In Progress", "material_used": 67.8}
        ]

def get_print_job_status_counts():
    """Get count of print jobs by status from sample data"""
    try:
        print_jobs = load_sample_print_jobs()
        status_counts = {}
        
        for job in print_jobs:
            status = job.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return status_counts
        
    except Exception as e:
        print(f"Error getting print job status counts: {e}")
        return {"Completed": 8, "In Progress": 3, "Failed": 2, "Pending": 1, "Cancelled": 1}

def get_recent_print_jobs(limit=10):
    """Get recent print jobs from sample data"""
    try:
        print_jobs = load_sample_print_jobs()
        
        # Sort by created_at if available, otherwise by id
        if print_jobs and 'created_at' in print_jobs[0]:
            print_jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        else:
            print_jobs.sort(key=lambda x: x.get('id', 0), reverse=True)
            
        return print_jobs[:limit]
        
    except Exception as e:
        print(f"Error getting recent print jobs: {e}")
        return []

def get_print_job_statistics():
    """Get print job statistics from sample data"""
    try:
        print_jobs = load_sample_print_jobs()
        
        total_jobs = len(print_jobs)
        completed_jobs = len([job for job in print_jobs if job.get('status') == 'Completed'])
        failed_jobs = len([job for job in print_jobs if job.get('status') == 'Failed'])
        in_progress_jobs = len([job for job in print_jobs if job.get('status') == 'In Progress'])
        
        # Calculate success rate
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Calculate total material used
        total_material_used = sum([
            job.get('material_used', 0) for job in print_jobs 
            if job.get('material_used') and pd.notna(job.get('material_used'))
        ])
        
        # Calculate average duration for completed jobs
        completed_durations = [
            job.get('actual_duration', 0) for job in print_jobs 
            if job.get('status') == 'Completed' and job.get('actual_duration') and pd.notna(job.get('actual_duration'))
        ]
        avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "in_progress_jobs": in_progress_jobs,
            "success_rate": round(success_rate, 1),
            "total_material_used": round(total_material_used, 2),
            "average_duration_minutes": round(avg_duration, 0)
        }
        
    except Exception as e:
        print(f"Error getting print job statistics: {e}")
        return {
            "total_jobs": 15,
            "completed_jobs": 8,
            "failed_jobs": 2,
            "in_progress_jobs": 3,
            "success_rate": 73.3,
            "total_material_used": 1456.7,
            "average_duration_minutes": 168
        }

def get_all_print_jobs(status=None, user_id=None, device_id=None, limit=None):
    """Get all print jobs with optional filtering"""
    try:
        print_jobs = load_sample_print_jobs()
        
        # Apply filters
        if status:
            if isinstance(status, list):
                print_jobs = [job for job in print_jobs if job.get('status') in status]
            else:
                print_jobs = [job for job in print_jobs if job.get('status') == status]
                
        if user_id:
            print_jobs = [job for job in print_jobs if job.get('user_id') == user_id]
            
        if device_id:
            print_jobs = [job for job in print_jobs if job.get('device_id') == device_id]
            
        # Apply limit
        if limit:
            print_jobs = print_jobs[:limit]
            
        return print_jobs
        
    except Exception as e:
        print(f"Error getting print jobs: {e}")
        return []
