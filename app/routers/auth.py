from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(
  tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
  user = db.query(models.User).filter(func.lower(models.User.email) == func.lower(user_cred.username)).first()

  if not user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

  if not utils.verify(user_cred.password, user.password):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

  access_token = oauth2.create_jwt(data = {"user_id": user.id})

  return {"access_token" : access_token, "token_type": "bearer"}

@router.post("/logout", response_model=schemas.BlacklistTokenResp)
def logout(token: str = Depends(oauth2.get_current_token), current_user: int = Depends(oauth2.get_current_user), db: Session = Depends(database.get_db)):
  bltoken = models.TokenBlack(token = token, email = current_user.email)

  db.add(bltoken)
  db.commit()
  db.refresh(bltoken)

  return bltoken