# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create the FastAPI app object
app = FastAPI()

# --- CORS Middleware ---
# This is crucial for allowing your React frontend (running on a different port)
# to communicate with this backend.
# origins = ["http://localhost:3000"] # Replace with your frontend's actual URL in production
origins = ["*"] # For development, allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Root endpoint to check if the server is running.
    """
    return {"message": "Welcome to the MatchWise AI Backend!"}

@app.get("/api/health")
def health_check():
    """
    A simple health check endpoint.
    """
    return {"status": "ok"}

# --- How to Run This Server ---
# 1. Make sure your virtual environment is active: source venv/bin/activate
# 2. Run this command in your terminal:
#    uvicorn main:app --reload --port 8011
#
# 3. Open your web browser and go to http://127.0.0.1:8011
#    You should see: {"message":"Welcome to the MatchWise AI Backend!"}