"""
Employee Service
Handles employee data management
"""

import os
import json
from typing import Dict, List, Optional, Any

# File paths for data storage
EMPLOYEES_FILE = 'data/employees.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class EmployeeService:
    def __init__(self):
        """Initialize the employee service"""
        pass
    
    def get_all_employees(self) -> List:
        """Get all employees"""
        try:
            if os.path.exists(EMPLOYEES_FILE):
                with open(EMPLOYEES_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Create empty employees file if it doesn't exist
                with open(EMPLOYEES_FILE, 'w') as f:
                    json.dump([], f)
                return []
        except Exception as e:
            print(f"Error loading employees: {e}")
            return []
    
    def get_employee(self, employee_id: int) -> Optional[Dict]:
        """Get an employee by ID"""
        employees = self.get_all_employees()
        
        for employee in employees:
            if employee.get("id") == employee_id:
                return employee
        
        return None
    
    def find_employee_by_punch_code(self, punch_code: str) -> Optional[Dict]:
        """Find an employee by punch code"""
        employees = self.get_all_employees()
        
        # First try to match by custom_id (string comparison)
        for employee in employees:
            if employee.get("custom_id") == punch_code:
                return employee
        
        # If not found, try to match by system id (numeric comparison)
        try:
            numeric_id = int(punch_code)
            for employee in employees:
                if employee.get("id") == numeric_id:
                    return employee
        except ValueError:
            pass  # Not a valid numeric ID
        
        return None
    
    def add_employee(self, employee_data: Dict) -> Dict:
        """Add a new employee"""
        employees = self.get_all_employees()
        
        # Generate a new ID if not provided
        if "id" not in employee_data:
            new_id = 1
            if employees:
                new_id = max(emp.get("id", 0) for emp in employees) + 1
            employee_data["id"] = new_id
        
        # Validate custom_id uniqueness
        if employee_data.get("custom_id"):
            for emp in employees:
                if emp.get("custom_id") == employee_data["custom_id"]:
                    return {"error": "This ID/Punch Code is already in use"}
        
        employees.append(employee_data)
        
        try:
            with open(EMPLOYEES_FILE, 'w') as f:
                json.dump(employees, f, indent=2)
            return employee_data
        except Exception as e:
            print(f"Error saving employee: {e}")
            return {"error": f"Failed to save employee: {str(e)}"}
    
    def update_employee(self, employee_id: int, update_data: Dict) -> Optional[Dict]:
        """Update an employee"""
        employees = self.get_all_employees()
        
        # Find the employee
        employee_index = None
        for i, emp in enumerate(employees):
            if emp.get("id") == employee_id:
                employee_index = i
                break
        
        if employee_index is None:
            return None
        
        # Validate custom_id uniqueness
        if "custom_id" in update_data:
            for i, emp in enumerate(employees):
                if i != employee_index and emp.get("custom_id") == update_data["custom_id"]:
                    return {"error": "This ID/Punch Code is already in use by another employee"}
        
        # Update only the fields provided
        for key, value in update_data.items():
            employees[employee_index][key] = value
        
        try:
            with open(EMPLOYEES_FILE, 'w') as f:
                json.dump(employees, f, indent=2)
            return employees[employee_index]
        except Exception as e:
            print(f"Error updating employee: {e}")
            return {"error": f"Failed to update employee: {str(e)}"}
    
    def delete_employee(self, employee_id: int) -> Optional[Dict]:
        """Delete an employee"""
        employees = self.get_all_employees()
        
        # Find the employee
        employee_index = None
        for i, emp in enumerate(employees):
            if emp.get("id") == employee_id:
                employee_index = i
                break
        
        if employee_index is None:
            return None
        
        # Remove the employee
        deleted_employee = employees.pop(employee_index)
        
        try:
            with open(EMPLOYEES_FILE, 'w') as f:
                json.dump(employees, f, indent=2)
            return deleted_employee
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return {"error": f"Failed to delete employee: {str(e)}"}

