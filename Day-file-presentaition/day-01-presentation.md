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

# Applied Programming - Day 1
## Setup & Your First API

**Duration:** 3 hours  
**Goal:** Build a working FastAPI app with 3 endpoints


---

## Course Structure (1/2)



### 📅 Timeline & Format

**Duration:** 3 Weeks
- **3 sessions** per week
- **3 hours** each session
- Mix of on-site & online
- Hands-on learning approach


---

## Course Structure (2/2)

### 📝 Assignments & Grading

<div class="columns">
<div>
**Required for each session:**
- ✅ Coding Assignment
- ✅ Work-Log documentation

**Grading Criteria:**
- 🎯 **Both** assignments mandatory
- 📦 Submitted via **GitHub**
- 📊 Final grade based on all assignments
- 💡 Content may adjust, workload stays same
</div><div>

**Important:**
> Your GitHub repositories are the single source of truth for grading!

</div></div>




---

## Today's Agenda

**Part 1** (60 min): Environment Setup  
→ Install Git, VS Code, uv

**Break** (15 min) ☕

**Part 2** (90 min): Build First API  
→ What is an API?  
→ Code together: 3 endpoints  
→ Try your API in `/docs`

**Part 3** (15 min): Homework & Wrap-up

---

## 🎯 By End of Today

You will have:
- ✅ Development environment ready
- ✅ Working FastAPI app
- ✅ 3 endpoints: `/`, `/status`, `/about`
- ✅ Knowledge to build 3 more for homework

**Questions are welcome! This is a beginner-friendly course.**

---

# Part 1: Environment Setup

Install 3 tools together, step by step:
1. Git
2. VS Code  
3. uv (Python package manager)

---

## Install Git

**Step 1:** Go to https://git-scm.com/downloads  
**Step 2:** Download for your OS (Windows/Mac)  
**Step 3:** Run installer (default settings)  
**Step 4:** Verify in terminal:

```powershell
git --version
```

Expected: `git version 2.43.0` or similar

✅ Git installed!

---

## Install VS Code

**Step 1:** Go to https://code.visualstudio.com/  
**Step 2:** Download and install  
**Step 3:** Open VS Code  
**Step 4:** Install Python extension
- Click Extensions (left sidebar)
- Search "Python"
- Install "Python" by Microsoft

✅ VS Code ready!

---

## Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify:**
```powershell
uv --version
```

✅ uv installed!

---

## 🎉 Setup Complete!

You have:
- Git (version control)
- VS Code (code editor)
- uv (package manager)

**Take a 15-minute break!** ☕

---

# ☕ Break (15 minutes)

---

# Part 2: Build Your First API

Let's create a real FastAPI application!

---

## What is an API?

**API = Application Programming Interface**

**Simple analogy:** Restaurant
- You (customer) → Order food
- Waiter (API) → Takes order to kitchen
- Kitchen (server) → Prepares food
- Waiter (API) → Brings food back

**In tech:**
- App asks API for data
- API gets data from server
- API returns data to app

---

## What is FastAPI?

**FastAPI** = Modern Python framework for building APIs

**Why FastAPI?**
- Fast to write code
- Fast to run
- **Automatic documentation** ← Amazing!
- Type hints for validation
- Great error messages

**Perfect for learning!**

---

## Step 1: Create Project

**Windows (PowerShell):**
```powershell
cd Documents
mkdir my-first-api
cd my-first-api
code .
```

**Mac:**
```bash
cd Documents
mkdir my-first-api
cd my-first-api
code .
```

This creates a folder and opens VS Code.

---

## Step 2: Install FastAPI

In VS Code terminal (`` Ctrl+` ``):

```powershell
uv add fastapi
```

This installs FastAPI and creates a virtual environment automatically.

---

## Step 3: Create main.py

1. In VS Code Explorer: Click "New File"
2. Name it: `main.py`
3. This is where we write our API code

---

## Step 4: Write Code Together

Type this in `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()
```

**What this does:**
- Line 1: Import FastAPI
- Line 3: Create your API application

---

## Step 5: Add First Endpoint

Add this below:

```python
@app.get("/")
def read_root():
    return {"message": "Hello World!"}
```

**What this does:**
- `@app.get("/")` → Handle GET requests to `/`
- `def read_root():` → Function name
- `return {...}` → Send back data (Python dict → JSON)

---

## Step 6: Run Your API

In terminal:

```powershell
uv run fastapi dev
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

🎉 **Your API is running!**

---

## Step 7: Try in Browser

**Open browser:**  
Go to: http://127.0.0.1:8000

**You should see:**
```json
{
  "message": "Hello World!"
}
```

✅ **It works!**

---

## Step 8: Check Auto Docs

**Go to:** http://127.0.0.1:8000/docs

You'll see:
- Interactive API documentation
- All endpoints listed
- "Try it out" buttons

**This is FastAPI's killer feature!**

---

## Step 9: Add Status Endpoint

Add this to `main.py`:

```python
@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.1.0",
        "day": 1
    }
```

**The API auto-reloads!**  
Check `/docs` → new endpoint appears automatically.

---

## Step 10: Try Status Endpoint

1. Go to: http://127.0.0.1:8000/docs
2. Find `GET /status`
3. Click "Try it out"
4. Click "Execute"

**Response:**
```json
{
  "status": "online",
  "version": "0.1.0",
  "day": 1
}
```

---

## Step 11: Add About Endpoint

Add this to `main.py`:

```python
@app.get("/about")
def get_about():
    return {
        "project": "My First API",
        "author": "Your Name",  # ← Change this!
        "course": "Applied Programming"
    }
```

---

## Your Complete main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.1.0",
        "day": 1
    }

@app.get("/about")
def get_about():
    return {
        "project": "My First API",
        "author": "Your Name",
        "course": "Applied Programming"
    }
```

---

## 🎉 You Built an API!

You now have **3 working endpoints:**
- `/` → Welcome message
- `/status` → API status
- `/about` → Project info

**Try them all in `/docs`!**

---

# Part 3: Homework

---

## 📝 Homework Assignment

**Goal:** Practice what you learned today  
**Time:** 30-45 minutes  
**Submit:** Your `main.py` file  
**Deadline:** Before Day 2 class

---

## Task 1: Square Calculator

**Create an endpoint that calculates the square of a number.**

**URL:** `/square/{number}`  
**Method:** GET  
**Example:** `/square/5`  

**Response:**
```json
{
  "number": 5,
  "square": 25,
  "calculation": "5 × 5 = 25"
}
```

---

## Task 1: Code Template

```python
@app.get("/square/{number}")
def calculate_square(number: int):
    result = number * number
    return {
        "number": number,
        "square": result,
        "calculation": f"{number} × {number} = {result}"
    }
```

**Try it:**
- `/square/5` → 25
- `/square/10` → 100
- `/square/7` → 49

---

## Task 2: Student Info

**Create an endpoint with YOUR information.**

**URL:** `/student`  
**Method:** GET  

**Response:**
```json
{
  "name": "Your Name",
  "semester": 1,
  "course": "Wirtschaftsinformatik",
  "university": "Your University"
}
```

**Important:** Use your real information!

---

## Task 2: Code Template

```python
@app.get("/student")
def get_student():
    return {
        "name": "Max Mustermann",  # ← Your name
        "semester": 1,              # ← Your semester
        "course": "Wirtschaftsinformatik",
        "university": "Your Uni"    # ← Your university
    }
```

---

## Task 3: Double Calculator

**Create another calculation endpoint.**

**URL:** `/double/{number}`  
**Method:** GET  
**Example:** `/double/7`  

**Response:**
```json
{
  "number": 7,
  "double": 14,
  "calculation": "7 × 2 = 14"
}
```

---

## Task 3: Code Template

```python
@app.get("/double/{number}")
def calculate_double(number: int):
    result = number * 2
    return {
        "number": number,
        "double": result,
        "calculation": f"{number} × 2 = {result}"
    }
```

---

## Homework Checklist

**Before submitting, make sure:**

- [ ] All 6 endpoints work (3 from class + 3 homework)
- [ ] `/square/{number}` calculates correctly
- [ ] `/student` has YOUR real information
- [ ] `/double/{number}` calculates correctly
- [ ] Try all endpoints in `/docs`
- [ ] Submit `main.py` file to course platform

---

## Complete main.py Structure

Your final file should have:

```python
from fastapi import FastAPI

app = FastAPI()

# Class endpoints (done together)
@app.get("/")
@app.get("/status")
@app.get("/about")

# Homework endpoints (you do)
@app.get("/square/{number}")
@app.get("/student")
@app.get("/double/{number}")
```

**Total: 6 endpoints**

---

## 💡 Tips for Success

1. **Try frequently** - Use `/docs` to check each endpoint
2. **Check types** - Path parameters are converted to `int` automatically
3. **Use f-strings** - For the calculation messages
4. **Read error messages** - They tell you exactly what's wrong
5. **Ask for help** - In class or forum if stuck

---

## 📚 Summary

**Today you learned:**
- ✅ Set up development environment
- ✅ What APIs are and why they're useful
- ✅ Created a FastAPI application
- ✅ Built 3 working endpoints
- ✅ Used automatic documentation at `/docs`

**You're an API developer now!** 🚀

---

## Key Takeaways

**Remember:**
1. FastAPI pattern: `@app.get("/path")` + function + `return dict`
2. Auto docs at `/docs` → try everything there
3. Run API: `uv run fastapi dev`
4. Check your work in `/docs` before submission

---

## Need Help?

**During class:** Raise your hand  
**Outside class:** Course forum or email instructor  

**Common issues:**
- API won't start? → Close other programs using port 8000
- Endpoint doesn't appear? → Check `/docs` to see all endpoints
- Import error? → Run `uv add package-name`

---

## 👀 Preview: Day 2

**Next class:**
- Python fundamentals (variables, functions, data types)
- HTTP & JSON basics
- POST requests (create data)
- Data validation with Pydantic

**Bring your questions!**

---

## 🎬 See You on Day 2!

**Next steps:**
1. Complete 3 homework endpoints
2. Try them all in `/docs`
3. Submit `main.py` to your github repository

**Great job today!** 👏

---

## Appendix: Quick Reference

**Terminal Commands:**
```powershell
cd folder          # Change directory
mkdir folder       # Create folder
code .             # Open VS Code
uv add package     # Install package
uv run fastapi dev # Start API
```

**FastAPI Pattern:**
```python
@app.get("/path")
def function_name():
    return {"key": "value"}
```

---

**End of Day 1** 🎉
