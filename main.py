from dotenv import load_dotenv

load_dotenv(".env")

from typing import Union
from fastapi import FastAPI
from fastapi import File, UploadFile
from pymongo import MongoClient
from db import db
import bson

app = FastAPI()

import embeddings


@app.get("/")
def read_root():
    return {"Hello": "server is running successfully"}


@app.post("/embeddings")
def upload(file: UploadFile = File(...), song_id: str = None):
    try:
        contents = file.file.read()
        with open("./music/" + file.filename, "wb") as f:
            f.write(contents)

        music_embeddings = embeddings.getEmbeddings(file.filename)

        # Save Embeddings to DB
        db.songs.insert_one(
            {
                "song_id": song_id,
                # convert numpy array to 2d array
                "embeddings": music_embeddings,
            }
        )

        return {
            "message": f"Successfully uploaded {file.filename}",
            "embeddings": music_embeddings,
            "filename": file.filename,
        }

    except Exception as e:
        # Handle the exception and print its details
        print(f"An exception occurred: {type(e).__name__} - {e}")
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
