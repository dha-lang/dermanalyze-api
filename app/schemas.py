from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
  first_name: str
  last_name: str

class UserCreate(BaseModel):
  first_name: str
  last_name: str
  email: EmailStr
  password: str

class UserResponse(UserBase):
  pass
  id: int
  email: EmailStr
  created_at: datetime

  class Config:
    orm_mode = True

class UserUpdate(UserBase):
  pass

class UserLogin(BaseModel):
  email: EmailStr
  password: str

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  id: Optional[str] = None

class BlacklistToken(BaseModel):
  token: str
  email: EmailStr

class BlacklistTokenResp(BaseModel):
  email: EmailStr
  logout_at: datetime

  class Config:
    orm_mode = True