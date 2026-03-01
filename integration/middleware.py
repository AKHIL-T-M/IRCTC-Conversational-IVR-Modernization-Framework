from legacy.vxml_parser import (
    get_main_menu,
    booking_flow,
    pnr_flow,
    cancel_flow,
    availability_flow
)

# In-memory session storage
sessions = {}

def process_request(session_id: str, user_input: str):

    # 🔹 If session does not exist → create new and show welcome
    if session_id not in sessions:
        sessions[session_id] = {"state": "menu"}

        return {
            "text": """Welcome to IRCTC Customer Care IVR.

Press 1 – Ticket Booking
Press 2 – PNR Status
Press 3 – Cancel Ticket
Press 4 – Train Availability
Press 9 – Talk to Customer Care Agent"""
        }

    current_state = sessions[session_id]["state"]

    # 🔹 MAIN MENU
    if current_state == "menu":

        if not user_input:
            return {
                "text": """Please choose an option:

Press 1 – Ticket Booking
Press 2 – PNR Status
Press 3 – Cancel Ticket
Press 4 – Train Availability
Press 9 – Talk to Customer Care Agent"""
            }

        menu = get_main_menu()

        if user_input in menu:
            next_step = menu[user_input]["next"]
            sessions[session_id]["state"] = next_step

            if next_step == "booking":
                return booking_flow("start")

            if next_step == "pnr":
                return pnr_flow()

            if next_step == "cancel":
                return cancel_flow()

            if next_step == "availability":
                return availability_flow()

            return {"text": menu[user_input]["text"]}

        return {"text": "Invalid option. Please try again."}

    # 🔹 BOOKING FLOW
    if current_state == "booking":
        sessions[session_id]["state"] = "source"
        return booking_flow("start")

    if current_state == "source":
        sessions[session_id]["source"] = user_input
        sessions[session_id]["state"] = "destination"
        return booking_flow("source")

    if current_state == "destination":
        sessions[session_id]["destination"] = user_input
        sessions[session_id]["state"] = "date"
        return booking_flow("destination")

    if current_state == "date":
        sessions[session_id]["date"] = user_input
        sessions[session_id]["state"] = "complete"
        return booking_flow("date")

    if current_state == "complete":
        sessions[session_id]["state"] = "menu"
        return {
            "text": """Your request has been completed.

Returning to Main Menu.

Press 1 – Ticket Booking
Press 2 – PNR Status
Press 3 – Cancel Ticket
Press 4 – Train Availability
Press 9 – Talk to Customer Care Agent"""
        }

    # 🔹 Safety fallback (auto recovery)
    sessions[session_id] = {"state": "menu"}

    return {
        "text": """System reset due to unexpected state.

Press 1 – Ticket Booking
Press 2 – PNR Status
Press 3 – Cancel Ticket
Press 4 – Train Availability"""
    }