from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import auth, users, history
from .config import settings

from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

description = """
Dermanalyze API is used to work the backends of Dermanalyze App.

List of operations you can do :

**Authentication:** 
- Login.
- Logout.

**Users:**
- Register.
- Get User Data.
- Update User Data.

**Prediction and Prediction History:**
- Post Prediction. - _work in progress_
- Get Prediction History. 
"""

tags_metadata = [
  {
    "name":"Users",
    "description":"Operations related to user, such as register and update user data.",
  },
  {
    "name":"Authentication",
    "description":"Operations related to user authentication, such as login and logout.",
  },
  {
    "name":"Predict",
    "description":"Operations related to prediction, such as prediction and prediction history.",
  },
]

app =  FastAPI(
  title="Dermanalyze API",
  description = description,
  version="0.0.1",
  openapi_tags=tags_metadata
)

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