from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import auth, users, history
from .config import settings

from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app =  FastAPI()

#Static file setup config
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(history.router)


@app.get("/")
def root():
  return {"message": "Welcome to Dermanalyze API!"}