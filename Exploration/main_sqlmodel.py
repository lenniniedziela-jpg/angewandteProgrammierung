from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, Relationship, select, or_, col
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Annotated

app = FastAPI(
    title="Notes API with SQLModel",
    description="Day 6 - SQLite Database with SQLModel",
    version="2.0.0"
)

# ----------------------------------------------------------------------------
# LINK TABLE (many-to-many: Note <-> Tag)
# ----------------------------------------------------------------------------

class NoteTagLink(SQLModel, table=True):
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


# ----------------------------------------------------------------------------
# DATABASE MODELS
# ----------------------------------------------------------------------------

class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)

    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)


# ----------------------------------------------------------------------------
# DATABASE SETUP
# ----------------------------------------------------------------------------

engine = create_engine("sqlite:///notes.db")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ----------------------------------------------------------------------------
# API MODELS (Input / Output)
# ----------------------------------------------------------------------------

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str

    class Config:
        from_attributes = True


# ----------------------------------------------------------------------------
# HELPER
# ----------------------------------------------------------------------------

def note_to_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )


def get_or_create_tags(session: Session, tag_names: list[str]) -> list[Tag]:
    tag_objects = []
    seen = set()

    for name in tag_names:
        name = name.lower().strip()
        if not name or name in seen:
            continue
        seen.add(name)

        existing = session.exec(select(Tag).where(Tag.name == name)).first()
        if existing:
            tag_objects.append(existing)
        else:
            new_tag = Tag(name=name)
            session.add(new_tag)
            tag_objects.append(new_tag)

    return tag_objects


# ----------------------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Notes API with SQLModel"}


@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = Note(title=note.title, content=note.content, category=note.category)
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
    created_after: Optional[str] = None,
    created_before: Optional[str] = None
) -> list[NoteResponse]:
    statement = select(Note)

    if category:
        statement = statement.where(Note.category == category)

    if search:
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search}%"),
                col(Note.content).ilike(f"%{search}%")
            )
        )

    if tag:
        statement = statement.join(Note.tags).where(Tag.name == tag.lower())

    notes = session.exec(statement).all()

    if created_after:
        notes = [n for n in notes if n.created_at.isoformat() >= created_after]
    if created_before:
        notes = [n for n in notes if n.created_at.isoformat() <= created_before]

    return [note_to_response(n) for n in notes]


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note_to_response(note)


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note_update.title:
        note.title = note_update.title
    if note_update.content:
        note.content = note_update.content
    if note_update.category:
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


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    tags = session.exec(select(Tag)).all()
    return sorted([tag.name for tag in tags])


@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    tag = session.exec(select(Tag).where(Tag.name == tag_name.lower())).first()
    if not tag:
        return []
    return [note_to_response(note) for note in tag.notes]


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    notes = session.exec(select(Note)).all()
    return sorted(set(n.category for n in notes))
