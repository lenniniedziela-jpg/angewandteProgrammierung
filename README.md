# API Project

Diese API ist eine einfache Notizverwaltung mit FastAPI und SQLModel. Sie kann Notizen speichern, alle Notizen anzeigen, einzelne Notizen laden sowie nach Kategorie, Tag oder Suchbegriff filtern.

Jede Notiz hat:
- einen `title`
- einen `content`
- eine `category`
- eine Liste von `tags`
- eine automatisch vergebene `id`
- ein `created_at` Datum

Die Daten werden in einer SQLite-Datenbank gespeichert. Beim ersten Start können vorhandene Einträge aus `data/notes.json` in die Datenbank uebernommen werden.

## API starten

Im Projektordner:

```bash
uv run python -m fastapi dev main.py
```

Danach läuft die API lokal unter:

```text
http://127.0.0.1:8000
```

Die interaktive Dokumentation findest du unter:

```text
http://127.0.0.1:8000/docs
```

## Wichtige Endpunkte

- `GET /notes` gibt alle Notizen zurueck
- `POST /notes` erstellt eine neue Notiz
- `GET /notes/{note_id}` gibt eine einzelne Notiz zurueck
- `GET /notes/stats` liefert einfache Statistiken
- `GET /categories` gibt alle vorhandenen Kategorien zurueck
- `GET /tags` gibt alle vorhandenen Tags zurueck

## Erlaubte Kategorien

Beim Erstellen einer Notiz muss `category` einer dieser Werte sein:

- `work`
- `personal`
- `school`
- `ideas`
- `general`
- `essen`

Die API normalisiert Kategorien auf Kleinbuchstaben. `Essen` wird also zu `essen`.

## Python-Beispiel: Notiz erstellen

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "title": "Meeting vorbereiten",
    "content": "Agenda und offene Punkte sammeln",
    "category": "work",
    "tags": ["meeting", "team"]
}

response = requests.post(f"{BASE_URL}/notes", json=payload)
print(response.status_code)
print(response.json())
```

Erwartung:
- Statuscode `201`
- die neu erstellte Notiz als JSON-Antwort

## Python-Beispiel: Alle Notizen abholen

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

response = requests.get(f"{BASE_URL}/notes")
print(response.status_code)

for note in response.json():
    print(note["id"], note["title"], note["category"])
```

Erwartung:
- Statuscode `200`
- eine Liste von Notizen

## Beispiel mit Filtern

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

params = {
    "category": "work",
    "tag": "meeting",
    "search": "agenda",
}

response = requests.get(f"{BASE_URL}/notes", params=params)
print(response.status_code)
print(response.json())
```

## Hinweis zur Validierung

Wenn die API beim Erstellen `422 Unprocessable Entity` zurueckgibt, liegt das meistens an ungueltigen Eingaben:

- `title` ist zu kurz oder leer
- `content` ist leer
- `category` ist nicht erlaubt
- `tags` enthalten leere Werte

## Projektziel

Die API eignet sich gut als einfache Uebung fuer:

- FastAPI-Grundlagen
- Arbeiten mit Request- und Response-Daten
- SQLite mit SQLModel
- Testen von API-Endpunkten mit Python `requests`
