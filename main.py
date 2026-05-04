from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json
from pathlib import Path
from collections import Counter
from typing import Optional


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/name/{name}")
def greet_name(name:str):
    return {"message": f"Hello, {name}!"}


@app.get("/name/{name}/{number}")
def greet_name_with_number(name: str, number: int):
    doubled_number = number * 2
    return {"message": f"Hallo, {name}, {doubled_number}"}


@app.get("/alter/{alter}")
def show_age(alter: int):
    return {"message": f"Dein Alter ist: {alter}"}


@app.get("/summe/{zahl1}/{zahl2}")
def add_age_numbers(zahl1: int, zahl2: int):
    ergebnis = zahl1 + zahl2
    return {"message": f"Die Summe aus {zahl1} + {zahl2} = {ergebnis}"}


###################################
### Note API Endpoints (Day2)
###################################


class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = Field(default_factory=list)


class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str
    tags: list[str] = Field(default_factory=list)
    

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


NOTES_FILE = Path("data/notes.json")


def load_notes():
    """Load notes from JSON file and return notes list and next ID."""
    notes_db = []
    note_id_counter = 1

    if NOTES_FILE.exists():
        with open(NOTES_FILE, "r") as f:
            data = json.load(f)
            notes_db = [Note(**note) for note in data]

        if notes_db:
            note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db_to_save):
    """Save notes to JSON file after each change."""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, "w") as f:
        notes_data = [note.model_dump() for note in notes_db_to_save]
        json.dump(notes_data, f, indent=2)


notes_db, note_id_counter = load_notes()


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note:
    global note_id_counter

    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=note.tags,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    notes_db.append(new_note)
    note_id_counter += 1
    save_notes(notes_db)

    return new_note


@app.get("/notes")
def list_notes(
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None
) -> list[Note]:
    filtered = notes_db

    if category:
        filtered = [n for n in filtered if n.category == category]
    if search:
        filtered = [n for n in filtered if search.lower() in n.title.lower() or search.lower() in n.content.lower()]
    if tag:
        filtered = [n for n in filtered if tag.lower() in [t.lower() for t in n.tags]]
    if created_after:
        filtered = [n for n in filtered if n.created_at >= created_after]
    if created_before:
        filtered = [n for n in filtered if n.created_at <= created_before]

    return filtered


@app.get("/notes/stats") # Tag 3
def get_note_stats():
    notes_db, _ = load_notes()

    categories = {}
    tags = {}

    for note in notes_db:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1

        for tag in note.tags:
            tag = tag.lower()

            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1

    top_tags = sorted(
        tags.items(),
        key=lambda item: item[1],
        reverse=True
    )[:5]

    return {
        "total_notes": len(notes_db),
        "by_category": categories,
        "top_tags": [
            {"tag": tag, "count": count}
            for tag, count in top_tags
        ],
        "unique_tags_count": len(tags)
    }


@app.get("/notes/category/{category}")
def get_notes_by_category(category: str):
    filtered_notes = []

    for note in notes_db:
        if note.category == category:
            filtered_notes.append(note)

    return filtered_notes

@app.get("/categories") # Tag 3
def list_categories() -> list[str]:
    """Get all unique categories from all notes"""
    notes_db, _ = load_notes()

    categories = set()

    for note in notes_db:
        categories.add(note.category)

    return sorted(categories)


@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str) -> list[Note]:
    """Get all notes in a specific category"""
    notes_db, _ = load_notes()

    filtered_notes = []

    for note in notes_db:
        if note.category == category_name:
            filtered_notes.append(note)

    return filtered_notes


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    for note in notes_db:
        if note.id == note_id:
            return note

    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found",
    )


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate) -> Note:
    notes_db, _ = load_notes()

    for i, note in enumerate(notes_db):
        if note.id == note_id:
            update_data = note_update.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(note, field, value)

            notes_db[i] = note
            save_notes(notes_db)
            return note

    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return {"message": "Note deleted"}

    raise HTTPException(status_code=404, detail="Note not found")






#Tag 3 

@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:

    namen = ["Alice", "Bob", "Charlie", "David", "Eve"]

    if not param1:
        return{"namen": namen}
    

    name_gefiltert = []
    for name in namen:
        if param1 and param1 in name:
            name_gefiltert.append(name)
            

    return {
        "param1": param1,
        "param2": param2,
        "namen": name_gefiltert
    }

## Hier wurde der Statistik-Endpoint für die Notes erweitert.
# Es wird berechnet, wie viele Notes es insgesamt gibt
# und wie viele Notes in jeder Kategorie gespeichert sind.
# Zusaetzlich werden alle Tags gezaehlt, die 5 häufigsten Tags
# ausgegeben und die Anzahl der unterschiedlichen Tags bestimmt.
# Die Route /notes/stats steht vor /notes/{note_id},
# damit "stats" nicht als ID gelesen wird.



       # ============================================================================
# DAY 4: Advanced API Features
# ============================================================================
# Goal: Write and run tests for our APIs
#       - Use pytest to write unit tests for our API endpoints
#       - Use FastAPI's TestClient to simulate API requests
#       - Use Requests library to test API endpoints from outside the app
# Topics: Testing FastAPI applications, pytest, TestClient, Requests library
# ============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

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
        raise HTTPException(status_code=400, detail="Age cannot be negative")

    is_adult = age >= 18

    return {
        "age": age,
        "is_adult": is_adult,
        "can_vote": is_adult,
        "can_drive": is_adult
    }


