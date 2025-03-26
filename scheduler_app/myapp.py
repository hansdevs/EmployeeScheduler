from flask import Flask, jsonify, request, send_from_directory, redirect, session

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = "supersecretkey"

# =====================
# In-memory "database"
# =====================
BUSINESS_INFO = {
    "name": "John Doe's Retail Store",
    "industry": "Retail",
    # "requirements": ["Office Desk", "Office Desk"],
    "hours": {
        0: {"open": 8,  "close": 17},
        1: {"open": 8,  "close": 17},
        2: {"open": 8,  "close": 17},
        3: {"open": 8,  "close": 17},
        4: {"open": 8,  "close": 17},
        5: {"open": 0,  "close": 0},
        6: {"open": 0,  "close": 0},
    }
}

EMPLOYEES = []
STATIONS  = []
SCHEDULE  = []
SCHEDULE_PUBLISHED = False

# Just for demo: user theme info
USER_INFO = {
    "username": "DemoUser",
    "theme": "light"
}

# -------------------------
# Landing page (index.html)
# -------------------------
@app.route("/")
def serve_landing():
    # Serve /static/pages/index.html
    return send_from_directory(app.static_folder + "/pages", "index.html")

# -------------------------
# Protected pages: user must be logged_in
# -------------------------
PROTECTED_PAGES = {
    "welcome.html",
    "/pages/schedule.html",
    "/pages/business.html",
    "/pages/employees.html",
    "/pages/stations.html",
    "/pages/official.html"
}

@app.route("/pages/<path:filename>")
def serve_pages(filename):
    """
    If user tries to access a protected page but isn't logged in,
    redirect them to getstarted.html
    """
    if filename in PROTECTED_PAGES and not session.get("logged_in"):
        return redirect("/pages/getstarted.html")

    return send_from_directory(app.static_folder + "/pages", filename)

# Add this route to handle CSS files in the pages directory
@app.route("/pages/<path:filename>.css")
def serve_css(filename):
    return send_from_directory(app.static_folder + "/pages", f"{filename}.css", mimetype='text/css')

# Add this route to handle JS files
@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(app.static_folder + "/js", filename, mimetype='application/javascript')

# -------------------------
# Sign Up (fake) route
# -------------------------
@app.route("/fake_signup", methods=["POST"])
def fake_signup():
    """
    From getstarted.html:
      companyName, fullName, email, password
    Must be: test, test, test@gmail.com, password
    """
    companyName = request.form.get("companyName","").strip()
    fullName    = request.form.get("fullName","").strip()
    email       = request.form.get("email","").strip()
    password    = request.form.get("password","").strip()

    if (companyName == "test" and fullName == "test" and
        email == "test@gmail.com" and password == "password"):
        session["logged_in"] = True
        return redirect("/pages/welcome.html")
    else:
        return (
            "<h2>Invalid test credentials for sign-up.<br>"
            "Expected: companyName='test', fullName='test', "
            "email='test@gmail.com', password='password' (8 chars)</h2>"
        )

# -------------------------
# Sign In (fake) route
# -------------------------
@app.route("/fake_signin", methods=["POST"])
def fake_signin():
    """
    From signin.html:
      email, password
    Must be: test@gmail.com, password
    """
    email    = request.form.get("email","").strip()
    password = request.form.get("password","").strip()

    if email == "test@gmail.com" and password == "password":
        session["logged_in"] = True
        return redirect("/pages/welcome.html")
    else:
        return (
            "<h2>Invalid credentials for sign-in.<br>"
            "Use email='test@gmail.com', password='password'.</h2>"
        )

# -------------------------
# User/Theme endpoints
# -------------------------
@app.route("/api/user", methods=["GET"])
def get_user():
    return jsonify(USER_INFO)

@app.route("/api/theme", methods=["PUT"])
def update_theme():
    data = request.json or {}
    new_theme = data.get("theme", "light")
    USER_INFO["theme"] = new_theme
    return jsonify({"status": "ok", "theme": new_theme})

# -------------------------
# BUSINESS API
# -------------------------
@app.route("/api/business", methods=["GET"])
def get_business():
    return jsonify(BUSINESS_INFO)

@app.route("/api/business", methods=["POST"])
def update_business():
    global BUSINESS_INFO
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    BUSINESS_INFO["name"] = data.get("name", BUSINESS_INFO["name"])
    BUSINESS_INFO["industry"] = data.get("industry", BUSINESS_INFO["industry"])
    
    # Handle requirements if they exist in the data
    if "requirements" in data:
        reqs = data.get("requirements")
        if isinstance(reqs, str):
            reqs = [r.strip() for r in reqs.split(",") if r.strip()]
        BUSINESS_INFO["requirements"] = reqs
    
    hours = data.get("hours", {})
    for d in range(7):
        day_key = str(d) if isinstance(hours, dict) and str(d) in hours else d
        if day_key in hours:
            day_hours = hours[day_key]
            if d not in BUSINESS_INFO["hours"]:
                BUSINESS_INFO["hours"][d] = {"open": 0, "close": 0}
            
            BUSINESS_INFO["hours"][d]["open"] = day_hours.get("open", BUSINESS_INFO["hours"][d]["open"])
            BUSINESS_INFO["hours"][d]["close"] = day_hours.get("close", BUSINESS_INFO["hours"][d]["close"])

    return jsonify({"status": "ok", "business": BUSINESS_INFO})


# -------------------------
# EMPLOYEES API
# -------------------------
@app.route("/api/employees", methods=["GET"])
def get_employees():
    return jsonify(EMPLOYEES)

@app.route("/api/employees", methods=["POST"])
def add_employee():
    global EMPLOYEES
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    new_name  = data.get("name", "").strip()
    new_type  = data.get("type", "").strip()
    new_color = data.get("color", "block-blue").strip()
    custom_id = data.get("custom_id")
    
    if custom_id:
        custom_id = str(custom_id).strip()
        # Check if custom_id is already in use
        if any(e.get("custom_id") == custom_id for e in EMPLOYEES):
            return jsonify({"error": "This ID/Punch Code is already in use"}), 400

    if not new_name:
        return jsonify({"error": "Employee name required"}), 400

    new_id = max([e["id"] for e in EMPLOYEES], default=0) + 1
    new_employee = {
        "id": new_id,
        "name": new_name,
        "type": new_type,
        "color": new_color
    }
    
    if custom_id:
        new_employee["custom_id"] = custom_id
        
    EMPLOYEES.append(new_employee)
    return jsonify({"status": "ok", "employee": new_employee})

# UPDATE EMPLOYEE ENDPOINT
@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    global EMPLOYEES
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
        
    employee = next((e for e in EMPLOYEES if e["id"] == employee_id), None)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    # Check if custom_id is being updated and is not already in use by another employee
    if "custom_id" in data:
        custom_id = data["custom_id"]
        if custom_id:
            custom_id = str(custom_id).strip()
            # Check if custom_id is already in use by another employee
            if any(e.get("custom_id") == custom_id and e["id"] != employee_id for e in EMPLOYEES):
                return jsonify({"error": "This ID/Punch Code is already in use"}), 400
        employee["custom_id"] = custom_id
    
    if "name" in data and data["name"].strip():
        employee["name"] = data["name"].strip()
        
    if "type" in data:
        employee["type"] = data["type"].strip()
        
    if "color" in data and data["color"].strip():
        employee["color"] = data["color"].strip()
        
    return jsonify({"status": "ok", "employee": employee})

# DELETE EMPLOYEE ENDPOINT
@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    global EMPLOYEES
    employee = next((e for e in EMPLOYEES if e["id"] == employee_id), None)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    EMPLOYEES.remove(employee)
    return jsonify({"status": "ok", "deleted_id": employee_id})

# -------------------------
# STATIONS API
# -------------------------
@app.route("/api/stations", methods=["GET"])
def get_stations():
    return jsonify(STATIONS)

@app.route("/api/stations", methods=["POST"])
def add_station():
    global STATIONS
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    new_name = data.get("name", "").strip()
    new_type = data.get("type", "").strip()
    if not new_name:
        return jsonify({"error": "Station name required"}), 400

    new_id = max([s["id"] for s in STATIONS], default=0) + 1
    new_station = {
        "id": new_id,
        "name": new_name,
        "type": new_type
    }
    STATIONS.append(new_station)
    return jsonify({"status": "ok", "station": new_station})

# -------------------------
# SCHEDULE API
# -------------------------
@app.route("/api/schedule", methods=["GET"])
def get_schedule():
    return jsonify({
        "schedule": SCHEDULE,
        "business": BUSINESS_INFO,
        "employees": EMPLOYEES,
        "stations": STATIONS,
        "is_published": SCHEDULE_PUBLISHED
    })

@app.route("/api/schedule", methods=["POST"])
def save_schedule():
    global SCHEDULE, SCHEDULE_PUBLISHED
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    shifts = data.get("shifts", [])
    action = data.get("action", "draft")

    if not isinstance(shifts, list):
        return jsonify({"error": "shifts must be a list"}), 400

    SCHEDULE = shifts
    if action == "publish":
        SCHEDULE_PUBLISHED = True
        return jsonify({"status": "published", "schedule": SCHEDULE})
    else:
        SCHEDULE_PUBLISHED = False
        return jsonify({"status": "draft_saved", "schedule": SCHEDULE})

# -------------------------
# OFFICIAL SCHEDULE API
# -------------------------
@app.route("/api/official_schedule", methods=["GET"])
def official_schedule():
    if not SCHEDULE_PUBLISHED:
        return jsonify({"error": "Schedule is not published"}), 400

    return jsonify({
        "schedule": SCHEDULE,
        "business": BUSINESS_INFO,
        "employees": EMPLOYEES,
        "stations": STATIONS,
        "is_published": SCHEDULE_PUBLISHED
    })

# -------------------------
# TIME CLOCK API
# -------------------------
# Placeholder for time clock data
TIME_CLOCK_DATA = {
    "settings": {
        "enforce_schedule": True,
        "allow_remote_punch": True,
        "require_photo": False
    },
    "punches": []  # Will store punch records
}

@app.route("/api/timeclock/settings", methods=["GET"])
def get_timeclock_settings():
    return jsonify(TIME_CLOCK_DATA["settings"])

@app.route("/api/timeclock/settings", methods=["POST"])
def update_timeclock_settings():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
        
    TIME_CLOCK_DATA["settings"]["enforce_schedule"] = data.get("enforce_schedule", 
                                                      TIME_CLOCK_DATA["settings"]["enforce_schedule"])
    TIME_CLOCK_DATA["settings"]["allow_remote_punch"] = data.get("allow_remote_punch", 
                                                        TIME_CLOCK_DATA["settings"]["allow_remote_punch"])
    TIME_CLOCK_DATA["settings"]["require_photo"] = data.get("require_photo", 
                                                   TIME_CLOCK_DATA["settings"]["require_photo"])
    
    return jsonify({"status": "ok", "settings": TIME_CLOCK_DATA["settings"]})

@app.route("/api/timeclock/punch", methods=["POST"])
def record_punch():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
        
    employee_id = data.get("employee_id")
    if not employee_id:
        return jsonify({"error": "Employee ID required"}), 400
        
    # Find employee by ID or custom_id
    employee = None
    for emp in EMPLOYEES:
        if str(emp["id"]) == str(employee_id) or str(emp.get("custom_id", "")) == str(employee_id):
            employee = emp
            break
            
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
        
    punch_type = data.get("type", "in")  # "in" or "out"
    timestamp = data.get("timestamp", None)  # Client can provide timestamp or we use server time
    
    # Create punch record
    punch = {
        "employee_id": employee["id"],
        "type": punch_type,
        "timestamp": timestamp,
        "verified": not TIME_CLOCK_DATA["settings"]["require_photo"]  # Auto-verify if photos not required
    }
    
    TIME_CLOCK_DATA["punches"].append(punch)
    
    return jsonify({
        "status": "ok", 
        "punch": punch,
        "employee": employee
    })

@app.route("/api/timeclock/status/<employee_id>", methods=["GET"])
def get_employee_status(employee_id):
    # Find employee by ID or custom_id
    employee = None
    for emp in EMPLOYEES:
        if str(emp["id"]) == str(employee_id) or str(emp.get("custom_id", "")) == str(employee_id):
            employee = emp
            break
            
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
        
    # Get the most recent punch for this employee
    employee_punches = [p for p in TIME_CLOCK_DATA["punches"] if p["employee_id"] == employee["id"]]
    employee_punches.sort(key=lambda x: x["timestamp"], reverse=True)
    
    current_status = "out"
    last_punch = None
    
    if employee_punches:
        last_punch = employee_punches[0]
        current_status = last_punch["type"]
        
    return jsonify({
        "employee": employee,
        "status": current_status,
        "last_punch": last_punch
    })

@app.route("/api/timeclock/report", methods=["GET"])
def get_timeclock_report():
    # Optional filter parameters
    employee_id = request.args.get("employee_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    # Filter punches based on parameters
    filtered_punches = TIME_CLOCK_DATA["punches"]
    
    if employee_id:
        filtered_punches = [p for p in filtered_punches if str(p["employee_id"]) == str(employee_id)]
        
    # Additional filtering by date would be implemented here
    
    # Group punches by employee
    report = {}
    for punch in filtered_punches:
        emp_id = punch["employee_id"]
        if emp_id not in report:
            employee = next((e for e in EMPLOYEES if e["id"] == emp_id), None)
            report[emp_id] = {
                "employee": employee,
                "punches": []
            }
        report[emp_id]["punches"].append(punch)
    
    return jsonify({
        "report": list(report.values())
    })

# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

