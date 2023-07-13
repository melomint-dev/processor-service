from dotenv import load_dotenv

load_dotenv(".env")

import os
from pathlib import Path
from typing import Union
from fastapi import FastAPI
from fastapi import File, UploadFile
from pymongo import MongoClient
from db import db
from datetime import datetime
from pydantic import BaseModel
import embeddings
from typing import List, Dict


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "server is running successfully"}


# create music directory to store tenporary music files
Path("./music").mkdir(parents=True, exist_ok=True)


class ResponseData(BaseModel):
    message: str = "Successfully uploaded"
    status_code: int = 200
    error: str = None
    similarity_scores: Dict[str, float] = {"0": 0.0, "1": 0.0}
    similarity_scores_song_ids: Dict[str, str] = {"0": "song_id_1", "1": "song_id_2"}
    similarity_scores_song_embedding_keys: Dict[str, int] = {"0": 0, "1": 0}
    # embeddings: List[List[float]] = [[0.5, 0.95, 0.75]]
    song_id: str = "filename.wav"

    def __init__(
        self,
        **data: Union[
            str, Dict[str, float], Dict[str, str], Dict[str, int], List[List[float]]
        ],
    ):
        super().__init__(**data)


@app.post("/embeddings", response_model=ResponseData)
def upload(file: UploadFile = File(...), song_id: str = None):
    try:
        contents = file.file.read()
        filename = "./music/" + file.filename
        with open(filename, "wb") as f:
            f.write(contents)

        # get all songs wiht oldest first order except the song which is being uploaded
        all_songs = db.songs.find(
            {"song_id": {"$ne": song_id}}, sort=[("created_at", 1)]
        )
        music_info = embeddings.get_embeddings_and_calculate_similarity_with_prev_songs(
            filename, all_songs
        )

        # Save Embeddings to DB
        db.songs.find_one_and_update(
            {"song_id": song_id},
            {
                "$set": {
                    "embeddings": music_info["embeddings"],
                    "updated_at": datetime.now(),
                },
                "$setOnInsert": {
                    "created_at": datetime.now(),
                },
            },
            upsert=True,
        )

        # delete the file
        os.remove(filename)

        response = ResponseData(
            message=f"Successfully uploaded {file.filename}",
            status_code=200,
            error=None,
            similarity_scores=music_info["similarity_scores"],
            similarity_scores_song_ids=music_info["similarity_scores_song_ids"],
            similarity_scores_song_embedding_keys=music_info[
                "similarity_scores_song_embedding_keys"
            ],
            # embeddings=music_info["embeddings"],
            song_id=song_id,
        )

        return response

    except Exception as e:
        # Handle the exception and print its details
        print(f"An exception occurred: {type(e).__name__} - {e}")
        return {
            "message": "There was an error uploading the file",
            "status_code": 400,
            "error": str(f"{type(e).__name__} - {e}"),
        }
    finally:
        file.file.close()
