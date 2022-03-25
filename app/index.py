from fastapi import FastAPI

app = FastAPI()

from .routers import users, auth

@app.get("/")
def root():
    return {"message": "Hello world"}

app.include_router(users.router)
app.include_router(auth.router)