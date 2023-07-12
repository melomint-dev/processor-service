from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(".env")

from typing import Union
from fastapi import FastAPI
from fastapi import File, UploadFile
from pymongo import MongoClient
from db import db
import bson
from datetime import datetime


app = FastAPI()

import embeddings


@app.get("/")
def read_root():
    return {"Hello": "server is running successfully"}


# create music directory to store tenporary music files
Path("./music").mkdir(parents=True, exist_ok=True)


@app.post("/embeddings")
def upload(file: UploadFile = File(...), song_id: str = None):
    try:
        contents = file.file.read()
        filename = "./music/" + file.filename
        with open(filename, "wb") as f:
            f.write(contents)

        # get all songs wiht oldest first order
        all_songs = db.songs.find().sort("created_at", 1)
        music_embeddings = (
            embeddings.get_embeddings_and_calculate_similarity_with_prev_songs(
                filename, all_songs
            )
        )

        # Save Embeddings to DB
        db.songs.insert_one(
            {
                "song_id": song_id,
                "embeddings": music_embeddings,
                "created_at": datetime.now(),
            }
        )

        # delete the file
        # os.remove(filename)

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
