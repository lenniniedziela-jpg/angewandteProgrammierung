import streamlit as st
import requests
#st.write ("is there apart where I say yes? No? Good, because I won't.")
 #durch die änderung der URL generiert er mir keine Texte mehr bei Text1 und Text2, da er die API nicht mehr erreichen kann. 

URL = "http://127.0.0.1:8000/"

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
category = st.text_input("Kategorie", placeholder = "Kategorie der Notiz" )
tags_input = st.text_input("Tags mit Komma getrennt", placeholder = "Tags getrennt durch Komma")


payload = {
    "title": title,
    "content": content,
    "category": category,
    "tags": [tag.strip() for tag in tags_input.split(",")] 
}

if st.button("Create Note"):
    response = requests.post("http://127.0.0.1:8000/notes", json=payload)
    note = response.json()
    print("init Note")




