"""
Time Clock Service
Handles all employee clock in/out functionality
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

# File paths for data storage
TIMECLOCK_FILE = 'data/timeclock.json'
TIMECLOCK_LOGS_FILE = 'data/timeclock_logs.json'
TIMECLOCK_SETTINGS_FILE = 'data/timeclock_settings.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class TimeClockService:
    def __init__(self, employee_service=None):
        """Initialize the time clock service"""
        self.employee_service = employee_service
        
    def load_timeclock_data(self) -> Dict:
        """Load the current time clock data"""
        try:
            if os.path.exists(TIMECLOCK_FILE):
                with open(TIMECLOCK_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create default structure if file doesn't exist
                default_data = {"employees": {}}
                with open(TIMECLOCK_FILE, 'w') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
        except Exception as e:
            print(f"Error loading time clock data: {e}")
            return {"employees": {}}
    
    def save_timeclock_data(self, data: Dict) -> bool:
        """Save time clock data to file"""
        try:
            with open(TIMECLOCK_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving time clock data: {e}")
            return False
    
    def load_timeclock_logs(self) -> List:
        """Load time clock logs"""
        try:
            if os.path.exists(TIMECLOCK_LOGS_FILE):
                with open(TIMECLOCK_LOGS_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create empty logs file if it doesn't exist
                with open(TIMECLOCK_LOGS_FILE, 'w') as f:
                    json.dump([], f)
                return []
        except Exception as e:
            print(f"Error loading time clock logs: {e}")
            return []
    
    def save_timeclock_logs(self, logs: List) -> bool:
        """Save time clock logs to file"""
        try:
            with open(TIMECLOCK_LOGS_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving time clock logs: {e}")
            return False
    
    def get_employee_status(self, employee_id: int) -> Dict:
        """Get the current status of an employee"""
        timeclock_data = self.load_timeclock_data()
        employee_id_str = str(employee_id)
        
        return timeclock_data["employees"].get(employee_id_str, {
            "status": "out",
            "last_punch": None
        })
    
    def get_all_statuses(self) -> Dict:
        """Get the status of all employees"""
        return self.load_timeclock_data()
    
    def record_punch(self, employee_id: int, timestamp: Optional[str] = None, manual: bool = False) -> Dict:
        """
        Record a punch (in or out) for an employee
        
        Args:
            employee_id: The ID of the employee
            timestamp: ISO format timestamp (defaults to current time if None)
            manual: Whether this is a manual punch by a manager
            
        Returns:
            Dict with punch information
        """
        # Convert to string for JSON dictionary keys
        employee_id_str = str(employee_id)
        
        # Get current timestamp if not provided
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
        
        # Load current timeclock data
        timeclock_data = self.load_timeclock_data()
        
        # Load employee data to get name and other details
        employee = None
        if self.employee_service:
            employee = self.employee_service.get_employee(employee_id)
        
        if not employee:
            return {"error": f"Employee with ID {employee_id} not found"}, 404
        
        # Determine if this is a punch in or out
        current_status = timeclock_data["employees"].get(employee_id_str, {"status": "out"})
        new_status = "out" if current_status.get("status") == "in" else "in"
        
        # Update the employee's status
        timeclock_data["employees"][employee_id_str] = {
            "status": new_status,
            "last_punch": timestamp,
            "name": employee.get("name", f"Employee {employee_id}"),
            "color": employee.get("color", "block-blue")
        }
        
        # Save the updated timeclock data
        self.save_timeclock_data(timeclock_data)
        
        # Record this punch in the logs
        timeclock_logs = self.load_timeclock_logs()
        
        punch_log = {
            "employee_id": employee_id,
            "employee_name": employee.get("name", f"Employee {employee_id}"),
            "timestamp": timestamp,
            "type": new_status,
            "color": employee.get("color", "block-blue"),
            "manual": manual
        }
        
        # If this is a punch out, calculate duration from last punch in
        if new_status == "out":
            # Find the most recent punch in for this employee
            for log in reversed(timeclock_logs):
                if log["employee_id"] == employee_id and log["type"] == "in":
                    # Calculate duration
                    punch_in_time = datetime.datetime.fromisoformat(log["timestamp"])
                    punch_out_time = datetime.datetime.fromisoformat(timestamp)
                    duration_seconds = (punch_out_time - punch_in_time).total_seconds()
                    duration_minutes = round(duration_seconds / 60)
                    
                    # Add duration to the log
                    punch_log["duration_minutes"] = duration_minutes
                    break
        
        timeclock_logs.append(punch_log)
        self.save_timeclock_logs(timeclock_logs)
        
        # Return the result
        result = {
            "success": True,
            "employee": employee,
            "punch": {
                "type": new_status,
                "timestamp": timestamp
            }
        }
        
        # Add duration if available
        if new_status == "out" and "duration_minutes" in punch_log:
            result["punch"]["duration_minutes"] = punch_log["duration_minutes"]
        
        return result
    
    def get_recent_activity(self, limit: int = 20) -> List:
        """Get recent time clock activity"""
        # Load the timeclock logs
        timeclock_logs = self.load_timeclock_logs()
        
        # Sort by timestamp (newest first) and limit entries
        recent_activity = sorted(timeclock_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        return recent_activity
    
    def get_clocked_in_employees(self) -> List:
        """Get a list of currently clocked in employees"""
        timeclock_data = self.load_timeclock_data()
        
        clocked_in = []
        for emp_id, status in timeclock_data["employees"].items():
            if status["status"] == "in":
                clocked_in.append({
                    "id": int(emp_id),
                    "name": status.get("name", f"Employee {emp_id}"),
                    "punch_time": status.get("last_punch"),
                    "color": status.get("color", "block-blue")
                })
        
        return clocked_in
    
    def generate_report(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict:
        """
        Generate a report of employee hours
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            Dict with report data
        """
        # Load the timeclock logs
        timeclock_logs = self.load_timeclock_logs()
        
        # Filter logs by date range
        filtered_logs = []
        for log in timeclock_logs:
            log_time = datetime.datetime.fromisoformat(log["timestamp"])
            if start_date <= log_time <= end_date:
                filtered_logs.append(log)
        
        # Group by employee and calculate total hours
        employee_hours = {}
        
        # First, organize punch pairs (in/out)
        for log in filtered_logs:
            emp_id = log["employee_id"]
            if emp_id not in employee_hours:
                employee_hours[emp_id] = {
                    "name": log["employee_name"],
                    "total_minutes": 0,
                    "punches": []
                }
            
            employee_hours[emp_id]["punches"].append(log)
        
        # Calculate hours for each employee
        for emp_id, data in employee_hours.items():
            # Sort punches by timestamp
            punches = sorted(data["punches"], key=lambda x: x["timestamp"])
            
            # Process punch pairs
            total_minutes = 0
            punch_pairs = []
            
            i = 0
            while i < len(punches) - 1:
                if punches[i]["type"] == "in" and punches[i+1]["type"] == "out":
                    # Calculate duration
                    in_time = datetime.datetime.fromisoformat(punches[i]["timestamp"])
                    out_time = datetime.datetime.fromisoformat(punches[i+1]["timestamp"])
                    duration_minutes = round((out_time - in_time).total_seconds() / 60)
                    
                    total_minutes += duration_minutes
                    
                    punch_pairs.append({
                        "in": punches[i]["timestamp"],
                        "out": punches[i+1]["timestamp"],
                        "duration_minutes": duration_minutes
                    })
                    
                    i += 2  # Skip to next potential pair
                else:
                    i += 1  # Skip unpaired punch
            
            employee_hours[emp_id]["total_minutes"] = total_minutes
            employee_hours[emp_id]["punch_pairs"] = punch_pairs
            employee_hours[emp_id]["hours"] = round(total_minutes / 60, 2)
            
            # Remove the raw punches from the response
            del employee_hours[emp_id]["punches"]
        
        return {
            "report": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "employees": employee_hours
            }
        }
    
    def get_settings(self) -> Dict:
        """Get time clock settings"""
        try:
            if os.path.exists(TIMECLOCK_SETTINGS_FILE):
                with open(TIMECLOCK_SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create default settings if file doesn't exist
                default_settings = {
                    "enforce_schedule": True,
                    "allow_remote_punch": True,
                    "require_photo": False
                }
                with open(TIMECLOCK_SETTINGS_FILE, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        except Exception as e:
            print(f"Error loading time clock settings: {e}")
            return {
                "enforce_schedule": True,
                "allow_remote_punch": True,
                "require_photo": False
            }
    
    def update_settings(self, settings: Dict) -> Dict:
        """Update time clock settings"""
        current_settings = self.get_settings()
        
        # Update settings
        for key, value in settings.items():
            current_settings[key] = value
        
        try:
            with open(TIMECLOCK_SETTINGS_FILE, 'w') as f:
                json.dump(current_settings, f, indent=2)
            return current_settings
        except Exception as e:
            print(f"Error saving time clock settings: {e}")
            return current_settings

