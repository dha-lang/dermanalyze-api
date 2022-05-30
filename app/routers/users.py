from fastapi import FastAPI, status, Depends, APIRouter, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
  prefix="/users",
  tags=['Users']
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

  hashed_pass = utils.Hash(user.password)
  user.password = hashed_pass

  new_user = models.User(**user.dict())
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user

@router.get("", response_model=schemas.UserResponse)
def get_user(current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
  user_data = db.query(models.User).filter(models.User.id == current_user.id).first()

  return user_data

@router.put("", response_model=schemas.UserResponse)
def update_user(updated_user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  user_query = db.query(models.User).filter(models.User.id == current_user.id)

  user_query.update(updated_user.dict(), synchronize_session=False)
  db.commit()

  return user_query.first()