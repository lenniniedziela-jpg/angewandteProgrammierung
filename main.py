from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path


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


class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str


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
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    notes_db.append(new_note)
    note_id_counter += 1
    save_notes(notes_db)

    return new_note


@app.get("/notes")
def list_notes() -> list[Note]:
    return notes_db


@app.get("/notes/stats")
def get_notes_stats():
    categories = {}

    for note in notes_db:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1

    return {
        "total_notes": len(notes_db),
        "by_category": categories,
    }


@app.get("/notes/category/{category}")
def get_notes_by_category(category: str):
    filtered_notes = []

    for note in notes_db:
        if note.category == category:
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


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return {"message": "Note deleted"}

    raise HTTPException(status_code=404, detail="Note not found")
