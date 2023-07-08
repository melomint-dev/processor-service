from typing import Union

from fastapi import FastAPI
from fastapi import File, UploadFile

app = FastAPI()

import embeddings 

# print()

@app.get("/")
def read_root():
    return {"Hello": "server is running successfully"}


@app.post("/embeddings")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
        
        music_embeddings = embeddings.getEmbeddings(file.filename)

        return {"message": f"Successfully uploaded {file.filename}", "embeddings": music_embeddings, "filename": file.filename}

    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()