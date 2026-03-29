from legacy.vxml_parser import (
    get_main_menu,
    booking_flow,
    pnr_flow, pnr_result,
    cancel_flow, cancel_pnr_lookup, cancel_confirmed,
    availability_flow, availability_result,
    MAIN_MENU_TEXT
)

# Session storage: keyed by session_id
sessions = {}


# ─────────────────────────────────────────────
# Voice → Menu Key Mapping
# ─────────────────────────────────────────────

def detect_voice_option(user_input: str):
    """Convert natural voice speech into menu key if applicable."""
    if not user_input:
        return user_input

    text = user_input.lower()

    if "cancel" in text:
        return "3"
    if "pnr" in text or "p n r" in text or "status" in text:
        return "2"
    if "book" in text or "booking" in text or "ticket" in text:
        return "1"
    if "availability" in text or "seat" in text or "available" in text:
        return "4"
    if "agent" in text or "customer care" in text or "support" in text or "human" in text:
        return "5"

    return user_input


# ─────────────────────────────────────────────
# Digit Validation Helpers
# ─────────────────────────────────────────────

def is_valid_digits(value: str, length: int) -> bool:
    return value.isdigit() and len(value) == length

def is_valid_date(value: str) -> bool:
    """Validate DDMMYYYY format."""
    if not is_valid_digits(value, 8):
        return False
    try:
        dd, mm, yyyy = int(value[:2]), int(value[2:4]), int(value[4:])
        return 1 <= dd <= 31 and 1 <= mm <= 12 and yyyy >= 2024
    except Exception:
        return False


# ─────────────────────────────────────────────
# Main IVR Request Processor
# ─────────────────────────────────────────────

def process_request(session_id: str, user_input: str):

    # ── NEW SESSION ──
    if session_id not in sessions:
        sessions[session_id] = {"state": "menu"}
        return {"text": MAIN_MENU_TEXT}

    sess = sessions[session_id]
    current_state = sess["state"]

    # Convert voice speech to menu key only when in menu state
    if current_state == "menu":
        user_input = detect_voice_option(user_input)


    # ════════════════════════════════════
    # MAIN MENU
    # ════════════════════════════════════

    if current_state == "menu":

        if not user_input:
            return {"text": MAIN_MENU_TEXT}

        menu = get_main_menu()

        if user_input in menu:
            next_step = menu[user_input]["next"]
            sess["state"] = next_step

            if next_step == "booking":
                sess["state"] = "source"
                return booking_flow("start")

            if next_step == "pnr":
                sess["state"] = "pnr_input"
                return pnr_flow()

            if next_step == "cancel":
                sess["state"] = "cancel_pnr"
                return cancel_flow()

            if next_step == "availability":
                sess["state"] = "train_input"
                return availability_flow()

            if next_step == "agent":
                sess["state"] = "menu"
                return {
                    "text": f"""Connecting you to IRCTC Customer Care Agent...

All agents are currently busy. Estimated wait time: 8 minutes.

Please stay on the line or try again later.

{MAIN_MENU_TEXT}"""
                }

        return {
            "text": f"""Sorry, I didn't understand that option.

You can say things like:
• Check PNR status
• Book a ticket
• Cancel my ticket
• Train availability
• Talk to customer care agent

{MAIN_MENU_TEXT}"""
        }


    # ════════════════════════════════════
    # PNR STATUS FLOW
    # ════════════════════════════════════

    if current_state == "pnr_input":
        if not user_input:
            return {"text": "Please enter your 10 digit PNR number:"}

        # Wait for full 10 digits
        digits_only = ''.join(filter(str.isdigit, user_input))
        if not is_valid_digits(digits_only, 10):
            return {
                "text": f"Invalid PNR. PNR must be exactly 10 digits.\nYou entered: {user_input}\n\nPlease enter your 10 digit PNR number:"
            }

        sess["state"] = "menu"
        return {"text": pnr_result(digits_only)}


    # ════════════════════════════════════
    # CANCEL TICKET FLOW
    # ════════════════════════════════════

    if current_state == "cancel_pnr":
        if not user_input:
            return {"text": "Please enter your 10 digit PNR number to cancel:"}

        digits_only = ''.join(filter(str.isdigit, user_input))
        if not is_valid_digits(digits_only, 10):
            return {
                "text": f"Invalid PNR. Must be exactly 10 digits.\n\nPlease enter your 10 digit PNR number to cancel:"
            }

        result = cancel_pnr_lookup(digits_only)
        sess["state"] = "confirm_cancel"
        sess["cancel_pnr"] = digits_only
        return {"text": result["text"]}

    if current_state == "confirm_cancel":
        if user_input == "1":
            pnr = sess.get("cancel_pnr", "XXXXXXXXXX")
            sess["state"] = "menu"
            return {"text": cancel_confirmed(pnr)}

        if user_input == "0":
            sess["state"] = "menu"
            return {"text": f"Cancellation aborted.\n\n{MAIN_MENU_TEXT}"}

        return {
            "text": "Press 1 to Confirm Cancellation or Press 0 to go back to Main Menu:"
        }


    # ════════════════════════════════════
    # TRAIN AVAILABILITY FLOW
    # ════════════════════════════════════

    if current_state == "train_input":
        if not user_input:
            return {"text": "Please enter 5-digit Train Number:"}

        digits_only = ''.join(filter(str.isdigit, user_input))
        if not is_valid_digits(digits_only, 5):
            return {
                "text": f"Invalid Train Number. Must be exactly 5 digits.\n\nPlease enter 5-digit Train Number:"
            }

        sess["state"] = "menu"
        return {"text": availability_result(digits_only)}


    # ════════════════════════════════════
    # BOOKING FLOW — MULTI-STEP
    # ════════════════════════════════════

    if current_state == "source":
        if not user_input or len(user_input.strip()) < 2:
            return {"text": "Please enter Source Station code (e.g. NDLS for New Delhi):"}
        sess["source"] = user_input.strip().upper()
        sess["state"] = "destination"
        return booking_flow("source")

    if current_state == "destination":
        if not user_input or len(user_input.strip()) < 2:
            return {"text": "Please enter Destination Station code (e.g. HWH for Howrah):"}
        sess["destination"] = user_input.strip().upper()
        sess["state"] = "date"
        return booking_flow("destination")

    if current_state == "date":
        if not user_input:
            return {"text": "Please enter Travel Date in DDMMYYYY format (e.g. 29032026):"}
        digits_only = ''.join(filter(str.isdigit, user_input))
        if not is_valid_date(digits_only):
            return {
                "text": f"Invalid date format. Please enter Travel Date in DDMMYYYY format (e.g. 29032026):"
            }
        sess["date"] = digits_only
        sess["state"] = "class"
        return booking_flow("date", sess)

    if current_state == "class":
        if user_input not in ["1", "2", "3", "4"]:
            return {
                "text": "Invalid selection. Please press:\n1 – Sleeper (SL)\n2 – 3rd AC (3A)\n3 – 2nd AC (2A)\n4 – 1st AC (1A)"
            }
        class_map = {"1": "Sleeper (SL)", "2": "3rd AC (3A)", "3": "2nd AC (2A)", "4": "1st AC (1A)"}
        sess["travel_class"] = class_map[user_input]
        sess["class_input"] = user_input
        sess["state"] = "passengers"
        return booking_flow("class", sess)

    if current_state == "passengers":
        if not user_input or not user_input.isdigit() or not (1 <= int(user_input) <= 6):
            return {
                "text": "Invalid count. Please enter number of passengers (1 to 6):"
            }
        sess["passengers"] = user_input
        sess["state"] = "confirm_booking"
        return booking_flow("passengers", sess)

    if current_state == "confirm_booking":
        if user_input == "1":
            sess["state"] = "menu"
            return booking_flow("confirm_booking_yes", sess)
        if user_input == "0":
            sess["state"] = "menu"
            return booking_flow("confirm_booking_no", sess)
        return {
            "text": f"Press 1 to Confirm your booking or Press 0 to Cancel:\n\n{_booking_summary_text(sess)}"
        }


    # ════════════════════════════════════
    # FALLBACK — Reset to menu
    # ════════════════════════════════════

    sessions[session_id] = {"state": "menu"}
    return {
        "text": f"System reset due to unexpected state.\n\n{MAIN_MENU_TEXT}"
    }


def _booking_summary_text(sess):
    src = sess.get("source", "?")
    dst = sess.get("destination", "?")
    pax = sess.get("passengers", "?")
    cls = sess.get("travel_class", "?")
    raw_date = sess.get("date", "00000000")
    fmt_date = f"{raw_date[:2]}-{raw_date[2:4]}-{raw_date[4:]}" if len(raw_date) == 8 else raw_date
    return f"From: {src} → {dst}\nDate: {fmt_date}\nClass: {cls}\nPassengers: {pax}"