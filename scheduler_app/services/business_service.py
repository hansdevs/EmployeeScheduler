"""
Business Service
Handles business account data management
"""

import os
import json
from typing import Dict, List, Optional, Any

# File paths for data storage
def get_company_file_path(company_id):
    """Get company-specific file path"""
    return f'data/company_{company_id}/business.json'

class BusinessService:
   def __init__(self, company_id=None):
       """Initialize the business service"""
       self.company_id = company_id
       
   def get_file_path(self):
       """Get the file path for this company"""
       if not self.company_id:
           return 'data/business.json'  # Default for backward compatibility
       return get_company_file_path(self.company_id)
   
   def get_business_info(self) -> Dict:
       """Get business information"""
       try:
           file_path = self.get_file_path()
           os.makedirs(os.path.dirname(file_path), exist_ok=True)
           
           if os.path.exists(file_path):
               with open(file_path, 'r') as f:
                   return json.load(f)
           else:
               # Create default business info if file doesn't exist
               default_info = {
                   "name": "Unnamed Business",
                   "industry": "",
                   "hours": {
                       "0": {"open": 9, "close": 17},  # Monday
                       "1": {"open": 9, "close": 17},  # Tuesday
                       "2": {"open": 9, "close": 17},  # Wednesday
                       "3": {"open": 9, "close": 17},  # Thursday
                       "4": {"open": 9, "close": 17},  # Friday
                       "5": {"open": 10, "close": 15},  # Saturday
                       "6": {"open": 0, "close": 0}    # Sunday (closed)
                   }
               }
               with open(file_path, 'w') as f:
                   json.dump(default_info, f, indent=2)
               return default_info
       except Exception as e:
           print(f"Error loading business info: {e}")
           return {
               "name": "Unnamed Business",
               "industry": "",
               "hours": {}
           }
    
   def update_business_info(self, info: Dict) -> Dict:
       """Update business information"""
       current_info = self.get_business_info()
       
       # Update fields
       for key, value in info.items():
           current_info[key] = value
       
       try:
           with open(self.get_file_path(), 'w') as f:
               json.dump(current_info, f, indent=2)
           return current_info
       except Exception as e:
           print(f"Error saving business info: {e}")
           return current_info
    
   def get_business_hours(self) -> Dict:
       """Get business hours"""
       business_info = self.get_business_info()
       return business_info.get("hours", {})
    
   def update_business_hours(self, hours: Dict) -> Dict:
       """Update business hours"""
       business_info = self.get_business_info()
       business_info["hours"] = hours
        
       try:
           with open(self.get_file_path(), 'w') as f:
               json.dump(business_info, f, indent=2)
           return business_info
       except Exception as e:
           print(f"Error saving business hours: {e}")
           return business_info

