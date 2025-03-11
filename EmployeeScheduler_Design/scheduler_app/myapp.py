from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =====================
# In-memory "database"
# =====================

BUSINESS_INFO = {
    "name": "Andreas Law Firm",
    "industry": "Law Firm",
    "requirements": ["Office Desk", "Office Desk"],
    "hours": {
        0: {"open":8, "close":17},
        1: {"open":8, "close":17},
        2: {"open":8, "close":17},
        3: {"open":8, "close":17},
        4: {"open":8, "close":17},
        5: {"open":0, "close":0},
        6: {"open":0, "close":0},
    }
}

EMPLOYEES = []
STATIONS  = []  # each station = {id, name, type?}
SCHEDULE  = []  # each shift = {station_id, employee_id, start, end, day}

SCHEDULE_PUBLISHED = False

@app.route("/")
def home():
    return redirect(url_for("schedule_page"))

# ----- BUSINESS PAGE -----
@app.route("/business", methods=["GET","POST"])
def business_page():
    global BUSINESS_INFO
    if request.method == "POST":
        BUSINESS_INFO["name"] = request.form.get("name","Unnamed Biz")
        BUSINESS_INFO["industry"] = request.form.get("industry","")
        reqs = request.form.get("requirements","")
        BUSINESS_INFO["requirements"] = [r.strip() for r in reqs.split(",") if r.strip()]

        for d in range(7):
            try:
                o = int(request.form.get(f"open_{d}","0"))
                c = int(request.form.get(f"close_{d}","0"))
                BUSINESS_INFO["hours"][d]["open"]  = o
                BUSINESS_INFO["hours"][d]["close"] = c
            except:
                BUSINESS_INFO["hours"][d]["open"]  = 0
                BUSINESS_INFO["hours"][d]["close"] = 0

        return redirect(url_for("business_page"))
    return render_template("business.html", business=BUSINESS_INFO)

# ----- EMPLOYEES PAGE -----
@app.route("/employees", methods=["GET","POST"])
def employees_page():
    global EMPLOYEES
    if request.method == "POST":
        new_name  = request.form.get("name","").strip()
        new_type  = request.form.get("type","").strip()
        new_color = request.form.get("color_class","block-blue").strip()
        if new_name:
            new_id = max([e["id"] for e in EMPLOYEES], default=0) + 1
            EMPLOYEES.append({
                "id": new_id,
                "name": new_name,
                "type": new_type,
                "color": new_color
            })
        return redirect(url_for("employees_page"))
    return render_template("employees.html", employees=EMPLOYEES)

# ----- STATIONS PAGE -----
@app.route("/stations", methods=["GET","POST"])
def stations_page():
    """
    Manage stations (like “Cash Register #1”, “Computer #2”).
    Each is a row on the schedule where you can assign employees.
    """
    global STATIONS
    if request.method == "POST":
        # Add station
        new_name = request.form.get("station_name","").strip()
        new_type = request.form.get("station_type","").strip()
        if new_name:
            new_id = max([s["id"] for s in STATIONS], default=0) + 1
            STATIONS.append({
                "id": new_id,
                "name": new_name,
                "type": new_type
            })
        return redirect(url_for("stations_page"))

    return render_template("stations.html", stations=STATIONS)

# ----- SCHEDULE PAGE -----
@app.route("/schedule", methods=["GET","POST"])
def schedule_page():
    global SCHEDULE, STATIONS, EMPLOYEES, BUSINESS_INFO, SCHEDULE_PUBLISHED
    saved_flag = request.args.get("saved","0")

    # We only handle "remove_station" or similar if you wanted that
    return render_template("schedule.html",
                           stations=STATIONS,
                           employees=EMPLOYEES,
                           schedule=SCHEDULE,
                           business=BUSINESS_INFO,
                           saved_flag=saved_flag,
                           schedule_published=SCHEDULE_PUBLISHED)

@app.route("/save_schedule", methods=["POST"])
def save_schedule():
    global SCHEDULE, SCHEDULE_PUBLISHED
    new_shifts_json = request.form.get("new_shifts","[]")
    publish_action  = request.form.get("publish_action","draft")

    try:
        loaded = json.loads(new_shifts_json)
    except:
        loaded = []
    SCHEDULE = loaded

    if publish_action == "publish":
        SCHEDULE_PUBLISHED = True
        return redirect(url_for("schedule_page", saved="published"))
    else:
        SCHEDULE_PUBLISHED = False
        return redirect(url_for("schedule_page", saved="1"))

# ----- OFFICIAL SCHEDULE -----
@app.route("/official_schedule")
def official_schedule():
    global EMPLOYEES, STATIONS, SCHEDULE, BUSINESS_INFO, SCHEDULE_PUBLISHED
    return render_template("official_schedule.html",
                           employees=EMPLOYEES,
                           stations=STATIONS,
                           schedule=SCHEDULE,
                           business=BUSINESS_INFO,
                           is_published=SCHEDULE_PUBLISHED)

if __name__ == "__main__":
    app.run(debug=True)
