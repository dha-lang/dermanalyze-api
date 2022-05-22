from passlib.context import CryptContext

passw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def Hash(pwd: str):
  return passw_context.hash(pwd)

def verify(plain_pass, hashed_pass):
  return passw_context.verify(plain_pass, hashed_pass)