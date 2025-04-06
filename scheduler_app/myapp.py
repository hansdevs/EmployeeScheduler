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
from http import HTTPStatus, cookies
from urllib.parse import parse_qs

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
   sys.path.insert(0, current_dir)

# Print the current directory and Python path for debugging
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# Import services - use relative imports since we're already in scheduler_app
try:
  # Import directly from local directories
  from services.employee_service import EmployeeService
  from services.business_service import BusinessService
  from services.timeclock_service import TimeClockService
  from services.export_service import ExportService
  from manager.timeclock_manager import TimeClockManager
  from services.station_service import StationService
  from services.schedule_service import ScheduleService
  from services.user_service import UserService
  from auth_middleware import AuthMiddleware
  print("Imported modules successfully")
except ImportError as e:
  # If imports fail, print detailed error and exit
  print(f"Error importing modules: {e}")
  print("Please make sure all Python files are in the correct directory")
  print("Current directory:", current_dir)
  print("Files in current directory:", os.listdir(current_dir))
  sys.exit(1)

# Initialize services
user_service = UserService()
auth_middleware = AuthMiddleware()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class SchedulerRequestHandler(http.server.SimpleHTTPRequestHandler):
   """Custom request handler for the scheduler application"""
   
   def do_GET(self):
       """Handle GET requests"""
       # Check authentication
       if not auth_middleware.process_request(self):
           return
       
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
       # Special case for signup and signin - don't check auth
       if self.path == '/api/signup' or self.path == '/api/signin':
           content_length = int(self.headers['Content-Length'])
           post_data = self.rfile.read(content_length)
           data = json.loads(post_data.decode('utf-8'))
           
           if self.path == '/api/signup':
               self.handle_signup(data)
               return
           elif self.path == '/api/signin':
               self.handle_signin(data)
               return
       
       # Check authentication for other POST requests
       if not auth_middleware.process_request(self):
           return
       
       if self.path.startswith('/api/'):
           content_length = int(self.headers['Content-Length'])
           post_data = self.rfile.read(content_length)
           data = json.loads(post_data.decode('utf-8'))
           self.handle_api_post(self.path, data)
           return
       
       # Handle form submissions
       if self.path == '/fake_signup':
           self.handle_fake_signup()
           return
       elif self.path == '/fake_signin':
           self.handle_fake_signin()
           return
       
       self.send_error(HTTPStatus.NOT_FOUND)
   
   def do_PUT(self):
       """Handle PUT requests"""
       # Check authentication
       if not auth_middleware.process_request(self):
           return
       
       if self.path.startswith('/api/'):
           content_length = int(self.headers['Content-Length'])
           post_data = self.rfile.read(content_length)
           data = json.loads(post_data.decode('utf-8'))
           self.handle_api_put(self.path, data)
           return
       
       self.send_error(HTTPStatus.NOT_FOUND)
   
   def do_DELETE(self):
       """Handle DELETE requests"""
       # Check authentication
       if not auth_middleware.process_request(self):
           return
       
       if self.path.startswith('/api/'):
           self.handle_api_delete(self.path)
           return
       
       self.send_error(HTTPStatus.NOT_FOUND)
   
   def handle_api_get(self, path, query_string):
       """Handle API GET requests"""
       query_params = urllib.parse.parse_qs(query_string)
       
       # Get company ID from user session if available
       company_id = None
       if hasattr(self, 'user') and self.user:
           company_id = self.user.get('id')
       
       # Create company-specific service instances
       employee_svc = EmployeeService(company_id)
       business_svc = BusinessService(company_id)
       station_svc = StationService(company_id)
       timeclock_svc = TimeClockService(employee_svc, company_id)
       schedule_svc = ScheduleService(employee_svc, station_svc, business_svc, company_id)
       
       # User endpoint
       if path == '/api/user':
           # Get the current user from the cookie
           cookie_str = self.headers.get('Cookie', '')
           cookie = cookies.SimpleCookie()
           cookie.load(cookie_str)
           
           if 'session_id' in cookie:
               session_id = cookie['session_id'].value
               user = user_service.validate_session(session_id)
               
               if user:
                   self.send_json_response(user)
                   return
           
           self.send_json_response({"error": "Not authenticated"}, 401)
           return
       
       # Logout endpoint
       if path == '/api/logout':
           # Get the session ID from the cookie
           cookie_str = self.headers.get('Cookie', '')
           cookie = cookies.SimpleCookie()
           cookie.load(cookie_str)
           
           if 'session_id' in cookie:
               session_id = cookie['session_id'].value
               success = user_service.logout(session_id)
               
               if success:
                   # Clear the cookie
                   cookie = cookies.SimpleCookie()
                   cookie['session_id'] = ''
                   cookie['session_id']['path'] = '/'
                   cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
                   
                   self.send_response(HTTPStatus.OK)
                   self.send_header('Content-Type', 'application/json')
                   self.send_header('Set-Cookie', cookie['session_id'].OutputString())
                   self.end_headers()
                   self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                   return
           
           self.send_json_response({"error": "Not authenticated"}, 401)
           return
       
       # Employees endpoint
       if path == '/api/employees':
           employees = employee_svc.get_all_employees()
           self.send_json_response(employees)
           return
       
       # Single employee endpoint
       if path.startswith('/api/employees/'):
           employee_id = int(path.split('/')[-1])
           employee = employee_svc.get_employee(employee_id)
           if not employee:
               self.send_json_response({"error": "Employee not found"}, 404)
               return
           self.send_json_response(employee)
           return
       
       # Stations endpoint
       if path == '/api/stations':
           stations = station_svc.get_all_stations()
           self.send_json_response(stations)
           return
       
       # Single station endpoint
       if path.startswith('/api/stations/'):
           station_id = int(path.split('/')[-1])
           station = station_svc.get_station(station_id)
           if not station:
               self.send_json_response({"error": "Station not found"}, 404)
               return
           self.send_json_response(station)
           return
       
       # Business endpoint
       if path == '/api/business':
           business_info = business_svc.get_business_info()
           self.send_json_response(business_info)
           return
       
       # Time clock status
       if path == '/api/timeclock/status':
           statuses = timeclock_svc.get_all_statuses()
           self.send_json_response(statuses)
           return
       
       # Employee time clock status
       if path.startswith('/api/timeclock/status/'):
           employee_id = int(path.split('/')[-1])
           status = timeclock_svc.get_employee_status(employee_id)
           self.send_json_response(status)
           return
       
       # Time clock activity
       if path == '/api/timeclock/activity':
           limit = int(query_params.get('limit', [20])[0])
           activity = timeclock_svc.get_recent_activity(limit)
           self.send_json_response({"activity": activity})
           return
       
       # Clocked in employees
       if path == '/api/timeclock/clocked-in':
           employees = timeclock_svc.get_clocked_in_employees()
           self.send_json_response({"employees": employees})
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
           
           try:
               start_date = datetime.datetime.fromisoformat(start_date_str)
               end_date = datetime.datetime.fromisoformat(end_date_str)
               report = timeclock_svc.generate_report(start_date, end_date)
               self.send_json_response(report)
           except ValueError:
               self.send_json_response({"error": "Invalid date format"}, 400)
           return
       
       # Time clock settings
       if path == '/api/timeclock/settings':
           settings = timeclock_svc.get_settings()
           self.send_json_response(settings)
           return
       
       # Schedule endpoint - Updated to use schedule service
       if path == '/api/schedule':
           schedule_data = schedule_svc.get_schedule_with_metadata(include_draft=True)
           self.send_json_response(schedule_data)
           return
       
       # Official schedule endpoint - Updated to use schedule service
       if path == '/api/official_schedule':
           # Only return published schedule
           if schedule_svc.is_schedule_published():
               schedule_data = schedule_svc.get_schedule_with_metadata(include_draft=False)
               self.send_json_response(schedule_data)
           else:
               # Return error if no schedule is published
               self.send_json_response({"error": "Schedule is not published"}, 400)
           return
       
       # If we get here, the endpoint wasn't found
       self.send_error(HTTPStatus.NOT_FOUND)
   
   def handle_api_post(self, path, data):
       """Handle API POST requests"""
       
       # Get company ID from user session if available
       company_id = None
       if hasattr(self, 'user') and self.user:
           company_id = self.user.get('id')
       
       # Create company-specific service instances
       employee_svc = EmployeeService(company_id)
       business_svc = BusinessService(company_id)
       station_svc = StationService(company_id)
       timeclock_svc = TimeClockService(employee_svc, company_id)
       schedule_svc = ScheduleService(employee_svc, station_svc, business_svc, company_id)
       
       # Theme endpoint
       if path == '/api/theme':
           # Get the current user from the cookie
           cookie_str = self.headers.get('Cookie', '')
           cookie = cookies.SimpleCookie()
           cookie.load(cookie_str)
           
           if 'session_id' in cookie:
               session_id = cookie['session_id'].value
               user = user_service.validate_session(session_id)
               
               if user and 'theme' in data:
                   success = user_service.update_user_theme(user['id'], data['theme'])
                   
                   if success:
                       self.send_json_response({"success": True})
                       return
           
           self.send_json_response({"error": "Not authenticated"}, 401)
           return
       
       # Employees endpoint
       if path == '/api/employees':
           result = employee_svc.add_employee(data)
           
           if "error" in result:
               self.send_json_response(result, 400)
           else:
               self.send_json_response(result, 201)
           return
       
       # Stations endpoint
       if path == '/api/stations':
           result = station_svc.add_station(data)
           
           if "error" in result:
               self.send_json_response(result, 400)
           else:
               self.send_json_response(result, 201)
           return
       
       # Business endpoint
       if path == '/api/business':
           result = business_svc.update_business_info(data)
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
               
               # Find the employee by punch code
               employee = employee_svc.find_employee_by_punch_code(punch_code)
               if not employee:
                   self.send_json_response({"error": f"No employee found with punch code: {punch_code}"}, 404)
                   return
               
               employee_id = employee["id"]
           
           # Process the punch
           result = timeclock_svc.record_punch(employee_id, timestamp, manual)
           
           if isinstance(result, tuple) and len(result) == 2 and "error" in result[0]:
               self.send_json_response(result[0], result[1])
           else:
               self.send_json_response(result)
           return
       
       # Time clock settings
       if path == '/api/timeclock/settings':
           result = timeclock_svc.update_settings(data)
           self.send_json_response(result)
           return
       
       # Schedule endpoint - Updated to use schedule service
       if path == '/api/schedule':
           action = data.get('action', 'draft')
           shifts = data.get('shifts', [])
           
           if action == 'publish':
               result = schedule_svc.publish_schedule(shifts)
           else:
               result = schedule_svc.save_draft_schedule(shifts)
           
           self.send_json_response(result)
           return
       
       # If we get here, the endpoint wasn't found
       self.send_error(HTTPStatus.NOT_FOUND)
   
   def handle_api_put(self, path, data):
       """Handle API PUT requests"""
       
       # Get company ID from user session if available
       company_id = None
       if hasattr(self, 'user') and self.user:
           company_id = self.user.get('id')
       
       # Create company-specific service instances
       employee_svc = EmployeeService(company_id)
       business_svc = BusinessService(company_id)
       station_svc = StationService(company_id)
       
       # Employee update endpoint
       if path.startswith('/api/employees/'):
           employee_id = int(path.split('/')[-1])
           result = employee_svc.update_employee(employee_id, data)
           
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
           result = station_svc.update_station(station_id, data)
           
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
       
       # Get company ID from user session if available
       company_id = None
       if hasattr(self, 'user') and self.user:
           company_id = self.user.get('id')
       
       # Create company-specific service instances
       employee_svc = EmployeeService(company_id)
       station_svc = StationService(company_id)
       
       # Employee delete endpoint
       if path.startswith('/api/employees/'):
           employee_id = int(path.split('/')[-1])
           result = employee_svc.delete_employee(employee_id)
           
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
           result = station_svc.delete_station(station_id)
           
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
   
   def handle_signup(self, data):
       """Handle user signup"""
       # Validate required fields
       required_fields = ['email', 'password', 'name', 'company_name']
       for field in required_fields:
           if field not in data or not data[field]:
               self.send_json_response({"error": f"Missing required field: {field}"}, 400)
               return
       
       # Create the user
       result = user_service.create_user(data)
       
       if "error" in result:
           self.send_json_response(result, 400)
           return
       
       # Set the session cookie
       cookie = cookies.SimpleCookie()
       cookie['session_id'] = result['session_id']
       cookie['session_id']['path'] = '/'
       cookie['session_id']['httponly'] = True
       cookie['session_id']['samesite'] = 'Lax'
       cookie['session_id']['max-age'] = 60 * 60 * 24 * 7  # 7 days
       
       # Send the response
       self.send_response(HTTPStatus.OK)
       self.send_header('Content-Type', 'application/json')
       self.send_header('Set-Cookie', cookie['session_id'].OutputString())
       self.end_headers()
       
       # Remove the session_id from the response
       del result['session_id']
       
       # Send the user data
       self.wfile.write(json.dumps(result).encode('utf-8'))
   
   def handle_signin(self, data):
       """Handle user signin"""
       # Validate required fields
       if 'email' not in data or not data['email'] or 'password' not in data or not data['password']:
           self.send_json_response({"error": "Email and password are required"}, 400)
           return
       
       # Authenticate the user
       user = user_service.authenticate_user(data['email'], data['password'])
       
       if not user:
           self.send_json_response({"error": "Invalid email or password"}, 401)
           return
       
       # Set the session cookie
       cookie = cookies.SimpleCookie()
       cookie['session_id'] = user['session_id']
       cookie['session_id']['path'] = '/'
       cookie['session_id']['httponly'] = True
       cookie['session_id']['samesite'] = 'Lax'
       cookie['session_id']['max-age'] = 60 * 60 * 24 * 7  # 7 days
       
       # Send the response
       self.send_response(HTTPStatus.OK)
       self.send_header('Content-Type', 'application/json')
       self.send_header('Set-Cookie', cookie['session_id'].OutputString())
       self.end_headers()
       
       # Remove the session_id from the response
       del user['session_id']
       
       # Send the user data
       self.wfile.write(json.dumps(user).encode('utf-8'))
   
   def handle_fake_signup(self):
       """Handle the fake signup form submission"""
       content_length = int(self.headers['Content-Length'])
       post_data = self.rfile.read(content_length).decode('utf-8')
       form_data = parse_qs(post_data)
       
       # Extract form data
       email = form_data.get('email', [''])[0]
       password = form_data.get('password', [''])[0]
       name = form_data.get('fullName', [''])[0]
       company_name = form_data.get('companyName', [''])[0]
       
       # Create the user
       result = user_service.create_user({
           'email': email,
           'password': password,
           'name': name,
           'company_name': company_name
       })
       
       if "error" in result:
           # Redirect to signup page with error
           self.send_response(302)
           self.send_header('Location', '/pages/getstarted.html?error=' + urllib.parse.quote(result['error']))
           self.end_headers()
           return
       
       # Set the session cookie
       cookie = cookies.SimpleCookie()
       cookie['session_id'] = result['session_id']
       cookie['session_id']['path'] = '/'
       cookie['session_id']['httponly'] = True
       cookie['session_id']['samesite'] = 'Lax'
       cookie['session_id']['max-age'] = 60 * 60 * 24 * 7  # 7 days
       
       # Redirect to welcome page
       self.send_response(302)
       self.send_header('Location', '/pages/welcome.html')
       self.send_header('Set-Cookie', cookie['session_id'].OutputString())
       self.end_headers()
   
   def handle_fake_signin(self):
       """Handle the fake signin form submission"""
       content_length = int(self.headers['Content-Length'])
       post_data = self.rfile.read(content_length).decode('utf-8')
       form_data = parse_qs(post_data)
       
       # Extract form data
       email = form_data.get('email', [''])[0]
       password = form_data.get('password', [''])[0]
       
       # Authenticate the user
       user = user_service.authenticate_user(email, password)
       
       if not user:
           # Redirect to signin page with error
           self.send_response(302)
           self.send_header('Location', '/pages/signin.html?error=Invalid+email+or+password')
           self.end_headers()
           return
       
       # Set the session cookie
       cookie = cookies.SimpleCookie()
       cookie['session_id'] = user['session_id']
       cookie['session_id']['path'] = '/'
       cookie['session_id']['httponly'] = True
       cookie['session_id']['samesite'] = 'Lax'
       cookie['session_id']['max-age'] = 60 * 60 * 24 * 7  # 7 days
       
       # Redirect to welcome page
       self.send_response(302)
       self.send_header('Location', '/pages/welcome.html')
       self.send_header('Set-Cookie', cookie['session_id'].OutputString())
       self.end_headers()
   
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

