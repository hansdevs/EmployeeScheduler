from flask import Flask, jsonify, request, send_from_directory, redirect, session

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = "supersecretkey"

# =====================
# In-memory "database"
# =====================
BUSINESS_INFO = {
    "name": "Andreas Law Firm",
    "industry": "Law Firm",
    "requirements": ["Office Desk", "Office Desk"],
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
    "schedule.html",
    "business.html",
    "employees.html",
    "stations.html",
    "official.html"
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
    reqs = data.get("requirements", BUSINESS_INFO["requirements"])

    if isinstance(reqs, str):
        reqs = [r.strip() for r in reqs.split(",") if r.strip()]
    BUSINESS_INFO["requirements"] = reqs

    hours = data.get("hours", {})
    for d in range(7):
        if str(d) in hours:
            open_h  = hours[str(d)].get("open", BUSINESS_INFO["hours"][d]["open"])
            close_h = hours[str(d)].get("close", BUSINESS_INFO["hours"][d]["close"])
            BUSINESS_INFO["hours"][d]["open"]  = open_h
            BUSINESS_INFO["hours"][d]["close"] = close_h

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

    if not new_name:
        return jsonify({"error": "Employee name required"}), 400

    new_id = max([e["id"] for e in EMPLOYEES], default=0) + 1
    new_employee = {
        "id": new_id,
        "name": new_name,
        "type": new_type,
        "color": new_color
    }
    EMPLOYEES.append(new_employee)
    return jsonify({"status": "ok", "employee": new_employee})

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
# Run the App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)