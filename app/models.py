from sqlalchemy import TIMESTAMP, Column, Integer, String, text
from .database import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, nullable=False)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  email = Column(String, nullable=False)
  password = Column(String, nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text('now()'))

class TokenBlack(Base):
  __tablename__ = "tokenblacklist"

  token = Column(String, primary_key=True, nullable=True, unique=True)
  email = Column(String, nullable=False)
  logout_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text('now()'))