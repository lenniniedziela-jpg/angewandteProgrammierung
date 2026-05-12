---
marp: true
theme: default
paginate: true

style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
---



# Applied Programming - Day 3
## REST API Design & Complete CRUD

**Duration:** 3 hours  
**Goal:** Extend Day 2 Note API with full CRUD, filtering, and resource relationships

---

## Course Planning Update

* Montag 4.5.2026 online
* Dienstag 5.5.2026 vor Ort
* Mittwoch 6.5.2026 online inkl. Aufzeichnung.

---


## Today's Agenda

**Part 1** (40 min): REST API Design Principles  
→ What is REST? Resource-oriented design

**Break** (15 min) ☕

**Part 2** (35 min): Path & Query Parameters  
→ /notes/{id} vs /notes?category=work

**Part 3** (75 min): Extend Note API v2.0  
→ Add tags, filters, PUT/DELETE, resource relationships

**Part 4** (15 min): Homework & Wrap-up

---

## 🎯 By End of Today

You will have:
- ✅ Understanding of REST principles
- ✅ Complete CRUD operations (POST, GET, PUT, DELETE)
- ✅ Query parameter filtering (category, search, tags)
- ✅ Resource relationships (`/tags/{tag}/notes`)
- ✅ Production-ready Note API v2.0

**Building on Day 2's foundation with professional features!**

---

# Part 1: REST API Design

Professional API architecture

---

## What is REST?

**REST = Representational State Transfer**

An architectural style for designing web APIs

**Key idea:** Everything is a **resource**
- Courses are resources
- Students are resources
- Enrollments are resources

**Resources have:**
- Unique URLs
- Standard operations (GET, POST, PUT, DELETE)
- Representations (usually JSON)

---

## REST Core Principles

**1. Resource-Based**
- URLs represent resources (nouns), not actions (verbs)  (`/courses` not `/getCourses`)

**2. HTTP Methods Have Meaning**
- GET = Retrieve
- POST = Create
- PUT = Update
- DELETE = Delete

**3. Stateless**
- Each request is independent
- Server doesn't remember previous requests

---

## Good vs Bad URL Design

**✅ GOOD (RESTful):**
```
GET    /courses              List all courses
GET    /courses/5            Get course with ID 5
POST   /courses              Create new course
PUT    /courses/5            Update course 5
DELETE /courses/5            Delete course 5
```

**❌ BAD (Not RESTful):**
```
GET    /getCourses           Verb in path
POST   /createCourse         Verb in path
GET    /courses/delete/5     Action as path
POST   /updateCourseById     Mixed approach
```

---

## Resource Hierarchy

**Organize URLs logically:**

```
/courses                    All courses
/courses/5                  Specific course
/courses/5/students         Students in course 5
/courses/5/students/12      Specific student in course

/students                   All students
/students/12                Specific student
/students/12/courses        Courses for student 12
```

**Pattern:** `/collection` → `/collection/{id}` → `/sub-collection`

---

## HTTP Status Codes (Quick Review)

| Code | Meaning | When to use |
|------|---------|-------------|
| **200** | OK | Successful GET/PUT/DELETE |
| **201** | Created | Successful POST |
| **400** | Bad Request | Invalid input |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable | Validation failed |
| **500** | Server Error | Something broke |

**FastAPI helps with most of these automatically!**

---

## REST Design Exercise

**Which is RESTful?**

**Option A:**
```
POST /createStudent
POST /deleteStudent
POST /updateStudent
```

**Option B:**
```
POST   /students
DELETE /students/5
PUT    /students/5
```

---

## REST Best Practices

**1. Use plural nouns:** `/courses` not `/course`

**2. Be consistent:** Don't mix `/courses` and `/course-list`

**3. Keep URLs simple:** Avoid deep nesting (max 2-3 levels)

**4. Use query params for filtering:** `/courses?semester=1`

**5. Return proper status codes:** Don't return 200 for errors!

---

# Break Time! ☕

**15 minutes**

When you return, we'll implement REST principles

---

# Part 2: Path & Query Parameters

Two ways to pass data in URLs

---

## Path Parameters

**Path parameters identify a specific resource:**

```python
@app.get("/courses/{course_id}")
def get_course(course_id: int):
    return {"id": course_id, "name": "Some Course"}
```

**URL:** `/courses/5`
**Result:** `course_id = 5`

**Characteristics:**
- Part of the path
- Required (must provide)
- Used for **identification**

---

## Hands-On Practice - Endpoint-Order

Create these endpoints and test them in order:

1. Create `/test/{value}` endpoint (returns the path parameter)
2. Create `/test/{value}/test2/{value2}` endpoint (returns both parameters)
3. Create `/test/123` endpoint (returns a fixed message)
4. Test different URLs and observe:
   - Does `/test/123` match the first or second endpoint?
   - What happens with `/test/hello`?
   - How does endpoint order affect which route matches?

Try reordering your endpoints and test again. Why does order matter?

---

## Path Parameter Examples

```python
@app.get("/courses/{course_id}")
def get_course(course_id: int):
    # course_id is automatically converted to int
    pass

@app.get("/courses/code/{course_code}")
def get_course_by_code(course_code: str):
    # course_code stays as string
    pass

@app.get("/students/{student_id}/courses/{course_id}")
def get_student_course(student_id: int, course_id: int):
    # Multiple path parameters
    pass
```

---

## Path Parameters: Type Conversion

**FastAPI automatically converts and validates:**

```python
@app.get("/courses/{course_id}")
def get_course(course_id: int):  # Must be int!
    pass
```

**URLs:**
- `/courses/5` ✅ → `course_id = 5`
- `/courses/42` ✅ → `course_id = 42`
- `/courses/abc` ❌ → 422 Validation Error

**FastAPI does the work for you!**

---

## Query Parameters

<div class='columns'>
<div>

**Query parameters filter or modify results:**

```python
@app.get("/courses")
def list_courses(semester: int = None):
    if semester:
        return filtered_courses
    return all_courses
```
</div>
<div>

**URLs:**
- `/courses` → All courses
- `/courses?semester=1` → Only semester 1
- `/courses?semester=2` → Only semester 2

**Characteristics:**
- After `?` in URL
- Optional (have default values)
- Used for **filtering, sorting, pagination**
</div>
</div>
---

## Multiple Query Parameters

**Combine filters:**

```python
@app.get("/courses")
def list_courses(
    semester: int = None,
    min_ects: int = 0,
    search: str = None
):
    # Apply all filters
    pass
```

**URLs:**
- `/courses?semester=1`
- `/courses?min_ects=5`
- `/courses?semester=1&min_ects=5`
- `/courses?search=programming`
- `/courses?semester=1&min_ects=5&search=info`

---

## Path vs Query: When to Use?

| Aspect | Path Parameter | Query Parameter |
|--------|----------------|-----------------|
| **Purpose** | Identify resource | Filter/modify results |
| **Required** | Yes | No (optional) |
| **Syntax** | `/courses/5` | `/courses?semester=1` |
| **Example** | Get course 5 | Get all semester 1 courses |
| **REST** | Part of resource URL | Modifies collection |

**Rule of thumb:** Path for ID, Query for filtering

---

## Query Parameters: Default Values

```python
@app.get("/courses")
def list_courses(
    semester: int = None,      # Optional, no filter if omitted
    limit: int = 10,           # Default 10 if not specified
    offset: int = 0            # Default 0 if not specified
):
    pass
```

**URLs:**
- `/courses` → semester=None, limit=10, offset=0
- `/courses?semester=1` → semester=1, limit=10, offset=0
- `/courses?limit=20` → semester=None, limit=20, offset=0

---

# Part 3: Extend the Note API

Building on Day 2's foundation!

---

## What We're Building Today

**Enhanced Note API v2.0:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/notes` | GET | List notes with **filters** (category, search, tags) |
| `/notes/{note_id}` | PUT | **Update** existing note |
| `/notes/{note_id}` | DELETE | **Delete** note |
| `/tags` | GET | List all unique tags |
| `/tags/{tag_name}/notes` | GET | Get all notes with specific tag |

**New features: Filtering, tags, complete CRUD!**

---

## Review: What We Have from Day 2

**Existing endpoints:**
- ✅ POST `/notes` - Create note
- ✅ GET `/notes` - List all notes
- ✅ GET `/notes/{note_id}` - Get specific note
- ✅ File persistence with `load_notes()` and `save_notes()`

**Data model:**
```python
class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str  # From homework!
    created_at: str
```

---

## Today's Enhancements

**We're adding:**

1. **Tags** - Array field for flexible categorization
2. **Query Parameters** - Filter notes by category, search text, tags
3. **PUT endpoint** - Update existing notes
4. **DELETE endpoint** - Remove notes
5. **Resource Relationship** - `/tags/{tag}/notes` endpoint

**Complete, production-ready CRUD API!**

---

## Step 1: Setup - Open Your Day 2 Project

**Navigate to your note-api from Day 2:**

```powershell
cd note-api
```

**Your current main.py should have:**
- NoteCreate and Note models
- load_notes() and save_notes() functions
- POST, GET (list), GET (by ID) endpoints

**We'll enhance this today!**

---

## Step 2: Update Data Models with Tags

**Update your NoteCreate model:**

```python
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []  # ← ADD THIS (default empty list)
```

**Update your Note model:**

```python
class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str] = []  # ← ADD THIS
    created_at: str
```

---

## Understanding Tags

**Tags vs Category:**

| Aspect | Category | Tags |
|--------|----------|------|
| **Count** | One category | Multiple tags |
| **Example** | `"work"` | `["urgent", "meeting", "client"]` |
| **Use case** | Broad classification | Detailed labeling |

**Example note:**
```json
{
  "title": "Project Meeting",
  "category": "work",
  "tags": ["urgent", "client", "Q2"]
}
```

---

## Step 3: Add Filtering to GET /notes

**Replace your existing list_notes function:**

```python
@app.get("/notes")
def list_notes(
    category: str = None,
    search: str = None,
    tag: str = None
) -> list[Note]:
    """
    List notes with optional filters
    
    - category: Filter by category
    - search: Search in title and content
    - tag: Filter by tag
    """
    notes_db, _ = load_notes()
    
    # Apply filters
    filtered = []
    for note in notes_db:
        # Filter by category
        if category and note.category != category:
            continue
        
        # Filter by search term
        if search:
            search_lower = search.lower()
            title_match = search_lower in note.title.lower()
            content_match = search_lower in note.content.lower()
            if not (title_match or content_match):
                continue
        
        # Filter by tag
        if tag and tag not in note.tags:
            continue
        
        filtered.append(note)
    
    return filtered
```

---

## Understanding the Filter Logic

<div class='columns'>
<div>

**Category filter:**
```python
if category and note.category != category:
    continue  # Skip this note
```

**Search filter:**
```python
if search:
    search_lower = search.lower()
    if search_lower not in title:
        continue
```

</div>
<div>

**Tag filter:**
```python
if tag and tag not in note.tags:
    continue  # Skip this note
```

**`continue` = skip to next note**
**Only notes passing ALL filters are added!**

</div>
</div>

---

## Try the Filters

**First, create some notes with tags:**

```json
{
  "title": "Team Meeting",
  "content": "Discuss Q2 goals",
  "category": "work",
  "tags": ["meeting", "urgent"]
}
```

**Then try filters:**
- `/notes?category=work` → Only work notes
- `/notes?search=meeting` → Notes containing "meeting"
- `/notes?tag=urgent` → Notes tagged as urgent
- `/notes?category=work&tag=urgent` → Combined filters!

---

## Step 4: Add PUT Endpoint (Update Note)

```python
@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate) -> Note:
    """Update an existing note"""
    
    notes_db, _ = load_notes()
    
    # Find the note
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            # Update note (keep id and created_at)
            updated_note = Note(
                id=note.id,
                title=note_update.title,
                content=note_update.content,
                category=note_update.category,
                tags=note_update.tags,
                created_at=note.created_at
            )
            
            notes_db[i] = updated_note
            save_notes(notes_db)
            return updated_note
    
    # Not found
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )
```

---

## Understanding PUT

**PUT = Replace entire resource**

<div class="columns">
<div>

```python
updated_note = Note(
    id=note.id,              # Keep original ID
    title=note_update.title, # New title
    content=note_update.content,
    category=note_update.category,
    tags=note_update.tags,
    created_at=note.created_at  # Keep original timestamp
)
```
</div><div>

**Key points:**
- Preserves ID and creation timestamp
- Updates everything else
- Saves to file
- Returns updated note

</div></div>

---

## Try PUT Endpoint

**In /docs:**

1. **Create a note** with POST `/notes`
2. **Note the ID** (e.g., ID = 1)
3. **Update it** with PUT `/notes/1`:
   ```json
   {
     "title": "Updated Title",
     "content": "New content",
     "category": "personal",
     "tags": ["updated"]
   }
   ```
4. **Verify** with GET `/notes/1`

**The note is updated!**

---

## Step 5: Add DELETE Endpoint

```python
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note"""
    
    notes_db, _ = load_notes()
    
    # Find and remove the note
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return  # 204 No Content
    
    # Not found
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )
```

---

## Understanding DELETE

**Status code 204 = No Content**

```python
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    notes_db.pop(i)  # Remove from list
    save_notes(notes_db)
    return  # No response body
```

**Why 204?**
- Delete was successful
- Nothing to return
- Standard REST practice

**If not found → 404**

---

## Try DELETE Endpoint

**In /docs:**

1. **Create a test note** with POST `/notes`
2. **Note the ID** (e.g., ID = 5)
3. **Delete it** with DELETE `/notes/5`
4. **Verify** with GET `/notes` (note should be gone)
5. **Try again** DELETE `/notes/5` → 404 Error

**Deletes are permanent!**

---

## Complete CRUD Operations

**You now have all CRUD operations:**

| Operation | HTTP Method | Endpoint | Purpose |
|-----------|-------------|----------|---------|
| **C**reate | POST | `/notes` | Create new note |
| **R**ead | GET | `/notes` | List notes |
| **R**ead | GET | `/notes/{id}` | Get single note |
| **U**pdate | PUT | `/notes/{id}` | Update note |
| **D**elete | DELETE | `/notes/{id}` | Delete note |

**Professional, production-ready API!**

---

## Step 6: Add Tags Resource Endpoint

**Get all unique tags across all notes:**

```python
@app.get("/tags")
def list_tags() -> list[str]:
    """Get all unique tags from all notes"""
    
    notes_db, _ = load_notes()
    
    # Collect all tags
    all_tags = set()
    for note in notes_db:
        for tag in note.tags:
            all_tags.add(tag)
    
    # Return sorted list
    return sorted(list(all_tags))
```

---

## Understanding Resource Relationships

**`/tags` is a separate resource:**

```
/notes          → Note resources
/tags           → Tag resources (derived from notes)
/tags/{tag}/notes → Relationship: notes for specific tag
```

**REST pattern: Collections and relationships**

**Benefits:**
- Discover available tags
- Navigate between resources
- RESTful architecture

---

## Step 7: Get Notes by Tag

**Add endpoint for tag-based retrieval:**

```python
@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str) -> list[Note]:
    """Get all notes with a specific tag"""
    
    notes_db, _ = load_notes()
    
    # Filter notes by tag
    filtered = []
    for note in notes_db:
        if tag_name in note.tags:
            filtered.append(note)
    
    return filtered
```

**URL pattern: `/tags/urgent/notes` → All notes with "urgent" tag**

---

## Resource Relationships in Action

**Try these in /docs:**

1. Create notes with various tags:
   - Note 1: `tags: ["urgent", "work"]`
   - Note 2: `tags: ["personal", "urgent"]`
   - Note 3: `tags: ["work", "meeting"]`

2. **GET `/tags`** → `["meeting", "personal", "urgent", "work"]`

3. **GET `/tags/urgent/notes`** → Returns Notes 1 and 2

4. **GET `/tags/meeting/notes`** → Returns Note 3

---

## Complete API Structure

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path

# Models with tags
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []

class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str] = []
    created_at: str

# Storage
NOTES_FILE = Path("data/notes.json")

# Functions
def load_notes(): ...
def save_notes(notes_db): ...

# App
app = FastAPI(...)
```

---

## Complete Endpoints Overview

```python
# CRUD operations
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note: ...

@app.get("/notes")
def list_notes(category: str = None, search: str = None, 
               tag: str = None) -> list[Note]: ...

@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note: ...

@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate) -> Note: ...

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int): ...

# Tag resources
@app.get("/tags")
def list_tags() -> list[str]: ...

@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str) -> list[Note]: ...
```

---

## 🎉 You Built a Complete REST API!

**What you accomplished:**

- ✅ Complete CRUD (Create, Read, Update, Delete)
- ✅ Query parameter filtering (category, search, tag)
- ✅ Path parameters for identification
- ✅ Resource relationships (`/tags/{tag}/notes`)
- ✅ Proper HTTP methods and status codes
- ✅ Array fields (tags)
- ✅ File persistence
- ✅ RESTful design patterns

**This is production-quality code!**

---

# Part 4: Homework

Extend your Note API further!

---

## 📝 Homework Assignment

**Goal:** Add advanced features to Note API + Database Migration  
**Time:** 150-240 minutes  
**Submit:** Your `main.py` file  
**Deadline:** Before Day 4 class

**6 mandatory tasks (including database migration)**

---

## Task 1: Combine Multiple Filters

**Enhance GET `/notes` to support all three filters simultaneously:**

<div class="columns">
<div>

```python
@app.get("/notes")
def list_notes(
    category: str = None,
    search: str = None,
    tag: str = None
):
    # Already implemented today!
    # Test that ALL three work together
    pass
```

</div><div>

**Test these combinations:**
- `/notes?category=work&tag=urgent`
- `/notes?search=meeting&category=work`
- `/notes?category=personal&tag=family&search=vacation`

</div></div>

---

## Task 2: Add Statistics Endpoint

**Show note statistics:**

<div class="columns">
<div>

```python
@app.get("/notes/stats")
def get_note_stats():
    """
    Get statistics about notes
    
    Returns:
    - Total notes
    - Notes per category
    - Most used tags (top 5)
    - Total number of unique tags
    """
    notes_db, _ = load_notes()
```

</div><div>
continued code
    
```python
    # Calculate statistics
    # ... your code here
    
    return {
        "total_notes": ...,
        "by_category": {...},
        "top_tags": [...],
        "unique_tags_count": ...
    }
```

</div></div>

---

## Task 2: Expected Output

```json
{
  "total_notes": 12,
  "by_category": {
    "work": 5,
    "personal": 4,
    "school": 3
  },
  "top_tags": [
    {"tag": "urgent", "count": 8},
    {"tag": "meeting", "count": 5},
    {"tag": "family", "count": 3},
    {"tag": "project", "count": 2},
    {"tag": "health", "count": 1}
  ],
  "unique_tags_count": 15
}
```

---

## Task 2: Implementation Hints

Read the Counter documentation: 

https://docs.python.org/3/library/collections.html#collections.Counter

---

## Task 3: Add Categories Resource Endpoint

<div class="columns">
<div>

**Get all unique categories:**

```python
@app.get("/categories")
def list_categories() -> list[str]:
    """Get all unique categories from all notes"""
    notes_db, _ = load_notes()
    
    # Collect unique categories
    # Return sorted list
    pass
```

</div><div>

**Add category-based retrieval:**

```python
@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str) -> list[Note]:
    """Get all notes in a specific category"""
    notes_db, _ = load_notes()
    
    # Filter notes by category
    pass
```

</div></div>

---

## Task 3: Expected Behavior

**URLs:**
- `/categories` → `["personal", "school", "work"]`
- `/categories/work/notes` → All notes with `category: "work"`
- `/categories/personal/notes` → All notes with `category: "personal"`

**Pattern matches `/tags` resource:**
```
/tags                 → List all tags
/tags/{tag}/notes     → Notes with specific tag

/categories                      → List all categories
/categories/{category}/notes     → Notes in specific category
```

---

## Task 4: Add PATCH Endpoint for Partial Updates

**Add partial update capability (advanced):**

<div class='columns'>
<div>

```python
from typing import Optional

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None

@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate) -> Note:
    """
    Partially update a note (only provided fields)
    
    Unlike PUT, PATCH only updates fields you provide
    """
    notes_db, _ = load_notes()
```

</div><div>
... continued code

```python
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            # Update only provided fields
            ...

            notes_db[i] = note
            save_notes(notes_db)
            return note
    
    raise HTTPException(status_code=404, detail="Note not found")
```

</div></div>

---

## Task 4: PUT vs PATCH

**Difference:**

| Method | Updates | Use case |
|--------|---------|----------|
| **PUT** | Entire resource | Replace all fields |
| **PATCH** | Partial fields | Update only specific fields |

**Examples:**

**PUT** `/notes/1` - Must provide ALL fields:
```json
{"title": "New", "content": "New", "category": "work", "tags": []}
```

**PATCH** `/notes/1` - Provide ONLY what you want to change:
```json
{"title": "Just change title"}
```

---

## Task 5: Date-Based Filtering

**Add date range filtering to the notes endpoint:**

<div class='columns'>
<div>

```python
@app.get("/notes")
def list_notes(
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: str = None,  # ISO date format
    created_before: str = None
):
    # Filter by date range
    # Hint: Compare ISO strings directly
    pass
```

</div><div>

**Examples:**
- `/notes?created_after=2026-04-01`
- `/notes?created_before=2026-04-30`
- `/notes?created_after=2026-04-01&created_before=2026-04-30`

**Both parameters are optional and can be combined with other filters!**

</div></div>

---

## Task 5: Implementation Hints

**ISO date strings can be compared directly:**

```python
if created_after and note.created_at < created_after:
    continue  # Skip notes created before the threshold

if created_before and note.created_at > created_before:
    continue  # Skip notes created after the threshold
```

**Why this works:**
- ISO format: `"2026-04-28T10:30:00"`
- String comparison works because ISO format is sortable
- `"2026-04-28"` < `"2026-04-29"` evaluates correctly

---

## Task 6: Database Migration 🗄️

**Replace JSON file storage with SQLite database using SQLModel**

**Why migrate to database?**
- ✅ Better concurrency (multiple users)
- ✅ Faster queries and searching
- ✅ Data integrity and transactions
- ✅ Professional, production-ready approach
- ✅ Easier to scale

**Essential skill for production applications!**

---

## Task 6: What is SQLModel?

**SQLModel = Pydantic + SQLAlchemy**

Documentation at **https://sqlmodel.tiangolo.com/**

<div class='columns'>
<div>

**Without ORM (raw SQL):**
```python
cursor.execute(
  "INSERT INTO notes (title, content) VALUES (?, ?)",
  (title, content)
)
result = cursor.fetchall()
```

</div>
<div>

**With SQLModel (Python objects):**
```python
note = Note(
  title=title,
  content=content
)
session.add(note)
session.commit()
```

</div>
</div>

**SQLModel translates Python code to SQL automatically!**

---

## Task 6: Step 1 - Install SQLModel

**Add SQLModel to your project:**

```powershell
uv add sqlmodel
```

**Look into the SQLite Database**:
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer)

**SQLModel will:**
- Create SQLite database file
- Manage database schema
- Handle transactions
- Provide query interface

**No need to write SQL!**

---

## Task 6: Step 2 - Define Database Models

**Create database models with proper relationships:**

<div class='columns'>
<div>

```python
from sqlmodel import SQLModel, Field, Session, create_engine, Relationship
from datetime import datetime
from typing import Optional

class Note(SQLModel, table=True):
    __tablename__ = 'notes'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Many-to-many relationship with Tag (implicit link table)
    tags: list["Tag"] = Relationship(back_populates="notes")
```

</div>
<div>

```python
class Tag(SQLModel, table=True):
    __tablename__ = 'tags'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # Unique tag name
    
    # Many-to-many relationship with Note (implicit link table)
    notes: list[Note] = Relationship(back_populates="tags")

# Create database engine
engine = create_engine("sqlite:///notes.db")

# Create tables (Note, Tag, and link table)
SQLModel.metadata.create_all(engine)
```

</div>
</div>

**SQLModel automatically creates a link table for the many-to-many relationship!**

---

## Task 6: Understanding Many-to-Many Relationships

**What happens behind the scenes:**

<div class='columns'>
<div>

**Tables created:**
1. **notes** table (id, title, content, category, created_at)
2. **tags** table (id, name)
3. **notelink** table (note_id, tag_id) ← Created automatically!

</div>
<div>

**The link table:**
- Connects notes and tags
- Allows one note to have many tags
- Allows one tag to be on many notes
- Created implicitly by SQLModel

</div>
</div>

---

**Example data:**

<div class='columns'>
<div>

**notes table:**
| id | title |
|----|-------|
| 1 | Team Meeting |
| 2 | Shopping List |

**tags table:**
| id | name |
|----|------|
| 1 | urgent |
| 2 | work |

</div>
<div>

**notelink table:**
| note_id | tag_id |
|---------|--------|
| 1 | 1 |
| 1 | 2 |
| 2 | 1 |

</div>
</div></div>
</div>


**Note 1 has tags "urgent" and "work", Note 2 has tag "urgent"**

---

## Task 6: Step 3 - Add Session Dependency

**Create database session for each request:**

<div class='columns'>
<div>

```python
from typing import Annotated
from fastapi import Depends

def get_session():
    """Create a new database session for each request"""
    with Session(engine) as session:
        yield session

# Type alias for cleaner code
SessionDep = Annotated[Session, Depends(get_session)]
```

**FastAPI will automatically:**
- Create a new session for each request
- Close the session when done
- Handle database transactions

---

## Task 6: Step 4 - Create Response Models

**Separate API models for input/output:**

<div class='columns'>
<div>

```python
from pydantic import BaseModel

# API Input model
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []
```

</div>
<div>

```python
# API Output model
class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    
    class Config:
        from_attributes = True
```

</div>
</div>

---

## Task 6: Step 5 - Update Create Endpoint

**Replace file operations with database operations (cut off in presentation):**

```python
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Create a new note in database"""
    
    # Create note
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    # Get or create tags (case-insensitive, deduplicated)
    tag_objects = []
    seen_tags = set()
    
    for tag_name in note.tags:
        tag_name_lower = tag_name.lower().strip()
        if not tag_name_lower or tag_name_lower in seen_tags:
            continue
        
        seen_tags.add(tag_name_lower)
        
        # Find existing tag or create new one
        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
            session.add(new_tag)
            tag_objects.append(new_tag)
    
    db_note.tags = tag_objects
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)  # Get the generated ID and load relationships
    
    # Convert to response model
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        category=db_note.category,
        tags=[tag.name for tag in db_note.tags],
        created_at=db_note.created_at.isoformat()
    )
```

---

## Task 6: Step 6 - Update List Endpoint

**Query database with filters (database-level) (cut off in presentation):**

```python
from sqlmodel import select, or_, col

@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None
) -> list[NoteResponse]:
    """List notes with filters"""
    
    # Build query
    statement = select(Note)
    
    # Apply filters
    if category:
        statement = statement.where(Note.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(Note.tags).where(Tag.name == tag_lower)
    
    # Execute query
    notes = session.exec(statement).all()
    
    # Convert to response models
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]
```

**All filtering happens in the database for better performance!**

---

## Task 6: Step 7 - Update Other Endpoints

**Pattern for all endpoints:**

```python
@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        ...

@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    ...

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    ...

@app.patch

...
```

---

## Task 6: Step 8 - Update Tag Endpoints

**Tag endpoints become much simpler (code cut off in presentation):**

```python
@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    """Get all unique tags from the Tag table"""
    statement = select(Tag)
    tags = session.exec(statement).all()
    
    return sorted([tag.name for tag in tags])

@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes with specific tag"""
    
    # Find the tag (case-insensitive)
    tag_lower = tag_name.lower()
    statement = select(Tag).where(Tag.name == tag_lower)
    tag = session.exec(statement).first()
    
    if not tag:
        return []  # No notes if tag doesn't exist
    
    # Return all notes associated with this tag
    return [
        NoteResponse(
            ...
        )
        for note in tag.notes
    ]
```

**The relationship automatically handles the join!**

---

## Task 6: Benefits You'll See

**After migration:**

| Feature | JSON Files | Database with Relationships |
|---------|------------|----------|
| **Speed** | Slow for large data | Fast queries with indexes |
| **Search** | Load all, filter | Database-level filtering |
| **Concurrency** | File locks | True transactions |
| **Relationships** | Manual arrays | Automatic joins via `Relationship()` |
| **Data integrity** | Manual validation | Database constraints & unique tags |
| **Scalability** | Limited | Excellent |

**Your API is now production-ready!** 🚀

---

## Task 6: Testing Your Migration

**After migration, test thoroughly:**

1. **Check database file:** `notes.db` should exist
2. **Verify data:** All notes from JSON migrated
3. **Test all endpoints:** POST, GET, PUT, DELETE
4. **Test filters:** category, search, tag still work
5. **Test relationships:** Tags work with multiple notes
6. **Test statistics:** Counts should match
7. **Restart server:** Data persists between restarts


---

## Task 6: Common Issues & Solutions

<div class='columns'>
<div>

**Issue 1: "Session is not defined"**
```python
# Always include session: SessionDep parameter
@app.get("/notes")
def list_notes(session: SessionDep):  # ← Don't forget!
    ...
```

**Issue 2: "Object not JSON serializable"**
```python
# Convert SQLModel objects to Pydantic models
return NoteResponse(...)  # ✅ Use response model
return note  # ❌ Don't return SQLModel object directly
```

</div>
<div>

**Issue 3: "Changes not saved"**
```python
# Always commit after changes
session.add(note)
session.commit()  # ← Don't forget!
session.refresh(note)  # Get updated data & relationships
```

**Issue 4: "Tags not loading"**
```python
# Access tags through the relationship
tags=[tag.name for tag in note.tags]  # ✅
tags=note.tags  # ❌ Returns Tag objects, not strings
```

</div>
</div>

---

## Task 6: Checklist

**Before considering Task 6 complete:**

<div class='columns'>
<div>

- [ ] SQLModel installed (`uv add sqlmodel`)
- [ ] Database models defined (Note and Tag with Relationship)
- [ ] Pydantic response models created
- [ ] Session dependency (`get_session`) set up
- [ ] All CRUD endpoints updated with `session: SessionDep`
- [ ] Tag get-or-create logic implemented

</div>
<div>

- [ ] Statistics endpoint using database queries
- [ ] All filters using database-level queries (joins for tags)
- [ ] `notes.db` file exists and contains data
- [ ] Server can restart without losing data
- [ ] All tests from Tasks 1-5 still pass

</div>
</div>

---

## Homework Checklist

**Before submission:**

<div class='columns'>
<div>

- [ ] Task 1: Combined filters work (all 3)
- [ ] Task 2: Statistics endpoint shows correct data
- [ ] Task 3: `/categories` and `/categories/{name}/notes` work
- [ ] Task 4: PATCH endpoint updates only provided fields
- [ ] Task 5: Date-based filtering works
- [ ] Task 6: Database migration completed (SQLModel + SQLite)

</div>
<div>

- [ ] All CRUD operations work with database
- [ ] Proper error handling (404 for missing resources)
- [ ] Data persists in `notes.db` file
- [ ] Tag relationships working properly
- [ ] Code is clean and well-commented

</div>
</div>

---

## Testing Your Homework (1/2)

**Try these comprehensive tests:**

1. **Filters:** `/notes?category=work&tag=urgent&search=meeting`
2. **Statistics:** `/notes/stats` (should show real data)
3. **Categories resource:** `/categories` and `/categories/work/notes`
4. **PATCH vs PUT:**
   - Create note with POST
   - PATCH to change only title
   - Verify other fields unchanged
5. **Date filtering:** `/notes?created_after=2026-04-01&created_before=2026-04-30`

---

## Testing Your Homework (2/2)

6. **Error cases:** Invalid IDs should return 404
7. **Database persistence:**
   - Stop and restart server - data should persist
   - Check `notes.db` file exists
   - Verify tag relationships work correctly
   - Use DB Browser to inspect database structure

---

# Summary & Wrap-up

What we learned today

---

## 🎓 Today's Achievements

<div class='columns'>
<div>

**REST API Design:**
- ✅ REST principles (resource-based)
- ✅ Good URL design patterns
- ✅ HTTP methods and status codes
- ✅ Resource relationships

**CRUD Operations:**
- ✅ Complete CRUD implementation
- ✅ PUT for full updates
- ✅ DELETE with proper status codes
- ✅ POST, GET from Day 2

</div>
<div>

**Advanced Features:**
- ✅ Query parameter filtering
- ✅ Array fields (tags)
- ✅ Multiple combined filters
- ✅ Resource relationships (`/tags/{tag}/notes`)
- ✅ File persistence maintained

**Built Today:**
- ✅ Enhanced Note API v2.0
- ✅ 7 working endpoints
- ✅ Production-ready code

</div>
</div>

---

## Key Takeaways

<div class='columns'>
<div>

**REST Design:**
- Use nouns for resources, not verbs
- HTTP methods define actions (GET, POST, PUT, DELETE)
- Path parameters identify resources
- Query parameters filter collections

</div><div>

**Real-World Skills:**
- Built on existing code (Day 2 foundation)
- Complete CRUD lifecycle
- Filtering with multiple parameters
- Resource relationships

</div></div>

**You now have a portfolio-worthy API!**



---

## 🔮 Preview: Day 4

**Next session we'll learn:**
- Advanced database queries
- Complex relationships (one-to-many, many-to-many)
- Database migrations with schema changes
- Query optimization
- More complex data models
- API authentication

**You'll already have database experience from Task 6!**

**We'll build on your migrated Note API!**

---

## 📚 Key Takeaways

**Remember:**
1. REST = Resources + HTTP methods
2. URLs should be nouns, not verbs
3. Path params identify, query params filter
4. Always handle errors (404 for not found)
5. Use proper status codes

**Your API is becoming professional!**

---

## 🎬 See You on Day 4!

**Next steps:**
1. Complete all 6 homework tasks (Tasks 1-6)
2. Test all combinations in `/docs`
3. Verify database migration works correctly
4. Make sure error handling works
5. Submit your `main.py` file

**You'll have a production-ready API with database persistence!**

**Great job today!** 👏

---

## Appendix: Quick Reference

**REST Principles:**
- Resources, not actions
- Standard HTTP methods
- Proper status codes

**Parameters:**
```python
# Path (required)
@app.get("/courses/{id}")

# Query (optional)
@app.get("/courses")
def list(semester: int = None)
```

---

## Error Raising:
```python
raise HTTPException(status_code=404, detail="Not found")
```

---

## Appendix: Common Patterns

<div class='columns'>
<div>

**List all:**
```python
@app.get("/resources")
def list_resources():
    return all_resources
```

**Get one:**
```python
@app.get("/resources/{id}")
def get_resource(id: int):
    # Find and return or 404
```

</div>
<div>

**Filter:**
```python
@app.get("/resources")
def list_resources(filter: str = None):
    # Apply filter if provided
```

</div>
</div>

---

## Resources

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- REST API Tutorial: https://restfulapi.net/

**Practice:**
- Try different filter combinations
- Add more courses to your database
- Experiment with search patterns

**Questions?** Ask in class or forum!

---

## Common Mistakes to Avoid

<div class='columns'>
<div>

1. **Using verbs in URLs**
   - ❌ `/getCourses`
   - ✅ `/courses`

2. **Wrong status codes**
   - ❌ Return 200 for errors
   - ✅ Return 404 for not found

</div>
<div>

3. **Not handling None**
   - ❌ `if semester:` (0 is falsy!)
   - ✅ `if semester is not None:`

4. **Case-sensitive search**
   - Remember to use `.lower()` or `.upper()`

</div>
</div>

---

**End of Day 3** 🎉
