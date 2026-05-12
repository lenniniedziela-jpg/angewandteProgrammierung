import streamlit as st
import requests
#st.write ("is there apart where I say yes? No? Good, because I won't.")
 #durch die änderung der URL generiert er mir keine Texte mehr bei Text1 und Text2, da er die API nicht mehr erreichen kann. 

URL = "http://127.0.0.1:8000/"


def get_notes(params=None):
    response = requests.get(f"{URL}notes", params=params)
    return response.json()

def request_no():
    response = requests.get(URL)
    response_json = response.json()
    return response_json["message"]
 
 
#Initialisierung
if "text1" not in st.session_state:
    st.session_state["text1"] = "Text"
    print("init Text1")
 
if "text2" not in st.session_state:
    st.session_state["text2"] = "Text"
    print("init Text2")
 
name = st.text_input("Name", placeholder="Enter your name") #Daten in Streamlit bekommen
st.write(name)



if st.button("Neuer Text1"):
    st.session_state["text1"]=request_no()
 
st.write(st.session_state["text1"])
 
if st.button("Neuer Text2"):
    st.session_state["text2"]=request_no()
 
 
st.write(st.session_state["text2"])


#if st.button("Notes"):
#    st.session_state["text3"]=request_no()
 
#st.write(st.session_state["text3"])


with st.expander("Session state"):
    st.write(st.session_state)

# Hausaufgabe

# 1. Schritt einfach die Base URL anpassen auf die unserer FastAPI 

title = st.text_input("Titel", placeholder = "Titel der Notiz")
content = st.text_area("Inhalt", placeholder = "Inhalt der Notiz")
category = st.text_input("Kategorie", placeholder = "work, personal, school, ideas oder general" )
tags_input = st.text_input("Tags mit Komma getrennt", placeholder = "Tags getrennt durch Komma")


payload = {
    "title": title,
    "content": content,
    "category": category,
    "tags": [tag.strip() for tag in tags_input.split(",") if tag.strip()] 
}

if st.button("Create Note"):
    response = requests.post("http://127.0.0.1:8000/notes", json=payload)
    note = response.json()
    print("init Note")

st.subheader("Notizen durchsuchen")

filter_category = st.selectbox(
    "Kategorie filtern",
    ["Alle", "work", "personal", "school", "ideas", "general"],
)
filter_search = st.text_input("Suche in Titel oder Inhalt")
filter_tag = st.text_input("Nach Tag filtern")

params = {}
if filter_category != "Alle":
    params["category"] = filter_category
if filter_search.strip():
    params["search"] = filter_search.strip()
if filter_tag.strip():
    params["tag"] = filter_tag.strip()

notes = get_notes(params)

if not notes:
    st.info("Keine passenden Notizen gefunden.")
else:
    note_options = {
        f"{note['id']} - {note['title']}": note
        for note in notes
    }

    selected_note_label = st.selectbox(
        "Notiz auswählen",
        list(note_options.keys()),
    )
    selected_note = note_options[selected_note_label]

    st.caption(f"{len(notes)} passende Notiz(en) gefunden")
    st.subheader(selected_note["title"])
    st.write(selected_note["content"])
    st.write(f"Kategorie: {selected_note['category']}")

    if selected_note["tags"]:
        st.write(f"Tags: {', '.join(selected_note['tags'])}")
    else:
        st.write("Tags: Keine")

    st.write(f"ID: {selected_note['id']}")
