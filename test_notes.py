import requests

BASE_URL = "http://127.0.0.1:8000"

# Hilfsfunktion: erstellt eine Test-Note und gibt die ID zurück
def create_test_note(title="Test Note", content="Test Content", category="Testing", tags=["test"]):
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": title,
        "content": content,
        "category": category,
        "tags": tags
    })
    return response


# ============================================================
# CRUD TESTS (5)
# ============================================================

def test_create_note():
    """Test: Note erstellen"""
    response = create_test_note(title="Neue Note", category="Work", tags=["pytest"])

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Neue Note"
    assert "id" in data
    assert "created_at" in data


def test_list_notes():
    """Test: Alle Notes auflisten"""
    response = requests.get(f"{BASE_URL}/notes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_note_by_id():
    """Test: Eine bestimmte Note per ID abrufen"""
    created = create_test_note(title="ID Test Note")
    note_id = created.json()["id"]

    response = requests.get(f"{BASE_URL}/notes/{note_id}")

    assert response.status_code == 200
    assert response.json()["id"] == note_id
    assert response.json()["title"] == "ID Test Note"


def test_patch_note():
    """Test: Note teilweise updaten (PATCH)"""
    created = create_test_note(title="Original Titel")
    note_id = created.json()["id"]

    response = requests.patch(f"{BASE_URL}/notes/{note_id}", json={
        "title": "Geänderter Titel"
    })

    assert response.status_code == 200
    assert response.json()["title"] == "Geänderter Titel"
    assert response.json()["content"] == "Test Content"  # unverändert


def test_delete_note():
    """Test: Note löschen"""
    created = create_test_note(title="Zu löschende Note")
    note_id = created.json()["id"]

    response = requests.delete(f"{BASE_URL}/notes/{note_id}")
    assert response.status_code in [200, 204]

    # Verifizieren dass die Note weg ist
    get_response = requests.get(f"{BASE_URL}/notes/{note_id}")
    assert get_response.status_code == 404


# ============================================================
# FILTER TESTS (4)
# ============================================================

def test_filter_by_category():
    """Test: Notes nach Kategorie filtern"""
    # 3 Notes in der Kategorie "FilterTest" erstellen
    for i in range(3):
        create_test_note(title=f"Filter Note {i}", category="FilterTest")

    response = requests.get(f"{BASE_URL}/notes?category=FilterTest")

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 3
    for note in notes:
        assert note["category"] == "FilterTest"


def test_filter_by_search():
    """Test: Notes per Suchbegriff filtern"""
    create_test_note(title="Suchbegriff XYZ123", content="Inhalt", category="Search")

    response = requests.get(f"{BASE_URL}/notes?search=XYZ123")

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    titles_and_contents = [n["title"] + n["content"] for n in notes]
    assert any("XYZ123" in text for text in titles_and_contents)


def test_filter_by_tag():
    """Test: Notes nach Tag filtern"""
    create_test_note(title="Tag Filter Test", tags=["uniquetag999"])

    response = requests.get(f"{BASE_URL}/notes?tag=uniquetag999")

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    for note in notes:
        assert "uniquetag999" in note["tags"]


def test_combined_filters():
    """Test: Mehrere Filter gleichzeitig"""
    create_test_note(title="Combined Filter Meeting", category="CombinedTest", tags=["urgent"])

    response = requests.get(f"{BASE_URL}/notes?category=CombinedTest&tag=urgent&search=Meeting")

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    for note in notes:
        assert note["category"] == "CombinedTest"
        assert "urgent" in note["tags"]


# ============================================================
# ERROR CASES (4)
# ============================================================

def test_create_note_missing_field():
    """Test: Note mit fehlendem Pflichtfeld erstellen → 422"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "Nur Titel"
        # content und category fehlen
    })

    assert response.status_code == 422


def test_get_nonexistent_note():
    """Test: Nicht existierende Note abrufen → 404"""
    response = requests.get(f"{BASE_URL}/notes/999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_nonexistent_note():
    """Test: Nicht existierende Note updaten → 404"""
    response = requests.patch(f"{BASE_URL}/notes/999999", json={
        "title": "Ghosttitel"
    })

    assert response.status_code == 404


def test_delete_nonexistent_note():
    """Test: Nicht existierende Note löschen → 404"""
    response = requests.delete(f"{BASE_URL}/notes/999999")

    assert response.status_code == 404


# ============================================================
# DAY 3 FEATURES (3)
# ============================================================

def test_notes_statistics():
    """Test: /notes/stats gibt korrekte Struktur zurück"""
    create_test_note(title="Stats Note", category="StatsTest", tags=["stats"])

    response = requests.get(f"{BASE_URL}/notes/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_notes" in data
    assert "by_category" in data
    assert "top_tags" in data
    assert "unique_tags_count" in data
    assert data["total_notes"] >= 1


def test_list_categories():
    """Test: /categories gibt sortierte Liste zurück"""
    create_test_note(category="KategorieA")
    create_test_note(category="KategorieB")

    response = requests.get(f"{BASE_URL}/categories")

    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert "KategorieA" in categories
    assert "KategorieB" in categories


def test_notes_by_category_endpoint():
    """Test: /categories/{cat}/notes gibt nur Notes dieser Kategorie zurück"""
    create_test_note(title="Kategorie Endpoint Test", category="SpecialCat")

    response = requests.get(f"{BASE_URL}/categories/SpecialCat/notes")

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    for note in notes:
        assert note["category"] == "SpecialCat"


def test_patch_multiple_fields():
    """Test: PATCH mit mehreren Feldern gleichzeitig"""
    created = create_test_note(title="Multi Patch", content="Alter Inhalt", category="AltKat")
    note_id = created.json()["id"]

    response = requests.patch(f"{BASE_URL}/notes/{note_id}", json={
        "title": "Neuer Titel",
        "content": "Neuer Inhalt"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Neuer Titel"
    assert data["content"] == "Neuer Inhalt"
    assert data["category"] == "AltKat"  # unverändert
