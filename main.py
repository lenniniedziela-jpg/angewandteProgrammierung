from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Annotated, Optional


from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field as PydanticField, field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine, select



app = FastAPI(
    title="Applied Programming Notes API",
    description="Task 6: Note API migrated from JSON to SQLite with SQLModel",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/name/{name}")
def greet_name(name: str):
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
### Note API Endpoints (Task 6)
###################################


class NoteTagLink(SQLModel, table=True):
    note_id: Optional[int] = Field(
        default=None,
        foreign_key="notes.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tags.id",
        primary_key=True,
    )


class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tags: list["Tag"] = Relationship(
        back_populates="notes",
        link_model=NoteTagLink,
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    notes: list["Note"] = Relationship(
        back_populates="tags",
        link_model=NoteTagLink,
    )

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        return value.strip().lower()


    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 30:
            raise ValueError("name must be 2 to 30 characters long")

        if not re.fullmatch(r"^[a-z0-9-]+$", value):
            raise ValueError("name must contain only lowercase letters, digits, and dashes")

        return value




ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas", "general", "Essen"}


class NoteCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = PydanticField(
        min_length=3,
        max_length=100,
        description="Short note title shown in lists",
        examples=["Shopping list", "Meeting prep"],
    )
    content: str = PydanticField(
        min_length=1,
        max_length=10_000,
        description="Main note content",
        examples=["Buy milk, bread and apples"],
    )
    category: str = PydanticField(
        min_length=2,
        max_length=30,
        pattern=r"^[a-z]+$",
        description="Lowercase category, e.g. work, personal, school",
        examples=["work"],
    )
    tags: list[str] = PydanticField(
        default_factory=list,
        max_length=10,
        description="Up to 10 tags, normalized to lowercase",
        examples=[["urgent", "meeting"]],
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must not be empty or whitespace")
        return value

    @field_validator("category", mode="before")
    @classmethod
    def normalize_and_validate_category(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("category must be a string")
        normalized = value.strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        normalized_tags = []
        seen = set()

        for tag in value:
            if not isinstance(tag, str):
                raise ValueError("tags must contain only strings")
            normalized = tag.strip().lower()

            if not normalized:
                raise ValueError("tags must not contain empty values")
            if len(normalized) < 2:
                raise ValueError("tags must be at least 2 characters long")
            if normalized in seen:
                continue

            seen.add(normalized)
            normalized_tags.append(normalized)

        return normalized_tags
class NoteUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str | None = PydanticField(default=None, min_length=3, max_length=100)
    content: str | None = PydanticField(default=None, min_length=1, max_length=10_000)
    category: str | None = PydanticField(
        default=None,
        min_length=2,
        max_length=30,
        pattern=r"^[a-z]+$",
    )
    tags: list[str] | None = PydanticField(default=None, max_length=10)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("title must not be empty or whitespace")
        return value

    @field_validator("category", mode="before")
    @classmethod
    def normalize_and_validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("category must be a string")

        normalized = value.strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value

        normalized_tags = []
        seen = set()

        for tag in value:
            if not isinstance(tag, str):
                raise ValueError("tags must contain only strings")
            normalized = tag.strip().lower()

            if not normalized:
                raise ValueError("tags must not contain empty values")
            if len(normalized) < 2:
                raise ValueError("tags must be at least 2 characters long")
            if normalized in seen:
                continue

            seen.add(normalized)
            normalized_tags.append(normalized)

        return normalized_tags
class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str
    created_at: str
    tags: list[str]


JSON_NOTES_FILE = Path("data/notes.json")
engine = create_engine("sqlite:///notes.db")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def note_to_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        created_at=note.created_at.isoformat(),
        tags=[tag.name for tag in note.tags],
    )


def get_or_create_tags(session: Session, tag_names: list[str]) -> list[Tag]:
    tag_objects = []
    seen = set()

    for name in tag_names:
        clean_name = name.lower().strip()
        if not clean_name or clean_name in seen:
            continue

        seen.add(clean_name)
        existing_tag = session.exec(
            select(Tag).where(Tag.name == clean_name)
        ).first()

        if existing_tag:
            tag_objects.append(existing_tag)
            continue

        new_tag = Tag(name=clean_name)
        session.add(new_tag)
        session.flush()
        tag_objects.append(new_tag)

    return tag_objects


def migrate_json_notes():
    if not JSON_NOTES_FILE.exists():
        return

    with Session(engine) as session:
        existing_note = session.exec(select(Note)).first()
        if existing_note:
            return

        with open(JSON_NOTES_FILE, "r") as f:
            raw_notes = json.load(f)

        for raw_note in raw_notes:
            created_at_value = raw_note.get("created_at")
            created_at = datetime.now(timezone.utc)

            if created_at_value:
                created_at = datetime.fromisoformat(created_at_value)

            db_note = Note(
                title=raw_note["title"],
                content=raw_note["content"],
                category=raw_note["category"],
                created_at=created_at,
            )
            db_note.tags = get_or_create_tags(session, raw_note.get("tags", []))

            session.add(db_note)

        session.commit()


migrate_json_notes()


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category,
    )
    db_note.tags = get_or_create_tags(session, note.tags)

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    return note_to_response(db_note)


@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
) -> list[NoteResponse]:
    notes = session.exec(select(Note)).all()

    if category:
        notes = [note for note in notes if note.category == category]

    if search:
        search_lower = search.lower()
        notes = [
            note for note in notes
            if search_lower in note.title.lower()
            or search_lower in note.content.lower()
        ]

    if tag:
        tag_lower = tag.lower()
        notes = [
            note for note in notes
            if tag_lower in [note_tag.name.lower() for note_tag in note.tags]
        ]

    if created_after:
        notes = [
            note for note in notes
            if note.created_at >= created_after
        ]

    if created_before:
        notes = [
            note for note in notes
            if note.created_at <= created_before
        ]

    return [note_to_response(note) for note in notes]


@app.get("/notes/stats")
def get_note_stats(session: SessionDep):
    notes = session.exec(select(Note)).all()

    categories = Counter(note.category for note in notes)
    tags = Counter(
        tag.name.lower()
        for note in notes
        for tag in note.tags
    )

    return {
        "total_notes": len(notes),
        "by_category": dict(categories),
        "top_tags": [
            {"tag": tag, "count": count}
            for tag, count in tags.most_common(5)
        ],
        "unique_tags_count": len(tags),
    }


@app.get("/notes/category/{category}")
def get_notes_by_category_legacy(
    category: str,
    session: SessionDep,
) -> list[NoteResponse]:
    notes = session.exec(
        select(Note).where(Note.category == category)
    ).all()
    return [note_to_response(note) for note in notes]


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    notes = session.exec(select(Note)).all()
    return sorted({note.category for note in notes})


@app.get("/categories/{category_name}/notes")
def get_notes_by_category(
    category_name: str,
    session: SessionDep,
) -> list[NoteResponse]:
    notes = session.exec(
        select(Note).where(Note.category == category_name)
    ).all()
    return [note_to_response(note) for note in notes]


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    tags = session.exec(select(Tag)).all()
    return sorted(tag.name for tag in tags)


@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    target_tag = session.exec(
        select(Tag).where(Tag.name == tag_name.lower())
    ).first()
    if not target_tag:
        return []

    return [note_to_response(note) for note in target_tag.notes]


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note with ID {note_id} not found",
        )

    return note_to_response(note)


@app.put("/notes/{note_id}")
def update_note(
    note_id: int,
    note_update: NoteCreate,
    session: SessionDep,
) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note with ID {note_id} not found",
        )

    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category
    note.tags = get_or_create_tags(session, note_update.tags)

    session.add(note)
    session.commit()
    session.refresh(note)

    return note_to_response(note)


@app.patch("/notes/{note_id}")
def partial_update_note(
    note_id: int,
    note_update: NoteUpdate,
    session: SessionDep,
) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.category is not None:
        note.category = note_update.category
    if note_update.tags is not None:
        note.tags = get_or_create_tags(session, note_update.tags)

    session.add(note)
    session.commit()
    session.refresh(note)

    return note_to_response(note)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()


@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:
    namen = ["Alice", "Bob", "Charlie", "David", "Eve"]

    if not param1:
        return {"namen": namen}

    name_gefiltert = []
    for name in namen:
        if param1 in name:
            name_gefiltert.append(name)

    return {
        "param1": param1,
        "param2": param2,
        "namen": name_gefiltert,
    }
