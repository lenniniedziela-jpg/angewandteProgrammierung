---
marp: true
theme: default
paginate: true
---

# Applied Programming - Day 7
## Frontend with Streamlit

---

## Today's Agenda

**Part 1** (2,5h): Hands-On (First Streamlit Application)

**Part 2** (15 min): Homework & Wrap-up

**Duration:** 3 hours  
**Goal:** Create first simple Streamlit-Application

---

## 🎯 By End of Today

You will have:
- ✅ A first Streamlit applicaton
- ✅ Input and output functionality
- ✅ Starting Point for Homework

**Streamlit a simple way to create GUIs**

---

# Part 1: Streamlit Hands-On

How Backend-People can build Frontends.

---

## Streamlit Test-App (Hands-On)

- Install Streamlit: ```uv add streamlit```
- Create and test a Streamlit "Hello, World!" app
- "Say no"-App as first Streamlit test
  - API Documentation: https://github.com/hotheadhacker/no-as-a-service
  - API Endpoint: https://naas.isalman.dev/no
    - Button in Streamlit that sends a request to the API endpoint when clicked and displays the response


---

## Streamlit Test-App (Code is cut off in presentation mode, look at .md file)

``` python
import streamlit as st
import requests

URL = "https://naas.isalman.dev/no"

def request_no():
    response = requests.get(URL)
    response_json = response.json()
    return response_json["reason"]

# Initialization
if 'text1' not in st.session_state:
    st.session_state['text1'] = request_no()
    print("init Text1")

if 'text' not in st.session_state:
    st.session_state['text'] = request_no()
    print("init Text")


name = st.text_input('Name', placeholder="Hier Name eingeben...")
st.write(name)


if st.button("Neuer Text1"):
    st.session_state['text1'] = request_no()

st.write(st.session_state["text1"])


if st.button("Neuer Text"):
    st.session_state['text'] = request_no()

st.write(st.session_state["text"])


with st.expander('session state'):
    st.write(st.session_state)
```

--- 


## 📝 Homework Assignment

**Goal:** Frontend for Notes-API 
**Time:** 3-4 hours  
**Submit:** frontend.py in repo
**Deadline:** Before Day 8 class


---

## Task 1: Frontend for Notes API

- Streamlit app with 2 functions from the Notes API
- Function 1: Show all notes
    - Display a list of note titles
    - Option to display content, tags, category, etc. for a selected title
- Function 2: Create a new note (form with title and content, button)
    - Create a new note (title, content, tags, category)
    - Newly created note should appear in the list

---

## Task 1: Tipps:

- Open 2 terminals:
    - First for FastAPI
    - Second for Streamlit
- Check the test_main.py file for example code if neccessary
- Click "Always Rerun" in Streamlit
- For multi input submission (Title, Content, Tags, Category):
    - Look at the docu to find appropriate input methods
    - To submit all inputs at once look at https://docs.streamlit.io/develop/api-reference/execution-flow/st.form

---

## Homework Checklist

**Before submission:**

- [ ] Test your App (create new notes and retrieve them)
- [ ] Write your Work-Log
- [ ] Push to GitHub


---

# Summary & Wrap-up

What we learned today

---

## 🎓 Today's Achievements

**Streamlit:**
- ✅ First Frontend with Streamlit


---

## 🔮 Preview: Day 8

**Next session we'll...**

- Structure your repos
- Clarify open points for final submission on Sunday.  


---

**End of Day 7** 🎉
