"""
Station Service
Handles station data management
"""

import os
import json
from typing import Dict, List, Optional, Any

# File paths for data storage
def get_company_file_path(company_id):
    """Get company-specific file path"""
    return f'data/company_{company_id}/stations.json'

class StationService:
    def __init__(self, company_id=None):
        """Initialize the station service"""
        self.company_id = company_id
        
    def get_file_path(self):
        """Get the file path for this company"""
        if not self.company_id:
            return 'data/stations.json'  # Default for backward compatibility
        return get_company_file_path(self.company_id)
    
    def get_all_stations(self) -> List:
        """Get all stations"""
        try:
            file_path = self.get_file_path()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # Create empty stations file if it doesn't exist
                with open(file_path, 'w') as f:
                    json.dump([], f)
                return []
        except Exception as e:
            print(f"Error loading stations: {e}")
            return []
    
    def get_station(self, station_id: int) -> Optional[Dict]:
        """Get a station by ID"""
        stations = self.get_all_stations()
        
        for station in stations:
            if station.get("id") == station_id:
                return station
        
        return None
    
    def add_station(self, station_data: Dict) -> Dict:
        """Add a new station"""
        stations = self.get_all_stations()
        
        # Generate a new ID if not provided
        if "id" not in station_data:
            new_id = 1
            if stations:
                new_id = max(st.get("id", 0) for st in stations) + 1
            station_data["id"] = new_id
        
        stations.append(station_data)
        
        try:
            file_path = self.get_file_path()
            with open(file_path, 'w') as f:
                json.dump(stations, f, indent=2)
            return station_data
        except Exception as e:
            print(f"Error saving station: {e}")
            return {"error": f"Failed to save station: {str(e)}"}
    
    def update_station(self, station_id: int, update_data: Dict) -> Optional[Dict]:
        """Update a station"""
        stations = self.get_all_stations()
        
        # Find the station
        station_index = None
        for i, st in enumerate(stations):
            if st.get("id") == station_id:
                station_index = i
                break
        
        if station_index is None:
            return None
        
        # Update only the fields provided
        for key, value in update_data.items():
            stations[station_index][key] = value
        
        try:
            file_path = self.get_file_path()
            with open(file_path, 'w') as f:
                json.dump(stations, f, indent=2)
            return stations[station_index]
        except Exception as e:
            print(f"Error updating station: {e}")
            return {"error": f"Failed to update station: {str(e)}"}
    
    def delete_station(self, station_id: int) -> Optional[Dict]:
        """Delete a station"""
        stations = self.get_all_stations()
        
        # Find the station
        station_index = None
        for i, st in enumerate(stations):
            if st.get("id") == station_id:
                station_index = i
                break
        
        if station_index is None:
            return None
        
        # Remove the station
        deleted_station = stations.pop(station_index)
        
        try:
            file_path = self.get_file_path()
            with open(file_path, 'w') as f:
                json.dump(stations, f, indent=2)
            return deleted_station
        except Exception as e:
            print(f"Error deleting station: {e}")
            return {"error": f"Failed to delete station: {str(e)}"}

