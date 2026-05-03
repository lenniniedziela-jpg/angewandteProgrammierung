import requests 

URL = "http://127.0.0.1:8000/"

def test_get_root():
    response = requests.get(URL)
    assert response.status_code == 200
    if response.status_code == 200:
        print("GET / - SUCCESS")
    else:
        print("GET / - FAILED")


if __name__ == "__main__":
    test_get_root()


def create_note(title, content, category):
    payload = {
        "title": title,
        "content": content,
        "category": category,
        "tags" : []
}
    response = requests.post(URL + "notes", json=payload)
    assert response.status_code == 200
    if response.status_code == 200:
        print("POST /notes - SUCCESS")
    else:
        print("POST /notes - FAILED")
    