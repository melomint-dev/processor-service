from typing import List, Dict
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
from sklearn.metrics.pairwise import cosine_similarity
import math

import json


def split_into_sub_embeddings(embeddings, sub_embedding_size):
    n_sub_embeddings = math.ceil(len(embeddings) / sub_embedding_size)
    remainder = len(embeddings) % sub_embedding_size
    if remainder > 0:
        padding = np.zeros(
            (sub_embedding_size - remainder, embeddings.shape[1]), dtype=np.float32
        )
        embeddings = np.vstack((embeddings, padding))
    return np.array_split(embeddings, n_sub_embeddings)


def calculate_similarity_matrix(embeddings1, embeddings2):
    similarity_matrix = np.zeros((len(embeddings1), len(embeddings2)))
    for i, embedding1 in enumerate(embeddings1):
        for j, embedding2 in enumerate(embeddings2):
            similarity = cosine_similarity(embedding1, embedding2)[0, 0]
            similarity_matrix[i, j] = similarity
    return similarity_matrix


def get_embeddings_and_calculate_similarity_with_prev_songs(
    current_song_filename: str, prev_songs_data: List[Dict[str, any]]
):
    tf.compat.v1.disable_eager_execution()  # Disable eager execution

    with tf.Graph().as_default():
        model = hub.load("https://tfhub.dev/google/vggish/1")

        # Load the first audio file
        waveform1, sample_rate1 = librosa.load(
            current_song_filename, sr=16000, mono=True, dtype=np.float32
        )

        waveform_tensor1 = tf.convert_to_tensor(waveform1, dtype=tf.float32)
        embeddings1 = model(waveform_tensor1)

        with tf.compat.v1.Session() as sess:
            sess.run(tf.compat.v1.global_variables_initializer())

            embeddings1_np = sess.run(embeddings1)

        print(embeddings1_np.shape)

        sub_embedding_size = 10

        # split the current song embeddings into sub embeddings
        sub_embeddings_curr_song = split_into_sub_embeddings(
            embeddings1_np, sub_embedding_size
        )

        # this object will store the highest similarity score found of the current sub embeddings with the previous songs
        similarity_scores = Dict[str, float]
        similarity_scores_song_ids = Dict[str, str]
        similarity_scores_song_embedding_keys = Dict[str, int]

        # initialize the similarity scores with 0 for all indices of the sub embeddings
        similarity_scores = {str(i): 0 for i in range(len(sub_embeddings_curr_song))}

        # initialize the similarity scores song ids with empty string
        similarity_scores_song_ids = {
            str(i): "" for i in range(len(sub_embeddings_curr_song))
        }

        # initialize the similarity scores song embedding key with -1
        similarity_scores_song_embedding_keys = {
            str(i): -1 for i in range(len(sub_embeddings_curr_song))
        }

        # iterate over the previous songs data
        for song_data in prev_songs_data:
            # get the embeddings of the previous song
            prev_song_embeddings = song_data["embeddings"]

            prev_song_np = np.array(prev_song_embeddings)

            sub_embeddings1 = sub_embeddings_curr_song
            sub_embeddings2 = split_into_sub_embeddings(
                prev_song_np, sub_embedding_size
            )

            # iterate over the embeddings and update the similarity scores

            for i, embedding1 in enumerate(sub_embeddings1):
                for j, embedding2 in enumerate(sub_embeddings2):
                    similarity = cosine_similarity(embedding1, embedding2)[0, 0]
                    if similarity > similarity_scores[str(i)]:
                        similarity_scores[str(i)] = similarity
                        similarity_scores_song_ids[str(i)] = song_data["song_id"]
                        similarity_scores_song_embedding_keys[str(i)] = j

        return {
            "similarity_scores": similarity_scores,
            "similarity_scores_song_ids": similarity_scores_song_ids,
            "similarity_scores_song_embedding_keys": similarity_scores_song_embedding_keys,
            "embeddings": embeddings1_np.tolist(),
        }


def main():
    get_embeddings_and_calculate_similarity_with_prev_songs()


if __name__ == "__main__":
    main()
