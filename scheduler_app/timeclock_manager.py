"""
Time Clock Manager
Coordinates all time clock components
"""

import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

# Change from absolute imports to relative imports
from employee_service import EmployeeService
from business_service import BusinessService
from timeclock_service import TimeClockService
from export_service import ExportService

class TimeClockManager:
    def __init__(self):
        """Initialize the time clock manager"""
        self.employee_service = EmployeeService()
        self.business_service = BusinessService()
        self.timeclock_service = TimeClockService(self.employee_service)
        self.export_service = ExportService(
            self.timeclock_service, 
            self.employee_service,
            self.business_service
        )
    
    def process_punch(self, punch_id: str, timestamp: Optional[str] = None) -> Tuple[Dict, int]:
        """
        Process a punch in/out request
        
        Args:
            punch_id: The ID or punch code entered by the employee
            timestamp: ISO format timestamp (defaults to current time if None)
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Find the employee
        employee = self.employee_service.find_employee_by_punch_code(punch_id)
        
        if not employee:
            return {"error": f"No employee found with ID/Code: {punch_id}"}, 404
        
        # Record the punch
        result = self.timeclock_service.record_punch(employee["id"], timestamp)
        
        if "error" in result:
            return result, 400
        
        return result, 200
    
    def get_employee_status(self, employee_id: int) -> Tuple[Dict, int]:
        """Get the current status of an employee"""
        employee = self.employee_service.get_employee(employee_id)
        
        if not employee:
            return {"error": f"Employee with ID {employee_id} not found"}, 404
        
        status = self.timeclock_service.get_employee_status(employee_id)
        return status, 200
    
    def get_all_statuses(self) -> Tuple[Dict, int]:
        """Get the status of all employees"""
        return self.timeclock_service.get_all_statuses(), 200
    
    def get_recent_activity(self, limit: int = 20) -> Tuple[Dict, int]:
        """Get recent time clock activity"""
        activity = self.timeclock_service.get_recent_activity(limit)
        return {"activity": activity}, 200
    
    def get_clocked_in_employees(self) -> Tuple[Dict, int]:
        """Get a list of currently clocked in employees"""
        employees = self.timeclock_service.get_clocked_in_employees()
        return {"employees": employees}, 200
    
    def generate_report(self, start_date: str, end_date: str) -> Tuple[Dict, int]:
        """
        Generate a report of employee hours
        
        Args:
            start_date: Start date for the report (ISO format)
            end_date: End date for the report (ISO format)
            
        Returns:
            Tuple of (report_data, status_code)
        """
        try:
            start_date_obj = datetime.datetime.fromisoformat(start_date)
            end_date_obj = datetime.datetime.fromisoformat(end_date)
        except ValueError:
            return {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
        
        report = self.timeclock_service.generate_report(start_date_obj, end_date_obj)
        return report, 200
    
    def get_settings(self) -> Tuple[Dict, int]:
        """Get time clock settings"""
        settings = self.timeclock_service.get_settings()
        return settings, 200
    
    def update_settings(self, settings: Dict) -> Tuple[Dict, int]:
        """Update time clock settings"""
        updated_settings = self.timeclock_service.update_settings(settings)
        return updated_settings, 200
    
    def export_timecard_to_csv(self, employee_id: int, start_date: str, end_date: str) -> Tuple[Optional[str], int]:
        """
        Export an employee's timecard to CSV
        
        Args:
            employee_id: The ID of the employee
            start_date: Start date for the report (ISO format)
            end_date: End date for the report (ISO format)
            
        Returns:
            Tuple of (csv_data, status_code)
        """
        try:
            start_date_obj = datetime.datetime.fromisoformat(start_date)
            end_date_obj = datetime.datetime.fromisoformat(end_date)
        except ValueError:
            return None, 400
        
        csv_data = self.export_service.export_timecard_to_csv(employee_id, start_date_obj, end_date_obj)
        
        if csv_data is None:
            return None, 404
        
        return csv_data, 200
    
    def export_report_to_csv(self, start_date: str, end_date: str) -> Tuple[Optional[str], int]:
        """
        Export a full time clock report to CSV
        
        Args:
            start_date: Start date for the report (ISO format)
            end_date: End date for the report (ISO format)
            
        Returns:
            Tuple of (csv_data, status_code)
        """
        try:
            start_date_obj = datetime.datetime.fromisoformat(start_date)
            end_date_obj = datetime.datetime.fromisoformat(end_date)
        except ValueError:
            return None, 400
        
        csv_data = self.export_service.export_report_to_csv(start_date_obj, end_date_obj)
        
        if csv_data is None:
            return None, 500
        
        return csv_data, 200

