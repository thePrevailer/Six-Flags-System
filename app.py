from flask import Flask, render_template, request, session, redirect, url_for, send_file
import csv, io, math, random, string, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sixflags-secret-key-2024'

# ── PARK DATA ──────────────────────────────────────────────────────────────────
PARKS = [
    {"name": "Six Flags Over Texas",        "city": "Arlington, TX",       "icon": "🤠", "lat": 32.7573,  "lng": -97.0706,  "rides": 45, "coasters": 13, "desc": "The original Six Flags since 1961 — Titan, Mr. Freeze, Batman: The Ride.",           "tags": ["Thrills", "Coasters", "Family"]},
    {"name": "Six Flags Fiesta Texas",       "city": "San Antonio, TX",     "icon": "🌮", "lat": 29.6037,  "lng": -98.6116,  "rides": 40, "coasters": 8,  "desc": "Nestled in a limestone quarry — home of Wonder Woman Golden Lasso Coaster.",       "tags": ["Thrills", "Shows", "Water Park"]},
    {"name": "Six Flags Over Georgia",       "city": "Austell, GA",         "icon": "🍑", "lat": 33.8124,  "lng": -84.5480,  "rides": 43, "coasters": 11, "desc": "The South's top thrill park with Twisted Cyclone and Goliath.",                      "tags": ["Coasters", "Family", "Halloween"]},
    {"name": "Six Flags Great Adventure",    "city": "Jackson, NJ",         "icon": "🗽", "lat": 40.1370,  "lng": -74.4336,  "rides": 48, "coasters": 14, "desc": "Kingda Ka — the world's tallest coaster — plus a 2,200-acre safari.",              "tags": ["World Records", "Safari", "Flagship"]},
    {"name": "Six Flags Magic Mountain",     "city": "Valencia, CA",        "icon": "🌅", "lat": 34.4253,  "lng": -118.5973, "rides": 50, "coasters": 20, "desc": "The Thrill Capital of the World™ with a record-breaking 20 coasters.",              "tags": ["Most Coasters", "Thrills", "LA"]},
    {"name": "Six Flags Great America",      "city": "Gurnee, IL",          "icon": "🌽", "lat": 42.3703,  "lng": -87.9373,  "rides": 44, "coasters": 13, "desc": "Home of Goliath — world's fastest, tallest, steepest wooden coaster.",              "tags": ["Midwest", "Coasters", "Fright Fest"]},
    {"name": "Six Flags New England",        "city": "Agawam, MA",          "icon": "🍂", "lat": 42.0709,  "lng": -72.6157,  "rides": 36, "coasters": 12, "desc": "Superman: The Ride and Wicked Cyclone on the Connecticut River.",                    "tags": ["New England", "Coasters", "Halloween"]},
    {"name": "Six Flags America",            "city": "Largo, MD",           "icon": "🏛️", "lat": 38.8823,  "lng": -76.8369,  "rides": 32, "coasters": 9,  "desc": "The DC metro's Six Flags with Superman: Ride of Steel and Water Park.",             "tags": ["DC Area", "Family", "Water Park"]},
    {"name": "Six Flags Discovery Kingdom", "city": "Vallejo, CA",          "icon": "🦁", "lat": 38.1468,  "lng": -122.2533, "rides": 40, "coasters": 7,  "desc": "Where coasters meet wildlife — marine shows and safari 30 min from SF.",           "tags": ["Bay Area", "Animals", "Family"]},
    {"name": "Six Flags St. Louis",          "city": "Eureka, MO",          "icon": "🌉", "lat": 38.5023,  "lng": -90.6274,  "rides": 40, "coasters": 10, "desc": "Missouri's thrill park since 1971 — The Boss ranked among the best woodies.",       "tags": ["Midwest", "Woodies", "Classic"]},
    {"name": "Six Flags Hurricane Harbor",   "city": "Litchfield Park, AZ", "icon": "☀️", "lat": 33.4942,  "lng": -112.3588, "rides": 28, "coasters": 4,  "desc": "Desert thrills and water slides — the Southwest's action destination.",            "tags": ["Southwest", "Water Park", "Thrills"]},
]

TICKETS = [
    {"name": "Single Day Pass",  "price": 79.99,  "note": "per person / one visit",      "features": ["Full-day park admission", "All standard rides", "Free parking", "Park map & guide"]},
    {"name": "Season Pass",      "price": 119.99, "note": "unlimited visits / full year", "features": ["Unlimited park visits", "All Six Flags parks", "10% dining discount", "Priority queue access", "Bring-a-Friend tickets"]},
    {"name": "Gold Season Pass", "price": 169.99, "note": "all-inclusive / full year",    "features": ["All Season Pass perks", "Free parking all year", "15% dining & retail off", "Flash Pass included", "Gold lounge access", "4 guest passes/year"]},
    {"name": "Platinum Pass",    "price": 229.99, "note": "VIP all-inclusive / full year","features": ["All Gold Pass perks", "Skip every line", "VIP concierge service", "20% dining & retail off", "Behind-the-scenes tour", "Unlimited guest passes"]},
]

# ── HELPERS ────────────────────────────────────────────────────────────────────
def haversine(lat1, lng1, lat2, lng2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def drive_time(miles):
    hours = (miles * 1.3) / 60
    if hours < 1:
        return f"{round(hours * 60)} min drive"
    h = int(hours)
    m = round((hours - h) * 60)
    return f"{h}h {m}m drive" if m else f"{h}h drive"

def geocode(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1, "countrycodes": "us"}
    headers = {"User-Agent": "SixFlagsSimulator/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=5)
    data = r.json()
    if not data:
        return None
    return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"]), "display": data[0]["display_name"]}

def make_ticket_id():
    return "SF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ── ROUTES ─────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("location"))

@app.route("/location", methods=["GET", "POST"])
def location():
    error = None
    if request.method == "POST":
        loc = request.form.get("location", "").strip()
        if not loc:
            error = "Please enter a city, state, or zip code."
        else:
            geo = geocode(loc)
            if not geo:
                error = "Could not find that location. Please try a US city or zip code."
            else:
                # Rank parks by distance
                ranked = []
                for p in PARKS:
                    dist = haversine(geo["lat"], geo["lng"], p["lat"], p["lng"])
                    ranked.append({**p, "dist": dist, "drive": drive_time(dist)})
                ranked.sort(key=lambda x: x["dist"])
                session["ranked_parks"] = ranked
                session["user_location"] = loc
                return redirect(url_for("parks"))
    return render_template("location.html", error=error)

@app.route("/parks", methods=["GET", "POST"])
def parks():
    ranked = session.get("ranked_parks")
    if not ranked:
        return redirect(url_for("location"))
    if request.method == "POST":
        park_name = request.form.get("park")
        chosen = next((p for p in ranked if p["name"] == park_name), ranked[0])
        session["chosen_park"] = chosen
        return redirect(url_for("tickets"))
    return render_template("parks.html", parks=ranked, location=session.get("user_location",""))

@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    if not session.get("chosen_park"):
        return redirect(url_for("location"))
    if request.method == "POST":
        ticket_name = request.form.get("ticket")
        ticket = next((t for t in TICKETS if t["name"] == ticket_name), None)
        if not ticket:
            return render_template("tickets.html", tickets=TICKETS, park=session["chosen_park"], error="Please select a ticket.")
        session["chosen_ticket"] = ticket
        return redirect(url_for("details"))
    return render_template("tickets.html", tickets=TICKETS, park=session["chosen_park"])

@app.route("/details", methods=["GET", "POST"])
def details():
    if not session.get("chosen_ticket"):
        return redirect(url_for("location"))
    error = None
    if request.method == "POST":
        first   = request.form.get("first_name","").strip()
        last    = request.form.get("last_name","").strip()
        email   = request.form.get("email","").strip()
        phone   = request.form.get("phone","").strip()
        dob     = request.form.get("dob","").strip()
        student = request.form.get("student") == "yes"
        school  = request.form.get("school","").strip()
        if not all([first, last, email, phone, dob]):
            error = "Please fill in all required fields."
        elif student and not school:
            error = "Please enter your school name."
        else:
            price   = session["chosen_ticket"]["price"]
            discount = round(price * 0.20, 2) if student else 0
            final   = round(price - discount, 2)
            ticket_id = make_ticket_id()
            session["user_details"] = {
                "first_name": first, "last_name": last,
                "email": email, "phone": phone, "dob": dob,
                "student": student, "school": school,
            }
            session["order"] = {
                "ticket_id": ticket_id,
                "base_price": price,
                "discount": discount,
                "final_price": final,
                "date": datetime.now().strftime("%b %d, %Y"),
            }
            return redirect(url_for("confirmation"))
    return render_template("details.html",
        park=session["chosen_park"],
        ticket=session["chosen_ticket"],
        location=session.get("user_location",""))

@app.route("/confirmation")
def confirmation():
    if not session.get("order"):
        return redirect(url_for("location"))
    return render_template("confirmation.html",
        park=session["chosen_park"],
        ticket=session["chosen_ticket"],
        user=session["user_details"],
        order=session["order"])

@app.route("/download-csv")
def download_csv():
    park   = session.get("chosen_park", {})
    ticket = session.get("chosen_ticket", {})
    user   = session.get("user_details", {})
    order  = session.get("order", {})

    rows = [
        ["Field", "Value"],
        ["Ticket ID",        order.get("ticket_id","")],
        ["First Name",       user.get("first_name","")],
        ["Last Name",        user.get("last_name","")],
        ["Email",            user.get("email","")],
        ["Phone",            user.get("phone","")],
        ["Date of Birth",    user.get("dob","")],
        ["Location Entered", session.get("user_location","")],
        ["Park Selected",    park.get("name","")],
        ["Park City",        park.get("city","")],
        ["Distance",         f"{park.get('dist','')} miles away"],
        ["Est. Drive Time",  park.get("drive","")],
        ["Ticket Type",      ticket.get("name","")],
        ["Base Price",       f"${order.get('base_price',0):.2f}"],
        ["Student",          "Yes" if user.get("student") else "No"],
        ["School",           user.get("school","N/A") if user.get("student") else "N/A"],
        ["Student Discount", f"-${order.get('discount',0):.2f} (20%)" if user.get("student") else "None"],
        ["Final Price Paid", f"${order.get('final_price',0):.2f}"],
        ["Purchase Date",    order.get("date","")],
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"SixFlags_Ticket_{order.get('ticket_id','receipt')}.csv"
    )
app = app
if __name__ == "__main__":
    app.run(debug=True)
