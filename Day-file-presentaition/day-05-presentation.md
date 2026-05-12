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

# Applied Programming - Day 5
## Pydantic Data Validation Deep Dive

**Duration:** 3 hours
**Goal:** Make your Notes API bulletproof with precise Pydantic models

---

## Where We Are

By now you can:

- ✅ Build GET / POST / PUT / PATCH / DELETE endpoints
- ✅ Use Pydantic models to receive request bodies
- ✅ Persist data (file or database)

**Today's focus:** Stop trusting your inputs.
Make Pydantic do the heavy lifting.

---

## Today's Agenda

**Part 1** (50 min): Why validation matters + Field constraints
→ `Field(...)`, lengths, ranges, patterns, optionals

**Break** (15 min) ☕

**Part 2** (50 min): Custom validators
→ `field_validator`, `model_validator`, normalization

**Part 3** (40 min): Model configuration & special types
→ `EmailStr`, `ConfigDict`, error responses

**Part 4** (25 min): Homework — harden the Notes models

---

## 🎯 By End of Today

You will be able to:

- ✅ Use `Field(...)` constraints fluently
- ✅ Write `field_validator` and `model_validator` functions
- ✅ Choose between Optional, default, and required
- ✅ Read and explain Pydantic 422 error responses
- ✅ Tighten loose models so bad data is rejected at the door

---

# Part 1: Why Validation Matters

The problem with trusting input

---

## Our Current Note Model

From Day 2 / Day 3:

```python
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []
```

**Looks fine, right?**

It is *typed*, but it is **not validated**.

---

## What Can Go Wrong?

All of these are accepted today:

```json
{ "title": "",        "content": "x", "category": "work", "tags": [] }
{ "title": "   ",     "content": "",  "category": "WORK", "tags": [] }
{ "title": "x" * 5000,"content": "y", "category": "wOrK", "tags": ["", " ", "URGENT", "urgent"] }
{ "title": "ok",      "content": "y", "category": "banana", "tags": [] }
```

Empty strings, whitespace, casing chaos, unknown categories,
duplicate / empty tags. **Garbage in → garbage forever.**

---

## Two Layers of Validation

<div class='columns'>
<div>

**Type validation (free):**

- `str`, `int`, `list[str]`
- Required vs optional
- Pydantic does this automatically

</div>
<div>

**Value validation (today):**

- "title must be 3–100 chars"
- "category must be one of: work, personal, school"
- "tags must be lowercase, unique, non-empty"

This is what stops bad data.

</div>
</div>

---

## How Pydantic Reports Errors

When validation fails, FastAPI returns **HTTP 422**:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 3 characters",
      "input": ""
    }
  ]
}
```

- `loc` → exactly where the bad value is
- `msg` → human-readable message
- You don't write any of this. Pydantic does.

---

## `Field(...)` — Adding Constraints

`Field` adds rules and metadata to a model attribute:

```python
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)
    category: str = Field(min_length=2, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=10)
```

**The first positional arg of `Field` is the default.**
Omit it (or use `...`) to mean "required".

---

## String Constraints

| Parameter        | Meaning                            |
|------------------|------------------------------------|
| `min_length`     | Minimum number of characters       |
| `max_length`     | Maximum number of characters       |
| `pattern`        | Regex the value must fully match   |

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    # category must be lowercase letters only
    category: str = Field(pattern=r"^[a-z]+$")
```

---

## Numeric Constraints

For `int` / `float` fields:

| Parameter | Meaning             |
|-----------|---------------------|
| `ge`      | greater or equal `>=` |
| `gt`      | strictly greater `>`  |
| `le`      | less or equal `<=`    |
| `lt`      | strictly less `<`     |

```python
class NoteCreate(BaseModel):
    title: str
    content: str
    priority: int = Field(default=1, ge=1, le=5)
```

---

## Required vs Optional vs Default

Three different shapes — know the difference:

```python
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str                         # required, no default
    content: str = ""                  # optional, default ""
    category: str = Field(default="general")
    description: str | None = None     # optional, can be None
    tags: list[str] = Field(default_factory=list)  # ← important!
```

⚠️ Never use `tags: list[str] = []` as a field default in a class —
use `default_factory=list` to avoid shared mutable state.

---

## Hands-On: Tighten `NoteCreate`

In your `main.py`, replace the current `NoteCreate` with:

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10_000)
    category: str = Field(min_length=2, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=10)
```

**Try in `/docs`:**

1. POST a note with `"title": ""` → expect 422
2. POST a note with 11 tags → expect 422
3. POST a valid note → expect 201

---

## Field Metadata for `/docs`

`Field` also documents your API:

```python
class NoteCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
        description="Short note title shown in lists",
        examples=["Shopping list", "Meeting prep"],
    )
    category: str = Field(
        description="Lowercase category, e.g. work, personal, school",
        examples=["work"],
    )
```

→ shows up automatically in Swagger UI at `/docs`.

---

# Break Time! ☕

**15 minutes**

When we come back: custom validators —
the part where you write the rules.

---

# Part 2: Custom Validators

When `Field(...)` is not enough

---

## When You Need a Custom Validator

`Field` covers length / range / regex.
You need a **validator** for things like:

- "category must be one of a fixed list"
- "strip whitespace from title"
- "tags must all be lowercase and unique"
- "if `category == 'work'`, `tags` must include `work`"

Pydantic v2 gives us two tools:

- `@field_validator` — one field at a time
- `@model_validator` — multiple fields together

---

## `@field_validator` Basics

```python
from pydantic import BaseModel, Field, field_validator

ALLOWED_CATEGORIES = {"work", "personal", "school", "ideas"}

class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str
    category: str

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category must be one of {sorted(ALLOWED_CATEGORIES)}"
            )
        return value
```

**Rules:**

- Always `@classmethod`
- **Return** the (possibly modified) value
- Raise `ValueError` on failure → becomes 422

---

## Validators Can Normalize Data

A validator doesn't have to just check — it can **clean**:

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    category: str

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("category")
    @classmethod
    def lowercase_category(cls, value: str) -> str:
        return value.strip().lower()
```

Now `"  Work  "` and `"WORK"` both become `"work"`.

---

## Validating List Fields — Tags

Tags are a classic mess: case, duplicates, empty strings.

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str
    category: str
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, raw: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for tag in raw:
            t = tag.strip().lower()
            if not t:
                raise ValueError("tags must not be empty strings")
            if t in seen:
                continue           # silently drop duplicates
            seen.add(t)
            cleaned.append(t)
        return cleaned
```

---

## Try the Tag Validator

Send this:

```json
{
  "title": "Team sync",
  "content": "Discuss roadmap",
  "category": "work",
  "tags": ["URGENT", "urgent", "  meeting  ", "Q2"]
}
```

You should get back tags:

```json
["urgent", "meeting", "q2"]
```

…and a `422` if any tag is just `""` or `"   "`.

---

## `mode="before"` vs `mode="after"`

By default validators run **after** type coercion.
Use `mode="before"` to see the raw input first.

```python
@field_validator("tags", mode="before")
@classmethod
def accept_comma_string(cls, raw):
    # Accept either a list or a single comma-separated string
    if isinstance(raw, str):
        return [t for t in raw.split(",") if t]
    return raw
```

Now both work:

```json
{ "tags": ["a", "b"] }
{ "tags": "a,b" }
```

---

## `@model_validator` — Cross-Field Rules

Some rules involve **multiple fields**:

> "If category is `work`, the tag list must contain `work`."

```python
from pydantic import model_validator
from typing_extensions import Self

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def work_notes_need_work_tag(self) -> Self:
        if self.category == "work" and "work" not in self.tags:
            raise ValueError("work notes must include the 'work' tag")
        return self
```

`mode="after"` → runs after each field is already validated.

---

## Field Validator vs Model Validator

<div class='columns'>
<div>

**`@field_validator("x")`**

- Sees one field
- Good for: cleaning, range checks, enums
- Returns the cleaned value

</div>
<div>

**`@model_validator(mode="after")`**

- Sees the whole model (`self`)
- Good for: rules that connect fields
- Returns `self`

</div>
</div>

**Rule of thumb:** start with `@field_validator`.
Reach for `@model_validator` only when you truly need 2+ fields.

---

## Common Pitfall: Forgetting to Return

```python
@field_validator("title")
@classmethod
def strip_title(cls, value: str) -> str:
    value.strip()        # ❌ result thrown away
```

Result: title is unchanged. No error. Just silently wrong.

```python
@field_validator("title")
@classmethod
def strip_title(cls, value: str) -> str:
    return value.strip()  # ✅
```

**Always return the value.**

---

# Part 3: Configuration & Special Types

Polish

---

## `EmailStr` — Built-In Email Validation

Suppose we add an `author_email` to a note:

```python
from pydantic import BaseModel, EmailStr

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    author_email: EmailStr
```

```bash
uv add email-validator
```

| Input                   | Result |
|-------------------------|--------|
| `"alice@uni.at"`        | ✅     |
| `"not-an-email"`        | 422    |
| `"alice@"`              | 422    |

---

## Other Useful Built-In Types

| Type             | Validates                          |
|------------------|------------------------------------|
| `EmailStr`       | Valid email address                |
| `HttpUrl`        | Valid http/https URL               |
| `PositiveInt`    | `int > 0`                          |
| `NonNegativeInt` | `int >= 0`                         |
| `UUID4`          | UUID version 4                     |
| `datetime`       | ISO 8601 strings → `datetime` obj  |

```python
from pydantic import HttpUrl, PositiveInt
from datetime import datetime
```

You're not writing the regexes. Pydantic ships them.

---

## `ConfigDict` — Model-Wide Settings

Tired of writing `.strip().lower()` in every validator?
Configure it once:

```python
from pydantic import BaseModel, ConfigDict, Field

class NoteCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,   # auto-strip all str fields
        extra="forbid",              # reject unknown fields
    )

    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1)
    category: str
    tags: list[str] = Field(default_factory=list)
```

---

## `extra="forbid"` — Catch Typos Early

With `extra="forbid"`:

```json
{
  "title": "ok",
  "content": "x",
  "category": "work",
  "tagz": ["typo"]      // 👀 typo
}
```

Returns 422 with:

```
Extra inputs are not permitted (loc: body.tagz)
```

Without it: `tagz` is silently ignored, and your note has no tags.
**Forbid extras during development. You'll thank yourself.**

---

## Two Models, Same Rules

`NoteCreate` (input) and `NoteUpdate` (partial input)
should share validation.

```python
class NoteCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1)
    category: str
    tags: list[str] = Field(default_factory=list, max_length=10)

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=1)
    category: str | None = None
    tags: list[str] | None = Field(default=None, max_length=10)
```

Constraints still apply *if* the field is given.
`None` means "don't change this field".

---

## What FastAPI Does With All This

```python
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep):
    # If we get here, `note` is GUARANTEED valid:
    #   - title 3..100 chars, stripped
    #   - category in allowed set
    #   - tags lowercase, unique, ≤ 10
    ...
```

Inside the endpoint you can stop writing defensive `if not title:` checks.
**The model is the contract.**

---

## Where Validation Belongs

<div class='columns'>
<div>

**✅ In Pydantic models:**

- Shape (types, required)
- Format (length, regex, enums)
- Normalization (strip, lower)
- Cross-field rules

</div>
<div>

**✅ In endpoint code:**

- "Does this note already exist?"
- "Is the user allowed to edit it?"
- Anything that needs the **database**

</div>
</div>

Pydantic doesn't know what's in your DB. Don't ask it to.

---

# Part 4: Homework

Tighten the Notes models

---

## 📝 Homework Assignment

**Goal:** Make the Notes API reject bad data using Pydantic only.
**Time:** ~2 hours
**Submit:** updated `main.py` + `test_validation.py`
**Deadline:** Before Day 6

You will edit:

- `NoteCreate`
- `NoteUpdate`
- `Tag` model

You will **not** add new endpoints. You will make the existing ones strict.

---

## Task 1 — `NoteCreate` Constraints

Apply at least these rules using `Field(...)`:

| Field      | Rule                                            |
|------------|-------------------------------------------------|
| `title`    | 3–100 chars, required                           |
| `content`  | 1–10 000 chars, required                        |
| `category` | 2–30 chars, lowercase letters only (regex)      |
| `tags`     | 0–10 items, default empty list                  |

Also set on the model:

- `str_strip_whitespace=True`
- `extra="forbid"`

---

## Task 2 — `NoteCreate` Validators

Write these validators:

1. **`title`** — reject titles that are only whitespace
   *(after stripping, length must still be ≥ 3)*
2. **`category`** — must be one of:
   `{"work", "personal", "school", "ideas", "general"}`
   Normalize to lowercase before checking.
3. **`tags`** — strip + lowercase each tag, drop duplicates,
   reject empty tags, reject tags shorter than 2 chars.

Test each rule with both a passing and a failing request.

---

## Task 3 — Cross-Field Rule

Add one `@model_validator(mode="after")` to `NoteCreate`:

> If `category == "work"`, the tag list must contain `"work"`.
> Otherwise raise `ValueError("work notes must include the 'work' tag")`.

This must be a *model* validator, not a field validator.
Explain in a comment why.

---

## Task 4 — `NoteUpdate` (Partial)

`NoteUpdate` is used by `PATCH /notes/{id}`.
Every field is optional, but **the constraints from Task 1 must still apply**
when a field *is* provided.

```python
class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    # ... your turn
```

`PATCH` with `{}` must succeed (no changes).
`PATCH` with `{"title": ""}` must return 422.

---

## Task 5 — Tighten the `Tag` Model

In `main.py`, the `Tag` SQLModel currently looks like:

```python
class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
```

Add validation so that `name` must:

- be 2–30 characters
- match `^[a-z0-9-]+$` (lowercase, digits, dashes only)
- be stripped + lowercased before saving

Hint: SQLModel inherits from Pydantic — `field_validator` works here too.

---

## Task 6 — Tests

Create `test_validation.py` with at least these tests:

```python
def test_create_note_rejects_short_title(client): ...
def test_create_note_rejects_unknown_category(client): ...
def test_create_note_normalizes_tags(client): ...
def test_create_note_forbids_extra_fields(client): ...
def test_work_note_requires_work_tag(client): ...
def test_patch_with_empty_body_succeeds(client): ...
def test_patch_with_invalid_title_fails(client): ...
def test_tag_name_rejects_uppercase(client): ...
```

Each failing case must assert `response.status_code == 422`.

---

## Submission Checklist

Before you submit, verify:

- [ ] `POST /notes` with `{"title": "", ...}` → 422
- [ ] `POST /notes` with `tagz` typo → 422 (`extra="forbid"`)
- [ ] `POST /notes` with category `"WORK"` → succeeds, stored as `"work"`
- [ ] `POST /notes` with duplicate tags → stored deduplicated
- [ ] `PATCH /notes/1` with `{}` → 200
- [ ] All 8 tests in `test_validation.py` pass
- [ ] `/docs` shows your `description` and `examples`

---

## Stretch (Optional)

If you finish early:

- Add an `author_email: EmailStr | None = None` field to `NoteCreate`
- Add a `priority: int = Field(default=3, ge=1, le=5)` field
- Make `created_at` validation reject future dates
  (hint: `@field_validator("created_at", mode="after")`)

---

## Recap — What You Learned Today

- **`Field(...)`** for length / range / regex / metadata
- **`@field_validator`** to clean & check single fields
- **`@model_validator(mode="after")`** for cross-field rules
- **`ConfigDict(str_strip_whitespace=True, extra="forbid")`**
- Built-in types: `EmailStr`, `HttpUrl`, `PositiveInt`
- Validation errors come back as **HTTP 422** with a clear `loc`

**Rule:** validate at the boundary, trust everything inside.

---

## See You on Day 6! 👋

Day 6: **Error handling & API architecture**

Bring your hardened Notes models — we'll build proper error
responses around them.
