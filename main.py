from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/name/{name}")
def greet_name(name:str):
    return {"message": f"Hello, {name}!"}


@app.get("/name/{name}/{number}")
def greet_name_with_number(name: str, number: int):
    doubled_number = number * 2
    return {"message": f"Hallo, {name}, {doubled_number}"}

