from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from integration.middleware import process_request, sessions

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class IVRRequest(BaseModel):
    session_id: str
    input: str

# Serve UI at root
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

# IVR endpoint
@app.post("/ivr")
def ivr_endpoint(data: IVRRequest):
    return process_request(data.session_id, data.input)

# Reset session endpoint
@app.post("/reset")
def reset_session(data: IVRRequest):
    if data.session_id in sessions:
        del sessions[data.session_id]
    return {"message": "Session reset successful"}