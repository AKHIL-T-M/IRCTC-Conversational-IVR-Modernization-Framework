# Simulated IRCTC Legacy VXML Decision Tree

def get_main_menu():
    return {
        "1": {"text": "You selected Ticket Booking.", "next": "booking"},
        "2": {"text": "You selected PNR Status.", "next": "pnr"},
        "3": {"text": "You selected Cancel Ticket.", "next": "cancel"},
        "4": {"text": "You selected Train Availability.", "next": "availability"},
        "9": {"text": "Connecting to customer care agent.", "next": "agent"}
    }


def booking_flow(step, data=None):
    """
    Simulated legacy booking flow
    """

    if step == "start":
        return {
            "text": "Please enter Source Station code.",
            "next": "source"
        }

    if step == "source":
        return {
            "text": "Please enter Destination Station code.",
            "next": "destination"
        }

    if step == "destination":
        return {
            "text": "Please enter Travel Date in DDMMYYYY format.",
            "next": "date"
        }

    if step == "date":
        return {
            "text": "Your ticket booking request is being processed.",
            "next": "complete"
        }

    return {
        "text": "Invalid booking step.",
        "next": "menu"
    }


def pnr_flow():
    return {
        "text": "Please enter your 10 digit PNR number.",
        "next": "pnr_input"
    }


def cancel_flow():
    return {
        "text": "Please enter your PNR number to cancel the ticket.",
        "next": "cancel_pnr"
    }


def availability_flow():
    return {
        "text": "Please enter Train Number to check availability.",
        "next": "train_input"
    }