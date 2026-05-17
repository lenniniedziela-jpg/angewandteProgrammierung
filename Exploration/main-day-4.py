from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path


NOTES_FILE = Path("data/notes.json")

def load_notes():
    """Load notes from JSON file and return notes list and next ID counter"""
    notes_db = []
    note_id_counter = 1

    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r') as f:
            data = json.load(f)
            notes_db = [Note(**note) for note in data]

            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)

        # ============================================================================
# DAY 4: Advanced API Features
# ============================================================================
# Goal: Write and run tests for our APIs
#       - Use pytest to write unit tests for our API endpoints
#       - Use FastAPI's TestClient to simulate API requests
#       - Use Requests library to test API endpoints from outside the app
# Topics: Testing FastAPI applications, pytest, TestClient, Requests library
# ============================================================================


# Create FastAPI application
app = FastAPI(
    title="Applied Programming Course API",
    description="Reference implementation for Day 4",
    version="1.0.0"
)

# ----------------------------------------------------------------------------
# PYDANTIC MODELS
# ----------------------------------------------------------------------------

class GreetingResponse(BaseModel):
    """Response model for greeting endpoints

    Attributes:
        message (str): The greeting message to be returned to the client
    """
    message: str

# ----------------------------------------------------------------------------
# DAY 4: API ENDPOINTS FOR TESTING
# ----------------------------------------------------------------------------

@app.get("/", response_model=GreetingResponse)
def read_root():
    """Welcome endpoint - returns greeting message"""
    return {"message": "Hello World!"}




@app.get("/greetings/{name}", response_model=GreetingResponse)
def read_greeting(name: str):
    """Personalized greeting endpoint - returns greeting message with name"""
    return {"message": f"Hello {name}!"}


# ----------------------------------------------------------------------------
# BUGGY ENDPOINT - For Teaching Purposes
# ----------------------------------------------------------------------------

@app.get("/is-adult/{age}")
def check_adult(age: int):
    """
    Check if person is an adult (18 or older)
    Example: /is-adult/17
    """

    if age < 0:
        raise HTTPException(status_code=400, detail="Age must be a positive integer")



    is_adult = age >= 18

    return {
        "age": age,
        "is_adult": is_adult,
        "can_vote": is_adult,
        "can_drive": is_adult
    }

 


