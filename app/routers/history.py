from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils, oauth2
from ..database import get_db

#Image related imports
from fastapi import File, UploadFile
import secrets
# from fastapi.staticfiles import StaticFiles
from PIL import Image

router = APIRouter(
  tags=['History']
)

@router.post("/predict", status_code=status.HTTP_201_CREATED, response_model=schemas.PredictResp)
async def predict_proto(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  FILEPATH = "./static/images/"
  filename = file.filename

  #test.png = ["test","png"]
  extension = filename.split(".")[1]

  if extension not in ["png", "jpg", "jpeg"]:
    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"File extension is not allowed.")

  #Changing the image name into randomized string to avoid naming conflicts.
  img_token = secrets.token_hex(10) + "." + extension
  generated_img_name = FILEPATH + img_token

  file_content = await file.read()

  with open(generated_img_name, "wb") as file:
    file.write(file_content)

  img = Image.open(generated_img_name)
  img = img.resize(size=(200,200))
  img.save(generated_img_name)

  file.close()

  img_url = "https://dermanalyze-api-dev.herokuapp.com" + generated_img_name[1:]

  # img_url = "localhost:8000" + generated_img_name[1:]

  new_prediction = models.Prediction(photo_url = img_url, pred_results = "Good image", owner_id = current_user.id)

  db.add(new_prediction)
  db.commit()
  db.refresh(new_prediction)

  return new_prediction

@router.get("/history", response_model = List[schemas.PredictResp])
def get_predictions_history(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
  predictions = db.query(models.Prediction).group_by(models.Prediction.id).filter(models.Prediction.owner_id == current_user.id).limit(limit).offset(skip).all()

  return predictions