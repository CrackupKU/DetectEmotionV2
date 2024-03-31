from fastapi import FastAPI, BackgroundTasks
import track_video_func
from firebase_admin import credentials, firestore, initialize_app
import pyrebase
from pathlib import Path
import shutil
import glob
from google.cloud import storage
import os
from google.oauth2 import service_account
import json
import dbmodels
from func import group_normalize, lcs
from decouple import config

cred = credentials.Certificate(config('CRED'))
initialize_app(cred)

config = {
    "apiKey": "AIzaSyCnKFxvLy787xvvLRvgOu9Sq2Nemb8Jrac",
    "authDomain": "crackup-c6205.firebaseapp.com",
    "databaseURL": "gs://crackup-c6205.appspot.com",
    "projectId": "crackup-c6205",
    "storageBucket": "crackup-c6205.appspot.com",
    "messagingSenderId": "183322287418",
    "appId": "1:183322287418:web:fa6e63de33a02778434403",
    "measurementId": "G-R0QWEL7K9Y",
}

app = FastAPI()

firebase = pyrebase.initialize_app(config)
db = firestore.client()

storage_fire = firebase.storage()

google_credentials = service_account.Credentials.from_service_account_file("./key.json")
GCS_CLIENT = storage.Client(credentials=google_credentials)
def upload_from_directory(directory_path: str, dest_bucket_name: str, dest_blob_name: str):
    rel_paths = glob.glob(directory_path+"/**", recursive=True)
    bucket = GCS_CLIENT.get_bucket(dest_bucket_name)
    for local_file in rel_paths:
        remote_path = f'{dest_blob_name}/{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)




def handler(file_path, name, id):
    Path(f"./characters/{name}/img/").mkdir(parents=True,exist_ok=True)
    track_video_func.run_video(file_path, name)
    storage_fire.child("metadata/"+name+".json").put(f"./characters/{name}/metadata.json")
    upload_from_directory(f"./characters/{name}", "metadata_crackup","")

    # update db {status, emotionlength, emotion, processingUrl, similarVideo}
    emotion = getEmotion(f"./characters/{name}")
    processingURL = ""

    #find similar
    emotionLength = group_normalize(f"./characters/{name}/"+"metadata.json")
    similarVideoId = ""


    mx = 0
    videos_ref = db.collection("videos")
    query = videos_ref.where("emotion", "==", emotion).stream()
    for doc in query:
        data = doc.to_dict()
        _mx = max(mx, lcs(emotionLength, data['emotionLength'], 10,10))
        if _mx > mx and data['id'] != id:
            mx = _mx
            similarVideoId = data['id']

    # # need id to ref
    videos_ref = db.collection("videos").document(id)

    videos_ref.update(
        {
            "emotion": emotion,
            "status": dbmodels.Status.PUBLISH,
            "processingUrl": processingURL,
            "emotionLength": emotionLength,
            "similarVideo": similarVideoId
        }
    )

    # remove local
    shutil.rmtree(f"./characters/{name}")
    os.remove(file_path)

def getEmotion(path):
    with open(path+"/emotion.json", 'r') as file:
        # Load the JSON data into a dictionary
        data = json.load(file)
        print(data["emotion"])
        ans = data["emotion"]
    return ans.upper()

    

# CRUD Operations
@app.post("/items/")
async def create_item(name: str,id:str, bt: BackgroundTasks):
    #dowlonad
    storage_fire.child("videos/"+name).download(name+".mp4")
    bt.add_task(handler, "./"+name+".mp4", name,id)
    return {"message": "Video upload processing in the background"}


