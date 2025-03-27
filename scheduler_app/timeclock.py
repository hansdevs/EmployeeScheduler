from flask import request, jsonify
import json
import os
import datetime
from myapp import app, get_employees  # Import the Flask app and get_employees function

# Get the path to the data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')
timeclock_file = os.path.join(data_dir, 'timeclock.json')

# Load timeclock data
def load_timeclock_data():
    if os.path.exists(timeclock_file):
        with open(timeclock_file, 'r') as f:
            return json.load(f)
    return {"settings": {"enforce_schedule": True, "allow_remote_punch": True, "require_photo": False}, "punches": []}

# Save timeclock data
def save_timeclock_data(data):
    with open(timeclock_file, 'w') as f:
        json.dump(data, f, indent=2)

# Find employee by ID or custom ID
def find_employee(employee_id, get_employees_func):
    # Get employees from the shared data
    employees = get_employees_func()
    
    # Debug print to verify what we're getting
    print(f"Type of employees in find_employee: {type(employees)}")
    
    # Try to find by ID or custom_id
    for emp in employees:
        if str(emp.get('id')) == str(employee_id) or emp.get('custom_id') == employee_id:
            return emp
    
    return None

# This function is needed for compatibility with other parts of the application
def record_punch(employee_id, timestamp=None, punch_type=None, photo_data=None, get_employees_func=None):
    """
    Record a punch for an employee
    
    Parameters:
    - employee_id: ID of the employee
    - timestamp: ISO format timestamp (default: current time)
    - punch_type: 'in' or 'out' (default: auto-determine based on last punch)
    - photo_data: Optional photo data for verification (default: None)
    - get_employees_func: Function to get employees (passed from app.py)
    """
    try:
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()
        
        # Find employee
        employee = find_employee(employee_id, get_employees_func)
        if not employee:
            return {"error": f"Employee not found with ID: {employee_id}"}, 404
        
        # Load timeclock data
        timeclock_data = load_timeclock_data()
        
        # If punch_type is not specified, determine it
        if punch_type is None:
            punch_type = "in"
            
            # Check if employee is already clocked in
            employee_punches = [p for p in timeclock_data.get('punches', []) 
                               if p.get('employee_id') == employee['id']]
            
            if employee_punches:
                # Sort by timestamp (newest first)
                employee_punches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                last_punch = employee_punches[0]
                
                # If last punch was "in", this should be "out"
                if last_punch.get('type') == 'in':
                    punch_type = "out"
        
        # Create punch record
        punch = {
            "employee_id": employee['id'],
            "employee_name": employee['name'],
            "timestamp": timestamp,
            "type": punch_type
        }
        
        # Add photo data if provided
        if photo_data:
            punch["photo_data"] = photo_data
        
        # Add to punches
        timeclock_data['punches'].append(punch)
        save_timeclock_data(timeclock_data)
        
        return {"employee": employee, "punch": punch}
    except Exception as e:
        print(f"ERROR in record_punch function: {e}")
        return {"error": str(e)}, 500

def setup_timeclock_routes(app, get_employees_func):
    """
    Setup all timeclock routes with the Flask app
    
    Parameters:
    - app: Flask app instance
    - get_employees_func: Function to get employees
    """
    
    @app.route('/api/timeclock/settings', methods=['GET'])
    def fetch_timeclock_settings():
        timeclock_data = load_timeclock_data()
        return jsonify(timeclock_data.get('settings', {}))

    @app.route('/api/timeclock/settings', methods=['POST'])
    def update_timeclock_settings():
        try:
            data = request.get_json(force=True)
            timeclock_data = load_timeclock_data()
            
            # Update settings
            timeclock_data['settings'] = {
                'enforce_schedule': data.get('enforce_schedule', True),
                'allow_remote_punch': data.get('allow_remote_punch', True),
                'require_photo': data.get('require_photo', False)
            }
            
            # Save to file
            save_timeclock_data(timeclock_data)
            
            return jsonify({"success": True, "settings": timeclock_data['settings']})
        except Exception as e:
            print(f"Error updating timeclock settings: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/timeclock/punch', methods=['POST'])
    def punch_timeclock():
        try:
            data = request.get_json(force=True)
            employee_id = data.get('employee_id')
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            photo_data = data.get('photo_data')  # Optional photo data
            
            print(f"Received punch request for employee_id: '{employee_id}' (type: {type(employee_id)})")
            
            # Get the current list of employees for logging
            employees = get_employees_func()
            print(f"Current EMPLOYEES list at time of punch request: {employees}")
            
            # Find employee
            employee = find_employee(employee_id, get_employees_func)
            if not employee:
                return jsonify({"error": f"Employee not found with ID: {employee_id}"}), 404
            
            # Load timeclock data
            timeclock_data = load_timeclock_data()
            
            # Determine punch type (in or out)
            punch_type = "in"
            
            # Check if employee is already clocked in
            employee_punches = [p for p in timeclock_data.get('punches', []) 
                               if p.get('employee_id') == employee['id']]
            
            if employee_punches:
                # Sort by timestamp (newest first)
                employee_punches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                last_punch = employee_punches[0]
                
                # If last punch was "in", this should be "out"
                if last_punch.get('type') == 'in':
                    punch_type = "out"
            
            # Create punch record
            punch = {
                "employee_id": employee['id'],
                "employee_name": employee['name'],
                "timestamp": timestamp,
                "type": punch_type
            }
            
            # Add photo data if provided
            if photo_data:
                punch["photo_data"] = photo_data
            
            # Add to punches
            timeclock_data['punches'].append(punch)
            save_timeclock_data(timeclock_data)
            
            return jsonify({"employee": employee, "punch": punch})
        except Exception as e:
            print(f"Error processing punch: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/timeclock/activity', methods=['GET'])
    def get_timeclock_activity():
        try:
            timeclock_data = load_timeclock_data()
            punches = timeclock_data.get('punches', [])
            
            # Sort by timestamp (newest first)
            punches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limit to most recent 20 punches
            recent_activity = punches[:20]
            
            return jsonify({"activity": recent_activity})
        except Exception as e:
            print(f"Error getting timeclock activity: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/timeclock/clocked-in', methods=['GET'])
    def get_clocked_in_employees():
        try:
            timeclock_data = load_timeclock_data()
            punches = timeclock_data.get('punches', [])
            
            # Get all employees
            all_employees = get_employees_func()
            
            # Create a dictionary to track the latest punch for each employee
            latest_punches = {}
            
            for punch in punches:
                emp_id = punch.get('employee_id')
                if emp_id not in latest_punches or punch.get('timestamp', '') > latest_punches[emp_id].get('timestamp', ''):
                    latest_punches[emp_id] = punch
            
            # Filter for employees who are clocked in
            clocked_in = []
            for emp_id, punch in latest_punches.items():
                if punch.get('type') == 'in':
                    # Find the employee details
                    employee = next((e for e in all_employees if e.get('id') == emp_id), None)
                    if employee:
                        clocked_in.append({
                            "id": employee.get('id'),
                            "name": employee.get('name'),
                            "color": employee.get('color', 'block-blue'),
                            "punch_time": punch.get('timestamp')
                        })
            
            return jsonify({"employees": clocked_in})
        except Exception as e:
            print(f"Error getting clocked in employees: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/timeclock/register-employee', methods=['POST'])
    def register_employee_with_timeclock():
        try:
            data = request.get_json(force=True)
            
            # This endpoint doesn't need to do anything special
            # since we're now sharing employee data between modules
            # But we'll keep it for compatibility with the frontend
            
            return jsonify({"success": True, "message": "Employee registered with timeclock system"})
        except Exception as e:
            print(f"Error registering employee with timeclock: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/timeclock/punch_endpoint', methods=['POST'])
    def punch_endpoint():
        try:
            data = request.get_json(force=True)
            employee_id = data.get('employee_id')
            punch_type = data.get('punch_type')  # Optional
            timestamp = data.get('timestamp')    # Optional
            photo_data = data.get('photo_data')  # Optional
            
            result = record_punch(employee_id, timestamp, punch_type, photo_data, get_employees_func)
            
            # Check if result is a tuple (response, status_code)
            if isinstance(result, tuple) and len(result) == 2:
                return jsonify(result[0]), result[1]
            
            # Otherwise, it's just the response data
            return jsonify(result)
        except Exception as e:
            print(f"Error in punch_endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    # Initialize timeclock data if it doesn't exist
    if not os.path.exists(timeclock_file):
        initial_data = {
            "settings": {
                "enforce_schedule": True,
                "allow_remote_punch": True,
                "require_photo": False
            },
            "punches": []
        }
        save_timeclock_data(initial_data)

    print("Timeclock routes have been set up successfully!")
    return record_punch

if __name__ == '__main__':
    # This won't run if imported by myapp.py
    # But allows for testing this file directly
    app.run(debug=True)

