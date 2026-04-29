# Six Flags Ticket Simulator 🎢

A full-stack web application simulating the Six Flags ticketing experience — built with **Python (Flask)** backend and styled HTML/CSS/JS templates.

## Features
- 📍 **Real location search** — enter any US city or zip code
- 🗺️ **Distance finder** — ranks all 11 Six Flags parks by distance using Haversine formula
- 🎟️ **4 ticket tiers** — Single Day, Season, Gold Season, Platinum
- 🎓 **Student discount** — 20% off with school name verification
- 📄 **CSV receipt** — full order details exported server-side in Python
- 🖨️ **Styled ticket printout** — animated ticket card with barcode

## Project Structure
```
Six-Flags-System/
├── app.py                  # Flask routes & backend logic (Python)
├── requirements.txt
├── templates/
│   ├── base.html           # Shared header/nav
│   ├── location.html       # Step 1 — Enter location
│   ├── parks.html          # Step 2 — Choose park + distances
│   ├── tickets.html        # Step 3 — Select ticket tier
│   ├── details.html        # Step 4 — User info + student status
│   └── confirmation.html   # Step 5 — Ticket + CSV download
└── sixflags_simulator.html # Standalone single-file version (HTML only)
```

## Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/location` | GET/POST | Enter your location |
| `/parks` | GET/POST | View & choose nearest parks |
| `/tickets` | GET/POST | Select a ticket tier |
| `/details` | GET/POST | Enter personal info |
| `/confirmation` | GET | View your ticket |
| `/download-csv` | GET | Download CSV receipt |

## Running Locally
```bash
pip install -r requirements.txt
python app.py
```
Open `http://localhost:5000` in your browser.
