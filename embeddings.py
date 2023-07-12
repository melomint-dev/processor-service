from typing import List, Dict
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import librosa
from sklearn.metrics.pairwise import cosine_similarity
import math

import json


# def split_into_sub_embeddings(embeddings, sub_embedding_size):
#     n_sub_embeddings = embeddings.shape[0] // sub_embedding_size
#     return np.array_split(embeddings[:n_sub_embeddings * sub_embedding_size], n_sub_embeddings)


def hello():
    print("Hello World")
    return "Hello World"


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


# def main():
#     tf.compat.v1.disable_eager_execution()  # Disable eager execution

#     with tf.Graph().as_default():
#         model = hub.load('https://tfhub.dev/google/vggish/1')

#         # Load the first audio file
#         waveform1, sample_rate1 = librosa.load("1.wav", sr=16000, mono=True, dtype=np.float32)
#         waveform_tensor1 = tf.convert_to_tensor(waveform1, dtype=tf.float32)
#         embeddings1 = model(waveform_tensor1)

#         # Load the second audio file
#         waveform2, sample_rate2 = librosa.load("2.wav", sr=16000, mono=True, dtype=np.float32)
#         waveform_tensor2 = tf.convert_to_tensor(waveform2, dtype=tf.float32)
#         embeddings2 = model(waveform_tensor2)

#         with tf.compat.v1.Session() as sess:
#             sess.run(tf.compat.v1.global_variables_initializer())

#             embeddings1_np,embeddings2_np  = sess.run([embeddings1,embeddings2])


#         print(embeddings1_np.shape)
#         # print(embeddings2_np.shape)

#         sub_embedding_size = 10
#         sub_embeddings1 = split_into_sub_embeddings(embeddings1_np, sub_embedding_size)
#         # sub_embeddings2 = split_into_sub_embeddings(embeddings2_np, sub_embedding_size)

#         print(len(sub_embeddings1))
#         # print(len(sub_embeddings2))

#         # similarity_matrix = calculate_similarity_matrix(sub_embeddings1, sub_embeddings2)
#         # print(similarity_matrix)
#         # print(similarity_matrix.shape)


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
        # sub_embeddings1 = split_into_sub_embeddings(embeddings1_np, sub_embedding_size)

        # print(len(sub_embeddings1))

        return embeddings1_np.tolist()


def main():
    get_embeddings_and_calculate_similarity_with_prev_songs()


if __name__ == "__main__":
    main()
