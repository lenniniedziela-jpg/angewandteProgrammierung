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

# Applied Programming - Day 4
## POST Endpoints & Creating Data

**Duration:** 3 hours  
**Goal:** Add course creation to our API

---

## Today's Agenda

**Part 1** (45 min): POST Requests & Pydantic Models  
→ Creating data vs retrieving data

**Break** (15 min) ☕

**Part 2** (65 min): Build POST Endpoints  
→ Create courses, validation, file persistence

**Part 3** (40 min): Writing Tests with pytest  
→ Test your own endpoints

**Part 4** (15 min): Homework & Wrap-up

---

## 🎯 By End of Today

You will have:
- ✅ POST endpoints that create data
- ✅ Pydantic models for validation
- ✅ File persistence for courses
- ✅ Basic pytest tests you wrote yourself
- ✅ Understanding of test-driven development

**Complete CRUD operations (Create + Read)!**

---

# Part 1: POST Requests & Pydantic

Creating data in APIs

---

## HTTP Methods Recap

| Method | Purpose | Example |
|--------|---------|---------|
| **GET** | Retrieve data | Get all courses |
| **POST** | Create data | Add new course |
| PUT | Update data | Change course info |
| DELETE | Remove data | Delete course |

**Today we focus on POST!**

---

## GET vs POST

**GET (what we've been doing):**
- Retrieves existing data
- Parameters in URL
- No body in request
- Safe (doesn't change data)

**POST (new today):**
- Creates new data
- Data in request body
- Changes server state
- Returns created resource

---

## POST Request Structure

```
POST /courses HTTP/1.1
Content-Type: application/json

{
  "code": "CS101",
  "name": "Computer Science Basics",
  "semester": 1,
  "ects": 5,
  "lecturer": "Prof. Smith"
}
```

**Body contains the data to create!**

---

## Why Pydantic Models?

**Problem without validation:**
```python
@app.post("/courses")
def create_course(course_data: dict):
    # What if code is missing?
    # What if ects is a string not int?
    # What if semester is negative?
```

**Solution: Pydantic models!**
- Automatic validation
- Type checking
- Clear documentation
- Better error messages

---

## Creating a Pydantic Model

```python
from pydantic import BaseModel

class CourseCreate(BaseModel):
    code: str
    name: str
    semester: int
    ects: int
    lecturer: str
```

**What this does:**
- Defines expected structure
- Enforces types
- Validates automatically
- Documents in /docs

---

## Using the Model

```python
@app.post("/courses")
def create_course(course: CourseCreate):
    # course.code is guaranteed to be a string
    # course.semester is guaranteed to be an int
    # All fields are guaranteed to exist
    
    new_course = {
        "id": generate_id(),
        "code": course.code,
        "name": course.name,
        "semester": course.semester,
        "ects": course.ects,
        "lecturer": course.lecturer
    }
    return new_course
```

---

## What Pydantic Validates

**Type checking:**
```json
{"code": "CS101", "semester": "one"}  ❌
{"code": "CS101", "semester": 1}      ✅
```

**Required fields:**
```json
{"code": "CS101"}                     ❌ Missing fields
{"code": "CS101", "name": "...", ...} ✅ All fields
```

**Returns 422 Unprocessable Entity on validation failure**

---

## Two Models Pattern

**CourseCreate** - What comes IN (no ID yet):
```python
class CourseCreate(BaseModel):
    code: str
    name: str
    semester: int
    ects: int
    lecturer: str
```

**Course** - What goes OUT (with ID):
```python
class Course(BaseModel):
    id: int
    code: str
    name: str
    semester: int
    ects: int
    lecturer: str
```

---

## Status Code: 201 Created

**When creating resources, use 201:**

```python
@app.post("/courses", status_code=201)
def create_course(course: CourseCreate):
    # Create and save course
    return new_course
```

**Why 201 not 200?**
- 201 specifically means "resource created"
- More semantic and correct
- Follows REST conventions

---

# Break Time! ☕

**15 minutes**

When you return, we'll add POST to our Course API

---

# Part 2: Build POST Endpoints

Add course creation

---

## What We're Adding

**New functionality:**
- POST /courses - Create new course
- File persistence (save to courses.json)
- Auto-increment IDs
- Duplicate detection (prevent same code twice)

**Building on Day 2 file concepts!**

---

## Step 1: Add Imports

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
```

**Same as Day 2 - we'll use file storage!**

---

## Step 2: Define Models

```python
class CourseCreate(BaseModel):
    """Model for creating courses (no ID)"""
    code: str
    name: str
    semester: int
    ects: int
    lecturer: str


class Course(BaseModel):
    """Model for courses (with ID)"""
    id: int
    code: str
    name: str
    semester: int
    ects: int
    lecturer: str
```

---

## Step 3: File Path Setup

```python
# File path for persistence
COURSES_FILE = Path("courses.json")
```

**Same pattern as Day 2 notes - no global variables!**

---

## Step 4: Load Courses Function

```python
def load_courses():
    """Load courses from JSON file and return courses list and next ID counter"""
    courses_db = []
    course_id_counter = 1
    
    if COURSES_FILE.exists():
        with open(COURSES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            courses_db = [Course(**course) for course in data]
            
            if courses_db:
                course_id_counter = max(c.id for c in courses_db) + 1
    
    return courses_db, course_id_counter
```

**Returns the loaded data - called at the start of each endpoint!**

---

## Step 5: Save Courses Function

```python
def save_courses(courses_db):
    """Save courses to JSON file after each change"""
    with open(COURSES_FILE, 'w', encoding='utf-8') as f:
        # Convert Course objects to dicts
        courses_data = [course.dict() for course in courses_db]
        json.dump(courses_data, f, indent=2, ensure_ascii=False)
```

**Takes courses_db as parameter - called after modifying data!**

---

## Step 6: Create FastAPI App

```python
app = FastAPI(
    title="StudyBuddy Course Catalog API",
    version="2.0.0"
)
```

**No loading on startup - we load in each endpoint function!**

---

## Step 7: Create POST Endpoint

```python
@app.post("/courses", status_code=201)
def create_course(course: CourseCreate) -> Course:
    """Create a new course"""
    # Load current courses
    courses_db, course_id_counter = load_courses()
    
    # Check for duplicate code
    for existing in courses_db:
        if existing.code.upper() == course.code.upper():
            raise HTTPException(
                status_code=409,
                detail=f"Course with code '{course.code}' already exists"
            )
    
    # Create new course
    new_course = Course(
        id=course_id_counter,
        **course.dict()
    )
    
    courses_db.append(new_course)
    save_courses(courses_db)
    
    return new_course
```

---

## Understanding Duplicate Check

```python
for existing in courses_db:
    if existing.code.upper() == course.code.upper():
        raise HTTPException(status_code=409, ...)
```

**Why status code 409?**
- 409 = Conflict
- Resource already exists
- Can't create duplicate

**Case-insensitive check:** PROG101 = prog101

---

## Understanding **course.dict()

```python
new_course = Course(
    id=course_id_counter,
    **course.dict()
)
```

**What this does:**
- `course.dict()` → `{"code": "...", "name": "...", ...}`
- `**` unpacks the dict
- Same as: `Course(id=1, code="...", name="...", ...)`

**Convenient way to copy all fields!**

---

## Step 8: Update GET Endpoints

**Update list endpoint to load courses:**

```python
@app.get("/courses")
def list_courses(semester: int = None, min_ects: int = 0) -> list[Course]:
    """List all courses with optional filters"""
    # Load courses
    courses_db, _ = load_courses()
    
    filtered = courses_db  # Already Pydantic Course objects
    
    if semester is not None:
        filtered = [c for c in filtered if c.semester == semester]
    
    if min_ects > 0:
        filtered = [c for c in filtered if c.ects >= min_ects]
    
    return filtered
```

---

## Step 9: Try Creating a Course

**In /docs, POST /courses:**

```json
{
  "code": "AI101", "name": "Artificial Intelligence Basics",
  "semester": 3, "ects": 6,
  "lecturer": "Prof. Dr. Wagner"
}
```

**Response (201 Created):**
```json
{
  "id": 1, "code": "AI101",
  "name": "Artificial Intelligence Basics",
  "semester": 3, "ects": 6,
  "lecturer": "Prof. Dr. Wagner"
}
```

---

## Verify File Persistence

1. Create a course via POST
2. Check: `courses.json` file exists!
3. Stop server (Ctrl+C)
4. Start server again
5. GET /courses → Your course is still there! 🎉

**Data persists between restarts!**

---

## Try Error Cases

<div class='columns'>
<div>

### ❌ Validation Errors (422)

**Missing field:**
```json
{"code": "AI101", "name": "AI Course"}
```
**Result:** 422 Unprocessable Entity

**Wrong type:**
```json
{"code": "AI101", "name": "AI", 
 "semester": "three", ...}
```
**Result:** 422 Unprocessable Entity

</div>
<div>

### ⚠️ Business Logic Errors

**Duplicate code (409 Conflict):**
```json
{"code": "AI101", 
 "name": "Different Course", 
 "semester": 1, "ects": 5,
 "lecturer": "Another Prof"}
```
**Result:** 409 Conflict

**Why 409?**
- Course code must be unique
- AI101 already exists
- Cannot create duplicate

</div>
</div>

---

# Part 3: Writing Tests with pytest

Test your own code!

---

## Why Write Tests?

**Benefits:**
- Catch bugs before users do
- Verify features work correctly
- Confidence when changing code
- Documentation of expected behavior

**Today: You'll write tests yourself!**

---

## Install pytest

```powershell
uv add pytest requests
```

**Two packages:**
- `pytest` - Testing framework
- `requests` - HTTP client for testing

---

## Testing Approaches: Overview

**Two ways to test FastAPI:**

<div class='columns'>
<div>

### 1️⃣ External Testing (requests)
- Real HTTP calls
- Server must be running
- Tests like real client
- Slower (network overhead)

```python
import requests
response = requests.get(
    "http://127.0.0.1:8000/"
)
```

</div>
<div>

### 2️⃣ Internal Testing (TestClient)
- No server needed
- Direct function calls
- Faster execution
- Built into FastAPI

```python
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get("/")
```

</div>
</div>

**We'll learn both!**

---

## Minimal Example: Hello World API

**Create a simple API (hello.py):**

<div class='columns'>
<div>

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/greet/{name}")
def greet_person(name: str):
    return {"greeting": f"Hello {name}!"}
```

</div><div>

**Two endpoints:**
- `GET /` → Returns hello message
- `GET /greet/{name}` → Greets person by name

</div></div>

---

## Approach 1: Testing with requests

**Create test_hello_requests.py:**

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_greet():
    """Test greeting endpoint"""
    response = requests.get(f"{BASE_URL}/greet/Alice")
    
    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello Alice!"}
```

**Requires server running!**

---

## Running requests-based Tests

**Terminal 1 - Start server:**
```powershell
uv run fastapi dev hello.py
```

**Terminal 2 - Run tests:**
```powershell
uv run pytest test_hello_requests.py -v
```

**Output:**
```
test_root ✅ PASSED
test_greet ✅ PASSED
```

**Pros:** Tests real HTTP behavior  
**Cons:** Need server running, slower

---

## Approach 2: Testing with TestClient

**Create test_hello_client.py:**

```python
from fastapi.testclient import TestClient
from hello import app  # Import your FastAPI app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_greet():
    """Test greeting endpoint"""
    response = client.get("/greet/Alice")   
    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello Alice!"}
```

**No server needed!**

---

## Running TestClient-based Tests

**Just run tests directly:**
```powershell
uv run pytest test_hello_client.py -v
```

**Output:**
```
test_root ✅ PASSED
test_greet ✅ PASSED
```

**Pros:** Fast, no server needed, easier setup  
**Cons:** Doesn't test real network layer

---

## Comparison: requests vs TestClient

<div class='columns'>
<div>

### requests Library
```python
import requests
BASE_URL = "http://127.0.0.1:8000"
def test_endpoint():
    response = requests.get(
        f"{BASE_URL}/path")
    assert response.status_code == 200
```

**When to use:**
- Integration testing
- Testing deployed APIs
- Testing external APIs
- Real-world scenarios

</div>
<div>

### TestClient
```python
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
def test_endpoint():
    response = client.get("/path")
    assert response.status_code == 200
```

**When to use:**
- Unit testing
- Development
- CI/CD pipelines
- Fast feedback

</div>
</div>

---

## Which One to Use?

**For homework and learning:**
- Start with `requests` (what we teach today)
- Easier to understand (real HTTP calls)
- See the API running

**For production projects:**
- Use `TestClient` (faster, better)
- No server management needed
- Preferred in professional settings

**Both test the same functionality!**

---

## Create Test File

**Create test_notes.py:**

```python
import requests
BASE_URL = "http://127.0.0.1:8000"
def test_create_note():
    """Test creating a new note"""
    # Arrange - prepare test data
    note_data = {
        "title": "Test Note",
        "content": "Test content",
        "category": "Testing",
        "tags": ["test", "pytest"]
    }
    # Act - make request
    response = requests.post(f"{BASE_URL}/notes", json=note_data)
    # Assert - check results
    assert response.status_code == 201
    assert response.json()["title"] == "Test Note"
```

---

## Arrange-Act-Assert Pattern

**Arrange:** Set up test data
```python
note_data = {"title": "Test Note", ...}
```

**Act:** Perform the action
```python
response = requests.post(...)
```

**Assert:** Check expectations
```python
assert response.status_code == 201
assert response.json()["title"] == "Test Note"
```

**Standard testing pattern!**

---

## Writing Your First Test

**Test GET /notes:**

```python
def test_list_notes():
    """Test listing all notes"""
    response = requests.get(f"{BASE_URL}/notes")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Simple and effective!**

---

## Test 404 Errors

```python
def test_get_nonexistent_note():
    """Test getting a note that doesn't exist"""
    response = requests.get(f"{BASE_URL}/notes/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**Testing error cases is important!**

---

## Test Query Parameters

```python
def test_filter_by_category():
    """Test filtering notes by category"""
    response = requests.get(f"{BASE_URL}/notes?category=Work")
    
    assert response.status_code == 200
    notes = response.json()
    
    # All returned notes should be in Work category
    for note in notes:
        assert note["category"] == "Work"
```

---

## Running Tests

**Make sure server is running:**
```powershell
# Terminal 1
uv run fastapi dev
```

**Run tests:**
```powershell
# Terminal 2
uv run pytest test_notes.py -v
```

**Output:**
```
test_create_note ✅ PASSED
test_list_notes ✅ PASSED
test_get_nonexistent_note ✅ PASSED
test_filter_by_category ✅ PASSED
```

---

## Writing Better Assertions

**Check multiple things:**
```python
def test_create_note():
    note_data = {
        "title": "Test Note",
        "content": "Test content", 
        "category": "Testing",
        "tags": ["test"]
    }
    response = requests.post(f"{BASE_URL}/notes", json=note_data)
    
    # Check status
    assert response.status_code == 201
    
    # Check response has all fields
    result = response.json()
    assert "id" in result
    assert result["title"] == "Test Note"
    assert result["category"] == "Testing"
    
    # Check it's in the list now
    list_response = requests.get(f"{BASE_URL}/notes")
    all_notes = list_response.json()
    note_ids = [n["id"] for n in all_notes]
    assert result["id"] in note_ids
```

---

## Apply What You Learned

**You now know how to write tests!**

In today's homework, you'll write comprehensive tests for your **Notes API** from Days 2 & 3.

**Test everything you built over the last two days!**

---

# Part 4: Homework

Test your Notes API comprehensively!

---

## 📝 Homework Assignment

**Goal:** Write comprehensive test suite for your Notes API  
**Time:** 90-120 minutes  
**Submit:** `test_notes.py` file  
**Deadline:** Before Day 5 class

**Test all features from Day 2 & Day 3!**

---

## What You're Testing

**Your Notes API from previous days includes:**

<div class='columns'>
<div>

**Day 2 Features:**
- POST /notes - Create note
- GET /notes - List notes
- GET /notes/{id} - Get specific note

**Day 3 Features:**
- PUT /notes/{id} - Update note
- DELETE /notes/{id} - Delete note
- Filtering (category, search, tag)
- Date-based filtering

</div>
<div>

**Day 3 Homework Features:**
- GET /notes/stats - Statistics
- GET /categories - List categories  
- GET /categories/{cat}/notes - Notes by category
- PATCH /notes/{id} - Partial updates
- Combined filters
- Database (if you did Task 6)

</div>
</div>

---

## Task 1: Write Basic CRUD Tests

**Test creating, reading, updating, and deleting notes: (cut off code)**

<div class='columns'>
<div>

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_create_note():
    """Test creating a new note"""
    note_data = {
        "title": "Test Note",
        "content": "Test content",
        "category": "Testing",
        "tags": ["test", "pytest"]
    }
    response = requests.post(
        f"{BASE_URL}/notes", 
        json=note_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert "id" in data
    assert "created_at" in data
```

</div>
<div>

```python
def test_list_notes():
    """Test listing all notes"""
    response = requests.get(
        f"{BASE_URL}/notes"
    )
    
    assert response.status_code == 200
    assert isinstance(
        response.json(), list
    )

def test_get_note_by_id():
    """Test getting specific note"""
    # First create a note
    create_resp = requests.post(
        f"{BASE_URL}/notes",
        json={...}
    )
    note_id = create_resp.json()["id"]
    
    # Then get it
    response = requests.get(
        f"{BASE_URL}/notes/{note_id}"
    )
    assert response.status_code == 200
```

</div>
</div>

---

## Task 1: More CRUD Tests

**Test updates and deletes: (code cut off)**

```python
def test_update_note():
    """Test updating a note (PUT)"""
    # Create note first
    create_resp = requests.post(f"{BASE_URL}/notes", json={...})
    note_id = create_resp.json()["id"]
    
    # Update it
    updated_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Updated",
        "tags": ["updated"]
    }
    response = requests.put(f"{BASE_URL}/notes/{note_id}", json=updated_data)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_note():
    """Test deleting a note"""
    # Create then delete
    create_resp = requests.post(f"{BASE_URL}/notes", json={...})
    note_id = create_resp.json()["id"]
    
    response = requests.delete(f"{BASE_URL}/notes/{note_id}")
    assert response.status_code in [200, 204]
    
    # Verify it's gone
    get_resp = requests.get(f"{BASE_URL}/notes/{note_id}")
    assert get_resp.status_code == 404
```

---

## Task 2: Test Filtering

**Test all filter combinations:**

```python
def test_filter_by_category():
    """Test filtering notes by category"""
    # Create notes in specific category
    for i in range(3):
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Work",
            "tags": []
        })
    
    ....

def test_filter_by_search():
    """Test search functionality"""
    response = requests.get(f"{BASE_URL}/notes?search=meeting")
    assert response.status_code == 200
    # Results should contain "meeting" in title or content

def test_filter_by_tag():
    """Test filtering by tag"""
    response = ...
    assert response.status_code == 200
```

---

## Task 2: Combined Filters

**Test multiple filters together:**

```python
def test_combined_filters():
    """Test using multiple filters at once"""
    response = requests.get(
        f"{BASE_URL}/notes?category=Work&tag=urgent&search=meeting"
    )
    
    ...
    
    # Verify all filters applied
    ...

def test_date_filtering():
    """Test date-based filtering (Day 3 Task 5)"""
    ...
```

---

## Task 3: Test Error Cases

**Test validation and error handling:**

```python
def test_create_note_missing_field():
    """Test creating note with missing required field"""
    invalid_note = {
        "title": "Test",
        # Missing content and category
    }
    response = requests.post(f"{BASE_URL}/notes", json=invalid_note)
    assert response.status_code == 422

def test_get_nonexistent_note():
    """Test getting a note that doesn't exist"""
    ...

def test_update_nonexistent_note():
    """Test updating a note that doesn't exist"""
    ...

def test_delete_nonexistent_note():
    """Test deleting a note that doesn't exist"""
    ...
```

---

## Task 4: Test Day 3 Homework Features

**Test statistics and categories endpoints:**

```python
def test_notes_statistics():
    """Test GET /notes/stats endpoint (Day 3 Task 2)"""
    response = requests.get(f"{BASE_URL}/notes/stats")
    ...

def test_list_categories():
    """Test GET /categories endpoint (Day 3 Task 3)"""
    ...

def test_notes_by_category():
    """Test GET /categories/{category}/notes (Day 3 Task 3)"""
    ...
```

---

## Task 4: Test PATCH Endpoint

**Test partial updates:**

```python
def test_patch_note_title_only():
    """Test PATCH to update only title (Day 3 Task 4)"""
    # Create note
    ...
    
    # Update only title
    ...
    
    # Check if only title is changed
    ...

def test_patch_multiple_fields():
    """Test PATCH with multiple fields"""
    # Similar but update title and content
    pass
```

---

## Homework Checklist

**Required tests (minimum 15):**

<div class='columns'>
<div>

**CRUD (5 tests):**
- [ ] test_create_note
- [ ] test_list_notes  
- [ ] test_get_note_by_id
- [ ] test_update_note
- [ ] test_delete_note

**Filtering (4 tests):**
- [ ] test_filter_by_category
- [ ] test_filter_by_search
- [ ] test_filter_by_tag
- [ ] test_combined_filters

</div>
<div>

**Error Cases (4 tests):**
- [ ] test_create_note_missing_field
- [ ] test_get_nonexistent_note
- [ ] test_update_nonexistent_note
- [ ] test_delete_nonexistent_note

**Day 3 Features (2+ tests):**
- [ ] test_notes_statistics
- [ ] test_patch_note

</div>
</div>

---

## Running Your Tests

**Start your API server:**
```powershell
# Terminal 1
uv run fastapi dev
```

**Run tests:**
```powershell
# Terminal 2  
uv run pytest test_notes.py -v

# Expected output:
# test_create_note ✅ PASSED
# test_list_notes ✅ PASSED
# ... (13 more tests)
# ========== 15 passed in 3.45s ==========
```

**All tests should pass!**

---

## Bonus Challenges (Optional)

**Extra tests for excellence:**

1. **Test tag endpoints:**
   - GET /tags
   - GET /tags/{tag_name}/notes

2. **Test edge cases:**
   - Empty strings
   - Very long content
   - Special characters
   - Unicode in titles

3. **Test database features** (if you did Day 3 Task 6):
   - Verify relationships work
   - Test many-to-many tags
   - Test database persistence

4. **Parametrized tests:**
   ```python
   import pytest
   
   @pytest.mark.parametrize("category", ["Work", "Personal", "Study"])
   def test_categories(category):
       # Test multiple categories at once
       pass
   ```

---

## 🎬 See You on Day 5!

**Next steps:**
1. Write comprehensive test suite for your Notes API
2. Test all features from Days 2 & 3
3. Make sure all tests pass
4. Submit `test_notes.py`

**Focus on quality tests - they're your safety net!** 💪

---

# Summary & Wrap-up

What we learned today

---

## 🎓 Today's Achievements

**POST Endpoints:**
- ✅ Create data with POST
- ✅ Pydantic models for validation
- ✅ Two-model pattern (Create vs Full)
- ✅ Status code 201 Created

**Testing:**
- ✅ pytest basics
- ✅ Writing your own tests
- ✅ Arrange-Act-Assert pattern
- ✅ Testing CRUD operations
- ✅ Testing error cases

**Persistence:**
- ✅ File operations (save/load)
- ✅ Data survives restarts

---

## 🔮 Preview: Day 5

**Next session we'll learn:**
- Advanced API testing patterns
- Test fixtures and cleanup
- Mocking and test isolation
- Integration vs unit tests
- CI/CD basics

**Building robust, well-tested APIs!**

---

## 📚 Key Takeaways

**Remember:**
1. **Test everything** - CRUD, filters, errors
2. **Arrange-Act-Assert** - Structure all tests this way
3. **Test errors too** - 404s, 422s are important
4. **Run tests often** - Before every commit
5. **Tests = Documentation** - Show how API should work
6. **Start simple** - Basic tests first, then edge cases

**Well-tested code is maintainable code!**

---

## Appendix: pytest Cheat Sheet

**Basic test structure:**
```python
def test_something():
    # Arrange
    # Act
    # Assert
    pass
```

**Common assertions:**
```python
assert value == expected
assert value in list
assert "text" in string
assert isinstance(obj, type)
```

**Run tests:**
```powershell
pytest test_file.py -v
```

---

## Appendix: Pydantic Field

**Field constraints:**
```python
from pydantic import Field

class Model(BaseModel):
    text: str = Field(..., min_length=3, max_length=50)
    number: int = Field(..., ge=0, le=100)  # 0 <= x <= 100
    optional: str = Field(default="default value")
```

**Parameters:**
- `min_length` / `max_length` - String length
- `ge` / `le` - Greater/less than or equal
- `gt` / `lt` - Greater/less than (strict)
- `default` - Default value if not provided

---

## Resources

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/tutorial/body/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/

**Testing:**
- Practice writing tests first (TDD)
- Test both success and error cases
- Keep tests simple and focused

**Questions?** Ask in class or forum!

---

**End of Day 4** 🎉
