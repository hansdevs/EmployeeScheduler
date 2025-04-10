"""
Schedule Service
Handles schedule data management
"""

import os
import json
from typing import Dict, List, Optional, Any, Union

# File paths for data storage
def get_company_draft_file_path(company_id):
    """Get company-specific draft file path"""
    return f'data/company_{company_id}/schedule_draft.json'

def get_company_published_file_path(company_id):
    """Get company-specific published file path"""
    return f'data/company_{company_id}/schedule_published.json'

# File paths for data storage
SCHEDULE_DRAFT_FILE = 'data/schedule_draft.json'
SCHEDULE_PUBLISHED_FILE = 'data/schedule_published.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class ScheduleService:
    def __init__(self, employee_service=None, station_service=None, business_service=None, company_id=None):
        """Initialize the schedule service"""
        self.employee_service = employee_service
        self.station_service = station_service
        self.business_service = business_service
        self.company_id = company_id
       
    def get_draft_file_path(self):
        """Get the draft file path for this company"""
        if not self.company_id:
            return SCHEDULE_DRAFT_FILE  # Default for backward compatibility
        return get_company_draft_file_path(self.company_id)
       
    def get_published_file_path(self):
        """Get the published file path for this company"""
        if not self.company_id:
            return SCHEDULE_PUBLISHED_FILE  # Default for backward compatibility
        return get_company_published_file_path(self.company_id)
   
    def get_draft_schedule(self) -> Dict:
        """Get the current draft schedule"""
        try:
            file_path = self.get_draft_file_path()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
           
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default structure if file doesn't exist
                default_data = {"schedule": [], "is_published": False}
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
        except Exception as e:
            print(f"Error loading draft schedule: {e}")
            return {"schedule": [], "is_published": False}
    
    def save_draft_schedule(self, schedule_data: List) -> Dict:
        """Save the draft schedule"""
        try:
            file_path = self.get_draft_file_path()
            data = {"schedule": schedule_data, "is_published": False}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return {"status": "saved", "message": "Schedule saved as draft"}
        except Exception as e:
            print(f"Error saving draft schedule: {e}")
            return {"status": "error", "message": f"Failed to save draft: {str(e)}"}
    
    def get_published_schedule(self) -> Dict:
        """Get the published schedule"""
        try:
            file_path = self.get_published_file_path()
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Add is_published flag if not present
                    if "is_published" not in data:
                        data["is_published"] = True
                    return data
            else:
                return {"schedule": [], "is_published": False}
        except Exception as e:
            print(f"Error loading published schedule: {e}")
            return {"schedule": [], "is_published": False}
    
    def publish_schedule(self, schedule_data: List) -> Dict:
        """Publish the schedule"""
        try:
            file_path = self.get_published_file_path()
            data = {"schedule": schedule_data, "is_published": True}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return {"status": "published", "message": "Schedule published successfully"}
        except Exception as e:
            print(f"Error publishing schedule: {e}")
            return {"status": "error", "message": f"Failed to publish schedule: {str(e)}"}
    
    def is_schedule_published(self) -> bool:
        """Check if a schedule is published"""
        published_data = self.get_published_schedule()
        return published_data.get("is_published", False) and len(published_data.get("schedule", [])) > 0
    
    def get_schedule_with_metadata(self, include_draft=True) -> Dict:
        """
        Get the schedule with metadata (employees, stations, business info)
        
        Args:
            include_draft: Whether to include draft schedule if no published schedule exists
            
        Returns:
            Dict with schedule and metadata
        """
        # Get published schedule first
        published_data = self.get_published_schedule()
        
        # If published schedule exists, return it with metadata
        if published_data.get("is_published", False) and len(published_data.get("schedule", [])) > 0:
            result = {
                "schedule": published_data.get("schedule", []),
                "is_published": True
            }
        elif include_draft:
            # Fall back to draft schedule if requested
            draft_data = self.get_draft_schedule()
            result = {
                "schedule": draft_data.get("schedule", []),
                "is_published": False
            }
        else:
            # No schedule available
            result = {
                "schedule": [],
                "is_published": False
            }
        
        # Add metadata
        if self.employee_service:
            result["employees"] = self.employee_service.get_all_employees()
        else:
            result["employees"] = []
            
        if self.station_service:
            result["stations"] = self.station_service.get_all_stations()
        else:
            result["stations"] = []
            
        if self.business_service:
            result["business"] = self.business_service.get_business_info()
        else:
            result["business"] = {}
        
        return result

