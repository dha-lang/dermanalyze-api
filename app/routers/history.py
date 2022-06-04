from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils, oauth2
from ..database import get_db

#Imports for prediction
import os
import cv2
import tensorflow as tf
import numpy as np

#Image related imports
from fastapi import File, UploadFile
import secrets
from PIL import Image

router = APIRouter(
  tags=['Predict']
)

base_dir = os.getcwd()
tflite_dir = os.path.join(base_dir, "tflites")
tflite_model_path = os.path.join(tflite_dir, "non_quantized_model_1.0.0.tflite")
labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc', 'unk']

@router.post("/predict", status_code=status.HTTP_201_CREATED, response_model=schemas.PredictResp)
async def predict_proto(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  FILEPATH = "./static/images/"
  filename = file.filename

  #test.png = ["test","png"]
  extension = filename.split(".")[1].lower()

  if extension not in ["png", "jpg", "jpeg"]: 
    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"File extension is not allowed.")

  #Changing the image name into randomized string to avoid naming conflicts.
  img_token = secrets.token_hex(10) + "." + extension
  generated_img_name = FILEPATH + img_token

  file_content = await file.read()

  with open(generated_img_name, "wb") as file:
    file.write(file_content)

  gbr = Image.open(generated_img_name)

  img = cv2.imread(generated_img_name, cv2.IMREAD_COLOR)
  img_dtype = img.dtype

  # apply shade of gray color constancy
  img = img.astype('float32')
  img_power = np.power(img, 6)
  rgb_vec = np.power(np.mean(img_power, (0,1)), 1/6)
  rgb_norm = np.sqrt(np.sum(np.power(rgb_vec, 2.0)))
  rgb_vec = rgb_vec/rgb_norm
  rgb_vec = 1 / (rgb_vec*np.sqrt(3))
  img = np.multiply(img, rgb_vec)
  img = np.clip(img, a_min=0, a_max=255)
  img = img.astype(img_dtype)

  # convert to tensor
  img_tensor = tf.convert_to_tensor(img)
  # resize into input size (256, 256)
  img_tensor = tf.image.resize(img_tensor, (256, 256)) 
  # rescale img to [0, 1]
  img_tensor = tf.cast(img_tensor, dtype=tf.float32) / tf.constant(256, dtype=tf.float32)
  # add dimension for batch
  input_data = tf.expand_dims(img_tensor, axis=0) 

  interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
  interpreter.allocate_tensors()

  input_details = interpreter.get_input_details()
  output_details = interpreter.get_output_details()

  interpreter.set_tensor(input_details[0]["index"], input_data)
  interpreter.invoke()

  tflite_results = interpreter.get_tensor(output_details[0]["index"])
  index = np.argmax(tflite_results)
  label = labels[index]

  gbr.save(generated_img_name)

  file.close()

  # img_url = "https://dermanalyze-api-dev.herokuapp.com" + generated_img_name[1:]

  # img_url = "localhost:8000" + generated_img_name[1:]

  img_url = "Google IP" + generated_img_name[1:]

  new_prediction = models.Prediction(photo_url = img_url, pred_results = label, owner_id = current_user.id)

  db.add(new_prediction)
  db.commit()
  db.refresh(new_prediction)

  return new_prediction

@router.get("/history", response_model = List[schemas.PredictResp])
def get_predictions_history(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
  predictions = db.query(models.Prediction).group_by(models.Prediction.id).filter(models.Prediction.owner_id == current_user.id).limit(limit).offset(skip).all()

  return predictions