# Streamlit Import
#Streamlit "Hello World" Example
#Say no app als test erstellen lassen 
#API nutzen die wir nicht entwickelt haben
#API Documentation 
#API Endpint
#Button in Streamlit der bei Klick eien Anfrage an die API sendet und die Antwort anzeigt


#To Do´s für  Nachmittag:
#Streamlit erstellen mit 2 Funktionen: 
#Alle Notizen anzeigen
# Liste von Titeln und Notizen anzeigen 
# Möglichkeit zu einem Titel den Inhalt, Tags, Category anzuzeigen


# - Funktion 2: Neue Notiz erstellen (Formular mit Titel und Inhalt, Button)
 #- Erstellen einer neuen Notiz (Titel, Inhalt, Tags, Category)
   # - Neu erstellte Notiz soll in Liste auftauchen



"part where I say yes? No? Good, because I won't."



import streamlit as st
import requests
#st.write ("is there apart where I say yes? No? Good, because I won't.")

URL = "https://naas.isalman.dev/no"

def request_no():
    response = requests.get(URL)
    response_json = response.json()
    return response_json["reason"]


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


with st.expander("Session state"):
    st.write(st.session_state)













