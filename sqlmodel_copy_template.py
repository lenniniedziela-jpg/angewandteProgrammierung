# Paste-Vorlage für main.py
# Diese Datei ist absichtlich KEINE eigenständige App.
# Du sollst diesen Block in main.py einfügen und dort den alten JSON-Notes-Teil ersetzen.
#
# Zusätzlich oben in main.py bei den Imports ergänzen:
#
# from collections import Counter
# from datetime import datetime
# from typing import Annotated, Optional
# from fastapi import Depends, HTTPException
# from pydantic import BaseModel, Field as PydanticField
# from sqlmodel import Field, Relationship, SQLModel, Session, create_engine, select
#
# WICHTIG:
# - app = FastAPI() in main.py behalten
# - den alten Notes-/JSON-Block löschen oder ersetzen
# - NICHT einfach nur ans Ende von main.py anhängen


# ----------------------------------------------------------------------------
# SQLMODEL NOTES BLOCK
# ----------------------------------------------------------------------------


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
    created_at: datetime = Field(default_factory=datetime.now)

    tags: list["Tag"] = Relationship(
        back_populates="notes",
        link_model=NoteTagLink,
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    notes: list[Note] = Relationship(
        back_populates="tags",
        link_model=NoteTagLink,
    )


class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = PydanticField(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str
    tags: list[str]

    class Config:
        from_attributes = True


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
) -> list[NoteResponse]:
    statement = select(Note)

    if category:
        statement = statement.where(Note.category == category)

    notes = session.exec(statement).all()

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


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
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


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()

    return {"message": "Note deleted"}


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
