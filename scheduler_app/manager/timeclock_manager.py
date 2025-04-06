"""
Time Clock Manager
Handles business logic for time clock operations
"""

import datetime
import json
import os
from typing import Dict, List, Optional, Tuple, Union

class TimeClockManager:
   """Manager class for time clock operations"""
   
   def __init__(self, employee_service, company_id=None):
       """Initialize the time clock manager"""
       self.employee_service = employee_service
       self.company_id = company_id
       self.data_dir = 'data'
       
       # Ensure data directory exists
       os.makedirs(self.data_dir, exist_ok=True)
       
       # Load existing punches
       self.punches = self._load_punches()
       
       # Load settings
       self.settings = self._load_settings()
   
   def _get_company_prefix(self) -> str:
       """Get the company prefix for file names"""
       if self.company_id:
           return f"{self.company_id}_"
       return ""
   
   def _get_punches_file(self) -> str:
       """Get the punches file path"""
       prefix = self._get_company_prefix()
       return os.path.join(self.data_dir, f"{prefix}punches.json")
   
   def _get_settings_file(self) -> str:
       """Get the settings file path"""
       prefix = self._get_company_prefix()
       return os.path.join(self.data_dir, f"{prefix}timeclock_settings.json")
   
   def _load_punches(self) -> List[Dict]:
       """Load punches from file"""
       try:
           with open(self._get_punches_file(), 'r') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           return []
   
   def _save_punches(self) -> None:
       """Save punches to file"""
       with open(self._get_punches_file(), 'w') as f:
           json.dump(self.punches, f, indent=2)
   
   def _load_settings(self) -> Dict:
       """Load settings from file"""
       try:
           with open(self._get_settings_file(), 'r') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           # Default settings
           return {
               "enforce_schedule": True,
               "allow_remote_punch": True,
               "require_photo": False
           }
   
   def _save_settings(self) -> None:
       """Save settings to file"""
       with open(self._get_settings_file(), 'w') as f:
           json.dump(self.settings, f, indent=2)
   
   def get_settings(self) -> Dict:
       """Get the current time clock settings"""
       return self.settings
   
   def update_settings(self, settings: Dict) -> Dict:
       """Update time clock settings"""
       # Update only the provided settings
       for key in ["enforce_schedule", "allow_remote_punch", "require_photo"]:
           if key in settings:
               self.settings[key] = settings[key]
       
       # Save the updated settings
       self._save_settings()
       
       return self.settings
   
   def record_punch(self, employee_id: int, timestamp_str: Optional[str] = None, manual: bool = False) -> Union[Dict, Tuple[Dict, int]]:
       """Record a punch for an employee"""
       # Validate employee exists
       employee = self.employee_service.get_employee(employee_id)
       if not employee:
           return {"error": f"Employee with ID {employee_id} not found"}, 404
       
       # Parse timestamp or use current time
       if timestamp_str:
           try:
               timestamp = datetime.datetime.fromisoformat(timestamp_str)
           except ValueError:
               return {"error": "Invalid timestamp format"}, 400
       else:
           timestamp = datetime.datetime.now()
       
       # Get the employee's current status
       status = self.get_employee_status(employee_id)
       
       # Determine if this is a punch in or out
       punch_type = "out" if status["status"] == "in" else "in"
       
       # Create the punch record
       punch = {
           "id": len(self.punches) + 1,
           "employee_id": employee_id,
           "timestamp": timestamp.isoformat(),
           "type": punch_type,
           "manual": manual
       }
       
       # If this is a punch out, calculate the duration
       duration_minutes = None
       if punch_type == "out" and status["last_punch"]:
           last_punch_time = datetime.datetime.fromisoformat(status["last_punch"])
           duration = timestamp - last_punch_time
           duration_minutes = int(duration.total_seconds() / 60)
           punch["duration_minutes"] = duration_minutes
       
       # Add the punch to the list
       self.punches.append(punch)
       
       # Save the updated punches
       self._save_punches()
       
       # Return the punch with employee info
       return {
           "punch": punch,
           "employee": employee
       }
   
   def get_employee_status(self, employee_id: int) -> Dict:
       """Get the current status of an employee"""
       # Find the most recent punch for this employee
       employee_punches = [p for p in self.punches if p["employee_id"] == employee_id]
       
       if not employee_punches:
           return {
               "employee_id": employee_id,
               "status": "out",
               "last_punch": None
           }
       
       # Sort by timestamp (newest first)
       employee_punches.sort(key=lambda p: p["timestamp"], reverse=True)
       last_punch = employee_punches[0]
       
       return {
           "employee_id": employee_id,
           "status": last_punch["type"],
           "last_punch": last_punch["timestamp"]
       }
   
   def get_all_statuses(self) -> Dict:
       """Get the status of all employees"""
       employees = self.employee_service.get_all_employees()
       statuses = {}
       
       for employee in employees:
           statuses[employee["id"]] = self.get_employee_status(employee["id"])
       
       return statuses
   
   def get_recent_activity(self, limit: int = 20) -> List[Dict]:
       """Get recent time clock activity"""
       # Sort punches by timestamp (newest first)
       sorted_punches = sorted(self.punches, key=lambda p: p["timestamp"], reverse=True)
       
       # Limit the number of punches
       limited_punches = sorted_punches[:limit]
       
       # Add employee names
       result = []
       for punch in limited_punches:
           employee = self.employee_service.get_employee(punch["employee_id"])
           if employee:
               punch_with_name = punch.copy()
               punch_with_name["employee_name"] = employee["name"]
               result.append(punch_with_name)
       
       return result
   
   def get_clocked_in_employees(self) -> List[Dict]:
       """Get a list of currently clocked in employees"""
       employees = self.employee_service.get_all_employees()
       clocked_in = []
       
       for employee in employees:
           status = self.get_employee_status(employee["id"])
           if status["status"] == "in":
               clocked_in.append({
                   "id": employee["id"],
                   "name": employee["name"],
                   "punch_time": status["last_punch"],
                   "color": employee.get("color", "block-blue")
               })
       
       return clocked_in
   
   def generate_report(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict:
       """Generate a time clock report for a date range"""
       # Filter punches by date range
       filtered_punches = [
           p for p in self.punches
           if start_date <= datetime.datetime.fromisoformat(p["timestamp"]) <= end_date
       ]
       
       # Group punches by employee
       employee_punches = {}
       for punch in filtered_punches:
           employee_id = punch["employee_id"]
           if employee_id not in employee_punches:
               employee_punches[employee_id] = []
           employee_punches[employee_id].append(punch)
       
       # Process each employee's punches
       report = {"employees": {}}
       
       for employee_id, punches in employee_punches.items():
           employee = self.employee_service.get_employee(employee_id)
           if not employee:
               continue
           
           # Sort punches by timestamp
           punches.sort(key=lambda p: p["timestamp"])
           
           # Pair punch-ins with punch-outs
           punch_pairs = []
           total_minutes = 0
           
           i = 0
           while i < len(punches) - 1:
               if punches[i]["type"] == "in" and punches[i+1]["type"] == "out":
                   # Calculate duration
                   in_time = datetime.datetime.fromisoformat(punches[i]["timestamp"])
                   out_time = datetime.datetime.fromisoformat(punches[i+1]["timestamp"])
                   duration = out_time - in_time
                   duration_minutes = int(duration.total_seconds() / 60)
                   
                   # Add to total
                   total_minutes += duration_minutes
                   
                   # Add pair
                   punch_pairs.append({
                       "in": punches[i]["timestamp"],
                       "out": punches[i+1]["timestamp"],
                       "duration_minutes": duration_minutes
                   })
                   
                   i += 2
               else:
                   # Skip unpaired punches
                   i += 1
           
           # Add to report
           report["employees"][employee_id] = {
               "name": employee["name"],
               "hours": round(total_minutes / 60, 2),
               "punch_pairs": punch_pairs
           }
       
       return {"report": report}

