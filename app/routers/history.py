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

# from keras.models import load_model
# import cv2
# import numpy as np
# import tensorflow as tf
# from tensorflow.python.keras import backend as K
# from tensorflow.python.keras.metrics import Metric
# from tensorflow.python.keras.utils import metrics_utils
# from tensorflow.python.ops import init_ops
# from tensorflow.python.ops import math_ops
# from tensorflow.python.keras.utils.generic_utils import to_list

#Image related imports
from fastapi import File, UploadFile
import secrets
# from fastapi.staticfiles import StaticFiles
from PIL import Image

router = APIRouter(
  tags=['Predict']
)

# class BalancedAccuracy(Metric):
#   def __init__(self, thresholds=None, top_k=None, class_id=None, name="balanced_accuracy", dtype=None):
#     super(BalancedAccuracy, self).__init__(name=name, dtype=dtype)
#     self.init_thresholds = thresholds
#     self.top_k = top_k
#     self.class_id = class_id

#     default_threshold = 0.5 if top_k is None else metrics_utils.NEG_INF
#     self.thresholds = metrics_utils.parse_init_thresholds(thresholds, default_threshold=default_threshold)
#     self.true_positives = self.add_weight('true_positives', shape=(len(self.thresholds),), initializer=init_ops.zeros_initializer)
#     self.true_negatives = self.add_weight('true_negatives', shape=(len(self.thresholds),), initializer=init_ops.zeros_initializer)
#     self.false_positives = self.add_weight('false_positives', shape=(len(self.thresholds),), initializer=init_ops.zeros_initializer)
#     self.false_negatives = self.add_weight('false_negatives', shape=(len(self.thresholds),), initializer=init_ops.zeros_initializer)

#   def update_state(self, y_true, y_pred, sample_weight=None):
#     return metrics_utils.update_confusion_matrix_variables(
#         {
#           metrics_utils.ConfusionMatrix.TRUE_POSITIVES: self.true_positives,
#           metrics_utils.ConfusionMatrix.FALSE_NEGATIVES: self.false_negatives,
#           metrics_utils.ConfusionMatrix.TRUE_NEGATIVES: self.true_negatives,
#           metrics_utils.ConfusionMatrix.FALSE_POSITIVES: self.false_positives,
#         },
#         y_true,
#         y_pred,
#         thresholds=self.thresholds,
#         top_k=self.top_k,
#         class_id=self.class_id,
#         sample_weight=sample_weight)

#   def result(self):
#     result = (math_ops.div_no_nan(self.true_positives, self.true_positives + self.false_negatives) +
#               math_ops.div_no_nan(self.true_negatives, self.true_negatives + self.false_positives)) / 2
#     return result[0] if len(self.thresholds) == 1 else result

#   def reset_state(self):
#     num_thresholds = len(to_list(self.thresholds))
#     K.batch_set_value(
#       [(v, np.zeros((num_thresholds,))) for v in self.variables])

#   def get_config(self):
#     config = {
#       'thresholds': self.init_thresholds,
#       'top_k': self.top_k,
#       'class_id': self.class_id
#     }
#     base_config = super(BalancedAccuracy, self).get_config()
#     return dict(list(base_config.items()) + list(config.items()))

# balanced_accuracy = BalancedAccuracy()

# model = load_model('./model/mlmodel1.h5', custom_objects={"BalancedAccuracy":BalancedAccuracy})

# labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc', 'unk']

base_dir = os.getcwd()
tflite_dir = os.path.join(base_dir, "tflites")
tflite_model_path = os.path.join(tflite_dir, "non_quantized_model_1.0.0.tflite")
labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc', 'unk']

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

  gbr = Image.open(generated_img_name)
  # gbr = cv2.imread(generated_img_name)
  # gbr = cv2.resize(gbr,(256,256))
  # # img = img.resize(size=(256,256))
  # gbr = np.reshape(gbr,[1,256,256,3])

  # predict = labels[np.argmax(model.predict(gbr))]

  # img = Image.open(generated_img_name)
  # gbr = cv2.imread(generated_img_name)
  # gbr = cv2.resize(gbr,(256,256))
  # # img = img.resize(size=(256,256))
  # gbr = np.reshape(gbr,[1,256,256,3])

  # predict = labels[np.argmax(model.predict(gbr))]

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

  img_url = "https://dermanalyze-api-dev.herokuapp.com" + generated_img_name[1:]

  # img_url = "localhost:8000" + generated_img_name[1:]

  # img_url = "Google IP" + generated_img_name[1:]

  new_prediction = models.Prediction(photo_url = img_url, pred_results = label, owner_id = current_user.id)

  db.add(new_prediction)
  db.commit()
  db.refresh(new_prediction)

  return new_prediction

@router.get("/history", response_model = List[schemas.PredictResp])
def get_predictions_history(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0):
  predictions = db.query(models.Prediction).group_by(models.Prediction.id).filter(models.Prediction.owner_id == current_user.id).limit(limit).offset(skip).all()

  return predictions