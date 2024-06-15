from fastapi import FastAPI, Body, Depends, File, UploadFile, HTTPException, status

import io
import os
import gcsfs
import json

# from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import create_access_token, verify_token
from app.model import PostSchema, UserSchema, UserLoginSchema, ResultSchema
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

from .model import single_user
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi.responses import JSONResponse
from google.cloud import firestore
from typing import List

# include CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

# Set the environment variable for Google Application Credentials
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Baca file JSON
if credentials_path and os.path.exists(credentials_path):
    with open(credentials_path) as f:
        credentials = json.load(f)
    print("Credentials loaded successfully:")
else:
    print("GOOGLE_APPLICATION_CREDENTIALS environment variable not set or file not found.")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "be-capstone-ezfarm-ddad185f9c24.json"
db = firestore.Client(project="be-capstone-ezfarm")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = []

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to EZFarm API!"}


# Endpoint for generating token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != single_user.username or form_data.password != single_user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": single_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Function to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

# an endpoint that requires authentication
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["sub"]}

# Prediction endpoint that requires authentication
@app.get("/predictions/")
async def get_all_predictions(current_user: dict = Depends(get_current_user)):
    prediction_ref = db.collection("Prediction").document("Bacterial Leaf Blight")
    docs = prediction_ref.get()
    
    if docs.exists:
        return {
            "Document data": docs.to_dict()
        }
    else:
        return { "error": "No such document!" }
    
# Fungsi untuk memuat model dari GCS ke file lokal sementara
def load_model_from_gcs(gcs_path, local_path):
    fs = gcsfs.GCSFileSystem()
    with fs.open(gcs_path, 'rb') as f_in:
        with open(local_path, 'wb') as f_out:
            f_out.write(f_in.read())
    # Load and return the model (this is the crucial change)
    model = load_model(local_path)  
    return model

# Path ke model di Google Cloud Storage
model_path = 'gs://ezfarm-buket/best_model3.h5'
local_model_path = 'app/best_model3.h5'

# Load model from GCS
model = load_model_from_gcs(model_path, local_model_path)
# model = load_model(local_model_path)  
# @app.post("/predict/")
# async def predict(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
#     contents = await file.read()
#     image = load_img(io.BytesIO(contents), target_size=(224, 224))
#     image = img_to_array(image)
#     image = np.expand_dims(image, axis=0)
#     image /= 255.0

#     # Make Prediction
#     prediction = model.predict(image)
#     predicted_class = np.argmax(prediction, axis=1)

#     class_names = ['Bacterial Leaf Blight', 'Healthy', 'Leaf Blast', 'Leaf Brown Spot', 'Leaf Scald']
    
#     predicted_label = class_names[predicted_class[0]]

#     # Ambil data penanganan dari Firestore, atau set pesan default jika "Healthy"
#     if predicted_label == "Healthy":
#         penanganan_data = ["No treatment needed. Keep up with regular care and monitoring."]
#         pencegahan_data = [
#             "Gunakan benih padi yang sehat dan bersertifikat.",
#             "Lakukan rotasi tanaman dengan tanaman non-inang.",
#             "Terapkan praktik pemupukan berimbang.",
#             "Jaga kebersihan lingkungan sawah dari gulma dan sisa tanaman.",
#             "Pantau tanaman secara teratur untuk mendeteksi gejala penyakit sejak dini."
#         ]
#         gejala_data = ["Tanaman tampak sehat, tumbuh subur, dan tidak menunjukkan gejala penyakit."]
#         deskripsi = "Tanaman padi dalam kondisi sehat, tidak terinfeksi oleh penyakit apapun."
#     else:
#         prediction_ref = db.collection("Prediction").document(predicted_label)
#         docs = prediction_ref.get()
#         penanganan_data = docs.to_dict().get("Penanganan", []) if docs.exists else []
#         pencegahan_data = docs.to_dict().get("pencegahan", []) if docs.exists else []
#         gejala_data = docs.to_dict().get("gejala", []) if docs.exists else []
#         deskripsi = docs.to_dict().get("deskripsi", []) if docs.exists else ''

#     # Buat hasil dengan detail penanganan
#     result_with_penanganan = {
#         "penyakit": predicted_label,
#         "deskripsi" : deskripsi,
#         "nama_tanaman": "Padi",
#         "penanganan": penanganan_data ,
#         "pencegahan" : pencegahan_data,
#         "gejala" : gejala_data 
#     }

#     return JSONResponse(content={'class': predicted_label,'result_with_penanganan': result_with_penanganan})

@app.post("/predict/")
async def predict(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        # Membaca isi file gambar
        contents = await file.read()
        image = load_img(io.BytesIO(contents), target_size=(224, 224))

        # Konversi gambar ke array
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image /= 255.0

        # Lakukan prediksi
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction, axis=1)

        # Dapatkan nama kelas dari prediksi
        class_names = ['Bacterial Leaf Blight', 'Healthy', 'Leaf Blast', 'Leaf Brown Spot', 'Leaf Scald']
        predicted_label = class_names[predicted_class[0]]

        # Ambil data penanganan dari Firestore
        if predicted_label == "Healthy":
            penanganan_data = ["No treatment needed. Keep up with regular care and monitoring."]
            pencegahan_data = [
                "Gunakan benih padi yang sehat dan bersertifikat.",
                "Lakukan rotasi tanaman dengan tanaman non-inang.",
                "Terapkan praktik pemupukan berimbang.",
                "Jaga kebersihan lingkungan sawah dari gulma dan sisa tanaman.",
                "Pantau tanaman secara teratur untuk mendeteksi gejala penyakit sejak dini."
            ]
            gejala_data = ["Tanaman tampak sehat, tumbuh subur, dan tidak menunjukkan gejala penyakit."]
            deskripsi = "Tanaman padi dalam kondisi sehat, tidak terinfeksi oleh penyakit apapun."
        else:
            prediction_ref = db.collection("Prediction").document(predicted_label)
            docs = prediction_ref.get()

            if docs.exists:
                penanganan_data = docs.to_dict().get("Penanganan", [])
                pencegahan_data = docs.to_dict().get("pencegahan", [])
                gejala_data = docs.to_dict().get("gejala", [])
                deskripsi = docs.to_dict().get("deskripsi", [])
            else:
                raise ValueError(f"Data penanganan untuk penyakit {predicted_label} tidak ditemukan di Firestore.")

        # Buat hasil dengan detail penanganan
        result_with_penanganan = {
            "penyakit": predicted_label,
            "deskripsi": deskripsi,
            "nama_tanaman": "Padi",
            "penanganan": penanganan_data,
            "pencegahan": pencegahan_data,
            "gejala": gejala_data
        }

        return JSONResponse(content={'class': predicted_label, 'result_with_penanganan': result_with_penanganan})

    except Exception as e:
        # Menangani error generik
        print(f"Error saat memprediksi: {e}")
        return JSONResponse(status_code=500, content={"detail": "Terjadi kesalahan internal."})

    except ValueError as e:
        # Menangani error spesifik (ValueError)
        print(f"Error Nilai: {e}")
        return JSONResponse(status_code=400, content={"detail": str(e)})


@app.get("/tracking")
async def get_all_tracking(current_user: dict = Depends(get_current_user)):
    prediction_ref = db.collection("tracking").document("tracking")
    docs = prediction_ref.get()
    
    if docs.exists:
        return {
            "data" : docs.to_dict()
        }
    else:
        return { "error": "No such document!" }