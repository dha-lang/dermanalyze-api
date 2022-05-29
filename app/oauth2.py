from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import schemas, database, models
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXP_MINUTES = settings.access_token_exp_minutes

def create_jwt(data: dict):
  data_to_encode = data.copy()

  exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXP_MINUTES)
  data_to_encode.update({"exp": exp})

  enc_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return enc_jwt

def verify_jwt(token: str, cred_exc):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    id: str = payload.get("user_id")

    if id is None:
      raise cred_exc

    token_data = schemas.TokenData(id=id)

  except JWTError:
    raise cred_exc

  return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
  cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = f"Could not validate credentials", headers={"WWW-Authenticate" : "Bearer"})

  check_token = db.query(models.TokenBlack).filter(models.TokenBlack.token == token).first()

  if check_token:
    raise cred_exc

  token = verify_jwt(token, cred_exc)

  user = db.query(models.User).filter(models.User.id == token.id).first()

  return user

def get_current_token(token: str = Depends(oauth2_scheme)):

  return token