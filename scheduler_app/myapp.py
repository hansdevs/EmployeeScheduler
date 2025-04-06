"""
Main Application
Handles HTTP requests using Python's built-in http.server
"""

import os
import sys
import json
import datetime
import http.server
import socketserver
import urllib.parse
from http import HTTPStatus

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Print the current directory and Python path for debugging
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# Import services
from employee_service import EmployeeService
from business_service import BusinessService
from timeclock_service import TimeClockService
from export_service import ExportService
from timeclock_manager import TimeClockManager
from station_service import StationService
from schedule_service import ScheduleService  # Import the new schedule service

# Initialize services
employee_service = EmployeeService()
business_service = BusinessService()
station_service = StationService()
timeclock_service = TimeClockService(employee_service)
export_service = ExportService(timeclock_service, employee_service, business_service)
timeclock_manager = TimeClockManager()
# Initialize schedule service with dependencies
schedule_service = ScheduleService(employee_service, station_service, business_service)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class SchedulerRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the scheduler application"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Debug: Print the requested path
        print(f"GET request for path: {path}")
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_get(path, parsed_path.query)
            return
        
        # Default route
        if path == '/':
            self.send_response(HTTPStatus.FOUND)
            self.send_header('Location', '/pages/welcome.html')
            self.end_headers()
            return
        
        # Serve static files
        # Check if the file exists in the static directory
        if path.startswith('/pages/') or path.startswith('/styles/') or path.startswith('/js/') or path.startswith('/images/'):
            file_path = os.path.join(current_dir, 'static' + path)
            print(f"Looking for file at: {file_path}")
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine content type
                content_type = self.guess_type(file_path)
                
                # Serve the file
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(HTTPStatus.OK)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    print(f"Error serving file: {e}")
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error serving file: {e}")
                    return
        
        # Fall back to default handler (which will likely return 404)
        return super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self.handle_api_post(self.path, data)
            return
        
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def do_PUT(self):
        """Handle PUT requests"""
        if self.path.startswith('/api/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self.handle_api_put(self.path, data)
            return
        
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/api/'):
            self.handle_api_delete(self.path)
            return
        
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def handle_api_get(self, path, query_string):
        """Handle API GET requests"""
        query_params = urllib.parse.parse_qs(query_string)
        
        # Employees endpoint
        if path == '/api/employees':
            employees = employee_service.get_all_employees()
            self.send_json_response(employees)
            return
        
        # Single employee endpoint
        if path.startswith('/api/employees/'):
            employee_id = int(path.split('/')[-1])
            employee = employee_service.get_employee(employee_id)
            if not employee:
                self.send_json_response({"error": "Employee not found"}, 404)
                return
            self.send_json_response(employee)
            return
        
        # Stations endpoint
        if path == '/api/stations':
            stations = station_service.get_all_stations()
            self.send_json_response(stations)
            return
        
        # Single station endpoint
        if path.startswith('/api/stations/'):
            station_id = int(path.split('/')[-1])
            station = station_service.get_station(station_id)
            if not station:
                self.send_json_response({"error": "Station not found"}, 404)
                return
            self.send_json_response(station)
            return
        
        # Business endpoint
        if path == '/api/business':
            business_info = business_service.get_business_info()
            self.send_json_response(business_info)
            return
        
        # Time clock status
        if path == '/api/timeclock/status':
            result, status_code = timeclock_manager.get_all_statuses()
            self.send_json_response(result, status_code)
            return
        
        # Employee time clock status
        if path.startswith('/api/timeclock/status/'):
            employee_id = int(path.split('/')[-1])
            result, status_code = timeclock_manager.get_employee_status(employee_id)
            self.send_json_response(result, status_code)
            return
        
        # Time clock activity
        if path == '/api/timeclock/activity':
            limit = int(query_params.get('limit', [20])[0])
            result, status_code = timeclock_manager.get_recent_activity(limit)
            self.send_json_response(result, status_code)
            return
        
        # Clocked in employees
        if path == '/api/timeclock/clocked-in':
            result, status_code = timeclock_manager.get_clocked_in_employees()
            self.send_json_response(result, status_code)
            return
        
        # Time clock report
        if path == '/api/timeclock/report':
            start_date_str = query_params.get('start_date', [None])[0]
            end_date_str = query_params.get('end_date', [None])[0]
            
            if not start_date_str:
                # Default to 7 days ago
                start_date_str = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            
            if not end_date_str:
                # Default to now
                end_date_str = datetime.datetime.now().isoformat()
            
            result, status_code = timeclock_manager.generate_report(start_date_str, end_date_str)
            self.send_json_response(result, status_code)
            return
        
        # Time clock settings
        if path == '/api/timeclock/settings':
            result, status_code = timeclock_manager.get_settings()
            self.send_json_response(result, status_code)
            return
        
        # Schedule endpoint - Updated to use schedule service
        if path == '/api/schedule':
            schedule_data = schedule_service.get_schedule_with_metadata(include_draft=True)
            self.send_json_response(schedule_data)
            return
        
        # Official schedule endpoint - Updated to use schedule service
        if path == '/api/official_schedule':
            # Only return published schedule
            if schedule_service.is_schedule_published():
                schedule_data = schedule_service.get_schedule_with_metadata(include_draft=False)
                self.send_json_response(schedule_data)
            else:
                # Return error if no schedule is published
                self.send_json_response({"error": "Schedule is not published"}, 400)
            return
        
        # If we get here, the endpoint wasn't found
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def handle_api_post(self, path, data):
        """Handle API POST requests"""
        
        # Employees endpoint
        if path == '/api/employees':
            result = employee_service.add_employee(data)
            
            if "error" in result:
                self.send_json_response(result, 400)
            else:
                self.send_json_response(result, 201)
            return
        
        # Stations endpoint
        if path == '/api/stations':
            result = station_service.add_station(data)
            
            if "error" in result:
                self.send_json_response(result, 400)
            else:
                self.send_json_response(result, 201)
            return
        
        # Business endpoint
        if path == '/api/business':
            result = business_service.update_business_info(data)
            self.send_json_response(result)
            return
        
        # Time clock punch
        if path == '/api/timeclock/punch':
            employee_id = data.get('employee_id')
            timestamp = data.get('timestamp')
            manual = data.get('manual', False)
            
            if not employee_id:
                # Try to use the punch code if provided
                punch_code = data.get('punch_code')
                if not punch_code:
                    self.send_json_response({"error": "Employee ID or punch code is required"}, 400)
                    return
                
                result, status_code = timeclock_manager.process_punch(punch_code, timestamp)
            else:
                # Convert to string if it's not already
                employee_id_str = str(employee_id)
                result, status_code = timeclock_manager.process_punch(employee_id_str, timestamp)
            
            self.send_json_response(result, status_code)
            return
        
        # Time clock settings
        if path == '/api/timeclock/settings':
            result, status_code = timeclock_manager.update_settings(data)
            self.send_json_response(result, status_code)
            return
        
        # Schedule endpoint - Updated to use schedule service
        if path == '/api/schedule':
            action = data.get('action', 'draft')
            shifts = data.get('shifts', [])
            
            if action == 'publish':
                result = schedule_service.publish_schedule(shifts)
            else:
                result = schedule_service.save_draft_schedule(shifts)
            
            self.send_json_response(result)
            return
        
        # If we get here, the endpoint wasn't found
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def handle_api_put(self, path, data):
        """Handle API PUT requests"""
        
        # Employee update endpoint
        if path.startswith('/api/employees/'):
            employee_id = int(path.split('/')[-1])
            result = employee_service.update_employee(employee_id, data)
            
            if not result:
                self.send_json_response({"error": "Employee not found"}, 404)
                return
            
            if "error" in result:
                self.send_json_response(result, 400)
                return
            
            self.send_json_response(result)
            return
        
        # Station update endpoint
        if path.startswith('/api/stations/'):
            station_id = int(path.split('/')[-1])
            result = station_service.update_station(station_id, data)
            
            if not result:
                self.send_json_response({"error": "Station not found"}, 404)
                return
            
            if "error" in result:
                self.send_json_response(result, 400)
                return
            
            self.send_json_response(result)
            return
        
        # If we get here, the endpoint wasn't found
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def handle_api_delete(self, path):
        """Handle API DELETE requests"""
        
        # Employee delete endpoint
        if path.startswith('/api/employees/'):
            employee_id = int(path.split('/')[-1])
            result = employee_service.delete_employee(employee_id)
            
            if not result:
                self.send_json_response({"error": "Employee not found"}, 404)
                return
            
            if "error" in result:
                self.send_json_response(result, 400)
                return
            
            self.send_json_response(result)
            return
        
        # Station delete endpoint
        if path.startswith('/api/stations/'):
            station_id = int(path.split('/')[-1])
            result = station_service.delete_station(station_id)
            
            if not result:
                self.send_json_response({"error": "Station not found"}, 404)
                return
            
            if "error" in result:
                self.send_json_response(result, 400)
                return
            
            self.send_json_response(result)
            return
        
        # If we get here, the endpoint wasn't found
        self.send_error(HTTPStatus.NOT_FOUND)
    
    def send_json_response(self, data, status_code=200):
        """Send a JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    """Run the HTTP server"""
    handler = SchedulerRequestHandler
    
    # Set the directory to serve static files from
    handler.directory = os.path.dirname(os.path.abspath(__file__))
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()

