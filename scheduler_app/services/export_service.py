"""
Export Service
Handles data export functionality (CSV, etc.)
"""

import csv
import io
import datetime
from typing import Dict, List, Optional, Any, BinaryIO

class ExportService:
    def __init__(self, timeclock_service=None, employee_service=None, business_service=None):
        """Initialize the export service"""
        self.timeclock_service = timeclock_service
        self.employee_service = employee_service
        self.business_service = business_service
    
    def export_timecard_to_csv(self, employee_id: int, start_date: datetime.datetime, 
                              end_date: datetime.datetime) -> Optional[str]:
        """
        Export an employee's timecard to CSV
        
        Args:
            employee_id: The ID of the employee
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            CSV data as a string, or None if error
        """
        if not self.timeclock_service or not self.employee_service:
            return None
        
        # Get the employee
        employee = self.employee_service.get_employee(employee_id)
        if not employee:
            return None
        
        # Generate the report
        report_data = self.timeclock_service.generate_report(start_date, end_date)
        
        # Extract this employee's data
        employee_data = report_data["report"]["employees"].get(str(employee_id))
        if not employee_data:
            # No data for this employee in the date range
            return self._create_empty_timecard_csv(employee, start_date, end_date)
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            f"Timecard for {employee['name']}",
            f"ID: {employee_id}",
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        ])
        writer.writerow([])  # Empty row
        
        writer.writerow([
            "Date",
            "Punch In",
            "Punch Out",
            "Duration (minutes)",
            "Duration (hours)"
        ])
        
        # Write punch pairs
        for pair in employee_data.get("punch_pairs", []):
            in_time = datetime.datetime.fromisoformat(pair["in"])
            out_time = datetime.datetime.fromisoformat(pair["out"])
            
            date_str = in_time.strftime("%Y-%m-%d")
            in_time_str = in_time.strftime("%H:%M:%S")
            out_time_str = out_time.strftime("%H:%M:%S")
            
            duration_minutes = pair["duration_minutes"]
            duration_hours = round(duration_minutes / 60, 2)
            
            writer.writerow([
                date_str,
                in_time_str,
                out_time_str,
                duration_minutes,
                duration_hours
            ])
        
        # Write summary
        writer.writerow([])  # Empty row
        writer.writerow(["Total Hours", employee_data["hours"]])
        
        return output.getvalue()
    
    def _create_empty_timecard_csv(self, employee: Dict, start_date: datetime.datetime, 
                                 end_date: datetime.datetime) -> str:
        """Create an empty timecard CSV when no data is available"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            f"Timecard for {employee['name']}",
            f"ID: {employee['id']}",
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        ])
        writer.writerow([])  # Empty row
        
        writer.writerow([
            "Date",
            "Punch In",
            "Punch Out",
            "Duration (minutes)",
            "Duration (hours)"
        ])
        
        # Write no data message
        writer.writerow(["No time clock data found for this period"])
        
        return output.getvalue()
    
    def export_report_to_csv(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Optional[str]:
        """
        Export a full time clock report to CSV
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            CSV data as a string, or None if error
        """
        if not self.timeclock_service:
            return None
        
        # Generate the report
        report_data = self.timeclock_service.generate_report(start_date, end_date)
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        business_name = "Unnamed Business"
        if self.business_service:
            business_info = self.business_service.get_business_info()
            business_name = business_info.get("name", "Unnamed Business")
        
        writer.writerow([
            f"Time Clock Report for {business_name}",
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        ])
        writer.writerow([])  # Empty row
        
        # Write summary section
        writer.writerow(["Employee Summary"])
        writer.writerow(["Employee", "Total Hours", "Punch Pairs"])
        
        employees_data = report_data["report"]["employees"]
        if not employees_data:
            writer.writerow(["No data for the selected period"])
        else:
            for emp_id, emp_data in employees_data.items():
                writer.writerow([
                    emp_data["name"],
                    emp_data["hours"],
                    len(emp_data.get("punch_pairs", []))
                ])
        
        writer.writerow([])  # Empty row
        
        # Write detailed section
        writer.writerow(["Detailed Punch Records"])
        writer.writerow(["Employee", "Date", "Punch In", "Punch Out", "Duration (minutes)"])
        
        if not employees_data:
            writer.writerow(["No data for the selected period"])
        else:
            for emp_id, emp_data in employees_data.items():
                for pair in emp_data.get("punch_pairs", []):
                    in_time = datetime.datetime.fromisoformat(pair["in"])
                    out_time = datetime.datetime.fromisoformat(pair["out"])
                    
                    date_str = in_time.strftime("%Y-%m-%d")
                    in_time_str = in_time.strftime("%H:%M:%S")
                    out_time_str = out_time.strftime("%H:%M:%S")
                    
                    writer.writerow([
                        emp_data["name"],
                        date_str,
                        in_time_str,
                        out_time_str,
                        pair["duration_minutes"]
                    ])
        
        return output.getvalue()

