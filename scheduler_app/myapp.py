from flask import Flask, request, jsonify, send_from_directory
import json
import os
import datetime

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Get the path to the data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Global variable to store employees
EMPLOYEES = []

# Load employees from data source
def load_employees():
  global EMPLOYEES
  try:
      # Try to load from employees.json if it exists
      employees_file = os.path.join(data_dir, 'employees.json')
      if os.path.exists(employees_file):
          with open(employees_file, 'r') as f:
              EMPLOYEES = json.load(f)
      else:
          # Initialize with empty list if file doesn't exist
          EMPLOYEES = []
  except Exception as e:
      print(f"Error loading employees: {e}")
      EMPLOYEES = []
  return EMPLOYEES

# Save employees to data source
def save_employees():
  try:
      employees_file = os.path.join(data_dir, 'employees.json')
      with open(employees_file, 'w') as f:
          json.dump(EMPLOYEES, f, indent=2)
  except Exception as e:
      print(f"Error saving employees: {e}")

# Function to get employees - can be imported by timeclock.py
def get_employees():
  global EMPLOYEES
  if not EMPLOYEES:
      load_employees()
  return EMPLOYEES  # Return the actual list, not a Response

# Routes for static files
@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'pages/index.html')

@app.route('/pages/<path:path>')
def serve_pages(path):
  return send_from_directory(os.path.join(app.static_folder, 'pages'), path)

@app.route('/js/<path:path>')
def serve_js(path):
  return send_from_directory(os.path.join(app.static_folder, 'js'), path)

@app.route('/styles/<path:path>')
def serve_styles(path):
  return send_from_directory(os.path.join(app.static_folder, 'styles'), path)

@app.route('/images/<path:path>')
def serve_images(path):
  return send_from_directory(os.path.join(app.static_folder, 'images'), path)

# API Routes
@app.route('/api/employees', methods=['GET'])
def get_all_employees():
  employees = get_employees()
  return jsonify(employees)

@app.route('/api/employees', methods=['POST'])
def add_employee():
  try:
      data = request.get_json(force=True)
      print("==== EMPLOYEE CREATION REQUEST ====")
      print(f"Request method: {request.method}")
      print(f"Request headers: {request.headers}")
      print(f"Raw request data: {request.data.decode('utf-8')}")
      print(f"Parsed JSON data (force=True): {data}")
      
      name = data.get('name', '').strip()
      type_val = data.get('type', '').strip()
      color = data.get('color', 'block-blue')
      custom_id = data.get('custom_id')
      
      if custom_id:
          custom_id = str(custom_id).strip()
      
      print(f"Parsed data: name={name}, type={type_val}, color={color}, custom_id={custom_id}")
      
      if not name:
          return jsonify({"error": "Employee name is required"}), 400
      
      # Check if custom_id is already in use
      employees = get_employees()
      if custom_id and any(emp.get('custom_id') == custom_id for emp in employees):
          return jsonify({"error": "This ID/Punch Code is already in use"}), 400
      
      # Generate a new ID (max existing ID + 1)
      new_id = 1
      if employees:
          new_id = max(emp.get('id', 0) for emp in employees) + 1
      
      # Create new employee
      new_employee = {
          'id': new_id,
          'name': name,
          'type': type_val,
          'color': color,
          'custom_id': custom_id
      }
      
      print(f"Adding new employee: {new_employee}")
      
      # Add to global list
      employees.append(new_employee)
      
      # Save to file
      save_employees()
      
      print(f"Current employees: {employees}")
      
      return jsonify(new_employee)
  except Exception as e:
      print(f"Error adding employee: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
  try:
      data = request.get_json(force=True)
      
      name = data.get('name', '').strip()
      type_val = data.get('type', '').strip()
      custom_id = data.get('custom_id')
      
      if custom_id:
          custom_id = str(custom_id).strip()
      
      if not name:
          return jsonify({"error": "Employee name is required"}), 400
      
      # Check if custom_id is already in use by another employee
      employees = get_employees()
      if custom_id and any(emp.get('custom_id') == custom_id and emp.get('id') != employee_id for emp in employees):
          return jsonify({"error": "This ID/Punch Code is already in use by another employee"}), 400
      
      # Find and update employee
      for emp in employees:
          if emp.get('id') == employee_id:
              emp['name'] = name
              emp['type'] = type_val
              emp['custom_id'] = custom_id
              
              # Save to file
              save_employees()
              
              return jsonify(emp)
      
      return jsonify({"error": "Employee not found"}), 404
  except Exception as e:
      print(f"Error updating employee: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
  try:
      employees = get_employees()
      
      # Find employee index
      index = None
      for i, emp in enumerate(employees):
          if emp.get('id') == employee_id:
              index = i
              break
      
      if index is not None:
          # Remove employee
          removed = employees.pop(index)
          
          # Save to file
          save_employees()
          
          return jsonify({"success": True, "removed": removed})
      
      return jsonify({"error": "Employee not found"}), 404
  except Exception as e:
      print(f"Error deleting employee: {e}")
      return jsonify({"error": str(e)}), 500

# Business routes
@app.route('/api/business', methods=['GET'])
def get_business_info():
  try:
      business_file = os.path.join(data_dir, 'business.json')
      if os.path.exists(business_file):
          with open(business_file, 'r') as f:
              business_data = json.load(f)
      else:
          # Default business info
          business_data = {
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
      
      return jsonify(business_data)
  except Exception as e:
      print(f"Error getting business info: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/business', methods=['POST'])
def update_business_info():
  try:
      data = request.get_json(force=True)
      
      # Validate required fields
      name = data.get('name', '').strip()
      if not name:
          return jsonify({"error": "Business name is required"}), 400
      
      # Create business data object
      business_data = {
          "name": name,
          "industry": data.get('industry', '').strip(),
          "hours": data.get('hours', {})
      }
      
      # Save to file
      business_file = os.path.join(data_dir, 'business.json')
      with open(business_file, 'w') as f:
          json.dump(business_data, f, indent=2)
      
      return jsonify({"success": True, "business": business_data})
  except Exception as e:
      print(f"Error updating business info: {e}")
      return jsonify({"error": str(e)}), 500

# Stations routes
@app.route('/api/stations', methods=['GET'])
def get_stations():
  try:
      stations_file = os.path.join(data_dir, 'stations.json')
      if os.path.exists(stations_file):
          with open(stations_file, 'r') as f:
              stations = json.load(f)
      else:
          stations = []
      
      return jsonify(stations)
  except Exception as e:
      print(f"Error getting stations: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/stations', methods=['POST'])
def add_station():
  try:
      data = request.get_json(force=True)
      
      # Validate required fields
      name = data.get('name', '').strip()
      if not name:
          return jsonify({"error": "Station name is required"}), 400
      
      # Load existing stations
      stations_file = os.path.join(data_dir, 'stations.json')
      if os.path.exists(stations_file):
          with open(stations_file, 'r') as f:
              stations = json.load(f)
      else:
          stations = []
      
      # Generate a new ID (max existing ID + 1)
      new_id = 1
      if stations:
          new_id = max(st.get('id', 0) for st in stations) + 1
      
      # Create new station
      new_station = {
          'id': new_id,
          'name': name,
          'type': data.get('type', '').strip()
      }
      
      # Add to list
      stations.append(new_station)
      
      # Save to file
      with open(stations_file, 'w') as f:
          json.dump(stations, f, indent=2)
      
      return jsonify(new_station)
  except Exception as e:
      print(f"Error adding station: {e}")
      return jsonify({"error": str(e)}), 500

# Schedule routes
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
  try:
      # Load schedule data
      schedule_file = os.path.join(data_dir, 'schedule.json')
      if os.path.exists(schedule_file):
          with open(schedule_file, 'r') as f:
              schedule_data = json.load(f)
      else:
          schedule_data = {
              "schedule": [],
              "is_published": False
          }
      
      # Load business info
      business_file = os.path.join(data_dir, 'business.json')
      if os.path.exists(business_file):
          with open(business_file, 'r') as f:
              business_data = json.load(f)
      else:
          business_data = {
              "name": "Unnamed Business",
              "industry": "",
              "hours": {}
          }
      
      # Load employees
      employees = get_employees()
      
      # Load stations
      stations_file = os.path.join(data_dir, 'stations.json')
      if os.path.exists(stations_file):
          with open(stations_file, 'r') as f:
              stations = json.load(f)
      else:
          stations = []
      
      # Combine all data
      response_data = {
          "schedule": schedule_data.get("schedule", []),
          "is_published": schedule_data.get("is_published", False),
          "business": business_data,
          "employees": employees,
          "stations": stations
      }
      
      return jsonify(response_data)
  except Exception as e:
      print(f"Error getting schedule: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/schedule', methods=['POST'])
def update_schedule():
  try:
      data = request.get_json(force=True)
      
      # Get shifts and action
      shifts = data.get('shifts', [])
      action = data.get('action', 'draft')  # 'draft' or 'publish'
      
      # Create schedule data
      schedule_data = {
          "schedule": shifts,
          "is_published": action == 'publish',
          "last_updated": datetime.datetime.now().isoformat()
      }
      
      # Save to file
      schedule_file = os.path.join(data_dir, 'schedule.json')
      with open(schedule_file, 'w') as f:
          json.dump(schedule_data, f, indent=2)
      
      return jsonify({
          "status": "published" if action == 'publish' else "draft",
          "message": "Schedule has been " + ("published" if action == 'publish' else "saved as draft")
      })
  except Exception as e:
      print(f"Error updating schedule: {e}")
      return jsonify({"error": str(e)}), 500

@app.route('/api/official_schedule', methods=['GET'])
def get_official_schedule():
  try:
      # Load schedule data
      schedule_file = os.path.join(data_dir, 'schedule.json')
      if os.path.exists(schedule_file):
          with open(schedule_file, 'r') as f:
              schedule_data = json.load(f)
      else:
          schedule_data = {
              "schedule": [],
              "is_published": False
          }
      
      # Check if schedule is published
      if not schedule_data.get('is_published', False):
          return jsonify({"error": "Schedule is not published"}), 400
      
      # Load business info
      business_file = os.path.join(data_dir, 'business.json')
      if os.path.exists(business_file):
          with open(business_file, 'r') as f:
              business_data = json.load(f)
      else:
          business_data = {
              "name": "Unnamed Business",
              "industry": "",
              "hours": {}
          }
      
      # Load employees
      employees = get_employees()
      
      # Load stations
      stations_file = os.path.join(data_dir, 'stations.json')
      if os.path.exists(stations_file):
          with open(stations_file, 'r') as f:
              stations = json.load(f)
      else:
          stations = []
      
      # Combine all data
      response_data = {
          "schedule": schedule_data.get("schedule", []),
          "is_published": True,
          "business": business_data,
          "employees": employees,
          "stations": stations
      }
      
      return jsonify(response_data)
  except Exception as e:
      print(f"Error getting official schedule: {e}")
      return jsonify({"error": str(e)}), 500

# User routes
@app.route('/api/user', methods=['GET'])
def get_user():
  # For demo purposes, return a mock user
  return jsonify({
      "id": 1,
      "name": "Demo User",
      "email": "demo@example.com",
      "role": "admin",
      "theme": "light"
  })

@app.route('/api/theme', methods=['PUT'])
def update_theme():
  try:
      data = request.get_json(force=True)
      theme = data.get('theme', 'light')
      
      # In a real app, we would update the user's theme preference in a database
      # For this demo, we'll just return success
      
      return jsonify({
          "success": True,
          "theme": theme
      })
  except Exception as e:
      print(f"Error updating theme: {e}")
      return jsonify({"error": str(e)}), 500

# Fake auth routes for demo
@app.route('/fake_signin', methods=['POST'])
def fake_signin():
  # Redirect to welcome page
  return send_from_directory(app.static_folder, 'pages/welcome.html')

@app.route('/fake_signup', methods=['POST'])
def fake_signup():
  # Redirect to welcome page
  return send_from_directory(app.static_folder, 'pages/welcome.html')

# Timeclock endpoint that uses the record_punch function from timeclock.py
@app.route('/api/timeclock/punch_endpoint', methods=['POST'])
def punch_endpoint():
    try:
        from timeclock import record_punch
        
        data = request.get_json(force=True)
        employee_id = data.get('employee_id')
        punch_type = data.get('punch_type')  # Optional
        timestamp = data.get('timestamp')    # Optional
        photo_data = data.get('photo_data')  # Optional
        
        result = record_punch(employee_id, timestamp, punch_type, photo_data)
        
        # Check if result is a tuple (response, status_code)
        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        
        # Otherwise, it's just the response data
        return jsonify(result)
    except Exception as e:
        print(f"Error in punch_endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Load employees on startup
load_employees()

if __name__ == '__main__':
  app.run(debug=True)

