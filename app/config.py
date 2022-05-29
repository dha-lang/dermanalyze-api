from pydantic import BaseSettings

class Settings(BaseSettings):
  db_hostname: str
  db_port: str
  db_password: str
  db_name: str
  db_username: str
  secret_key: str
  algorithm: str
  access_token_exp_minutes: int

  class Config:
    env_file = ".env"

#Only use .env in development, in production, you need to set this down

settings = Settings()