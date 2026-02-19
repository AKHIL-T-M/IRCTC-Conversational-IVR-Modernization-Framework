from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "IRCTC IVR Backend Running Successfully"}

@app.get("/booking_menu")
def booking_menu():
    return {
        "message": "Welcome to IRCTC IVR Booking Menu",
        "options": {
            "1": "Book a Ticket",
            "2": "Check PNR Status",
            "3": "Cancel a Ticket",
            "4": "Exit"
        }
    }

@app.get("/booking_menu/book_ticket")
def book_ticket():
    return {
        "message": "Booking a ticket. Please provide the following details:",
        "required_details": [
            "Passenger Name",
            "Age",
            # "Gender",
            # "Source Station",
            # "Destination Station",
            # "Travel Date"
        ]
    }
