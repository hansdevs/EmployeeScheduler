# Add these imports at the top of your myapp.py file
import os
import json
import datetime
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# File paths for data storage
EMPLOYEES_FILE = 'data/employees.json'
TIMECLOCK_FILE = 'data/timeclock.json'
TIMECLOCK_LOGS_FILE = 'data/timeclock_logs.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Helper function to load JSON data
def load_json(file_path, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Create the file with default data if it doesn't exist
            with open(file_path, 'w') as f:
                json.dump(default, f)
            return default
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default

# Helper function to save JSON data
def save_json(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")
        return False

# Serve static files
@app.route('/pages/<path:path>')
def serve_pages(path):
    return send_from_directory('static/pages', path)

@app.route('/styles/<path:path>')
def serve_styles(path):
    return send_from_directory('static/styles', path)

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)

@app.route('/images/<path:path>')
def serve_images(path):
    return send_from_directory('static/images', path)

# Default route
@app.route('/')
def index():
    return redirect('/pages/welcome.html')

# API Routes for Employees
@app.route('/api/employees', methods=['GET', 'POST'])
def handle_employees():
    if request.method == 'GET':
        employees = load_json(EMPLOYEES_FILE, [])
        return jsonify(employees)
    
    elif request.method == 'POST':
        employees = load_json(EMPLOYEES_FILE, [])
        new_employee = request.json
        
        # Generate a new ID if not provided
        if 'id' not in new_employee:
            new_id = 1
            if employees:
                new_id = max(emp['id'] for emp in employees) + 1
            new_employee['id'] = new_id
        
        employees.append(new_employee)
        save_json(EMPLOYEES_FILE, employees)
        return jsonify(new_employee), 201

@app.route('/api/employees/<int:employee_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_employee(employee_id):
    employees = load_json(EMPLOYEES_FILE, [])
    
    # Find the employee
    employee_index = None
    for i, emp in enumerate(employees):
        if emp['id'] == employee_id:
            employee_index = i
            break
    
    if employee_index is None:
        return jsonify({"error": "Employee not found"}), 404
    
    if request.method == 'GET':
        return jsonify(employees[employee_index])
    
    elif request.method == 'PUT':
        update_data = request.json
        # Update only the fields provided
        for key, value in update_data.items():
            employees[employee_index][key] = value
        save_json(EMPLOYEES_FILE, employees)
        return jsonify(employees[employee_index])
    
    elif request.method == 'DELETE':
        deleted_employee = employees.pop(employee_index)
        save_json(EMPLOYEES_FILE, employees)
        return jsonify(deleted_employee)

# Time Clock API Routes
@app.route('/api/timeclock/status', methods=['GET'])
def get_timeclock_status():
    """Get the current status of all employees (clocked in or out)"""
    timeclock_data = load_json(TIMECLOCK_FILE, {"employees": {}})
    return jsonify(timeclock_data)

@app.route('/api/timeclock/status/<int:employee_id>', methods=['GET'])
def get_employee_timeclock_status(employee_id):
    """Get the current status of a specific employee"""
    timeclock_data = load_json(TIMECLOCK_FILE, {"employees": {}})
    employee_status = timeclock_data["employees"].get(str(employee_id), {"status": "out", "last_punch": None})
    return jsonify(employee_status)

@app.route('/api/timeclock/punch', methods=['POST'])
def punch_timeclock():
    """Record a punch (in or out) for an employee"""
    data = request.json
    employee_id = data.get('employee_id')
    
    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400
    
    # Convert to string for JSON dictionary keys
    employee_id_str = str(employee_id)
    
    # Load current timeclock data
    timeclock_data = load_json(TIMECLOCK_FILE, {"employees": {}})
    
    # Load employee data to get name and other details
    employees = load_json(EMPLOYEES_FILE, [])
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    
    if not employee:
        return jsonify({"error": f"Employee with ID {employee_id} not found"}), 404
    
    # Get current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Determine if this is a punch in or out
    current_status = timeclock_data["employees"].get(employee_id_str, {"status": "out"})
    new_status = "out" if current_status.get("status") == "in" else "in"
    
    # Update the employee's status
    timeclock_data["employees"][employee_id_str] = {
        "status": new_status,
        "last_punch": timestamp,
        "name": employee.get("name", f"Employee {employee_id}"),
        "color": employee.get("color", "block-blue")
    }
    
    # Save the updated timeclock data
    save_json(TIMECLOCK_FILE, timeclock_data)
    
    # Record this punch in the logs
    timeclock_logs = load_json(TIMECLOCK_LOGS_FILE, [])
    
    punch_log = {
        "employee_id": employee_id,
        "employee_name": employee.get("name", f"Employee {employee_id}"),
        "timestamp": timestamp,
        "type": new_status,
        "color": employee.get("color", "block-blue")
    }
    
    # If this is a punch out, calculate duration from last punch in
    if new_status == "out":
        # Find the most recent punch in for this employee
        for log in reversed(timeclock_logs):
            if log["employee_id"] == employee_id and log["type"] == "in":
                # Calculate duration
                punch_in_time = datetime.datetime.fromisoformat(log["timestamp"])
                punch_out_time = datetime.datetime.fromisoformat(timestamp)
                duration_seconds = (punch_out_time - punch_in_time).total_seconds()
                duration_minutes = round(duration_seconds / 60)
                
                # Add duration to the log
                punch_log["duration_minutes"] = duration_minutes
                break
    
    timeclock_logs.append(punch_log)
    save_json(TIMECLOCK_LOGS_FILE, timeclock_logs)
    
    return jsonify({
        "success": True,
        "employee": employee,
        "punch": {
            "type": new_status,
            "timestamp": timestamp
        }
    })

@app.route('/api/timeclock/activity', methods=['GET'])
def get_timeclock_activity():
    """Get recent timeclock activity"""
    # Load the timeclock logs
    timeclock_logs = load_json(TIMECLOCK_LOGS_FILE, [])
    
    # Sort by timestamp (newest first) and limit to 20 entries
    recent_activity = sorted(timeclock_logs, key=lambda x: x["timestamp"], reverse=True)[:20]
    
    return jsonify({"activity": recent_activity})

@app.route('/api/timeclock/clocked-in', methods=['GET'])
def get_clocked_in_employees():
    """Get a list of currently clocked in employees"""
    timeclock_data = load_json(TIMECLOCK_FILE, {"employees": {}})
    
    clocked_in = []
    for emp_id, status in timeclock_data["employees"].items():
        if status["status"] == "in":
            clocked_in.append({
                "id": int(emp_id),
                "name": status.get("name", f"Employee {emp_id}"),
                "punch_time": status.get("last_punch"),
                "color": status.get("color", "block-blue")
            })
    
    return jsonify({"employees": clocked_in})

@app.route('/api/timeclock/report', methods=['GET'])
def get_timeclock_report():
    """Generate a report of employee hours"""
    # Get date range from query parameters (default to last 7 days)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        if start_date_str:
            start_date = datetime.datetime.fromisoformat(start_date_str)
        else:
            # Default to 7 days ago
            start_date = datetime.datetime.now() - datetime.timedelta(days=7)
            
        if end_date_str:
            end_date = datetime.datetime.fromisoformat(end_date_str)
        else:
            # Default to now
            end_date = datetime.datetime.now()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    # Load the timeclock logs
    timeclock_logs = load_json(TIMECLOCK_LOGS_FILE, [])
    
    # Filter logs by date range
    filtered_logs = []
    for log in timeclock_logs:
        log_time = datetime.datetime.fromisoformat(log["timestamp"])
        if start_date <= log_time <= end_date:
            filtered_logs.append(log)
    
    # Group by employee and calculate total hours
    employee_hours = {}
    
    # First, organize punch pairs (in/out)
    for log in filtered_logs:
        emp_id = log["employee_id"]
        if emp_id not in employee_hours:
            employee_hours[emp_id] = {
                "name": log["employee_name"],
                "total_minutes": 0,
                "punches": []
            }
        
        employee_hours[emp_id]["punches"].append(log)
    
    # Calculate hours for each employee
    for emp_id, data in employee_hours.items():
        # Sort punches by timestamp
        punches = sorted(data["punches"], key=lambda x: x["timestamp"])
        
        # Process punch pairs
        total_minutes = 0
        punch_pairs = []
        
        i = 0
        while i < len(punches) - 1:
            if punches[i]["type"] == "in" and punches[i+1]["type"] == "out":
                # Calculate duration
                in_time = datetime.datetime.fromisoformat(punches[i]["timestamp"])
                out_time = datetime.datetime.fromisoformat(punches[i+1]["timestamp"])
                duration_minutes = round((out_time - in_time).total_seconds() / 60)
                
                total_minutes += duration_minutes
                
                punch_pairs.append({
                    "in": punches[i]["timestamp"],
                    "out": punches[i+1]["timestamp"],
                    "duration_minutes": duration_minutes
                })
                
                i += 2  # Skip to next potential pair
            else:
                i += 1  # Skip unpaired punch
        
        employee_hours[emp_id]["total_minutes"] = total_minutes
        employee_hours[emp_id]["punch_pairs"] = punch_pairs
        employee_hours[emp_id]["hours"] = round(total_minutes / 60, 2)
        
        # Remove the raw punches from the response
        del employee_hours[emp_id]["punches"]
    
    return jsonify({
        "report": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "employees": employee_hours
        }
    })

@app.route('/api/timeclock/settings', methods=['GET', 'POST'])
def handle_timeclock_settings():
    """Get or update timeclock settings"""
    settings_file = 'data/timeclock_settings.json'
    
    if request.method == 'GET':
        settings = load_json(settings_file, {
            "enforce_schedule": True,
            "allow_remote_punch": True,
            "require_photo": False
        })
        return jsonify(settings)
    
    elif request.method == 'POST':
        current_settings = load_json(settings_file, {})
        new_settings = request.json
        
        # Update settings
        for key, value in new_settings.items():
            current_settings[key] = value
        
        save_json(settings_file, current_settings)
        return jsonify(current_settings)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

