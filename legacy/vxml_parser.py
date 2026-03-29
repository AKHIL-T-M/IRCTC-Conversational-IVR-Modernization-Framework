# Simulated IRCTC Legacy VXML Decision Tree
# Full realistic flow for all IVR options

MAIN_MENU_TEXT = """Welcome to IRCTC Customer Care IVR.

Press 1 – Ticket Booking
Press 2 – PNR Status
Press 3 – Cancel Ticket
Press 4 – Train Availability
Press 5 – Talk to Customer Care Agent"""


def get_main_menu():
    return {
        "1": {"text": "You selected Ticket Booking.", "next": "booking"},
        "2": {"text": "You selected PNR Status.", "next": "pnr"},
        "3": {"text": "You selected Cancel Ticket.", "next": "cancel"},
        "4": {"text": "You selected Train Availability.", "next": "availability"},
        "5": {"text": "Connecting to customer care agent.", "next": "agent"}
    }


# ─────────────────────────────────
# BOOKING FLOW
# ─────────────────────────────────

def booking_flow(step, session=None):
    if step == "start":
        return {
            "text": "Ticket Booking selected.\nPlease enter Source Station code (e.g. NDLS for New Delhi):",
            "next": "source"
        }

    if step == "source":
        return {
            "text": "Please enter Destination Station code (e.g. HWH for Howrah):",
            "next": "destination"
        }

    if step == "destination":
        return {
            "text": "Please enter Travel Date in DDMMYYYY format (e.g. 29032026):",
            "next": "date"
        }

    if step == "date":
        return {
            "text": "Select Travel Class:\nPress 1 – Sleeper (SL)\nPress 2 – 3rd AC (3A)\nPress 3 – 2nd AC (2A)\nPress 4 – 1st AC (1A)",
            "next": "class"
        }

    if step == "class":
        classes = {"1": "Sleeper (SL)", "2": "3rd AC (3A)", "3": "2nd AC (2A)", "4": "1st AC (1A)"}
        sel = session.get("class_input", "2") if session else "2"
        cls = classes.get(sel, "3rd AC (3A)")
        return {
            "text": f"Class {cls} selected.\nHow many passengers? Enter 1 to 6:",
            "next": "passengers"
        }

    if step == "passengers":
        return {
            "text": _build_booking_summary(session),
            "next": "confirm_booking"
        }

    if step == "confirm_booking_yes":
        import random
        pnr = random.randint(1000000000, 9999999999)
        src = session.get("source", "?")
        dst = session.get("destination", "?")
        cls = session.get("travel_class", "3rd AC")
        pax = session.get("passengers", "1")
        raw_date = session.get("date", "00000000")
        fmt_date = f"{raw_date[:2]}-{raw_date[2:4]}-{raw_date[4:]}" if len(raw_date) == 8 else raw_date
        return {
            "text": f"""✅ Booking Confirmed!

PNR: {pnr}
From: {src} → {dst}
Date: {fmt_date}
Class: {cls}
Passengers: {pax}

Your e-ticket has been sent to your registered mobile and email.

{MAIN_MENU_TEXT}""",
            "next": "menu"
        }

    if step == "confirm_booking_no":
        return {
            "text": f"Booking cancelled.\n\n{MAIN_MENU_TEXT}",
            "next": "menu"
        }

    return {"text": "Invalid booking step.", "next": "menu"}


def _build_booking_summary(session):
    if not session:
        return "Please confirm your booking. Press 1 to Confirm, Press 0 to Cancel."
    src = session.get("source", "?")
    dst = session.get("destination", "?")
    pax = session.get("passengers", "?")
    cls = session.get("travel_class", "?")
    raw_date = session.get("date", "00000000")
    fmt_date = f"{raw_date[:2]}-{raw_date[2:4]}-{raw_date[4:]}" if len(raw_date) == 8 else raw_date
    return f"""Booking Summary:
From: {src} → {dst}
Date: {fmt_date}
Class: {cls}
Passengers: {pax}

Press 1 – Confirm Booking
Press 0 – Cancel"""


# ─────────────────────────────────
# PNR FLOW
# ─────────────────────────────────

def pnr_flow():
    return {
        "text": "PNR Status selected.\nPlease enter your 10 digit PNR number:",
        "next": "pnr_input"
    }


def pnr_result(pnr):
    import random
    trains = [
        ("12301", "HOWRAH RAJDHANI", "NDLS", "HWH"),
        ("12302", "HOWRAH RAJDHANI", "HWH", "NDLS"),
        ("12951", "MUMBAI RAJDHANI", "NDLS", "BCT"),
        ("12627", "KARNATAKA EXP", "SBC", "NDLS"),
        ("16526", "ISLAND EXPRESS", "CAPE", "SBC"),
    ]
    t = random.choice(trains)
    coaches = ["B1", "B2", "B3", "A1", "A2", "H1", "S1", "S2"]
    seat = random.randint(1, 72)
    statuses = ["CONFIRMED", "CONFIRMED", "CONFIRMED", "WL/3", "RAC/12"]
    status = random.choice(statuses)
    return f"""PNR {pnr} Status:

Train: {t[0]} {t[1]}
From: {t[2]} → {t[3]}
Date: 29-Mar-2026
Coach: {random.choice(coaches)}, Seat: {seat}
Status: {status}

{MAIN_MENU_TEXT}"""


# ─────────────────────────────────
# CANCEL FLOW
# ─────────────────────────────────

def cancel_flow():
    return {
        "text": "Cancel Ticket selected.\nPlease enter your 10 digit PNR number to cancel:",
        "next": "cancel_pnr"
    }


def cancel_pnr_lookup(pnr):
    import random
    trains = [
        ("12301", "HOWRAH RAJDHANI"),
        ("12951", "MUMBAI RAJDHANI"),
        ("12627", "KARNATAKA EXPRESS"),
    ]
    t = random.choice(trains)
    return {
        "text": f"""PNR {pnr} found:
Train: {t[0]} {t[1]}
Status: CONFIRMED
Refund: ₹{random.randint(800, 2500)}

Press 1 – Confirm Cancellation
Press 0 – Go Back to Main Menu""",
        "next": "confirm_cancel",
        "pnr": pnr
    }


def cancel_confirmed(pnr):
    import random
    return f"""✅ Ticket Cancelled Successfully!

PNR: {pnr}
Refund of ₹{random.randint(800, 2500)} will be credited within 5–7 working days to your original payment method.

{MAIN_MENU_TEXT}"""


# ─────────────────────────────────
# AVAILABILITY FLOW
# ─────────────────────────────────

def availability_flow():
    return {
        "text": "Train Availability selected.\nPlease enter 5-digit Train Number to check availability:",
        "next": "train_input"
    }


def availability_result(train_no):
    import random
    avail = {
        "1A": f"{random.randint(0, 10)} seats available",
        "2A": f"{random.randint(0, 20)} seats available",
        "3A": "AVAILABLE" if random.random() > 0.3 else f"WL/{random.randint(1, 30)}",
        "SL": "AVAILABLE" if random.random() > 0.2 else f"WL/{random.randint(1, 50)}",
    }
    return f"""Train {train_no} Availability (29-Mar-2026):

1A (First AC): {avail['1A']}
2A (Second AC): {avail['2A']}
3A (Third AC): {avail['3A']}
SL (Sleeper): {avail['SL']}

{MAIN_MENU_TEXT}"""